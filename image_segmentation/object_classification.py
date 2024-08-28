from collections import defaultdict
from typing import List, Tuple

import cv2
import numpy as np
import torch
import torchvision
from PIL import Image
from scipy.spatial import distance
from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14


class CosineSimilarity:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()

    def load_model(self) -> nn.Module:
        weights = torchvision.models.ViT_H_14_Weights.DEFAULT
        model = vit_h_14(weights=weights)
        model.heads = nn.Sequential(*list(model.heads.children())[:-1])
        model = model.to(self.device)
        return model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        img = Image.open(image_path)
        transformations = tr.Compose(
            [tr.ToTensor(), tr.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), tr.Resize((518, 518))])
        img = transformations(img).float()
        img = img.unsqueeze_(0).to(self.device)
        return img


class ObjectClassifier:
    def __init__(self, segmenter, similarity_model: CosineSimilarity):
        self.segmenter = segmenter
        self.similarity_model = similarity_model
        self.categories: defaultdict[int, List[Tuple[int, float]]] = defaultdict(list)

        self.embeddings: List[torch.Tensor] = []
        self.images_of_objects: List[Image.Image] = []

    def compute_color_histogram(self, image: Image.Image, bins: int = 16) -> np.ndarray:
        image = image.convert('RGB')
        histogram = []

        for channel in range(3):
            channel_hist = cv2.calcHist([np.array(image)], [channel], None, [bins], [0, 256])
            channel_hist = cv2.normalize(channel_hist, channel_hist).flatten()
            histogram.append(channel_hist)

        histogram = np.concatenate(histogram)
        return histogram

    def compute_color_similarity(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        return 1 - distance.braycurtis(hist1, hist2)

    def crop_objects_from_images(self) -> List[Tuple[int, Image.Image]]:
        cropped_objects = []

        for _, image_data in enumerate(self.segmenter.images):
            index = 0
            if image_data.objects_coords:
                for bbox in image_data.objects_coords:
                    cropped_object = self.crop_image(image_data.data, bbox)
                    cropped_objects.append((index, cropped_object))
                    self.images_of_objects.append(cropped_object)
                    index += 1
        return cropped_objects

    def crop_image(self, image: np.ndarray, bbox: Tuple[Tuple[int, int], Tuple[int, int]]) -> Image.Image:
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        (x_min, y_min), (x_max, y_max) = bbox
        cropped_image = pil_image.crop((x_min, y_min, x_max, y_max))
        return cropped_image

    def compute_embeddings_for_cropped_objects(self, ):

        for index in range(len(self.images_of_objects)):
            object_image = self.images_of_objects[index]

            temp_path = f"images/temp/object_{index}.jpg"
            object_image.save(temp_path)

            image_tensor = self.similarity_model.preprocess_image(temp_path)
            with torch.no_grad():
                embedding = self.similarity_model.model(image_tensor).cpu()
            self.embeddings.append(embedding)

    def group_objects_by_similarity(self, threshold: float = 0.8, color_weight: float = 0.5) -> defaultdict:
        self.crop_objects_from_images()
        self.compute_embeddings_for_cropped_objects()
        self.assign_categories_based_on_similarity(self.images_of_objects, threshold, color_weight)
        return self.categories

    def assign_categories_based_on_similarity(self, images: List[Image.Image], threshold: float, color_weight: float):
        num_objects = len(self.embeddings)
        visited = set()
        category_id = 0

        for index_i in range(num_objects):
            if index_i in visited:
                continue

            self.categories[category_id].append((index_i, 1))
            visited.add(index_i)

            for index_j in range(index_i + 1, num_objects):
                combined_similarity = self.calculate_combined_similarity(images, index_i, index_j, color_weight)

                if combined_similarity >= threshold:
                    self.add_image_to_category(index_j, combined_similarity, category_id, visited)

            category_id += 1

    def calculate_combined_similarity(self, images: List[Image.Image], index_i: int, index_j: int,
                                      color_weight: float) -> float:
        hist_i = self.compute_color_histogram(images[index_i])
        hist_j = self.compute_color_histogram(images[index_j])

        embedding_i = self.embeddings[index_i]
        embedding_j = self.embeddings[index_j]

        feature_similarity = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()
        color_similarity = self.compute_color_similarity(hist_i, hist_j)

        combined_similarity = (color_weight * color_similarity) + ((1 - color_weight) * feature_similarity)

        return combined_similarity

    def add_image_to_category(self, index: int, similarity: float, category_id: int, visited: set):
        added_to_category = False

        for images_in_category in self.categories.values():
            temp_index = 0  # Potential index of given image in different category
            for img_index, prev_similarity in images_in_category:
                if index == img_index:
                    # If previous similarity was worse, delete from that category; otherwise, do nothing
                    if prev_similarity < similarity:
                        images_in_category.pop(temp_index)
                    else:
                        added_to_category = True
                    break
                temp_index += 1

        # New image that was not yet categorized
        if not added_to_category:
            self.categories[category_id].append((index, similarity))
            visited.add(index)
