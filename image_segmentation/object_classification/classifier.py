import os
from typing import List, Dict

import numpy as np
import torch

from PIL import Image as PILImage

from image_segmentation.constants import TEMP_IMAGE_DIR
from image_segmentation.object_classification.feature_extraction import FeatureSimilarity, ImageElementProcessor
from image_segmentation.utils import delete_temp_images
from objects_counter.db.dataops.image import update_element_classification
from objects_counter.db.models import Image, ImageElement


class ObjectClassifier:

    def __init__(self, segmenter, feature_similarity_model: FeatureSimilarity):
        self.segmenter = segmenter
        self.similarity_model = feature_similarity_model

        self.embeddings: Dict[int, List[torch.Tensor]] = {}
        self.histograms: Dict[int, List[np.ndarray]] = {}

        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

    def classify_objects(self, image: ImageElement) -> None:
        """Processes each object in the image to compute embeddings and histograms."""
        for element in image.elements:
            embedding, histogram = ImageElementProcessor.process_image_element(element)
            self.embeddings[element.id] = embedding
            self.histograms[element.id] = histogram

    def calculate_similarity(self, obj_i: ImageElement, obj_j: ImageElement, color_weight: float = 0.7) -> float:
        """Calculates combined feature and color similarity between two objects."""
        hist_i = self.histograms[obj_i.id]
        hist_j = self.histograms[obj_j.id]

        embedding_i = self.embeddings[obj_i.id]
        embedding_j = self.embeddings[obj_j.id]

        # pylint: disable=not-callable
        feature_sim = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_sim = compute_color_similarity(hist_i, hist_j)

        return (color_weight * color_sim) + ((1 - color_weight) * feature_sim)

    def group_objects_by_similarity(self, image: Image, threshold: float = 0.7, color_weight: float = 0.7) -> None:
        """Groups objects by their similarity based on a combination of feature and color similarity."""
        self.crop_objects(image)
        self.compute_embeddings()
        self.compute_histograms()
        self.assign_categories_based_on_similarity(image, threshold, color_weight)
        delete_temp_images(TEMP_IMAGE_DIR)

    def assign_categories_based_on_similarity(self, image: Image, threshold, color_weight):
        """Assigns objects to categories based on their similarity scores."""
        objects = image.elements
        num_objects = len(objects)
        analyzed_objects = set()

        category_id = 1

        for index_i in range(num_objects):
            obj_i = objects[index_i]
            if obj_i.id in analyzed_objects:
                continue

            if not obj_i.classification:
                bbox = obj_i.top_left, obj_i.bottom_right
                update_element_classification(bbox, f"{category_id}", 1.0)
                analyzed_objects.add(obj_i.id)

            for index_j in range(index_i + 1, num_objects):
                obj_j = objects[index_j]
                combined_similarity = self.calculate_similarity(obj_i, obj_j, color_weight)

                if combined_similarity >= threshold:
                    self.add_object_to_category(obj_j, combined_similarity, category_id)
                    analyzed_objects.add(obj_j.id)

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
