# pylint: disable-all
import os
from collections import defaultdict
from typing import List, Tuple

import cv2
import numpy as np
import torch
import torchvision
from PIL import Image
from scipy.spatial import distance
from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14

from image_segmentation.segment_anything_object_counter import Object


class CosineSimilarity:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()

    def load_model(self) -> nn.Module:
        weights = torchvision.models.ViT_H_14_Weights.DEFAULT
        model = vit_h_14(weights=weights)
        model.heads = nn.Sequential(*list(model.heads.children())[:-1])
        model = model.to(self.device)
        return model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        img = Image.open(image_path)
        transformations = tr.Compose(
            [tr.ToTensor(), tr.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), tr.Resize((518, 518))])
        img = transformations(img).float()
        img = img.unsqueeze_(0).to(self.device)
        return img


class ObjectClassifier:
    TEMP_IMAGE_DIR = "images/temp"

    def __init__(self, segmenter, similarity_model: CosineSimilarity, image_index: int = 0):
        self.segmenter = segmenter
        self.similarity_model = similarity_model
        self.image_index = image_index

        self.embeddings: List[torch.Tensor] = []
        self.analyzed_images = set()

        if not os.path.exists(self.TEMP_IMAGE_DIR):
            os.makedirs(self.TEMP_IMAGE_DIR)

    @staticmethod
    def compute_color_histogram(image: Image.Image, bins: int = 16) -> np.ndarray:
        """Computes the color histogram of an image."""
        image = image.convert('RGB')
        histogram = []

        # Calculate histogram for each channel
        for channel in range(3):
            channel_hist = cv2.calcHist([np.array(image)], [channel], None, [bins], [0, 256])
            channel_hist = cv2.normalize(channel_hist, channel_hist).flatten()
            histogram.append(channel_hist)

        return np.concatenate(histogram)

    @staticmethod
    def compute_color_similarity(hist1: np.ndarray, hist2: np.ndarray) -> float:
        """ Computes the color similarity between two histograms. """
        return 1 - distance.braycurtis(hist1, hist2)

    @staticmethod
    def crop_image(image: np.ndarray, bbox: Tuple[Tuple[int, int], Tuple[int, int]]) -> Image.Image:
        """Crops a single object from the image using the bounding box."""
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        (x_min, y_min), (x_max, y_max) = bbox
        return pil_image.crop((x_min, y_min, x_max, y_max))

    def load_image_from_temp(self, index: int) -> np.ndarray:
        """Load an image from the temp directory given its index."""
        filename = f"object_{index}.jpg"
        temp_path = os.path.join(self.TEMP_IMAGE_DIR, filename)
        image = Image.open(temp_path)
        return image

    def save_cropped_image(self, cropped_image: Image.Image, index: int) -> None:
        """Saves the cropped object image to the temp directory with a unique filename."""
        image_path = os.path.join(self.TEMP_IMAGE_DIR, f"object_{index}.jpg")
        cropped_image.save(image_path)

    def delete_images_from_temp_directory(self) -> None:
        """Deletes image files from the specified temporary directory."""

        for filename in os.listdir(self.TEMP_IMAGE_DIR):
            file_path = os.path.join(self.TEMP_IMAGE_DIR, filename)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    def crop_objects_from_images(self) -> None:
        """Crops objects from the specified image and saves them to the temp directory."""
        image_data = self.segmenter.images[self.image_index]
        objects = image_data.categories[0]

        # Check if objects have been found - initially all the objects are stored in first category
        if not image_data.categories or not image_data.categories[0]:
            return []

        for obj in objects:
            bbox = (obj.top_left_coord, obj.bottom_right_coord)
            cropped_image = self.crop_image(image_data.data, bbox)
            self.save_cropped_image(cropped_image, obj.index)

    def compute_embeddings_for_cropped_objects(self) -> None:
        """Computes and stores embeddings for all cropped object images."""
        for filename in sorted(os.listdir(self.TEMP_IMAGE_DIR)):
            temp_path = os.path.join(self.TEMP_IMAGE_DIR, filename)
            image_tensor = self.similarity_model.preprocess_image(temp_path)

            with torch.no_grad():
                embedding = self.similarity_model.model(image_tensor).cpu()

            self.embeddings.append(embedding)

    def calculate_combined_similarity(self, index_i: int, index_j: int, color_weight: float) -> float:
        """Calculate combined similarity between two images based on their indices."""
        image_i = self.load_image_from_temp(index_i)
        image_j = self.load_image_from_temp(index_j)

        hist_i = self.compute_color_histogram(image_i)
        hist_j = self.compute_color_histogram(image_j)

        embedding_i = self.embeddings[index_i]
        embedding_j = self.embeddings[index_j]

        # pylint: disable=not-callable
        feature_similarity = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_similarity = self.compute_color_similarity(hist_i, hist_j)

        combined_similarity = (color_weight * color_similarity) + ((1 - color_weight) * feature_similarity)

        return combined_similarity

    # TODO: write a better algorithm for assigning categories
    def assign_categories_based_on_similarity(self, threshold: float, color_weight: float):
        """Assigns objects to categories based on their similarity and returns the result."""
        image = self.segmenter.images[self.image_index]
        objects = image.categories[0]

        num_objects = len(self.embeddings)
        category_id = 0

        categories = []

        for index_i in range(num_objects):
            if index_i in self.analyzed_images:
                continue

            new_category = []
            obj_i = objects[index_i]
            new_category.append(Object(
                obj_i.index,
                obj_i.top_left_coord,
                obj_i.bottom_right_coord,
                probability=1.0))

            categories.append(new_category)
            self.analyzed_images.add(index_i)

            for index_j in range(index_i + 1, num_objects):
                combined_similarity = self.calculate_combined_similarity(index_i, index_j, color_weight)
                obj_j = objects[index_j]

                if combined_similarity >= threshold:
                    self.add_object_to_category(obj_j, combined_similarity, category_id, categories)

            category_id += 1

        self.segmenter.images[self.image_index].categories = categories

    def add_object_to_category(self, new_object: Object, similarity: float, category_id: int, categories: list):
        """Adds an image to a category or updates its similarity if it's already present in a category."""

        # Iterate through all categories to check if the image exists elsewhere
        for cat_id, category in enumerate(categories):
            if cat_id == category_id:
                continue

            # Look for the image in the current category
            for i, obj in enumerate(category):
                if obj.index == new_object.index:
                    if similarity > obj.probability:
                        # Remove the image from the previous category if the new similarity is better
                        category.pop(i)
                        break
                    else:
                        return

        # The object was not found in another category or the found object had a lower probability
        new_object.probability = similarity
        categories[category_id].append(new_object)
        self.analyzed_images.add(new_object.index)

    def group_objects_by_similarity(self, threshold: float = 0.7, color_weight: float = 0.7) -> defaultdict:
        self.crop_objects_from_images()
        self.compute_embeddings_for_cropped_objects()
        self.assign_categories_based_on_similarity(threshold, color_weight)
        # self.delete_images_from_temp_directory()
