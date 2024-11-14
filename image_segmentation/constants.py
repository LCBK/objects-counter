import os

import numpy as np

TEMP_IMAGE_DIR = os.path.join("images", "temp")
DEFAULT_COLOR_WEIGHT = 0.5

BW = 20
A = 1.0
SIGMA = 1.0

ISCC_NBS_CENTROIDS_RGB = np.array([
    [231, 141, 170],    # PINK
    [186, 42, 94],      # RED
    [217, 89, 45],      # ORANGE
    [131, 75, 44],      # BROWN
    [215, 182, 74],     # YELLOW
    [94, 94, 9],        # OLIVE
    [160, 194, 69],     # YELLOW GREEN
    [73, 193, 114],     # GREEN
    [66, 114, 195],     # BLUE
    [158, 66, 189],     # PURPLE
    [231, 225, 233],    # WHITE
    [147, 142, 147],    # GRAY
    [43, 41, 43],       # BLACK
    ], dtype=np.float32) / 255.0
