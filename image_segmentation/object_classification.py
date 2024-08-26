from collections import defaultdict

import cv2
import torch
import torchvision
from PIL import Image
from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14


class CosineSimilarity:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()

    def load_model(self):
        weights = torchvision.models.ViT_H_14_Weights.DEFAULT
        model = vit_h_14(weights=weights)
        model.heads = nn.Sequential(*list(model.heads.children())[:-1])
        model = model.to(self.device)
        return model

    def preprocess_image(self, image_path):
        img = Image.open(image_path)
        transformations = tr.Compose(
            [tr.ToTensor(), tr.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), tr.Resize((518, 518))])
        img = transformations(img).float()
        img = img.unsqueeze_(0).to(self.device)
        return img


class ObjectClassifier:
    def __init__(self, segmenter, similarity_model):
        self.segmenter = segmenter
        self.similarity_model = similarity_model
        self.categories = defaultdict(list)

    def crop_objects_from_images(self):
        cropped_objects = []
        for _, image_data in enumerate(self.segmenter.images):
            index = 0
            if image_data.objects_coords:
                for bbox in image_data.objects_coords:
                    cropped_image = self.crop_image(image_data.data, bbox)
                    cropped_objects.append((index, cropped_image))
                    index = index + 1
        return cropped_objects

    def crop_image(self, image, bbox):
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        (x_min, y_min), (x_max, y_max) = bbox
        cropped_image = pil_image.crop((x_min, y_min, x_max, y_max))
        return cropped_image

    def compute_embeddings_for_cropped_objects(self, cropped_objects):
        embeddings = []
        for index, obj_image in cropped_objects:
            temp_path = f"images/temp/temp_cropped_object_{index}.jpg"
            obj_image.save(temp_path)

            image_tensor = self.similarity_model.preprocess_image(temp_path)
            with torch.no_grad():
                embedding = self.similarity_model.model(image_tensor).cpu()
            embeddings.append((index, embedding))

        return embeddings

    def group_objects_by_similarity(self, threshold=0.8):
        cropped_objects = self.crop_objects_from_images()
        embeddings = self.compute_embeddings_for_cropped_objects(cropped_objects)
        self.assign_categories_based_on_similarity(embeddings, cropped_objects, threshold)
        return self.categories

    def assign_categories_based_on_similarity(self, embeddings, images, threshold=0.6):
        num_objects = len(embeddings)
        visited = set()
        category_id = 0

        for i in range(num_objects):
            index_i, embedding_i = embeddings[i]

            if index_i in visited:
                continue

            # Create a new category for the first uncategorized image
            self.categories[category_id].append((index_i, images[index_i], 1))
            visited.add(index_i)

            # Compare with other images
            for j in range(i + 1, num_objects):
                index_j, embedding_j = embeddings[j]
                similarity = torch.nn.functional.cosine_similarity(embedding_i, embedding_j).item()

                if similarity >= threshold:
                    added_to_category = False

                    # Check if image[j] is already in a category
                    for cat_id, category_images in self.categories.items():
                        index = 0
                        for img_index, _, prev_similarity in category_images:
                            if index_j == img_index:
                                # If new similarity is better delete from the existing category
                                if prev_similarity < similarity:
                                    category_images.pop(index)
                                else:
                                    added_to_category = True
                                break
                            index = index + 1

                    if not added_to_category:
                        # Image[j] is not categorized, add it to the current category
                        self.categories[category_id].append((index_j, images[index_j], similarity))
                        visited.add(index_j)

            # Move to the next category after processing
            category_id += 1
