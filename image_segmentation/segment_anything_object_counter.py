import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor

log = logging.getLogger(__name__)

@dataclass
class Image:
    data: Any
    result: Any = None
    objects_coords: Any = None

class SegmentAnythingObjectCounter:
    def __init__(self, sam_checkpoint_path, model_type="vit_h"):
        log.info("Creating new Segment Anything Object Counter")
        log.info("PyTorch version: %s", torch.__version__)
        log.info("Torchvision version: %s", torchvision.__version__)
        log.info("CUDA is available: %s", torch.cuda.is_available())

        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)

        if torch.cuda.is_available():
            self.sam.to(device="cuda")
        else:
            self.sam.to(device="cpu")

        self.predictor = SamPredictor(self.sam)
        self.images = []

    def add_image(self, data):
        self.images.append(Image(data))
        return len(self.images) - 1

    def set_image_objects_coords(self, index, coords):
        self.images[index].objects_coords = coords

    def calculate_image_mask(self, index, points):
        if index < 0 or index >= len(self.images):
            log.error("Given image index is out of bounds. index: %s images array size: %s", index, len(self.images))
            return False
        self.predictor.set_image(self.images[index].data)
        masks, _, _ = self.predictor.predict(point_coords=np.array(points),
                                             point_labels=np.array([1] * len(points)),
                                             multimask_output=True)
        self.images[index].result = masks[2]
        return True

    def get_image_mask(self, index):
        if index < 0 or index >= len(self.images):
            log.error("Given image index is out of bounds. index: %s images array size: %s", index, len(self.images))
            return None
        return self.images[index].result

    def process_mask(self, mask):
        result_mask = np.array(mask) * 255
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
        return binary_image

    def extract_bounding_boxes(self, contours):
        objects_bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            objects_bounding_boxes.append(((x, y), (x + w, y + h)))
        return objects_bounding_boxes

    def get_object_count(self, index):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + str(index) + " images array size:" + str(
                len(self.images)))
            return None, None
        result_mask = self.get_image_mask(index=index)
        if result_mask is None:
            return None, None
        binary_image = self.process_mask(result_mask)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        object_count = len(contours)

        log.info("Number of objects found: %s", object_count)

        objects_coords = self.get_bounding_boxes(index)
        self.set_image_objects_coords(index, objects_coords)
        return object_count

    def get_bounding_boxes(self, index):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + str(index) + " images array size:" + str(
                len(self.images)))
            return []

        result_mask = self.get_image_mask(index=index)
        if result_mask is None:
            return []
        binary_image = self.process_mask(result_mask)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bounding_boxes = self.extract_bounding_boxes(contours)
        return bounding_boxes
