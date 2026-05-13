"""
Quantitative Analysis — Ratings & Quality
Compares content quality between Netflix and Prime Video
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import scipy.stats as stats
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
    df   = pd.read_csv(path)
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["popularity"]   = pd.to_numeric(df["popularity"],   errors="coerce")
    df["year"]         = pd.to_numeric(df["year"],         errors="coerce")
    return df[df["vote_average"] > 0].copy()


# ── Chart 1 — Rating distributions (box + violin) ────────────────────────────
def plot_rating_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Box plot
    data_n = df[df["platform"] == "Netflix"]["vote_average"]
    data_p = df[df["platform"] == "Prime Video"]["vote_average"]

    axes[0].boxplot(
        [data_n, data_p],
        labels=["Netflix", "Prime Video"],
        patch_artist=True,
        boxprops=dict(facecolor="#333"),
        medianprops=dict(color="white", linewidth=2),
        whiskerprops=dict(color="white"),
        capprops=dict(color="white"),
        flierprops=dict(markerfacecolor="white", markersize=4),
    )
    # Color the boxes
    colors = [NETFLIX_COLOR, PRIME_COLOR]
    for patch, color in zip(axes[0].patches, colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    axes[0].set_title("Rating Distribution — Box Plot", fontsize=14)
    axes[0].set_ylabel("TMDb Vote Average")

    # Violin plot
    parts = axes[1].violinplot(
        [data_n, data_p],
        positions=[1, 2],
        showmedians=True,
        showmeans=False,
    )
    for pc, color in zip(parts["bodies"], colors):
        pc.set_facecolor(color)
        pc.set_alpha(0.7)
    parts["cmedians"].set_color("white")
    parts["cbars"].set_color("white")
    parts["cmins"].set_color("white")
    parts["cmaxes"].set_color("white")

    axes[1].set_xticks([1, 2])
    axes[1].set_xticklabels(["Netflix", "Prime Video"])
    axes[1].set_title("Rating Distribution — Violin Plot", fontsize=14)
    axes[1].set_ylabel("TMDb Vote Average")

    plt.suptitle("Content Quality Comparison", fontsize=16, y=1.02)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "07_rating_distributions.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 2 — Avg rating over time ───────────────────────────────────────────
def plot_ratings_over_time(df: pd.DataFrame):
    yearly = (
        df[df["year"] >= 2010]
        .groupby(["year", "platform"])["vote_average"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    for platform, color in COLOR_MAP.items():
        data = yearly[yearly["platform"] == platform]
        ax.plot(data["year"], data["vote_average"],
                marker="o", label=platform,
                color=color, linewidth=2.5, markersize=6)
        ax.fill_between(data["year"], data["vote_average"],
                        alpha=0.08, color=color)

    ax.set_title("Average Content Rating Over Time", fontsize=16, pad=15)
    ax.set_xlabel("Year")
    ax.set_ylabel("Avg TMDb Vote Average")
    ax.set_ylim(5, 9)
    ax.legend(fontsize=12)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "08_ratings_over_time.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 3 — Rating category breakdown ──────────────────────────────────────
def plot_rating_categories(df: pd.DataFrame):
    cat_order  = ["Poor", "Average", "Good", "Great"]
    cat_counts = (
        df.groupby(["platform", "rating_category"])
        .size()
        .reset_index(name="count")
    )
    # Percentage within each platform
    totals = cat_counts.groupby("platform")["count"].transform("sum")
    cat_counts["pct"] = (cat_counts["count"] / totals * 100).round(1)

    fig, ax = plt.subplots(figsize=(10, 6))

    platforms  = ["Netflix", "Prime Video"]
    x          = np.arange(len(cat_order))
    bar_width  = 0.35

    for i, (platform, color) in enumerate(COLOR_MAP.items()):
        data   = cat_counts[cat_counts["platform"] == platform]
        data   = data.set_index("rating_category").reindex(cat_order).fillna(0)
        offset = x + i * bar_width

        bars = ax.bar(offset, data["pct"], width=bar_width,
                      label=platform, color=color, alpha=0.85)

        for bar, val in zip(bars, data["pct"]):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.5,
                        f"{val:.1f}%", ha="center",
                        fontsize=9, color="white")

    ax.set_xticks(x + bar_width / 2)
    ax.set_xticklabels(cat_order)
    ax.set_title("Rating Category Breakdown by Platform", fontsize=16, pad=15)
    ax.set_ylabel("% of Titles")
    ax.legend(fontsize=12)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "09_rating_categories.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Statistical test ──────────────────────────────────────────────────────────
def run_ttest(df: pd.DataFrame):
    netflix = df[df["platform"] == "Netflix"]["vote_average"].dropna()
    prime   = df[df["platform"] == "Prime Video"]["vote_average"].dropna()

    t_stat, p_value = stats.ttest_ind(netflix, prime)

    print("\n=== RATINGS INSIGHTS ===")
    print(f"\nNetflix   — mean: {netflix.mean():.2f}, "
          f"median: {netflix.median():.2f}, std: {netflix.std():.2f}")
    print(f"Prime Video — mean: {prime.mean():.2f}, "
          f"median: {prime.median():.2f}, std: {prime.std():.2f}")
    print(f"\nT-test result:")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value:     {p_value:.4f}")

    if p_value < 0.05:
        better = "Netflix" if netflix.mean() > prime.mean() else "Prime Video"
        print(f"  Result: Statistically significant difference (p < 0.05)")
        print(f"  {better} has significantly higher rated content.")
    else:
        print(f"  Result: No statistically significant difference (p >= 0.05)")
        print(f"  Both platforms have comparable content quality.")

    print(f"\nPopularity comparison:")
    for platform in ["Netflix", "Prime Video"]:
        pop = df[df["platform"] == platform]["popularity"].dropna()
        print(f"  {platform} avg popularity: {pop.mean():.2f}")


if __name__ == "__main__":
    print("Loading clean data...")
    df = load()

    print("\nGenerating charts...")
    plot_rating_distribution(df)
    plot_ratings_over_time(df)
    plot_rating_categories(df)

    run_ttest(df)
    print("\nRatings analysis complete.")