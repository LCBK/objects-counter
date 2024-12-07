import matplotlib.pyplot as plt
import numpy as np
from PIL import Image as PILImage

from image_segmentation.object_classification.feature_extraction import ColorSimilarity
from tests.analysis.colors import calculate_similarity_matrix
from tests.helpers import organize_images_by_category
from tests.visualization_helper import plot_similarity_heatmap


def parse_lighting_condition(filenames):
    """Organize filenames based on their lighting condition."""
    direct_files = [file for file in filenames if "direct" in file]
    diffused_files = [file for file in filenames if "diffused" in file]
    return {"direct": direct_files, "diffused": diffused_files}


def calculate_histograms_per_condition(image_dict, color_similarity):
    """Compute histograms separately for each lighting condition."""
    condition_histograms = {"direct": {}, "diffused": {}}
    for category, files in image_dict.items():
        split_files = parse_lighting_condition(files)
        for condition, file_list in split_files.items():
            condition_histograms[condition][category] = [color_similarity.get_histogram(PILImage.open(file)) for file in
                file_list]
    return condition_histograms


def plot_histogram_comparison(histograms_direct, histograms_diffused, title, category):
    """Overlay histograms for direct and diffused lighting conditions."""
    bins = np.linspace(0, 1, 50)
    plt.figure(figsize=(10, 6))
    for idx, (direct_hist, diffused_hist) in enumerate(zip(histograms_direct, histograms_diffused)):
        plt.plot(bins[:-1], np.histogram(direct_hist, bins=bins)[0], alpha=0.5, label=f"Bezpośrednie ({idx + 1})")
        plt.plot(bins[:-1], np.histogram(diffused_hist, bins=bins)[0], alpha=0.5, label=f"Rozproszone ({idx + 1})")
    plt.title(f"{title} - {category}", fontsize=14)
    plt.xlabel("Wartość histogramu", fontsize=12)
    plt.ylabel("Liczba pikseli", fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.show()


def visualize_lighting_effects(image_dict, categories, color_similarity):
    """Visualize differences in classification between lighting conditions."""
    histograms = calculate_histograms_per_condition(image_dict, color_similarity)

    for condition, hist_data in histograms.items():
        similarity_matrices = calculate_similarity_matrix(hist_data, categories,
                                                          color_similarity.compute_color_similarity)
        mean_similarity, median_similarity, worst_similarity = similarity_matrices

        plot_similarity_heatmap(mean_similarity, title=f"Średnie podobieństwo - {condition.capitalize()}",
                                subtitle="Warunki oświetlenia")
        plot_similarity_heatmap(median_similarity, title=f"Mediana podobieństwa - {condition.capitalize()}",
                                subtitle="Warunki oświetlenia")
        plot_similarity_heatmap(worst_similarity, title=f"Najgorsze podobieństwo - {condition.capitalize()}",
                                subtitle="Warunki oświetlenia")

    # Side-by-side and difference heatmaps
    for metric, title in zip(["mean", "median", "worst"], ["Średnie", "Mediana", "Najgorsze"]):
        direct_matrix = similarity_matrices["direct"][f"{metric}_similarity"]
        diffused_matrix = similarity_matrices["diffused"][f"{metric}_similarity"]
        difference_matrix = direct_matrix - diffused_matrix

        # Side-by-side comparison
        plot_similarity_heatmap(direct_matrix, title=f"{title} podobieństwo - Bezpośrednie",
                                subtitle="Porównanie oświetlenia")
        plot_similarity_heatmap(diffused_matrix, title=f"{title} podobieństwo - Rozproszone",
                                subtitle="Porównanie oświetlenia")

        # Difference heatmap
        plot_similarity_heatmap(difference_matrix, title=f"Różnica w {title} podobieństwie",
                                subtitle="Bezpośrednie vs. Rozproszone")

    # Overlayed histograms for individual elements and colors
    for category in categories:
        direct_histograms = histograms["direct"].get(category, [])
        diffused_histograms = histograms["diffused"].get(category, [])
        if direct_histograms and diffused_histograms:
            plot_histogram_comparison(direct_histograms, diffused_histograms, title="Porównanie histogramów",
                                      category=category)


def main():
    image_dir = "C:\\Users\\alicj\\JetBrains\\PycharmProjects\\ObjectCounter\\tests\\elements"
    color_categories = ["black", "red", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "white"]
    element_categories = ["egg", "cube"]

    combined_categories = [f"{element}-{color}" for element in element_categories for color in color_categories]
    image_dict = organize_images_by_category(image_dir, combined_categories)
    image_dict = {key: value for key, value in sorted(image_dict.items())}

    color_similarity = ColorSimilarity()
    visualize_lighting_effects(image_dict, image_dict.keys(), color_similarity)


if __name__ == "__main__":
    main()
