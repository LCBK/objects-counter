import os

import cv2
import numpy as np
import torch
from PIL import Image as PILImage
from torch import nn
from torchvision import transforms as tr

from image_segmentation.constants import TEMP_IMAGE_DIR, CENTROIDS_RGB, BW, A, SIGMA
from image_segmentation.utils import crop_element
from objects_counter.db.dataops.image import get_image_by_id
from objects_counter.db.models import ImageElement


class ImageElementProcessor:
    def __init__(self, feature_similarity_model, color_similarity_model):
        self.feature_similarity_model = feature_similarity_model
        self.color_similarity_model = color_similarity_model

    def process_image_element(self, element: ImageElement) -> tuple:
        """Crops, saves, computes embedding, computes histogram, and deletes element image."""
        image = get_image_by_id(element.image_id)
        image_data = np.array(PILImage.open(image.filepath[:-4] + "_processed.bmp"))

        cropped_image = crop_element(image_data, element.top_left, element.bottom_right)

        temp_image_path = os.path.join(TEMP_IMAGE_DIR, f"element_{element.id}.bmp")
        cropped_image.save(temp_image_path)

        embedding = self._calculate_embedding(temp_image_path)
        histogram = self._calculate_histogram(temp_image_path)

        os.remove(temp_image_path)
        return embedding, histogram

    def _calculate_embedding(self, image_path: str) -> torch.Tensor:
        """Calculates the embedding for the image at the given path."""
        image_tensor = self.feature_similarity_model.preprocess_image(image_path)
        return self.feature_similarity_model.get_embedding(image_tensor)

    def _calculate_histogram(self, image_path: str) -> np.ndarray:
        """Calculates the histogram for the image at the given path."""
        image = PILImage.open(image_path)
        return self.color_similarity_model.get_histogram(image)


class FeatureSimilarity:
    """Calculates feature similarities of the object using cosine similarity"""

    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()

    def load_model(self) -> nn.Module:
        """Loads a pretrained Vision Transformer model."""
        # todo: load from disk
        model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitg14_reg_lc')
        model = model.to(self.device)
        return model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocesses the image before embedding extraction."""
        img = PILImage.open(image_path).convert('RGB')
        transformations = tr.Compose([tr.ToTensor(), tr.Resize((518, 518), tr.InterpolationMode.BICUBIC),
                                      tr.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))])
        img = transformations(img).float().unsqueeze_(0).to(self.device)
        return img

    def get_embedding(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """Generates the embedding vector for the given image tensor."""
        with torch.no_grad():
            embedding = self.model(image_tensor)
        return embedding


class ColorSimilarity:
    """Calculates color similarities of the object using histograms"""

    ISCC_NBS_CENTROIDS_LUV = cv2.cvtColor(ISCC_NBS_CENTROIDS_RGB, cv2.COLOR_RGB2Luv).reshape(-1, 3)

    @staticmethod
    def compute_color_similarity(hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Computes the RGWHI similarity between two histograms."""
        raw_score = ColorSimilarity.__calculate_histogram_intersection(hist1, hist2)
        max_score = ColorSimilarity.__calculate_histogram_intersection(hist1, hist1)

        return ColorSimilarity.__normalize_score(raw_score, max_score)

    @staticmethod
    def __calculate_histogram_intersection(hist_model: np.ndarray, hist_target: np.ndarray) -> float:
        """Calculates the weighted intersection score between two histograms."""
        intersection_score = 0.0
        num_bins = len(hist_model)

        for i in range(num_bins):
            for j in range(num_bins):
                distance = ColorSimilarity.__color_distance(ColorSimilarity.ISCC_NBS_CENTROIDS_LUV[i],
                                                            ColorSimilarity.ISCC_NBS_CENTROIDS_LUV[j])
                weight = ColorSimilarity.__weight_function(distance)
                if weight > 0:
                    intersection_score += min(hist_model[i], hist_target[j]) * weight

        return intersection_score

    @staticmethod
    def __color_distance(c1: np.ndarray, c2: np.ndarray) -> float:
        """Computes the Euclidean distance between two colors in LUV space."""
        return np.sqrt(np.sum((c1 - c2) ** 2))

    @staticmethod
    def __weight_function(distance: float) -> float:
        """Applies a weight based on color distance, using a Gaussian function."""
        if distance <= BW:
            return (A / (np.sqrt(2 * np.pi) * SIGMA)) * np.exp(-distance ** 2 / (2 * SIGMA ** 2))
        return 0.0

    @staticmethod
    def __normalize_score(raw_score: float, max_score: float) -> float:
        """Normalizes the raw analysis score to a percentage."""
        return (raw_score / max_score) if max_score != 0 else 0.0

    @staticmethod
    def get_histogram(image: PILImage) -> np.ndarray:
        """Computes a color histogram for an image, ignoring white background pixels."""
        image = image.resize((256, 256))

        mask = ColorSimilarity.__get_mask(image)
        image = np.array(image)

        image = image.astype(np.float32) / 255.0
        image = cv2.cvtColor(image, cv2.COLOR_RGB2Luv)

        histogram = np.zeros(len(ColorSimilarity.ISCC_NBS_CENTROIDS_LUV))

        for i, pixel in enumerate(image.reshape(-1, 3)):
            if mask.reshape(-1)[i]:
                closest_index = ColorSimilarity.__find_closest_bin_color(pixel)
                histogram[closest_index] += 1

        histogram = histogram / np.sum(histogram)
        return histogram

    @staticmethod
    def __get_mask(image: PILImage):
        image = image.convert('RGB')
        mask = np.array(
            [not (np.array(image)[x][y] == np.array([255, 255, 255])).all() for x in range(image.height) for y in
             range(image.width)])
        mask.resize(image.height, image.width)
        return mask

    @staticmethod
    def __find_closest_bin_color(pixel_luv: np.ndarray) -> int:
        """Finds the index of the closest ISCC-NBS color centroid in LUV space."""
        distances = np.sqrt(np.sum((ColorSimilarity.ISCC_NBS_CENTROIDS_LUV - pixel_luv) ** 2, axis=1))
        return np.argmin(distances)
