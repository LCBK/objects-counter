import os

import cv2
import numpy as np
import torch
from PIL import Image as PILImage
from scipy.spatial import distance
from torch import nn
from torchvision import transforms as tr

from image_segmentation.constants import TEMP_IMAGE_DIR
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
        image_data = np.array(PILImage.open(image.filepath[:-4] + "_processed" + image.filepath[-4:]))

        cropped_image = crop_element(image_data, element.top_left, element.bottom_right)

        temp_image_path = os.path.join(TEMP_IMAGE_DIR, f"element_{element.id}.jpg")
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
        return self.color_similarity_model.compute_color_histogram(image, bins=8)


class FeatureSimilarity:
    """Calculates feature similarities of the object using cosine similarity"""

    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()

    def load_model(self) -> nn.Module:
        """Loads a pretrained Vision Transformer model."""
        model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitg14_reg_lc')
        model = model.to(self.device)
        return model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocesses the image before embedding extraction."""
        img = PILImage.open(image_path)
        transformations = tr.Compose(
            [tr.ToTensor(), tr.Resize((224, 224), tr.InterpolationMode.BICUBIC),
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

    @staticmethod
    def compute_color_histogram(image: PILImage, bins: int = 16) -> np.ndarray:
        """Computes a color histogram for an image."""
        image = image.convert('RGB')
        histogram = cv2.calcHist([np.array(image)], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
        histogram = cv2.normalize(histogram, histogram, 1.0, 0.0, cv2.NORM_L1)

        return histogram

    @staticmethod
    def compute_color_similarity(hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Calculates the Bray-Curtis distance between two histograms."""
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)
