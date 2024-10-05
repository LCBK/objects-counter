import logging
from typing import List, Dict, Any, Tuple

from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.utils import display_element
from objects_counter.db.models import Image, ImageElement

log = logging.getLogger(__name__)


def group_elements_by_classification(elements: List[ImageElement]) -> Dict[str, List[ImageElement]]:
    """
    Groups ImageElements by their classification.
    """
    grouped_elements = {}
    for element in elements:
        classification = element.classification
        if classification not in grouped_elements:
            grouped_elements[classification] = []
        grouped_elements[classification].append(element)
    return grouped_elements


def compute_similarity_and_map(classifier, elements_1: List[ImageElement], elements_2: List[ImageElement],
                               threshold: float = 0.7, color_weight: float = 0.8) -> Dict[int, int]:
    """
    Computes the similarity between the first objects from image_1 and image_2, and updates the category mapping.
    """
    similarity_map = {}

    for idx1, elem1 in enumerate(elements_1):
        max_similarity = float('-inf')
        best_match_idx = None

        for idx2, elem2 in enumerate(elements_2):
            similarity = classifier.calculate_similarity(elem1[1], elem2[1], color_weight=color_weight)

            if similarity > max_similarity and similarity >= threshold:
                max_similarity = similarity
                best_match_idx = idx2

        if best_match_idx is not None:
            similarity_map[idx1] = best_match_idx

    return similarity_map


def find_missing_elements(image_1: Image, image_2: Image, classifier: ObjectClassifier) -> Dict[str, Any]:
    """
    Identifies and reports all missing elements between two images.
    Returns a structured result including all discrepancies found.
    """
    elements_1 = get_elements_with_certainty_one(image_1.elements)
    elements_2 = get_elements_with_certainty_one(image_2.elements)

    if not elements_1 or not elements_2:
        log.error("Failed to retrieve object elements from the images.")
        return {"status": "error", "message": "Failed to retrieve object elements from images"}

    if len(elements_1) != len(elements_2):
        log.error("Number of categories does not match between the two images.")
        return {"status": "error", "message": "Number of categories mismatch"}

    mapping = compute_similarity_and_map(classifier, elements_1, elements_2, threshold=0.7, color_weight=0.8)

    missing_elements = []

    for i, (classification_1, element_1) in enumerate(elements_1):
        if i in mapping:
            mapped_index_2 = mapping[i]

            element_2 = elements_2[mapped_index_2]
            classification_2 = element_2[0]

            category_1_size = sum(1 for element in image_1.elements if element.classification == classification_1)
            category_2_size = sum(1 for element in image_2.elements if element.classification == classification_2)

            if category_1_size != category_2_size:
                display_element(element_1)
                display_element(element_2)
                missing_elements.append({"category_image_1": classification_1, "count_image_1": category_1_size,
                                         "category_image_2": classification_2, "count_image_2": category_2_size})

    return {"status": "success", "missing_elements": missing_elements}


def get_elements_with_certainty_one(elements: List[ImageElement]) -> [List[Tuple[int, ImageElement]]]:
    result = []
    classifications_seen = set()

    for element in elements:
        if element.certainty == 1.0 and element.classification not in classifications_seen:
            result.append((element.classification, element))
            classifications_seen.add(element.classification)

    return result if result else None
