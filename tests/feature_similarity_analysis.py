import os
import statistics
import time
from collections import defaultdict

import numpy as np
import pandas as pd
import torch
from PIL import Image as PILImage
from torchvision import transforms as tr

from image_segmentation.object_classification.feature_extraction import FeatureSimilarity
from visualization_helper import plot_similarity_heatmap


class NoPaddingFeatureSimilarity(FeatureSimilarity):
    """Feature similarity model with no padding."""

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess the image with no padding."""
        img = PILImage.open(image_path).convert('RGB')
        transformations = tr.Compose([
            tr.ToTensor(),
            tr.Resize((224, 224), tr.InterpolationMode.BICUBIC),
            tr.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))])
        return transformations(img).float().unsqueeze_(0).to(self.device)


class SmallPaddingFeatureSimilarity(FeatureSimilarity):
    """Feature similarity model with small padding."""

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess the image with small padding."""
        img = PILImage.open(image_path).convert('RGB')
        padding = int(max(img.size) * 0.05)
        transformations = tr.Compose([
            tr.Pad(padding=padding, fill=255),
            tr.Resize((224, 224), tr.InterpolationMode.BICUBIC),
            tr.ToTensor(),
            tr.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
        ])
        return transformations(img).float().unsqueeze_(0).to(self.device)


class SquarePaddingFeatureSimilarity(FeatureSimilarity):
    """Feature similarity model with square padding."""

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess the image with square padding."""
        original_img = PILImage.open(image_path)
        max_size = 224
        desired_size = 155

        resize_ratio = desired_size / float(max(original_img.size))
        resized_width = int(original_img.width * resize_ratio)
        resized_height = int(original_img.height * resize_ratio)
        resized_img = original_img.resize((resized_width, resized_height))

        canvas = PILImage.new("RGB", (max_size, max_size), (255, 255, 255))
        top_left_x = (max_size - resized_width) // 2
        top_left_y = (max_size - resized_height) // 2
        canvas.paste(resized_img, (top_left_x, top_left_y))

        transformations = tr.Compose(
            [tr.ToTensor(), tr.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))])
        return transformations(canvas).float().unsqueeze_(0).to(self.device)


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
    image_dir = "C:\\Users\\alicj\\Desktop\\Train-dataset"
    categories = ["cylinder", "train", "station"]

    class_dict = organize_images_by_category(image_dir, categories)
    class_names = list(class_dict.keys())

    feature_model = SmallPaddingFeatureSimilarity()
    similarity_df = calculate_feature_similarity(class_dict, class_names, feature_model)

    plot_similarity_heatmap(similarity_df, title="Feature-Based Similarity Between Classes",
                            subtitle="Small Padding",
                            font="Arial")


if __name__ == "__main__":
    main()
