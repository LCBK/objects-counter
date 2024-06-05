import argparse

import cv2
import numpy as np


def fill_holes(image_path, output_path):
    # Read the image
    image = cv2.imread("helpers\\images\\" + image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError(f"Image not found at {image_path}")

    # Apply a binary threshold to ensure the image is binary
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Invert the binary image
    inverted_binary_image = cv2.bitwise_not(binary_image)

    # Perform morphological closing (dilation followed by erosion)
    kernel = np.ones((6, 6), np.uint8)
    closed_image = cv2.morphologyEx(inverted_binary_image, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Invert the image back to original
    result_image = cv2.bitwise_not(closed_image)

    # Save the result
    cv2.imwrite("helpers\\images\\" + output_path, result_image)

    print(f"Processed image saved as {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill holes in a binary image",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", dest="input", help="read this file", metavar="FILE", required=True)
    parser.add_argument("-o", "--output", dest="output", help="write filled image here", metavar="FILE", required=True)
    args = parser.parse_args()

    fill_holes(args.input, args.output)
