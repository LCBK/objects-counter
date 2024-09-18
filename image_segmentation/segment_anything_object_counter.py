import logging

import cv2
import numpy as np
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor

from objects_counter.db.dataops.image import bulk_set_elements, get_background_points
from objects_counter.db.models import Image
# pylint: disable=R0903
log = logging.getLogger(__name__)


class SegmentAnythingObjectCounter:

    class ImageCache:
        def __init__(self, image_mask, points_selected):
            self.image_mask = image_mask
            self.points_selected = points_selected

        def is_valid(self, current_points_selected):
            return self.points_selected == current_points_selected

    def __init__(self, sam_checkpoint_path, model_type="vit_h"):
        log.info("Creating new Segment Anything Object Counter")
        log.info("PyTorch version: %s", torch.__version__)
        log.info("Torchvision version: %s", torchvision.__version__)
        log.info("CUDA is available: %s", torch.cuda.is_available())

        assert sam_checkpoint_path is not None
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)

        if torch.cuda.is_available():
            self.sam.to(device="cuda")
        else:
            self.sam.to(device="cpu")

        self.predictor = SamPredictor(self.sam)
        self.cache = []

    def get_mask_cache(self, image_id, current_points):
        for cached_image_id, cache_data in self.cache:
            if cached_image_id == image_id and cache_data.is_valid(current_points):
                return cache_data.image_mask
            if cached_image_id == image_id and not cache_data.is_valid(current_points):
                self.cache.remove([image_id, cache_data])
                return None
        return None

    def add_mask_cache(self, image_id, current_points, cache_data):
        if(len(self.cache)) > 10:
            self.cache = self.cache[1:]
        cache = self.ImageCache(cache_data, current_points)
        self.cache.append([image_id, cache])

    def calculate_image_mask(self, image: Image) -> object:
        points = get_background_points(image)
        cache_data = self.get_mask_cache(image.id, points)
        if cache_data is not None:
            return cache_data

        image_data = cv2.imread(image.filepath)
        self.predictor.set_image(image_data)
        masks, _, _ = self.predictor.predict(point_coords=np.array(points),
                                             point_labels=np.array([1] * len(points)),
                                             multimask_output=True)
        self.add_mask_cache(image.id, points, masks[2])
        return masks[2]

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

    def remove_small_masks(self, image, contours):
        new_contours = []
        image_data = cv2.imread(image.filepath)
        image_pixels = image_data.shape[0] * image_data.shape[1]
        contour_removal_threshold = image_pixels / 100
        for contour in contours:
            if cv2.contourArea(contour) < contour_removal_threshold:
                cv2.drawContours(image_data, [contour], -1, color=(0, 0, 0), thickness=cv2.FILLED)
            else:
                new_contours.append(contour)
        return new_contours

    def extract_bounding_boxes(self, contours):
        objects_bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            objects_bounding_boxes.append(((x, y), (x + w, y + h)))
        return objects_bounding_boxes

    def get_object_count(self, image: Image) -> int:
        result_mask = self.calculate_image_mask(image)
        if result_mask is None:
            log.warning("No mask found for image: %s", image.id)
            return 0
        binary_image = self.process_mask(result_mask)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = self.remove_small_masks(image, contours)
        object_count = len(contours)

        log.info("Number of objects found: %s", object_count)

        bounding_boxes = self.get_bounding_boxes(contours)
        bulk_set_elements(image, bounding_boxes)
        return object_count

    def get_bounding_boxes(self, contours):
        if contours is None:
            return []
        bounding_boxes = self.extract_bounding_boxes(contours)
        return bounding_boxes
