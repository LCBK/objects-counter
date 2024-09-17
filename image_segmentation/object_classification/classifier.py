import os
from typing import List

import numpy as np
import torch
from PIL import Image

from .feature_extraction import CosineSimilarity, compute_color_histogram, compute_color_similarity
from ..constants import TEMP_IMAGE_DIR
from ..object_detection.object_segmentation import Object
from ..utils import crop_image


class ObjectClassifier:

    def __init__(self, segmenter, similarity_model: CosineSimilarity):
        self.segmenter = segmenter
        self.similarity_model = similarity_model
        self.embeddings: List[torch.Tensor] = []
        self.analyzed_images = set()

        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

    def crop_objects(self, image: Image) -> None:
        """Crops detected objects from the image and saves them to the temporary directory."""
        image_data = np.array(Image.open(image.filepath))
        objects = image.categories[0]

        for obj in objects:
            cropped_image = crop_image(image_data, obj.top_left_coord, obj.bottom_right_coord)
            cropped_image.save(os.path.join(TEMP_IMAGE_DIR, f"object_{obj.index}.jpg"))

    def compute_embeddings(self) -> None:
        """Computes embeddings for all cropped images."""
        for filename in sorted(os.listdir(TEMP_IMAGE_DIR)):
            image_tensor = self.similarity_model.preprocess_image(os.path.join(TEMP_IMAGE_DIR, filename))
            embedding = self.similarity_model.get_embedding(image_tensor)
            self.embeddings.append(embedding)

    def calculate_similarity(self, index_i: int, index_j: int, color_weight: float = 0.7) -> float:
        """Calculates combined feature and color similarity between two objects."""
        hist_i = compute_color_histogram(Image.open(f"{TEMP_IMAGE_DIR}/object_{index_i}.jpg"))
        hist_j = compute_color_histogram(Image.open(f"{TEMP_IMAGE_DIR}/object_{index_j}.jpg"))

        embedding_i = self.embeddings[index_i]
        embedding_j = self.embeddings[index_j]

        # pylint: disable=not-callable
        feature_sim = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_sim = compute_color_similarity(hist_i, hist_j)

        return (color_weight * color_sim) + ((1 - color_weight) * feature_sim)

    def group_objects_by_similarity(self, image: Image, threshold: float = 0.7, color_weight: float = 0.7) -> None:
        """Groups objects by their similarity based on a combination of feature and color similarity."""
        self.crop_objects(image)
        self.compute_embeddings()
        self.assign_categories_based_on_similarity(threshold, color_weight)

    def assign_categories_based_on_similarity(self, image: Image, threshold, color_weight):
        """Assigns objects to categories based on their similarity scores."""
        objects = image.categories[0]

        num_objects = len(self.embeddings)
        category_id = 0
        categories = []

        for index_i in range(num_objects):
            if index_i in self.analyzed_images:
                continue

            new_category = [
                Object(
                    objects[index_i].index,
                    objects[index_i].top_left_coord,
                    objects[index_i].bottom_right_coord,
                    probability=1.0)]

            categories.append(new_category)
            self.analyzed_images.add(index_i)

            for index_j in range(index_i + 1, num_objects):
                combined_similarity = self.calculate_similarity(index_i, index_j, color_weight)

                if combined_similarity >= threshold:
                    self.add_object_to_category(objects[index_j], combined_similarity, category_id, categories)

            category_id += 1

        image.categories = categories

    def add_object_to_category(self, new_object, similarity, category_id, categories):
        """Adds an object to a category or updates its similarity if already present in another category."""

        # Check if the object already exists in another category
        for cat_id, category in enumerate(categories):
            if cat_id == category_id:
                continue

            for i, obj in enumerate(category):
                if obj.index == new_object.index:
                    # Update similarity if the new one is higher, or skip
                    if similarity > obj.probability:
                        category.pop(i)  # Remove the object from the current category
                        break
                    else:
                        return

        # Add the object to the current category
        new_object.probability = similarity
        categories[category_id].append(new_object)
        self.analyzed_images.add(new_object.index)
