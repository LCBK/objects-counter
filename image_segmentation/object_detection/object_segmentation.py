import logging
from typing import Tuple, List, Dict

import cv2
import numpy as np
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor

from objects_counter.db.dataops.image import bulk_set_elements, get_background_points
from objects_counter.db.models import Image

log = logging.getLogger(__name__)


class ObjectSegmentation:
    """Handles image segmentation and object detection using the Segment Anything Model (SAM)."""

    class ImageCache:
        def __init__(self, predictor: SamPredictor):
            self.features = predictor.features
            self.original_size = predictor.original_size
            self.input_size = predictor.input_size

    def __init__(self, sam_checkpoint_path, model_type="vit_h"):
        log.info("Creating new Segment Anything Object Counter")
        log.info("PyTorch version: %s", torch.__version__)
        log.info("Torchvision version: %s", torchvision.__version__)
        log.info("CUDA is available: %s", torch.cuda.is_available())

        assert sam_checkpoint_path is not None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path).to(self.device)
        self.predictor = SamPredictor(self.sam)
        self.cache: Dict[int, ObjectSegmentation.ImageCache] = {}
        self.current_image_id = None

    def _set_image(self, image: Image) -> None:
        if self.current_image_id == image.id:
            assert self.predictor.is_image_set is True
            return
        if image.id in self.cache:
            self.current_image_id = image.id
            self.predictor.features = self.cache[image.id].features
            self.predictor.original_size = self.cache[image.id].original_size
            self.predictor.input_size = self.cache[image.id].input_size
            self.predictor.is_image_set = True
            return
        image_data = cv2.imread(image.filepath)
        self.predictor.set_image(image_data)
        assert self.predictor.is_image_set is True
        self.current_image_id = image.id
        self.cache[image.id] = ObjectSegmentation.ImageCache(self.predictor)

    def calculate_mask(self, image: Image) -> np.ndarray:
        """Calculates and assigns a mask to the image based on input points."""
        self._set_image(image)
        points, labels = get_background_points(image)
        masks, _, _ = self.predictor.predict(point_coords=np.array(points),
                                             point_labels=np.array([1 if label else 0 for label in labels]),
                                             multimask_output=True)
        return masks[2]

    def _process_mask(self, mask):
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

    def _remove_small_masks(self, image, contours, threshold_fraction = 0.001):
        new_contours = []
        image_data = cv2.imread(image.filepath)
        image_pixels = image_data.shape[0] * image_data.shape[1]
        contour_removal_threshold = image_pixels * threshold_fraction
        for contour in contours:
            if cv2.contourArea(contour) < contour_removal_threshold:
                cv2.drawContours(image_data, [contour], -1, color=(0, 0, 0), thickness=cv2.FILLED)
            else:
                new_contours.append(contour)
        return new_contours

    def _extract_bounding_boxes(self, contours) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Extracts bounding boxes from contours."""
        objects_bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            objects_bounding_boxes.append(((x, y), (x + w, y + h)))
        return objects_bounding_boxes

    def _remove_background_from_image(self, image: Image, contours) -> None:
        img = cv2.imread(image.filepath)
        fill_color = [255, 255, 255]
        mask_value = 255
        stencil = np.zeros(img.shape[:-1]).astype(np.uint8)
        cv2.fillPoly(stencil, contours, mask_value)
        sel = stencil != mask_value
        img[sel] = fill_color
        cv2.imwrite(image.filepath[:-4] + "_processed.bmp", img)

    def count_objects(self, image: Image) -> int:
        result_mask = self.calculate_mask(image)
        if result_mask is None:
            log.warning("No mask found for image: %s", image.id)
            return 0
        binary_image = self._process_mask(result_mask)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = self._remove_small_masks(image, contours)
        self._remove_background_from_image(image, contours)
        object_count = len(contours)
        log.info("Number of objects detected: %s", object_count)
        bounding_boxes = self._get_bounding_boxes(contours)
        bulk_set_elements(image, bounding_boxes)
        return object_count

    def _get_bounding_boxes(self, contours):
        """Returns bounding boxes of detected objects in the image."""
        if contours is None:
            return []
        bounding_boxes = self._extract_bounding_boxes(contours)
        return bounding_boxes
