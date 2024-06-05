import argparse

import cv2
import numpy as np
from PIL import Image


def binarize_image(img_path, target_path, threshold):
    """Binarize an image."""
    image_file = Image.open("helpers\\images\\" + img_path)
    image = image_file.convert('L')  # convert image to monochrome
    image = np.array(image)
    image = binarize_array(image, threshold)
    cv2.imwrite(target_path, image)


def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binarize an image",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", dest="input", help="read this file", metavar="FILE", required=True)
    parser.add_argument("-o", "--output", dest="output", help="write binarized file here", metavar="FILE",
                        required=True)
    parser.add_argument("--threshold", dest="threshold", default=200, type=int, help="Threshold when to show white")
    args = parser.parse_args()

    binarize_image(args.input, "helpers\\images\\" + args.output, args.threshold)
