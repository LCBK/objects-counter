import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def remove_background(input_path, output_path):
    img = cv2.imread(input_path)

    lower = np.array([100, 100, 100])
    upper = np.array([255, 255, 255])

    # Create mask to only select black
    thresh = cv2.inRange(img, lower, upper)

    result = cv2.bitwise_and(img, img, mask=thresh)

    cv2.imwrite(output_path, result)




if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python remove_background.py <input_image_path> <output_image_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    remove_background(input_path, output_path)
