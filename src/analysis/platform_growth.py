"""
Quantitative Analysis — Platform Growth
Analyzes content volume trends over time for Netflix vs Prime Video
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

# ── Style ─────────────────────────────────────────────────────────────────────
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
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df[df["year"] >= 2010].copy()   # focus on streaming era


# ── Chart 1 — Content added per year ─────────────────────────────────────────
def plot_yearly_growth(df: pd.DataFrame):
    yearly = (
        df.groupby(["year", "platform"])
        .size()
        .reset_index(name="count")
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    for platform, color in COLOR_MAP.items():
        data = yearly[yearly["platform"] == platform]
        ax.plot(data["year"], data["count"], marker="o",
                label=platform, color=color, linewidth=2.5, markersize=6)
        ax.fill_between(data["year"], data["count"],
                        alpha=0.1, color=color)

    ax.set_title("Content Added Per Year — Netflix vs Prime Video",
                 fontsize=16, pad=15)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Titles")
    ax.legend(fontsize=12)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "01_yearly_growth.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 2 — Movies vs TV split per platform ─────────────────────────────────
def plot_content_type_split(df: pd.DataFrame):
    type_counts = (
        df.groupby(["platform", "type"])
        .size()
        .reset_index(name="count")
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    for ax, (platform, color) in zip(axes, COLOR_MAP.items()):
        data   = type_counts[type_counts["platform"] == platform]
        labels = data["type"].str.replace("_", " ").str.title()
        ax.pie(data["count"], labels=labels, autopct="%1.1f%%",
               colors=[color, "#888888"],
               textprops={"color": "white"}, startangle=90)
        ax.set_title(platform, fontsize=14, color=color)

    fig.suptitle("Movies vs TV Series Split", fontsize=16, y=1.02)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "02_content_type_split.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 3 — Decade distribution ─────────────────────────────────────────────
def plot_decade_distribution(df: pd.DataFrame):
    decade_counts = (
        df.groupby(["decade", "platform"])
        .size()
        .reset_index(name="count")
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    platforms = ["Netflix", "Prime Video"]
    decades   = sorted(decade_counts["decade"].dropna().unique())
    x         = range(len(decades))
    bar_width  = 0.35

    for i, platform in enumerate(platforms):
        data   = decade_counts[decade_counts["platform"] == platform]
        counts = [data[data["decade"] == d]["count"].values[0]
                  if d in data["decade"].values else 0
                  for d in decades]
        offset = [xi + i * bar_width for xi in x]
        ax.bar(offset, counts, width=bar_width,
               label=platform, color=list(COLOR_MAP.values())[i],
               alpha=0.85)

    ax.set_xticks([xi + bar_width / 2 for xi in x])
    ax.set_xticklabels([str(int(d)) + "s" for d in decades])
    ax.set_title("Content by Decade — How Old is Each Platform's Library?",
                 fontsize=16, pad=15)
    ax.set_xlabel("Decade")
    ax.set_ylabel("Number of Titles")
    ax.legend(fontsize=12)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "03_decade_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Console insights ──────────────────────────────────────────────────────────
def print_insights(df: pd.DataFrame):
    print("\n=== GROWTH INSIGHTS ===")

    for platform in ["Netflix", "Prime Video"]:
        p = df[df["platform"] == platform]
        recent = p[p["year"] >= 2020]
        print(f"\n{platform}:")
        print(f"  Total titles (2010+):  {len(p)}")
        print(f"  Titles since 2020:     {len(recent)} "
              f"({len(recent)/len(p)*100:.1f}% of library)")
        print(f"  Most active year:      "
              f"{p.groupby('year').size().idxmax()} "
              f"({p.groupby('year').size().max()} titles)")
        print(f"  Movies / TV ratio:     "
              f"{len(p[p['type']=='movie'])} / {len(p[p['type']=='tv_series'])}")


if __name__ == "__main__":
    print("Loading clean data...")
    df = load()

    print("\nGenerating charts...")
    plot_yearly_growth(df)
    plot_content_type_split(df)
    plot_decade_distribution(df)

    print_insights(df)
    print("\nGrowth analysis complete.")