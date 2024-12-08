import math
from typing import List

import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from tests.helpers import translate_category


def plot_similarity_heatmap(similarity_df, title, subtitle, game_name="Na skrzydłach"):
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
    plt.title(f"{game_name}\n{title}\n({subtitle})\n", fontsize=14, fontweight="bold")
    plt.xticks(rotation=90, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.show()


def display_images_in_grid(images: List[str], category_name: str, image_size=(100, 100), grid_width=5):
    """
    Display images in a grid format with classifications as titles.
    """
    total_images = len(images)

    num_rows = math.ceil(total_images / grid_width)

    fig, axes = plt.subplots(num_rows, grid_width, figsize=(grid_width * 3, num_rows * 3))
    axes = axes.flatten()

    current_index = 0

    for file_path in images:
        if current_index >= len(axes):
            break

        ax = axes[current_index]
        current_index += 1

        try:
            img = Image.open(file_path).resize(image_size)

            ax.imshow(img)
            ax.axis('off')
            ax.set_title(f"Klasyfikacja: {category_name}", fontsize=8)
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            ax.axis('off')

    for ax in axes[current_index:]:
        ax.axis('off')

    plt.tight_layout()
    plt.show()

