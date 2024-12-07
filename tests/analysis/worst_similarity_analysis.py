import os

import matplotlib.pyplot as plt
import torch
from PIL import Image as PILImage

from tests.helpers import organize_images_by_category
from tests.analysis.feature_similarity import SquarePaddingFeatureSimilarity, calculate_embeddings


def find_worst_similarity_pairs(embeddings, class_names):
    """Find the worst analysis pairs for each category."""
    worst_pairs = {}
    for class_name in class_names:
        embeddings_list = embeddings[class_name]
        worst_similarity = float('inf')
        worst_pair = None

        for i, emb_1 in enumerate(embeddings_list):
            for j, emb_2 in enumerate(embeddings_list):
                if j <= i:
                    continue
                similarity = torch.nn.functional.cosine_similarity(emb_1, emb_2).item()
                if similarity < worst_similarity:
                    worst_similarity = similarity
                    worst_pair = (i, j)

        if worst_pair:
            worst_pairs[class_name] = (worst_pair, worst_similarity)

    return worst_pairs


def display_worst_pairs(image_paths_dict, worst_pairs, output_dir="output"):
    """Display and save the worst analysis pairs side by side."""
    os.makedirs(output_dir, exist_ok=True)

    for category, ((idx1, idx2), similarity) in worst_pairs.items():
        img1_path = image_paths_dict[category][idx1]
        img2_path = image_paths_dict[category][idx2]

        img1 = PILImage.open(img1_path).convert('RGB')
        img2 = PILImage.open(img2_path).convert('RGB')

        # Create a side-by-side plot
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        ax[0].imshow(img1)
        ax[0].axis('off')
        ax[0].set_title("Image 1")

        ax[1].imshow(img2)
        ax[1].axis('off')
        ax[1].set_title("Image 2")

        plt.suptitle(f"Category: {category}\nWorst Similarity: {similarity:.2f}", fontsize=14)
        plt.tight_layout()

        # Save the visualization
        output_path = os.path.join(output_dir, f"{category}_worst_similarity.png")
        plt.savefig(output_path)
        plt.close()


def main():
    image_dir = "C:\\Users\\Alicja\\Desktop\\Train-dataset - Copy"
    categories = ["train", "station", "cylinder"]

    class_dict = organize_images_by_category(image_dir, categories)
    class_names = list(class_dict.keys())

    feature_model = SquarePaddingFeatureSimilarity()
    embeddings = calculate_embeddings(class_dict, feature_model)

    worst_pairs = find_worst_similarity_pairs(embeddings, class_names)
    display_worst_pairs(class_dict, worst_pairs)


if __name__ == "__main__":
    main()
