import argparse

import cv2


def count_objects(image_path):
    # Read the image
    image = cv2.imread("helpers\\images\\" + image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError(f"Image not found at {image_path}")

    # Apply a binary threshold to ensure the image is binary
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the objects
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Count the number of contours found
    object_count = len(contours)

    print(f"Number of objects found: {object_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count objects in a binary image",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", dest="input", help="read this file", metavar="FILE", required=True)
    args = parser.parse_args()

    count_objects(args.input)
