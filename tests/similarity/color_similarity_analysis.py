import time

import numpy as np
import pandas as pd
from PIL import Image as PILImage

from image_segmentation.object_classification.feature_extraction import ColorSimilarity
from tests.helpers import log_timing_statistics, organize_images_by_category
from tests.visualization_helper import plot_similarity_heatmap


def calculate_color_similarity_matrix(histograms, class_names):
    """Calculate feature similarity matrix for given histograms."""
    similarity_matrix = np.zeros((len(class_names), len(class_names)))
    worst_similarity_matrix = np.zeros((len(class_names), len(class_names)))

    for i, class_1 in enumerate(class_names):
        for j, class_2 in enumerate(class_names[i:], start=i):
            similarities = _compute_pairwise_similarities(histograms[class_1], histograms[class_2], class_1 == class_2)

            mean_similarity = np.mean(similarities) if similarities else 0
            worst_similarity = np.min(similarities) if similarities else 0

            similarity_matrix[i, j] = similarity_matrix[j, i] = mean_similarity
            worst_similarity_matrix[i, j] = worst_similarity_matrix[j, i] = worst_similarity

    return pd.DataFrame(similarity_matrix, index=class_names, columns=class_names), pd.DataFrame(
        worst_similarity_matrix, index=class_names, columns=class_names)


def calculate_histograms(class_dict):
    """Compute histograms for all images in each class."""
    histograms = {}
    times = []

    for class_name, paths in class_dict.items():
        class_histograms, class_times = _process_class_histogram(paths)
        histograms[class_name] = class_histograms
        times.extend(class_times)

    log_timing_statistics(times)
    return histograms


def _process_class_histogram(paths):
    histograms = []
    times = []

    for path in paths:
        start_time = time.perf_counter()
        histogram = ColorSimilarity.get_histogram(PILImage.open(path))
        end_time = time.perf_counter()

        histograms.append(histogram)
        times.append(end_time - start_time)

    return histograms, times


def _compute_pairwise_similarities(histograms_1, histograms_2, same_class):
    """Compute pairwise similarities between two sets of histograms."""
    similarities = []
    for i, hist_i in enumerate(histograms_1):
        for j, hist_j in enumerate(histograms_2):
            if same_class and j <= i:
                continue
            similarity = ColorSimilarity.compute_color_similarity(hist_i, hist_j)
            similarities.append(similarity)
    return similarities


def main():
    image_dir = "C:\\Users\\Alicja\\PycharmProjects\\objects-counter\\tests\\elements"
    categories = ["blue", "green", "purple", "red", "yellow", "brown", "green", "pink", "white"]

    class_dict = organize_images_by_category(image_dir, categories)
    class_names = list(class_dict.keys())

    histograms = calculate_histograms(class_dict)
    similarity_df, worst_similarity_df = calculate_color_similarity_matrix(histograms, class_names)

    plot_similarity_heatmap(similarity_df, title="Color-Based Similarity Between Classes", subtitle="Mean value",
                            font="Arial")

    plot_similarity_heatmap(worst_similarity_df, title="Color-Based Similarity Between Classes", subtitle="Worst value",
                            font="Arial")


if __name__ == "__main__":
    main()
