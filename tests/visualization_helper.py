import matplotlib.pyplot as plt
import seaborn as sns


def plot_similarity_heatmap(similarity_df, title, subtitle, font):
    """Plots a heatmap for the similarity matrix."""
    plt.figure(figsize=(10, 8))
    sns.set(font=font)
    sns.heatmap(similarity_df, annot=True, cmap="bwr", cbar=True, fmt=".2f", vmin=0.0, vmax=1.0)
    plt.title(f"{title}\n{subtitle}", fontsize=16)
    plt.tight_layout()
    plt.show()
