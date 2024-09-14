import logging
from collections import namedtuple
from dataclasses import dataclass
from typing import Any, List, Tuple

import cv2
import numpy as np
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor

log = logging.getLogger(__name__)


class Object:
    index: int
    top_left_coord: Tuple[float, float]
    bottom_right_coord: Tuple[float, float]
    probability: float

    def __init__(self, index: int, top_left: Tuple[float, float], bottom_right: Tuple[float, float],
                 probability: float):
        self.index = index
        self.top_left_coord = top_left
        self.bottom_right_coord = bottom_right
        self.probability = probability


@dataclass
class Image:
    data: np.ndarray
    mask: Any
    categories: List[List[Object]]

    def __init__(self, data: np.ndarray):
        self.data = data
        self.mask = None
        self.categories = []


class SegmentAnythingObjectCounter:
    images: List[Image]

    def __init__(self, sam_checkpoint_path: str, model_type: str = "vit_h") -> None:
        log.info("Creating new Segment Anything Object Counter")
        log.info("PyTorch version: %s", torch.__version__)
        log.info("Torchvision version: %s", torchvision.__version__)
        log.info("CUDA is available: %s", torch.cuda.is_available())

        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam.to(device=device)
        self.predictor = SamPredictor(self.sam)

        self.images = []

    def add_image(self, image: np.ndarray) -> int:
        """Adds a new image to the counter."""
        self.images.append(Image(data=image))
        return len(self.images) - 1

    def add_objects_from_bounding_boxes(self, image_index, bounding_boxes) -> None:
        """Creates new objects from bounding boxes and adds them to the specified image."""
        new_objects = []
        index = 0
        for top_left, bottom_right in bounding_boxes:
            new_object = Object(index=index, top_left=top_left, bottom_right=bottom_right, probability=0.0)
            new_objects.append(new_object)
            index += 1

        self.images[image_index].categories.append(new_objects)

    def calculate_image_mask(self, image_index: int, points: List[Tuple[float, float]]):
        """Calculates and sets the mask for the specified image based on provided points."""
        if image_index < 0 or image_index >= len(self.images):
            log.error("Given image index is out of bounds. index: %s images array size: %s", image_index,
                      len(self.images))
            return False
        self.predictor.set_image(self.images[image_index].data)
        masks, _, _ = self.predictor.predict(point_coords=np.array(points), point_labels=np.array([1] * len(points)),
                                             multimask_output=True)
        self.images[image_index].mask = masks[2]
        return True

    def get_image_mask(self, image_index: int):
        """Returns the mask for the specified image."""
        if image_index < 0 or image_index >= len(self.images):
            log.error("Given image index is out of bounds. index: %s images array size: %s", image_index,
                      len(self.images))
            return None
        return self.images[image_index].mask

    def process_mask(self, mask):
        """Processes the mask to a binary image."""
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

    def get_object_count(self, image_index: int) -> int:
        """Counts the number of objects in the specified image and updates the objects list."""
        if image_index < 0 or image_index >= len(self.images):
            print("Given image index is out of bounds. index: " + str(image_index) + " images array size:" + str(
                len(self.images)))
            return None

        mask = self.get_image_mask(image_index)
        if mask is None:
            return None

        binary_mask = self.process_mask(mask)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        object_count = len(contours)

        log.info(f"Number of objects found: {object_count}")

        bounding_boxes = self.get_image_bounding_boxes(image_index)
        self.add_objects_from_bounding_boxes(image_index, bounding_boxes)

        return object_count

    def get_image_bounding_boxes(self, image_index: int) -> List[Tuple[int, int, int, int]]:
        """Extracts bounding boxes for objects in the specified image."""
        if image_index < 0 or image_index >= len(self.images):
            log.error(f"Image index {image_index} is out of bounds. Total images: {len(self.images)}.")
            return []

        mask = self.get_image_mask(image_index)

        if mask is None:
            return []

        binary_mask = self.process_mask(mask)

        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = self.extract_bounding_boxes(contours)
        return bounding_boxes

    def extract_bounding_boxes(self, contours: List[np.ndarray]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Extracts bounding boxes from contours."""
        bounding_boxes = []

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            top_left = (x, y)
            bottom_right = (x + width, y + height)
            bounding_boxes.append((top_left, bottom_right))

        return bounding_boxes
