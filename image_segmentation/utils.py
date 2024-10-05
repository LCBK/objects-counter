import os
from typing import Tuple

import cv2
import numpy as np
from PIL import ImageDraw
from PIL import Image as PILImage

from objects_counter.db.dataops.image import get_image_by_id
from objects_counter.db.models import ImageElement


def display_element(element: ImageElement):
    image = get_image_by_id(element.image_id)
    image_data = np.array(PILImage.open(image.filepath))

    cropped_image = crop_element(image_data, element.top_left, element.bottom_right)

    draw = ImageDraw.Draw(cropped_image)
    draw.text((0, 0), "Class: " + str(element.classification))

    cropped_image.show()


def crop_element(image: np.ndarray, top_left: Tuple[float, float], bottom_right: Tuple[float, float]) -> PILImage.Image:
    """Crops the image based on bounding box coordinates."""
    pil_image = PILImage.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    (x_min, y_min), (x_max, y_max) = top_left, bottom_right
    return pil_image.crop((x_min, y_min, x_max, y_max))


def delete_temp_images(directory: str) -> None:
    """Deletes all images in the temporary directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
