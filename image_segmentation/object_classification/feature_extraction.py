import cv2
import numpy as np
import torch
import torchvision
from PIL import Image
from scipy.spatial import distance
from torch import nn
from torchvision import transforms as tr
from torchvision.models import vit_h_14


class CosineSimilarity:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()

    def load_model(self) -> nn.Module:
        """Loads a pretrained Vision Transformer model."""
        weights = torchvision.models.ViT_H_14_Weights.DEFAULT
        model = vit_h_14(weights=weights)
        model.heads = nn.Sequential(*list(model.heads.children())[:-1])
        model = model.to(self.device)
        return model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocesses the image before embedding extraction."""
        img = Image.open(image_path)
        transformations = tr.Compose(
            [tr.ToTensor(), tr.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), tr.Resize((518, 518))])
        img = transformations(img).float().unsqueeze_(0).to(self.device)
        return img

    def get_embedding(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """Generates the embedding vector for the given image tensor."""
        with torch.no_grad():
            embedding = self.model(image_tensor).cpu()
        return embedding


def compute_color_histogram(image: Image.Image, bins: int = 16) -> np.ndarray:
    """Computes a color histogram for an image."""
    image = image.convert('RGB')
    histogram = []

    # Calculate histogram for each channel
    for channel in range(3):
        channel_hist = cv2.calcHist([np.array(image)], [channel], None, [bins], [0, 256])
        channel_hist = cv2.normalize(channel_hist, channel_hist).flatten()
        histogram.append(channel_hist)

    return np.concatenate(histogram)


def compute_color_similarity(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """Calculates the Bray-Curtis distance between two histograms."""
    return 1 - distance.braycurtis(hist1, hist2)
