import os
from typing import List, Dict
import logging
import numpy as np
import torch

from image_segmentation.constants import TEMP_IMAGE_DIR, DEFAULT_COLOR_WEIGHT
from image_segmentation.object_classification.feature_extraction import FeatureSimilarity, ImageElementProcessor, \
    ColorSimilarity
from image_segmentation.utils import delete_temp_images
from objects_counter.db.dataops.image import update_element_classification_by_id
from objects_counter.db.models import Image, ImageElement
from statistics import mean

log = logging.getLogger(__name__)


class ObjectClassifier:

    def __init__(self, segmenter, feature_similarity_model: FeatureSimilarity, color_similarity_model: ColorSimilarity):
        self.segmenter = segmenter
        self.feature_similarity_model = feature_similarity_model
        self.color_similarity_model = color_similarity_model

        self.embeddings: Dict[int, List[torch.Tensor]] = {}
        self.histograms: Dict[int, List[np.ndarray]] = {}

        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

    def process_image_elements(self, image: Image) -> None:
        """Processes each object in the image to compute embeddings and histograms."""
        for element in image.elements:
            self.process_element(element)

    def process_element(self, element: ImageElement) -> None:
        """Crops the image element, computes its embedding and histogram, and cleans up."""
        # Here we assume the ImageElementProcessor has been instantiated as a class member
        processor = ImageElementProcessor(self.feature_similarity_model, self.color_similarity_model)
        embedding, histogram = processor.process_image_element(element)
        self.embeddings[element.id] = embedding
        self.histograms[element.id] = histogram

    def calculate_similarity(self, obj_i: ImageElement, obj_j: ImageElement,
                             color_weight: float = DEFAULT_COLOR_WEIGHT) -> float:
        """Calculates combined feature and color similarity between two objects."""
        if self.histograms and self.embeddings:
            hist_i = self.histograms[obj_i.id]
            hist_j = self.histograms[obj_j.id]

            embedding_i = self.embeddings[obj_i.id]
            embedding_j = self.embeddings[obj_j.id]
        else:
            embedding_i, hist_i = self.process_element(obj_i)
            embedding_j, hist_j = self.process_element(obj_j)

        # pylint: disable=not-callable
        feature_sim = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_sim = self.color_similarity_model.compute_color_similarity(hist_i, hist_j)

        return (color_weight * color_sim) + ((1 - color_weight) * feature_sim)

    def group_objects_by_similarity(self, image: Image, threshold: float = 0.7,
                                    color_weight: float = DEFAULT_COLOR_WEIGHT) -> None:
        """Groups objects by their similarity based on a combination of feature and color similarity."""
        self.process_image_elements(image)
        self.assign_categories_based_on_similarity(image, threshold, color_weight)
        delete_temp_images(TEMP_IMAGE_DIR)

    def preprocess_dataset(self, dataset):
        dataset.elements = [element for image in dataset.images for element in image.elements]
        for element in dataset.elements:
            if element.id not in self.histograms or element.id not in self.embeddings:
                self.process_element(element)
        dataset.representatives = [element for element in dataset.elements if element.is_leader]
        dataset.categories = [representative.classification for representative in dataset.representatives]
        dataset.category_count = {category: 0 for category in dataset.categories}
        for element in dataset.elements:
            dataset.category_count[element.classification] += 1
        dataset.preprocessed = True

    def classify_image_element_based_on_dataset(self, image_element, dataset):
        if not dataset.preprocessed:
            log.error("Please run preprocess_dataset() before using classification on dataset")

        classification_results = {category: [] for category in dataset.categories}
        for element in dataset.elements:
            classification_results[element.classification].append(self.calculate_similarity(image_element, element))
        classification = [[category, mean(classification_results[category])] for category in dataset.categories]
        classification = sorted(classification, key=lambda x: x[1], reverse=True)
        print(image_element.id, classification)
        return classification

    def classify_images_based_on_dataset(self, images: List[Image], dataset):
        """Classify images elements based on dataset"""
        self.preprocess_dataset(dataset)
        for image in images:
            self.process_image_elements(image)
        elements = [element for image in images for element in image.elements]
        result = {category: 0 for category in dataset.categories}
        for element in elements:
            classes_probabilities = self.classify_image_element_based_on_dataset(element, dataset)
            element.classification = classes_probabilities[0][0]
            element.certainty = classes_probabilities[0][1]
            result[element.classification] += 1
            element_dict_classification = {category: 0 for category in dataset.categories}
            for probability in classes_probabilities:
                element_dict_classification[probability[0]] = probability[1]
            element.probabilities = element_dict_classification

        result = {category: dataset.category_count[category] for category in dataset.categories}

        assigned_elements = []
        for _ in elements:
            best_candidates = {category: (None, 0) for category in dataset.categories}
            for element in elements:
                if element in assigned_elements:
                    continue
                for category in dataset.categories:
                    best_result = -1
                    for compared_category in dataset.categories:
                        probabilities = element.probabilities
                        best_result = max(best_result, probabilities[category] - probabilities[compared_category])
                    if best_candidates[category][0] is None or best_candidates[category][1] < best_result:
                        best_candidates[category] = (element, best_result)
            current_candidate = (None, 0, None)
            for category in dataset.categories:
                if result[category] == 0:
                    continue
                if current_candidate[0] is None or current_candidate[1] < best_candidates[category][1]:
                    current_candidate = (best_candidates[category][0], best_candidates[category][1], category)
            if current_candidate[0] is not None:
                element = current_candidate[0]
                category = current_candidate[2]
                certainty = element.probabilities[category]
                assigned_elements.append(element)
                element.classification = category
                element.certainty = certainty
                result[category] -= 1

        for element in elements:
            if element in assigned_elements:
                continue
            result[element.classification] -= 1

        result = {category: dataset.category_count[category] - result[category] for category in dataset.categories}

        return result




    def assign_dataset_categories_to_image(self, image: Image, dataset):
        """Assigns categories based on dataset and image representatives. Meant to be used DURING dataset creation"""
        self.preprocess_dataset(dataset)
        self.process_image_elements(image)
        image_representatives = [element for element in image.elements if element.is_leader]
        representatives = image_representatives + dataset.representatives
        for element in image.elements:
            best_certainty = 0
            best_category = None
            for representative in representatives:
                current_certainty = self.calculate_similarity(element, representative)
                if current_certainty > best_certainty:
                    best_category = representative.classification
                    best_certainty = current_certainty
                assert best_category is not None
                self.update_element_category(element.id, best_category, best_certainty)

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
