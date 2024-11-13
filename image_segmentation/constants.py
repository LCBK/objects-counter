import os

import numpy as np

TEMP_IMAGE_DIR = os.path.join("images", "temp")
DEFAULT_COLOR_WEIGHT = 0.5

BW = 20
A = 1.0
SIGMA = 1.0

ISCC_NBS_CENTROIDS_RGB = np.array([
    [255, 192, 203],    # PINK
    [255, 0, 0],        # RED
    [255, 165, 0],      # ORANGE
    [150, 75, 0],       # BROWN
    [255, 255, 0],      # YELLOW
    [128, 128, 0],      # OLIVE
    [128, 255, 0],      # YELLOW GREEN
    [0, 255, 0],        # GREEN
    [0, 0, 255],        # BLUE
    [128, 0, 128],      # PURPLE
    [255, 255, 255],    # WHITE
    [128, 128, 128],    # GRAY
    [0, 0, 0],          # BLACK
], dtype=np.float32) / 255.0
