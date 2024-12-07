import numpy as np
import pandas as pd
from PIL import Image as PILImage

from image_segmentation.object_classification.feature_extraction import ColorSimilarity
from tests.helpers import organize_images_by_category
from tests.visualization_helper import plot_similarity_heatmap


def calculate_similarity_matrix(histograms, categories, compute_similarity_fn):
    """Calculate similarity matrices for given histograms and categories."""
    mean_similarity_matrix = np.zeros((len(categories), len(categories)))
    median_similarity_matrix = np.zeros_like(mean_similarity_matrix)
    worst_similarity_matrix = np.zeros_like(mean_similarity_matrix)

    for i, category_i in enumerate(categories):
        for j, category_j in enumerate(categories):
            if j >= i:
                print(f"Calculating similarity between: {category_j} & {category_j}")

                similarities = _compute_pairwise_similarities(
                    histograms[str(category_i)], histograms[str(category_j)],
                    compute_similarity_fn)

                mean_similarity = np.mean(similarities) if similarities else 0
                median_similarity = np.median(similarities) if similarities else 0
                worst_similarity = np.min(similarities) if similarities else 0

                mean_similarity_matrix[i, j] = mean_similarity_matrix[j, i] = mean_similarity
                median_similarity_matrix[i, j] = median_similarity_matrix[j, i] = median_similarity
                worst_similarity_matrix[i, j] = worst_similarity_matrix[j, i] = worst_similarity

    return (pd.DataFrame(mean_similarity_matrix, index=categories, columns=categories),
            pd.DataFrame(median_similarity_matrix, index=categories, columns=categories),
            pd.DataFrame(worst_similarity_matrix, index=categories, columns=categories),)


def calculate_histograms(image_dict):
    """Compute histograms for all images in each category."""
    histograms = {}
    for category, paths in image_dict.items():
        histograms[category] = [ColorSimilarity.get_histogram(PILImage.open(path)) for path in paths]
    return histograms


def _compute_pairwise_similarities(histograms_1, histograms_2, compute_similarity_fn):
    """Compute pairwise similarities between two sets of histograms."""
    similarities = []
    for i, hist_i in enumerate(histograms_1):
        for j, hist_j in enumerate(histograms_2):
            if j >= i:
                if histograms_1 is histograms_2 and j == i:
                    continue
                similarities.append(compute_similarity_fn(hist_i, hist_j))
    return similarities


def main():
    image_dir = "C:\\Users\\alicj\\JetBrains\\PycharmProjects\\ObjectCounter\\tests\\elements"
    color_categories = ["black", "red", "brown", "orange",  "yellow", "green", "blue",  "purple", "pink", "white"]
    element_categories = ["egg", "cube"]

    combined_categories = [f"{element}-{color}" for element in element_categories for color in color_categories]
    image_dict = organize_images_by_category(image_dir, combined_categories)
    image_dict = {key: value for key, value in sorted(image_dict.items())}

    histograms = calculate_histograms(image_dict)

    mean_similarity_df, median_similarity_df, worst_similarity_df = calculate_similarity_matrix(histograms,
                                                                                                image_dict.keys(),
                                                                                                ColorSimilarity.compute_color_similarity)
    plot_similarity_heatmap(mean_similarity_df, title="Średnie podobieństwo kolorów między klasami",
                            subtitle="W połączonych kategoriach", game_name="Na skrzydłach")
    plot_similarity_heatmap(median_similarity_df, title="Mediana podobieństwa kolorów między klasami",
                            subtitle="W połączonych kategoriach", game_name="Na skrzydłach")
    plot_similarity_heatmap(worst_similarity_df, title="Najgorszy przypadek podobieństwa kolorów między klasami",
                            subtitle="W połączonych kategoriach", game_name="Na skrzydłach")


if __name__ == "__main__":
    main()
