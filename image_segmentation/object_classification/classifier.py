import os
from typing import List

import numpy as np
import torch

from PIL import Image as PILImage

from image_segmentation.constants import TEMP_IMAGE_DIR
from image_segmentation.object_classification.feature_extraction import CosineSimilarity, compute_color_histogram, \
    compute_color_similarity
from image_segmentation.utils import crop_image, delete_temp_images
from objects_counter.db.dataops.image import update_element_classification
from objects_counter.db.models import Image, ImageElement


class ObjectClassifier:

    def __init__(self, segmenter, similarity_model: CosineSimilarity):
        self.segmenter = segmenter
        self.similarity_model = similarity_model
        self.embeddings: List[torch.Tensor] = []
        self.analyzed_images = set()

        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

    def crop_objects(self, image: Image) -> None:
        """Crops detected objects from the image and saves them to the temporary directory."""
        image_data = np.array(PILImage.open(image.filepath))
        objects = image.elements

        for obj in objects:
            cropped_image = crop_image(image_data, obj.top_left, obj.bottom_right)
            cropped_image.save(os.path.join(TEMP_IMAGE_DIR, f"object_{obj.id}.jpg"))

    def compute_embeddings(self) -> None:
        """Computes embeddings for all cropped images."""
        for filename in sorted(os.listdir(TEMP_IMAGE_DIR)):
            image_tensor = self.similarity_model.preprocess_image(os.path.join(TEMP_IMAGE_DIR, filename))
            embedding = self.similarity_model.get_embedding(image_tensor)
            self.embeddings.append(embedding)

    def calculate_similarity(self, obj_i: ImageElement, obj_j: ImageElement, color_weight: float = 0.7) -> float:
        """Calculates combined feature and color similarity between two objects."""
        min_index = obj_i.image.elements[0].id

        hist_i = compute_color_histogram(PILImage.open(f"{TEMP_IMAGE_DIR}/object_{obj_i.id}.jpg"))
        hist_j = compute_color_histogram(PILImage.open(f"{TEMP_IMAGE_DIR}/object_{obj_j.id}.jpg"))

        embedding_i = self.embeddings[obj_i.id - min_index]
        embedding_j = self.embeddings[obj_j.id - min_index]

        # pylint: disable=not-callable
        feature_sim = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_sim = compute_color_similarity(hist_i, hist_j)

        return (color_weight * color_sim) + ((1 - color_weight) * feature_sim)

    def group_objects_by_similarity(self, image: Image, threshold: float = 0.7, color_weight: float = 0.7) -> None:
        """Groups objects by their similarity based on a combination of feature and color similarity."""
        delete_temp_images(TEMP_IMAGE_DIR)
        self.crop_objects(image)
        self.compute_embeddings()
        self.assign_categories_based_on_similarity(image, threshold, color_weight)
        delete_temp_images(TEMP_IMAGE_DIR)

    def assign_categories_based_on_similarity(self, image: Image, threshold, color_weight):
        """Assigns objects to categories based on their similarity scores."""
        objects = image.elements
        num_objects = len(objects)

        category_id = 1

        for index_i in range(num_objects):
            obj_i = objects[index_i]
            if obj_i.id in self.analyzed_images:
                continue

            if not obj_i.classification:
                bbox = obj_i.top_left, obj_i.bottom_right
                update_element_classification(bbox, f"{category_id}", 1.0)
                self.analyzed_images.add(obj_i.id)

            for index_j in range(index_i + 1, num_objects):
                obj_j = objects[index_j]
                combined_similarity = self.calculate_similarity(obj_i, obj_j, color_weight)

                if combined_similarity >= threshold:
                    self.add_object_to_category(obj_j, combined_similarity, category_id)

            category_id += 1

    def add_object_to_category(self, new_object, similarity, category_id):
        """Adds an object to a category or updates its similarity if already present in another category."""

        # Check if the object already has a classification
        if new_object.classification:
            # If it already has a classification, check if we should update it
            if similarity > new_object.certainty:
                # Update the classification and certainty if the new similarity is higher
                bbox = new_object.top_left, new_object.bottom_right
                update_element_classification(bbox, f"{category_id}", similarity)
        else:
            # If the object doesn't have a classification, assign it
            bbox = new_object.top_left, new_object.bottom_right
            update_element_classification(bbox, f"{category_id}", similarity)

        self.analyzed_images.add(new_object.id)
