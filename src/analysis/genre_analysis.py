"""
Quantitative Analysis — Genre Analysis
Compares genre strategies between Netflix and Prime Video
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

NETFLIX_COLOR = "#E50914"
PRIME_COLOR   = "#00A8E1"
COLOR_MAP     = {"Netflix": NETFLIX_COLOR, "Prime Video": PRIME_COLOR}

sns.set_theme(style="darkgrid")
plt.rcParams.update({
    "figure.facecolor": "#0f0f0f",
    "axes.facecolor":   "#1a1a1a",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "grid.color":       "#333333",
})

VISUALS_PATH = os.path.join("..", "..", "visuals")


def load() -> pd.DataFrame:
    path = os.path.join("..", "..", "data", "processed", "clean_titles.csv")
    return pd.read_csv(path)


# ── Chart 1 — Top genres side by side ────────────────────────────────────────
def plot_top_genres(df: pd.DataFrame):
    top_n = 10

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, (platform, color) in zip(axes, COLOR_MAP.items()):
        # Filter to one platform, count genres, take top 10
        data = (
            df[df["platform"] == platform]["primary_genre"]
            .value_counts()
            .head(top_n)
            .reset_index()
        )
        data.columns = ["primary_genre", "count"]
        data = data.sort_values("count")

        bars = ax.barh(data["primary_genre"], data["count"],
                       color=color, alpha=0.85)

        # Add value labels
        for bar, val in zip(bars, data["count"]):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=10, color="white")

        ax.set_title(f"{platform} — Top {top_n} Genres",
                     fontsize=14, color=color, pad=12)
        ax.set_xlabel("Number of Titles")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.suptitle("Genre Strategy Comparison", fontsize=18, y=1.02)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "04_top_genres.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()

# ── Chart 2 — Genre overlap heatmap ──────────────────────────────────────────
def plot_genre_heatmap(df: pd.DataFrame):
    # Get top 12 genres overall
    top_genres = (
        df["primary_genre"]
        .value_counts()
        .head(12)
        .index.tolist()
    )

    filtered = df[df["primary_genre"].isin(top_genres)]

    pivot = (
        filtered.groupby(["primary_genre", "platform"])
        .size()
        .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        pivot,
        annot=True,
        fmt="d",
        cmap="RdBu",
        linewidths=0.5,
        linecolor="#333",
        ax=ax,
        cbar_kws={"label": "Number of Titles"},
    )

    ax.set_title("Genre Heatmap — Netflix vs Prime Video",
                 fontsize=16, pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "05_genre_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 3 — Genre diversity score ──────────────────────────────────────────
def plot_genre_diversity(df: pd.DataFrame):
    """
    Genre diversity = number of unique genres per platform.
    Also shows avg genre_count per title (how multi-genre each title is).
    """
    diversity = (
        df.groupby("platform")
        .agg(
            unique_genres=("primary_genre", "nunique"),
            avg_genres_per_title=("genre_count", "mean"),
        )
        .reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Unique genres
    colors = [NETFLIX_COLOR, PRIME_COLOR]
    axes[0].bar(diversity["platform"], diversity["unique_genres"],
                color=colors, alpha=0.85, width=0.5)
    axes[0].set_title("Unique Genres in Library", fontsize=14)
    axes[0].set_ylabel("Count")
    for i, v in enumerate(diversity["unique_genres"]):
        axes[0].text(i, v + 0.3, str(v), ha="center",
                     fontsize=13, color="white")

    # Avg genres per title
    axes[1].bar(diversity["platform"], diversity["avg_genres_per_title"],
                color=colors, alpha=0.85, width=0.5)
    axes[1].set_title("Avg Genre Tags Per Title", fontsize=14)
    axes[1].set_ylabel("Avg Count")
    for i, v in enumerate(diversity["avg_genres_per_title"]):
        axes[1].text(i, v + 0.02, f"{v:.2f}", ha="center",
                     fontsize=13, color="white")

    plt.suptitle("Genre Diversity — Which Platform is More Varied?",
                 fontsize=16, y=1.02)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "06_genre_diversity.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Console insights ──────────────────────────────────────────────────────────
def print_insights(df: pd.DataFrame):
    print("\n=== GENRE INSIGHTS ===")

    for platform in ["Netflix", "Prime Video"]:
        p = df[df["platform"] == platform]
        top3 = p["primary_genre"].value_counts().head(3)
        print(f"\n{platform}:")
        print(f"  Top 3 genres: {', '.join(top3.index.tolist())}")
        print(f"  Unique genres: {p['primary_genre'].nunique()}")
        print(f"  Avg genres per title: {p['genre_count'].mean():.2f}")
        print(f"  Drama share: {len(p[p['primary_genre']=='Drama'])/len(p)*100:.1f}%")


if __name__ == "__main__":
    print("Loading clean data...")
    df = load()

    print("\nGenerating charts...")
    plot_top_genres(df)
    plot_genre_heatmap(df)
    plot_genre_diversity(df)

    print_insights(df)
    print("\nGenre analysis complete.")