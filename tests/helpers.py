import os
import statistics
from collections import defaultdict


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
