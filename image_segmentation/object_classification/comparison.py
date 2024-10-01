import logging
import os
from typing import List, Dict, Tuple, Any

import numpy as np
from PIL import Image as PILImage

from image_segmentation.constants import TEMP_IMAGE_DIR
from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.utils import crop_element
from objects_counter.db.models import Image, ImageElement

log = logging.getLogger(__name__)


def load_image(filepath: str) -> np.ndarray:
    """
    Loads an image from the given filepath and returns it as a NumPy array.
    """
    try:
        return np.array(PILImage.open(filepath))
    except FileNotFoundError as e:
        log.error(f"Image file not found: {e}")
        return None


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


def crop_and_save_object(image_data: np.ndarray, element: ImageElement, category: str) -> bool:
    """
    Crops and saves the image element.
    Returns True if saved successfully, otherwise False.
    """
    if image_data is None:
        return False

    cropped_image = crop_element(image_data, element.top_left, element.bottom_right)
    if cropped_image is None:
        return False

    filepath = os.path.join(TEMP_IMAGE_DIR, f"object_{element.id}")
    cropped_image.save(filepath)
    return True


def process_image_elements(image: Image) -> List[ImageElement]:
    """
    Processes the image elements by cropping and saving the first object from each classification category.
    Returns a list of the processed ImageElement objects.
    """
    image_data = load_image(image.filepath)
    if image_data is None:
        return []

    grouped_elements = group_elements_by_classification(image.elements)
    processed_elements = []

    for classification, elements in grouped_elements.items():
        if elements:
            first_element = elements[0]
            if crop_and_save_object(image_data, first_element, classification):
                processed_elements.append(first_element)

    return processed_elements


def crop_and_save_images(image_1: Image, image_2: Image) -> Tuple[List[ImageElement], List[ImageElement]]:
    """
    Crops and saves the first object from each classification category in image_1 and image_2.
    Returns the indices of processed objects for each image.
    """
    first_elements_1 = process_image_elements(image_1)
    first_elements_2 = process_image_elements(image_2)
    return first_elements_1, first_elements_2


def compare_number_of_elements(image_1: Image, image_2: Image) -> bool:
    """
    Compares the number of objects between two images.
    Returns True if they match, otherwise False.
    """
    num_elements_image_1 = len(image_1.elements)
    num_elements_image_2 = len(image_2.elements)

    log.info("Number of elements in image 1: %s", num_elements_image_1)
    log.info("Number of elements in image 2: %s", num_elements_image_2)

    return num_elements_image_1 == num_elements_image_2


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
            similarity = classifier.calculate_similarity(elem1, elem2, color_weight=color_weight)

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
    # Check if the number of categories match
    categories_image_1 = set(element.classification for element in image_1.elements if element.classification)
    categories_image_2 = set(element.classification for element in image_2.elements if element.classification)

    if len(categories_image_1) != len(categories_image_2):
        log.error("Number of categories does not match between the two images.")
        return {"status": "error", "message": "Number of categories mismatch"}

    # Log and compare the total number of elements even though the comparison will occur regardless
    compare_number_of_elements(image_1, image_2)

    # Get the ImageElement objects from the cropped images
    elements_1, elements_2 = crop_and_save_images(image_1, image_2)

    if not elements_1 or not elements_2:
        log.error("Failed to retrieve object elements from the images.")
        return {"status": "error", "message": "Failed to retrieve object elements from images"}

    mapping = compute_similarity_and_map(classifier, elements_1, elements_2, threshold=0.7, color_weight=0.8)

    missing_elements = []

    # Identify mismatches in counts
    for idx1, elem1 in enumerate(elements_1):
        if idx1 in mapping:
            # Retrieve the mapped element from image_2 using the mapping
            mapped_idx2 = mapping[idx1]
            mapped_element_2 = elements_2[mapped_idx2]

            # Calculate the number of elements with the same classification in image_1
            category_1_size = sum(1 for element in image_1.elements if element.classification == elem1.classification)

            # Calculate the number of elements with the same classification in image_2
            category_2_size = sum(1 for element in image_2.elements if element.classification == mapped_element_2.classification)

            # Check if the count of elements differs between the two categories
            if category_1_size != category_2_size:
                missing_elements.append({
                    "category_image_1": elem1.classification,  # Classification name instead of idx1
                    "count_image_1": category_1_size,
                    "category_image_2": mapped_element_2.classification,
                    "count_image_2": category_2_size,
                })

    return {"status": "success", "missing_elements": missing_elements}
