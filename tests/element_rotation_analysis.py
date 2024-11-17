import os
import statistics
import time
from collections import defaultdict

import numpy as np
import pandas as pd
import torch

from tests.feature_similarity_analysis import SquarePaddingFeatureSimilarity
from tests.visualization_helper import plot_similarity_heatmap


def calculate_embeddings(class_dict, feature_model):
    """Precompute embeddings for all images in the class dictionary."""
    embeddings = {}
    times = []

    for class_name, paths in class_dict.items():
        class_embeddings = []
        for path in paths:
            start_time = time.perf_counter()
            embedding = feature_model.get_embedding(feature_model.preprocess_image(path))
            end_time = time.perf_counter()

            class_embeddings.append(embedding)
            times.append(end_time - start_time)

        embeddings[class_name] = class_embeddings

    mean_time = statistics.mean(times) if times else 0
    median_time = statistics.median(times) if times else 0

    print(f"Mean time: {mean_time}")
    print(f"Median: {median_time}")
    return embeddings


def calculate_feature_similarity(class_dict, class_names, feature_model):
    """Calculate the feature similarity matrix for given image classes."""
    embeddings = calculate_embeddings(class_dict, feature_model)

    similarity_matrix = np.zeros((len(class_names), len(class_names)))

    for i, class_1 in enumerate(class_names):
        for j, class_2 in enumerate(class_names[i:], start=i):
            similarities = []

            for k, embedding_1 in enumerate(embeddings[class_1]):
                for l, embedding_2 in enumerate(embeddings[class_2]):
                    if class_1 == class_2 and l <= k:
                        continue
                    print(f"Calculating similarity between {class_1}[{k}] and {class_2}[{l}]")
                    similarity = torch.nn.functional.cosine_similarity(embedding_1, embedding_2).item()
                    similarities.append(similarity)

            mean_similarity = np.mean(similarities) if similarities else 0
            similarity_matrix[i, j] = mean_similarity
            similarity_matrix[j, i] = mean_similarity

    return pd.DataFrame(similarity_matrix, index=class_names, columns=class_names)


def organize_images_by_category(image_dir, categories):
    """Organize images into categories based on their file names."""
    class_dict = defaultdict(list)
    for file_name in os.listdir(image_dir):
        for category in categories:
            if category in file_name.lower():
                class_dict[category].append(os.path.join(image_dir, file_name))
                break
    return class_dict


def main():
    image_dir = "C:\\Users\\alicj\\Desktop\\Train-rotation-dataset"
    categories = ["rotated", "horizontal", "vertical"]

    class_dict = organize_images_by_category(image_dir, categories)
    class_names = list(class_dict.keys())

    feature_model = SquarePaddingFeatureSimilarity()
    similarity_df = calculate_feature_similarity(class_dict, class_names, feature_model)

    plot_similarity_heatmap(similarity_df, title="Feature-Based Similarity Between Classes",
                            subtitle="How rotation affects similarity?",
                            font="Arial")


if __name__ == "__main__":
    main()
