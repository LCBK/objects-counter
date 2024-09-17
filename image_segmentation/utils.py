import os
from typing import Tuple

import cv2
import numpy as np
from PIL import Image


def crop_image(image: np.ndarray, top_left: Tuple[float, float], bottom_right: Tuple[float, float]) -> Image.Image:
    """Crops the image based on bounding box coordinates."""
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    (x_min, y_min), (x_max, y_max) = top_left, bottom_right
    return pil_image.crop((x_min, y_min, x_max, y_max))


def delete_temp_images(directory: str) -> None:
    """Deletes all images in the temporary directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
