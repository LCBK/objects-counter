import matplotlib.pyplot as plt
import seaborn as sns

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
