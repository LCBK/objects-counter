import os
from typing import List, Dict

import numpy as np
import torch

from image_segmentation.constants import TEMP_IMAGE_DIR
from image_segmentation.object_classification.feature_extraction import FeatureSimilarity, ImageElementProcessor, \
    ColorSimilarity
from image_segmentation.utils import delete_temp_images
from objects_counter.db.dataops.image import update_element_classification_by_id
from objects_counter.db.models import Image, ImageElement


class ObjectClassifier:

    def __init__(self, segmenter, feature_similarity_model: FeatureSimilarity, color_similarity_model: ColorSimilarity):
        self.segmenter = segmenter
        self.feature_similarity_model = feature_similarity_model
        self.color_similarity_model = color_similarity_model

        self.embeddings: Dict[int, List[torch.Tensor]] = {}
        self.histograms: Dict[int, List[np.ndarray]] = {}

        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

    def process_elements(self, image: Image) -> None:
        """Processes each object in the image to compute embeddings and histograms."""
        for element in image.elements:
            embedding, histogram = self.process_image_element(image)
            self.embeddings[element.id] = embedding
            self.histograms[element.id] = histogram

    def process_image_element(self, element: ImageElement) -> tuple:
        """Crops the image element, computes its embedding and histogram, and cleans up."""
        # Here we assume the ImageElementProcessor has been instantiated as a class member
        processor = ImageElementProcessor(self.feature_similarity_model, self.color_similarity_model)
        return processor.process_image_element(element)

    def calculate_similarity(self, obj_i: ImageElement, obj_j: ImageElement, color_weight: float = 0.7) -> float:
        """Calculates combined feature and color similarity between two objects."""
        if self.histograms and self.embeddings:
            hist_i = self.histograms[obj_i.id]
            hist_j = self.histograms[obj_j.id]

            embedding_i = self.embeddings[obj_i.id]
            embedding_j = self.embeddings[obj_j.id]
        else:
            embedding_i, hist_i = self.process_image_element(obj_i)
            embedding_j, hist_j = self.process_image_element(obj_j)

        # pylint: disable=not-callable
        feature_sim = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_sim = self.color_similarity_model.compute_color_similarity(hist_i, hist_j)

        return (color_weight * color_sim) + ((1 - color_weight) * feature_sim)

    def group_objects_by_similarity(self, image: Image, threshold: float = 0.7, color_weight: float = 0.7) -> None:
        """Groups objects by their similarity based on a combination of feature and color similarity."""
        self.process_elements(image)
        self.assign_categories_based_on_similarity(image, threshold, color_weight)
        delete_temp_images(TEMP_IMAGE_DIR)

    def assign_categories_based_on_similarity(self, image: Image, threshold: float, color_weight: float) -> None:
        """Assigns elements to categories based on their similarity scores."""
        elements = image.elements
        num_elements = len(elements)
        analyzed_elements = set()
        category_id = 1

        for index_i in range(num_elements):
            element_i = elements[index_i]

            if element_i.id in analyzed_elements:
                continue

            if not element_i.classification:
                self.update_element_category(element_i.id, category_id, certainty=1.0)
                analyzed_elements.add(element_i.id)

            for index_j in range(index_i + 1, num_elements):
                element_j = elements[index_j]
                similarity_score = self.calculate_similarity(element_i, element_j, color_weight)

                if similarity_score >= threshold:
                    self.assign_element_to_category(element_j, similarity_score, category_id)
                    analyzed_elements.add(element_j.id)

            category_id += 1

    def assign_element_to_category(self, element: ImageElement, similarity: float, category_id: int) -> None:
        """Assigns an element to a category or updates its similarity score if already classified."""
        if element.classification:
            if similarity > element.certainty:
                self.update_element_category(element.id, category_id, similarity)
        else:
            self.update_element_category(element.id, category_id, similarity)

    def update_element_category(self, element_id: int, category_id: int, certainty: float) -> None:
        """Updates the classification and certainty of an element based on its ID."""
        update_element_classification_by_id(element_id, str(category_id), certainty)
