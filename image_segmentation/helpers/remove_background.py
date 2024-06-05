import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def remove_background(input_path, output_path):
    input_image = Image.open(input_path)
    output = remove(input_image)
    output_np = np.array(output)

    if output_np.shape[2] == 4:
        output_np = cv2.cvtColor(output_np, cv2.COLOR_RGBA2BGRA)

    transparent_to_white(output_np, output_path)


def transparent_to_white(image, output_path):
    if image is None:
        raise ValueError("Image not found")

    # Check if the image has an alpha channel
    if image.shape[2] == 4:
        # Split the image into its color channels and alpha channel
        b, g, r, alpha = cv2.split(image)

        # Normalize the alpha channel to range [0, 1]
        alpha_normalized = alpha / 255.0

        # Create a white background
        white_background = np.ones_like(b, dtype=np.uint8) * 255

        # Blend the original image with the white background using the alpha channel
        b = b * alpha_normalized + white_background * (1 - alpha_normalized)
        g = g * alpha_normalized + white_background * (1 - alpha_normalized)
        r = r * alpha_normalized + white_background * (1 - alpha_normalized)

        # Merge the channels back without the alpha channel
        image = cv2.merge((b.astype(np.uint8), g.astype(np.uint8), r.astype(np.uint8)))
    else:
        raise ValueError("The image does not have an alpha channel.")

    # Save the result
    cv2.imwrite("helpers\\images\\" + output_path, image)

    print(f"Processed image saved as {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python remove_background.py <input_image_path> <output_image_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    remove_background(input_path, output_path)
