import os
import statistics
from collections import defaultdict

element_translation = {
    "egg": ("Jajko", "n"),
    "cube": ("Kostka", "ż"),
    "token": ("Żeton", "n")
}

color_translation = {
    "blue": {"m": "Niebieski", "ż": "Niebieska", "n": "Niebieskie"},
    "green": {"m": "Zielony", "ż": "Zielona", "n": "Zielone"},
    "purple": {"m": "Fioletowy", "ż": "Fioletowa", "n": "Fioletowe"},
    "red": {"m": "Czerwony", "ż": "Czerwona", "n": "Czerwone"},
    "yellow": {"m": "Żółty", "ż": "Żółta", "n": "Żółte"},
    "brown": {"m": "Brązowy", "ż": "Brązowa", "n": "Brązowe"},
    "pink": {"m": "Różowy", "ż": "Różowa", "n": "Różowe"},
    "white": {"m": "Biały", "ż": "Biała", "n": "Białe"},
    # Token values
    "wheat": {"n": "Pszenicy"},
    "fish": {"n": "Ryby"},
    "worm": {"n": "Glizdy"},
    "berry": {"n": "Jagód"},
    "rat": {"n": "Gryzoni"}
}


def translate_category(category):
    """Translate category to format <element>-<color>."""
    try:
        element, color = category.split("-")
        translated_element, gender = element_translation.get(element, (element.capitalize(), "n"))
        translated_color = color_translation.get(color, {}).get(gender, color.capitalize())
        return f"{translated_element} {translated_color.lower()}"
    except ValueError:
        return category


def log_timing_statistics(times):
    """Log timing statistics."""
    if times:
        print(f"Mean time: {statistics.mean(times)}")
        print(f"Median time: {statistics.median(times)}")


def organize_images_by_category(image_dir, categories):
    """Organize images into categories based on their file names."""
    class_dict = defaultdict(list)
    for file_name in os.listdir(image_dir):
        for category in categories:
            if category in file_name.lower():
                class_dict[category].append(os.path.join(image_dir, file_name))
                break
    return class_dict
