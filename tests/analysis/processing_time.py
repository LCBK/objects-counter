import os
import time

import matplotlib.pyplot as plt
from PIL import Image as PILImage

from objects_counter import app
from objects_counter.api.default.views import feature_similarity_model, color_similarity_model


def resize_image(image_path, resolution):
    """Resize the image to the given resolution."""
    with PILImage.open(image_path) as img:
        resized_img = img.resize(resolution)
    return resized_img


def compute_feature_vector(image_path):
    """Compute feature vector and measure processing time."""
    image_tensor = feature_similarity_model.preprocess_image(image_path)

    start = time.perf_counter()
    feature_vector = feature_similarity_model.get_embedding(image_tensor)
    end = time.perf_counter()
    return feature_vector, end - start


def compute_histogram(image):
    """Compute histogram and measure processing time."""
    start = time.perf_counter()
    histogram = color_similarity_model.get_histogram(image)
    end = time.perf_counter()
    return histogram, end - start


def analyze_resolution_influence(image_paths, resolutions):
    """Analyze processing times for different resolutions."""
    results = {resolution: {"Feature Times": [], "Histogram Times": []} for resolution in resolutions}

    for resolution in resolutions:
        for image_path in image_paths:
            resized_image = resize_image(image_path, resolution)
            try:
                resized_image.save(image_path[:-4] + "_resized.jpg")

                _, feature_time = compute_feature_vector(image_path[:-4] + "_resized.jpg")
                _, histogram_time = compute_histogram(resized_image)
                results[resolution]["Feature Times"].append(feature_time)
                results[resolution]["Histogram Times"].append(histogram_time)

                os.remove(image_path[:-4] + "_resized.jpg")
            except FileNotFoundError:
                continue

    return results


def plot_processing_times(results):
    """Plot processing times for feature extraction and histogram computation."""
    resolutions = list(results.keys())
    avg_feature_times = [
        sum(results[res]["Feature Times"]) / len(results[res]["Feature Times"])
        for res in resolutions
    ]
    avg_histogram_times = [
        sum(results[res]["Histogram Times"]) / len(results[res]["Histogram Times"])
        for res in resolutions
    ]

    plt.figure(figsize=(10, 6))
    plt.plot(resolutions, avg_feature_times, label="Czas obliczania wektora cech", marker="o")
    plt.plot(resolutions, avg_histogram_times, label="Czas obliczania histogramu", marker="o")
    plt.xlabel("Rozdzielczość (px)")
    plt.ylabel("Średni czas przetwarzania (s)")
    plt.title("Wpływ rozdzielczości obrazów na czas przetwarzania")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    with app.app.app_context():
        image_dir = "/home/shairys/objects/objects-counter/tests/elements/diffused"
        image_paths = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith(".jpg")]
        resolutions = [(16, 16), (32, 32), (64, 64), (128, 128), (224, 224), (518, 518)]

        results = analyze_resolution_influence(image_paths, resolutions)
        plot_processing_times(results)
