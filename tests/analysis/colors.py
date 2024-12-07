import cv2
import numpy as np
import pandas as pd
from PIL import Image as PILImage

from image_segmentation.constants import CENTROIDS_RGB
from image_segmentation.object_classification.feature_extraction import ColorSimilarity
from tests.helpers import organize_images_by_category
from tests.visualization_helper import plot_similarity_heatmap

CENTROIDS_RGB_LEVEL_2 = np.array([
    [
        [230, 134, 151],  # PINK
        [185, 40, 66],  # RED
        [234, 154, 144],  # YELLOW PINK
        [215, 71, 42],  # REDDISH ORANGE
        [122, 44, 38],  # REDDISH BROWN
        [220, 125, 52],  # ORANGE
        [127, 72, 41],  # BROWN
        [227, 160, 69],  # ORANGE YELLOW
        [151, 107, 57],  # YELLOWISH BROWN
        [217, 180, 81],  # YELLOW
        [127, 97, 41],  # OLIVE BROWN
        [208, 196, 69],  # GREENISH YELLOW
        [114, 103, 44],  # OLIVE
        [160, 194, 69],  # YELLOW GREEN
        [62, 80, 31],  # OLIVE GREEN
        [74, 195, 77],  # YELLOWISH GREEN
        [79, 191, 154],  # GREEN
        [67, 189, 184],  # BLUISH GREEN
        [62, 166, 198],  # GREENISH BLUE
        [59, 116, 192],  # BLUE
        [79, 71, 198],  # PURPLISH BLUE
        [120, 66, 197],  # VIOLET
        [172, 74, 195],  # PURPLE
        [187, 48, 164],  # REDDISH PURPLE
        [229, 137, 191],  # PURPLISH PINK
        [186, 43, 119],  # PURPLISH RED
        [231, 225, 233],  # WHITE
        [147, 142, 147],  # GRAY
        [43, 41, 43],  # BLACK
    ]], dtype=np.float32) / 255.0


class ConfigurableCentroidsColorSimilarity(ColorSimilarity):
    def __init__(self, centroids_rgb):
        self.ISCC_NBS_CENTROIDS_LUV = cv2.cvtColor(centroids_rgb, cv2.COLOR_RGB2Luv).reshape(-1, 3)
        super().__init__()


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


def calculate_histograms(image_dict, color_similarity):
    """Compute histograms for all images in each category."""
    histograms = {}
    for category, paths in image_dict.items():
        histograms[category] = [color_similarity.get_histogram(PILImage.open(path)) for path in paths]
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


def analyze_with_varying_centroids(image_dict, categories, centroid_sets):
    """Analyze the effect of varying centroids on similarity metrics."""
    results = []

    for i, centroids in enumerate(centroid_sets):
        color_similarity = ConfigurableCentroidsColorSimilarity(centroids)
        histograms = calculate_histograms(image_dict, color_similarity)

        mean_df, median_df, worst_df = calculate_similarity_matrix(
            histograms, categories, color_similarity.compute_color_similarity)

        results.append({
            "centroids": centroids,
            "mean_similarity": mean_df,
            "median_similarity": median_df,
            "worst_similarity": worst_df,
        })

        plot_similarity_heatmap(mean_df, title="Średnie podobieństwo", subtitle=f"Poziom: {i + 1}")
        plot_similarity_heatmap(median_df, title="Mediana podobieństw", subtitle=f"Poziom: {i + 1}")
        plot_similarity_heatmap(worst_df, title="Najgorszy przypadek podobieństwa", subtitle=f"Poziom: {i + 1}")

    return results


def main():
    image_dir = "C:\\Users\\alicj\\Desktop\\Test"
    color_categories = ["black", "red", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "white"]
    element_categories = ["egg", "cube"]

    combined_categories = [f"{element}-{color}" for element in element_categories for color in color_categories]
    image_dict = organize_images_by_category(image_dir, combined_categories)
    image_dict = {key: value for key, value in sorted(image_dict.items())}

    centroid_sets = [CENTROIDS_RGB, CENTROIDS_RGB_LEVEL_2]
    analyze_with_varying_centroids(image_dict, image_dict.keys(), centroid_sets)


if __name__ == "__main__":
    main()
