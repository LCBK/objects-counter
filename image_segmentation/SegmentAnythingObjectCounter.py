import numpy as np
import matplotlib.pyplot as plt
import cv2
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor


class Image:
    def __init__(self, data, type):
        self.data = data  # to do
        self.result = None

class SegmentAnythingObjectCounter:
    def __init__(self, sam_checkpoint_path, model_type="vit_h"):
        print("Creating new Segment Anything Object Counter")
        print("PyTorch version:", torch.__version__)
        print("Torchvision version:", torchvision.__version__)
        print("CUDA is available:", torch.cuda.is_available())
        if not torch.cuda.is_available():
            raise Exception("Cuda is not available")
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
        self.sam.to(device="cuda")
        self.predictor = SamPredictor(self.sam)
        self.images = []

    def add_image(self, data, type):
        self.images.append(Image(data, type))
        return len(self.images) - 1

    def calculate_image_mask(self, index, points):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + index + " images array size:" + len(self.images))
            return False
        self.predictor.set_image(self.images[index].data)
        masks, scores, logits = self.predictor.predict(
            point_coords=np.array(points),
            point_labels=np.array([1] * len(points)),
            multimask_output=True)
        self.images[index].result = masks[2]
        return True

    def get_image_mask(self, index):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + index + " images array size:" + len(self.images))
            return None
        return self.images[index].result

    def get_object_count(self, index):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + index + " images array size:" + len(self.images))
            return None, None
        result_mask = self.get_image_mask(index=index)
        result_mask = np.array(result_mask) * 255
        # Find contours of the objects

        cv2.imwrite("result.png", result_mask)
        image = cv2.imread("result.png", cv2.IMREAD_GRAYSCALE)
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
        cv2.imwrite("result2.png", image)
        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Count the number of contours found
        object_count = len(contours)

        print(f"Number of objects found: {object_count}")

        return object_count


