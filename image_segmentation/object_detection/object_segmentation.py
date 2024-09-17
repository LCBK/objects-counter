import logging
from typing import Tuple, List

import cv2
import numpy as np
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor

from objects_counter.db.dataops.image import get_background_points, bulk_set_elements
from objects_counter.db.models import Image

log = logging.getLogger(__name__)


class Object:
    """Represents an individual detected object in an image."""
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


class ObjectSegmentation:
    """Handles image segmentation and object detection using the Segment Anything Model (SAM)."""

    def __init__(self, sam_checkpoint_path: str, model_type: str = "vit_h"):
        log.info("Initializing Object Segmentation.")
        log.info(f"PyTorch version: {torch.__version__}")
        log.info(f"Torchvision version: {torchvision.__version__}")
        log.info(f"CUDA is available: {torch.cuda.is_available()}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path).to(self.device)
        self.predictor = SamPredictor(self.sam)

    def calculate_mask(self, image: Image):
        """Calculates and assigns a mask to the image based on input points."""
        image_data = cv2.imread(image.filepath)
        self.predictor.set_image(image_data)
        points = get_background_points(image)
        masks, _, _ = self.predictor.predict(point_coords=np.array(points), point_labels=np.array([1] * len(points)),
                                             multimask_output=True)
        return masks[2]

    def process_mask(self, mask: np.ndarray) -> np.ndarray:
        """Converts mask to binary format and processes edges for contour detection."""
        result_mask = np.array(mask) * 255
        h, w = result_mask.shape

        for x in range(h):
            if result_mask[x, 0] == 0:
                cv2.floodFill(result_mask, None, (0, x), 255)
            if result_mask[x, w - 1] == 0:
                cv2.floodFill(result_mask, None, (w - 1, x), 255)

        for y in range(w):
            if result_mask[0, y] == 0:
                cv2.floodFill(result_mask, None, (y, 0), 255)
            if result_mask[h - 1, y] == 0:
                cv2.floodFill(result_mask, None, (y, h - 1), 255)

        _, binary_image = cv2.threshold(result_mask, 127, 255, cv2.THRESH_BINARY_INV)
        return binary_image

    def get_bounding_boxes(self, contours) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Returns bounding boxes of detected objects in the image."""
        if contours is None:
            return []

        bounding_boxes = self.extract_bounding_boxes(contours)

        return bounding_boxes

    def count_objects(self, image: Image) -> int:
        result_mask = self.calculate_mask(image)
        if result_mask is None:
            return 0

        binary_mask = self.process_mask(result_mask)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        object_count = len(contours)
        log.info(f"Number of objects detected: {object_count}")

        bounding_boxes = self.get_bounding_boxes(contours)
        bulk_set_elements(image, bounding_boxes)

        return object_count

    def extract_bounding_boxes(self, contours: List[np.ndarray]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Extracts bounding boxes from contours."""
        bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            bounding_boxes.append(((x, y), (x + w, y + h)))
        return bounding_boxes

    # def add_objects_from_bounding_boxes(self, image_index: int,  #                                     bounding_boxes: List[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:  #     """Adds detected objects to the image based on bounding boxes."""  #     new_objects = []  #     index = 0  #     for top_left, bottom_right in bounding_boxes:  #         new_object = Object(index=index, top_left=top_left, bottom_right=bottom_right, probability=0.0)  #         new_objects.append(new_object)  #         index += 1  #  #     self.images[image_index].categories.append(new_objects)
