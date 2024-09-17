import os
from PIL import Image


def save_cropped_image(image: Image.Image, path: str) -> None:
    """Saves a cropped image to the specified path."""
    image.save(path)


def delete_temp_images(directory: str) -> None:
    """Deletes all images in the temporary directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
