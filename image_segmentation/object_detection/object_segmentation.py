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

    def process_mask(self, mask):
        """Converts mask to binary format and processes edges for contour detection."""
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

    def get_bounding_boxes(self, contours) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Returns bounding boxes of detected objects in the image."""
        if contours is None:
            return []

        bounding_boxes = self.extract_bounding_boxes(contours)

        return bounding_boxes

    def count_objects(self, image: Image) -> int:
        result_mask = self.calculate_mask(image)
        if result_mask is None:
            log.warning("No mask found for image: %s", image.id)
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
