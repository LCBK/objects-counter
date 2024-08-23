import cv2

from segment_anything_object_counter import SegmentAnythingObjectCounter

import numpy as np
import torch
import torchvision
from PIL import Image
from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14


class CosineSimilarity:
    """Class tasked with comparing similarity between two images """

    def __init__(self, image_path_1, image_path_2, device=None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.image_path_1 = image_path_1
        self.image_path_2 = image_path_2

    def model(self):
        wt = torchvision.models.ViT_H_14_Weights.DEFAULT
        model = vit_h_14(weights=wt)
        model.heads = nn.Sequential(*list(model.heads.children())[:-1])
        model = model.to(self.device)

        return model

    def process_test_image(self, image_path):
        """Processing images
        Parameters
        ----------
        image_path :str

        Returns
        -------
        Processed image : str
        """
        img = Image.open(image_path)
        transformations = tr.Compose([tr.ToTensor(),
                                      tr.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
                                      tr.Resize((518, 518))])
        img = transformations(img).float()
        img = img.unsqueeze_(0)

        img = img.to(self.device)

        return img

    def get_embeddings(self):
        """Computer embessings given images

        Parameters
        image_paths : str
        Returns
        -------
        embeddings: np.ndarray
        """
        img1 = self.process_test_image(self.image_path_1)
        img2 = self.process_test_image(self.image_path_2)
        model = self.model()

        emb_one = model(img1).detach().cpu()
        emb_two = model(img2).detach().cpu()

        return emb_one, emb_two

    def compute_scores(self):
        """Computes cosine similarity between two vectors."""
        emb_one, emb_two = self.get_embeddings()
        scores = torch.nn.functional.cosine_similarity(emb_one, emb_two)

        return scores.numpy().tolist()


class ClassifyObjects:
    sam = None
    index = None

    def __init__(self):
        image = cv2.imread("images/test2.jpg")
        sam_checkpoint = "/home/shairys/objects/objects-counter/sam_vit_h_4b8939.pth"
        self.sam = SegmentAnythingObjectCounter(sam_checkpoint)
        self.index = self.sam.add_image(image)

    def get_object_from_image(self):
        points = [[1883.3709677419356, 1080.145161290323], [562.0806451612904, 873.693548387097],
                  [2915.6290322580644, 1462.0806451612905]]
        self.sam.calculate_image_mask(index=self.index, points=points)

        if self.index < 0 or self.index >= len(self.sam.images):
            print("Given image index is out of bounds. index: " + self.index + " images array size:" + len(self.images))
            return None, None
        result_mask = self.sam.get_image_mask(index=self.index)
        result_mask = np.array(result_mask) * 255
        image = np.ascontiguousarray(result_mask, dtype=np.uint8)
        for x in range(0, image.shape[0]):
            if image[x][0] == 0:
                cv2.floodFill(image, None, (0, x), 255)
            if image[x][image.shape[1] - 1] == 0:
                cv2.floodFill(image, None, (image.shape[1] - 1, x), 255)
        for y in range(0, image.shape[1]):
            if image[0][y] == 0:
                cv2.floodFill(image, None, (y, 0), 255)
            if image[image.shape[0] - 1][y] == 0:
                cv2.floodFill(image, None, (y, image.shape[0] - 1), 255)
        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        objects_bounding_boxes = []
        for i in range(len(contours)):
            min_x = int(min(contours[i][t][0][0] for t in range(contours[i].shape[0])))
            max_x = int(max(contours[i][t][0][0] for t in range(contours[i].shape[0])))
            min_y = int(min(contours[i][t][0][1] for t in range(contours[i].shape[0])))
            max_y = int(max(contours[i][t][0][1] for t in range(contours[i].shape[0])))
            objects_bounding_boxes.append([[min_x, min_y], [max_x, max_y]])

        # Save images based on coords
        objects_images_path = "images/objects/"
        whole_image = Image.open("images/test2.jpg")
        width, height = whole_image.size

        for i in range(0, len(objects_bounding_boxes)):
            bounding_box = objects_bounding_boxes[i]
            left = bounding_box[0][0]
            top = bounding_box[1][1]
            right = bounding_box[1][0]
            bottom = bounding_box[0][1]

            object_image = whole_image.crop((left, bottom, right, top))
            object_image.save(objects_images_path + str(i) + ".jpg")

    def find_similar(self):
        winner = 0
        winning_image = 0
        for i in range(2, 8):
            similarity = CosineSimilarity("images/objects/1.jpg", "images/objects/" + str(i) + ".jpg")
            temp = similarity.compute_scores()
            if temp[0] > winner:
                winner = temp[0]
                winning_image = i
        print("Winning image is: " + str(winning_image) + ".jpg")

classify = ClassifyObjects()
# points = [[1883.3709677419356, 1080.145161290323], [562.0806451612904, 873.693548387097],
#           [2915.6290322580644, 1462.0806451612905]]
#
# classify.get_object_from_image()
classify.find_similar()
