from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor


@dataclass
class Image:
    data: Any
    result: Any = None


class SegmentAnythingObjectCounter:
    def __init__(self, sam_checkpoint_path, model_type="vit_h"):
        print("Creating new Segment Anything Object Counter")
        print("PyTorch version:", torch.__version__)
        print("Torchvision version:", torchvision.__version__)
        print("CUDA is available:", torch.cuda.is_available())
        assert torch.cuda.is_available(), "CUDA is not available"
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
        self.sam.to(device="cuda")
        self.predictor = SamPredictor(self.sam)
        self.images = []

    def add_image(self, data):
        self.images.append(Image(data))
        return len(self.images) - 1

    def calculate_image_mask(self, index, points):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + index + " images array size:" + len(self.images))
            return False
        self.predictor.set_image(self.images[index].data)
        masks, _, _ = self.predictor.predict(
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
        # Count the number of contours found
        object_count = len(objects_bounding_boxes)

        print(f"Number of objects found: {object_count}")

        return object_count, objects_bounding_boxes
