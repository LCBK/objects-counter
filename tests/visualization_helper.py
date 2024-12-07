import math
from typing import Dict, List

import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from tests.helpers import translate_category


def plot_similarity_heatmap(similarity_df, title, subtitle, game_name="Gra"):
    """Plot a heatmap of similarity values with improved readability."""
    similarity_df_polish = similarity_df.rename(
        index=lambda x: translate_category(x),
        columns=lambda x: translate_category(x)
    )

    plt.figure(figsize=(10, 8))
    sns.set(font="Arial")
    sns.heatmap(
        similarity_df_polish,
        annot=True,
        fmt=".2f",
        cmap="bwr",
        cbar=True,
        linewidths=0.5,
        vmin=0.0,
        vmax=1.0
    )
    plt.title(f"{title}\n({subtitle})\n", fontsize=14, fontweight="bold")
    plt.xticks(rotation=90, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.show()


def display_images_in_grid(classifications: Dict[str, List[str]], image_size=(100, 100), grid_width=5):
    """
    Display images in a grid format with classifications as titles.

    :param classifications: A dictionary with classification as keys and lists of file paths as values.
    :param image_size: Tuple specifying the size (width, height) to resize each image.
    :param grid_width: Number of images per row in the grid.
    """
    # Count total number of images
    total_images = sum(len(paths) for paths in classifications.values())

    # Calculate number of rows needed
    num_rows = math.ceil(total_images / grid_width)

    # Create a figure for the grid
    fig, axes = plt.subplots(num_rows, grid_width, figsize=(grid_width * 3, num_rows * 3))
    axes = axes.flatten()  # Flatten the axes for easy indexing

    # Track the current image index
    current_index = 0

    for classification, file_paths in classifications.items():
        for file_path in file_paths:
            if current_index >= len(axes):
                break

            ax = axes[current_index]
            current_index += 1

            try:
                # Open and resize the image
                img = Image.open(file_path).resize(image_size)

                # Display the image
                ax.imshow(img)
                ax.axis('off')  # Hide axes
                ax.set_title(classification, fontsize=8)  # Add classification as title
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")
                ax.axis('off')  # If error, keep the grid slot empty

    # Hide unused axes
    for ax in axes[current_index:]:
        ax.axis('off')

    plt.tight_layout()
    plt.show()