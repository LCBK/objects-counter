import numpy as np
import matplotlib.pyplot as plt
import cv2
import torch
import torchvision
from segment_anything import sam_model_registry, SamPredictor


class Image:
    def __init__(self, data, type):
        self.data = data  # to do
        self.result = None

class SegmentAnythingObjectCounter:
    def __init__(self, sam_checkpoint_path, model_type="vit_h"):
        print("Creating new Segment Anything Object Counter")
        print("PyTorch version:", torch.__version__)
        print("Torchvision version:", torchvision.__version__)
        print("CUDA is available:", torch.cuda.is_available())
        if not torch.cuda.is_available():
            raise Exception("Cuda is not available")
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint_path)
        self.sam.to(device="cuda")
        self.predictor = SamPredictor(self.sam)
        self.images = []

    def add_image(self, data, type):
        self.images.append(Image(data, type))
        return len(self.images) - 1

    def calculate_image_mask(self, index, points):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + index + " images array size:" + len(self.images))
            return False
        self.predictor.set_image(self.images[index].data)
        masks, scores, logits = self.predictor.predict(
            point_coords=np.array(points),
            point_labels=np.array([1] * len(points)),
            multimask_output=True)
        self.images[index].result = masks[2]
        return True

    def get_image_mask(self, index):
        if index < 0 or index >= len(self.images):
            print("Given image index is out of bounds. index: " + index + " images array size:" + len(self.images))
            return None
        return self.images[index].result


