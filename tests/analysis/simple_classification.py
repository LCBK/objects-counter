import os
from typing import List, Dict

import cv2
from PIL import Image as PILImage

from image_segmentation.object_classification.classifier import ObjectClassifier
from objects_counter import app
from objects_counter.api.default.views import feature_similarity_model, color_similarity_model, sam
from objects_counter.db.dataops.image import insert_element, get_image_by_id, insert_image
from tests.visualization_helper import display_images_in_grid

ELEMENT_TYPES = ["cube", "egg", "token"]
ELEMENT_COLORS = ["black", "red", "brown", "orange", "yellow", "green", "blue", "purple", "white", "gray"]
TOKEN_SUBCATEGORIES = ["wheat", "worm", "rat", "fish", "berry"]


def parse_filename_for_attributes(filename):
    """Extract type and color from filename."""
    parts = filename.split("-")
    element_type = parts[3]
    color = parts[4]
    return element_type, color


def map_elements_to_filenames(elements_path: List[str]) -> Dict[int, str]:
    """Map element IDs to filenames."""
    id_to_filename_map = {}

    for element_path in elements_path:
        image_element = insert_image(element_path, element_path)
        cv2.imwrite(image_element.filepath[:-4] + "_processed.bmp", cv2.imread(element_path))

        pil_image = PILImage.open(element_path)
        insert_element(image_element, (0, 0), (pil_image.width, pil_image.height))

        id_to_filename_map[image_element.id] = element_path

    return id_to_filename_map


def perform_classification(elements: Dict[int, str], threshold: float, color_weight: float):
    """Perform classification based on similarity."""
    classifier = ObjectClassifier(sam, feature_similarity_model, color_similarity_model)
    single_elements = []
    for element_id, element_path in elements.items():
        element = get_image_by_id(element_id)
        classifier.process_image_elements(element)
        single_elements.append(element.elements[0])

    classifier.assign_categories_based_on_similarity(single_elements, threshold, color_weight)


def get_user_input_for_category(images, category_name):
    """Display images and get user input for type and color."""
    print(f"Displaying images for category: {category_name}")
    display_images_in_grid(images, category_name)

    element_type = input(f"Podaj typ elementu (Opcje: {ELEMENT_TYPES}): ").strip()

    if element_type == "token":
        element_color = input(f"Podaj podkategorię żetonu (Opcje: {TOKEN_SUBCATEGORIES}): ").strip()
    else:
        element_color = input(f"Podaj kolor elementu (Opcje: {ELEMENT_COLORS}): ").strip()
    return element_type, element_color


def validate_classifications(classifications):
    """Validate classifications against filenames."""
    results = []

    for classification, elements in classifications.items():
        predicted_type, predicted_color = get_user_input_for_category(elements, classification)

        for filename in elements:
            actual_type, actual_color = parse_filename_for_attributes(filename)

            is_correct_type = (predicted_type == actual_type)
            is_correct_color = (predicted_color == actual_color)

            results.append({
                "filename": filename,
                "predicted_type": predicted_type,
                "predicted_color": predicted_color,
                "actual_type": actual_type,
                "actual_color": actual_color,
                "is_correct_type": is_correct_type,
                "is_correct_color": is_correct_color,
                "is_correct_overall": is_correct_type and is_correct_color
            })

    return results


def analyze_results(validation_results):
    """Analyze and report classification performance."""
    type_correct = sum(res["is_correct_type"] for res in validation_results)
    color_correct = sum(res["is_correct_color"] for res in validation_results)
    total = len(validation_results)

    print(f"Analiza wyników klasyfikacji:")
    print(f"Poprawna klasyfikacja typu: {type_correct}/{total} ({type_correct / total:.2%})")
    print(f"Poprawna klasyfikacja koloru: {color_correct}/{total} ({color_correct / total:.2%})")

    # Detailed analysis per category and color
    category_analysis = {}
    for res in validation_results:
        key = (res["actual_type"], res["actual_color"])
        if key not in category_analysis:
            category_analysis[key] = {"total": 0, "correct": 0}
        category_analysis[key]["total"] += 1
        if res["is_correct_type"] and res["is_correct_color"]:
            category_analysis[key]["correct"] += 1

    for (element_type, color), stats in category_analysis.items():
        print(f"Kategoria: {element_type}-{color}: "
              f"{stats['correct']}/{stats['total']} poprawnych ({stats['correct'] / stats['total']:.2%})")


def main():
    with app.app.app_context():
        image_dir = "/home/shairys/objects/objects-counter/tests/test_data"
        filenames = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".jpg")]

        elements = map_elements_to_filenames(filenames)

        perform_classification(elements, threshold=0.7, color_weight=0.5)

        classification_results = {}
        for element_id, element_path in elements.items():
            image = get_image_by_id(element_id)
            element = image.elements[0]

            classification = element.classification

            if classification not in classification_results:
                classification_results[classification] = []
            classification_results[classification].append(element_path)

        validation_results = validate_classifications(classification_results)

        analyze_results(validation_results)


if __name__ == "__main__":
    main()
