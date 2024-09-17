import logging
import os
import sys
from typing import List, Dict, Tuple

import numpy as np
from PIL import Image

from image_segmentation.constants import TEMP_IMAGE_DIR
from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.utils import crop_image

log = logging.getLogger(__name__)


def compare_number_of_elements(image_1: Image, image_2: Image) -> bool:
    """
    Compares the number of objects between two images.
    Returns True if they match, otherwise False.
    """
    num_elements_image_1 = sum(len(category) for category in image_1.categories)
    num_elements_image_2 = sum(len(category) for category in image_2.categories)

    log.info(f"Number of elements in image 1: {num_elements_image_1}")
    log.info(f"Number of elements in image 2: {num_elements_image_2}")

    return num_elements_image_1 == num_elements_image_2


def crop_and_save_images(image_1: Image, image_2: Image) -> Tuple[List[int], List[int]]:
    """
    Crops and saves the first object from each category in image_1 and image_2, and returns their indices.
    """
    first_objects_1_indices = []
    first_objects_2_indices = []

    image_data_1 = np.array(Image.open(image_1.filepath))
    image_data_2 = np.array(Image.open(image_2.filepath))

    for i, cat in enumerate(image_1.categories):
        if len(cat) > 0:
            obj = cat[0]
            cropped_image = crop_image(image_data_1, obj.top_left_coord, obj.bottom_right_coord)
            filepath = os.path.join(TEMP_IMAGE_DIR, f"image_1_object_{i}.jpg")
            cropped_image.save(filepath)
            first_objects_1_indices.append(i)

    for i, cat in enumerate(image_2.categories):
        if len(cat) > 0:
            obj = cat[0]
            cropped_image = crop_image(image_data_2, obj.top_left_coord, obj.bottom_right_coord)
            filepath = os.path.join(TEMP_IMAGE_DIR, f"image_2_object_{i}.jpg")
            cropped_image.save(filepath)
            first_objects_2_indices.append(len(first_objects_1_indices) + i)

    return first_objects_1_indices, first_objects_2_indices


def compute_similarity_and_map(classifier: ObjectClassifier, objects_1_indices: List[int], objects_2_indices: List[int],
                               threshold: float, color_weight: float) -> Dict[int, int]:
    """
    Computes the similarity between the first objects from image_1 and image_2, and updates the category mapping.
    """
    category_mapping = {}
    used_indices_2 = set()  # To keep track of used indices from image_2

    # Compute embeddings for all cropped objects
    classifier.compute_embeddings()

    for idx1 in objects_1_indices:
        best_similarity = -1
        most_similar_idx = -1

        for idx2 in objects_2_indices:
            if idx2 in used_indices_2:
                continue

            similarity = classifier.calculate_similarity(idx1, idx2, color_weight)
            if similarity > best_similarity:
                best_similarity = similarity
                most_similar_idx = idx2

        if most_similar_idx != -1 and best_similarity >= threshold:
            used_indices_2.add(most_similar_idx)
            category_mapping[idx1] = most_similar_idx
            log.info(f"Category {idx1} from Image 1 is most similar to Category {most_similar_idx} from Image 2 with "
                     f"similarity score {best_similarity}")

    return category_mapping


def find_missing_elements(image_1: Image, image_2: Image, classifier: ObjectClassifier) -> None:
    """
    Identifies and reports missing elements between two images.
    Exits with an error if the number of categories does not match.
    """
    # Compare the number of categories between the two images
    if len(image_1.categories) != len(image_2.categories):
        log.error("Number of categories does not match between the two images.")
        sys.exit(1)

    if not compare_number_of_elements(image_1, image_2):
        # Get the indices of objects to compare
        objects_1_indices, objects_2_indices = crop_and_save_images(image_1, image_2)

        # Compute the similarity and obtain the mapping
        mapping = compute_similarity_and_map(classifier, objects_1_indices, objects_2_indices, threshold=0.7, color_weight=0.8)

        image_1_mapped_indices = set(mapping.keys())

        for idx1, category_1 in enumerate(image_1.categories):
            if idx1 in image_1_mapped_indices:
                mapped_idx2 = mapping[idx1]
                category_2 = image_2.categories[mapped_idx2]

                if len(category_1) != len(category_2):
                    log.warning(
                        f"Category {idx1} in Image 1 has {len(category_1)} objects, "
                        f"but Category {mapped_idx2} in Image 2 has {len(category_2)} objects."
                    )

    else:
        log.info("All elements are present.")
