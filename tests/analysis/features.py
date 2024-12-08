import numpy as np
import pandas as pd
import torch
from PIL import Image as PILImage
from torchvision import transforms as tr

from image_segmentation.object_classification.feature_extraction import FeatureSimilarity
from tests.helpers import organize_images_by_category
from tests.visualization_helper import plot_similarity_heatmap


class NoPaddingFeatureSimilarity(FeatureSimilarity):
    """Feature analysis model with no padding."""

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess the image with no padding."""
        img = PILImage.open(image_path).convert('RGB')
        transformations = tr.Compose([
            tr.Resize((224, 224), tr.InterpolationMode.BICUBIC)
        ])
        image_after_transformations = transformations(img)
        image_after_transformations.show("Obiekt ze po standardowej zmianie rozmiaru")
        return transformations(img).float().unsqueeze_(0).to(self.device)


class SmallPaddingFeatureSimilarity(FeatureSimilarity):
    """Feature analysis model with small padding."""

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess the image with small padding."""
        img = PILImage.open(image_path).convert('RGB')
        padding = int(max(img.size) * 0.05)
        transformations = tr.Compose([
            tr.Pad(padding=padding, fill=255),
            tr.Resize((224, 224), tr.InterpolationMode.BICUBIC)])
        image_after_transformations = transformations(img)
        image_after_transformations.show("Obiekt z małym dopełnieniem")
        return transformations(img).float().unsqueeze_(0).to(self.device)


class SquarePaddingFeatureSimilarity(FeatureSimilarity):
    """Feature analysis model with square padding."""

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess the image with square padding."""
        original_img = PILImage.open(image_path)
        max_size = 224
        desired_size = 155  # ~70% size of the image in pixels

        resize_ratio = desired_size / float(max(original_img.size))
        resized_width = int(original_img.width * resize_ratio)
        resized_height = int(original_img.height * resize_ratio)
        resized_img = original_img.resize((resized_width, resized_height))

        image_with_padding = PILImage.new("RGB", (max_size, max_size), (255, 255, 255))
        top_left_x = (max_size - resized_width) // 2
        top_left_y = (max_size - resized_height) // 2
        image_with_padding.paste(resized_img, (top_left_x, top_left_y))

        image_with_padding.show("Obiekt z zachowanymi proporcjami oraz dopełnieniem")

        transformations = tr.Compose([
            tr.ToTensor(),
            tr.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))])

        return transformations(image_with_padding).float().unsqueeze_(0).to(self.device)


def calculate_embeddings(class_dict, feature_model):
    """Compute embeddings for all images in each class."""
    embeddings = {}

    for class_name, paths in class_dict.items():
        class_embeddings = _process_class_embeddings(paths, feature_model)
        embeddings[class_name] = class_embeddings

    return embeddings


def _process_class_embeddings(paths, feature_model):
    embeddings = []

    for path in paths:
        embedding = feature_model.get_embedding(feature_model.preprocess_image(path))
        embeddings.append(embedding)

    return embeddings


def calculate_feature_similarity_matrix(embeddings, class_names):
    """Calculate feature analysis matrix for given embeddings."""
    similarity_matrix = np.zeros((len(class_names), len(class_names)))
    worst_similarity_matrix = np.zeros((len(class_names), len(class_names)))

    for i, class_1 in enumerate(class_names):
        for j, class_2 in enumerate(class_names[i:], start=i):
            similarities = _compute_pairwise_similarities(embeddings[class_1], embeddings[class_2], class_1 == class_2)

            mean_similarity = np.mean(similarities) if similarities else 0
            worst_similarity = np.min(similarities) if similarities else 0

            similarity_matrix[i, j] = similarity_matrix[j, i] = mean_similarity
            worst_similarity_matrix[i, j] = worst_similarity_matrix[j, i] = worst_similarity

    return pd.DataFrame(similarity_matrix, index=class_names, columns=class_names), pd.DataFrame(
        worst_similarity_matrix, index=class_names, columns=class_names)


def _compute_pairwise_similarities(embeddings_1, embeddings_2, same_class):
    """Compute pairwise similarities between two sets of embeddings."""
    similarities = []
    for k, emb_1 in enumerate(embeddings_1):
        for l, emb_2 in enumerate(embeddings_2):
            if same_class and l <= k:
                continue
            similarity = torch.nn.functional.cosine_similarity(emb_1, emb_2).item()
            similarities.append(similarity)
    return similarities


def main():
    image_dir = "/home/shairys/objects/objects-counter/tests/elements/test"
    categories = ["cube", "egg", "token"]

    class_dict = organize_images_by_category(image_dir, categories)
    class_names = list(class_dict.keys())

    feature_model = SmallPaddingFeatureSimilarity()
    embeddings = calculate_embeddings(class_dict, feature_model)

    similarity_df, _ = calculate_feature_similarity_matrix(embeddings, class_names)



if __name__ == "__main__":
    main()
