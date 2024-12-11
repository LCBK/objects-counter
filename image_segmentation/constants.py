import os

import numpy as np

TEMP_IMAGE_DIR = os.path.join("images", "temp")
DEFAULT_COLOR_WEIGHT = 0.3

BW = 60
SIGMA = 18

ISCC_NBS_CENTROIDS_RGB = np.array([
    [
        [230, 134, 151],    # PINK
        [185, 50, 66],      # RED
        [220, 125, 52],     # ORANGE
        [127, 72, 41],      # BROWN
        [217, 180, 81],     # YELLOW
        [114, 103, 44],     # OLIVE
        [160, 194, 69],     # YELLOW GREEN
        [79, 191, 154],     # GREEN
        [59, 116, 192],     # BLUE
        [172, 74, 195],     # PURPLE
        [231, 225, 233],    # WHITE
        [147, 142, 147],    # GRAY
        [43, 41, 43],       # BLACK
    ]], dtype=np.float32) / 255.0
