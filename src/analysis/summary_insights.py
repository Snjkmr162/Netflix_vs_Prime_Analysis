"""
Summary Insights — Single dashboard visual combining all key findings
This is your LinkedIn hero image
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np

NETFLIX_COLOR = "#E50914"
PRIME_COLOR   = "#00A8E1"
COLOR_MAP     = {"Netflix": NETFLIX_COLOR, "Prime Video": PRIME_COLOR}

plt.rcParams.update({
    "figure.facecolor": "#0f0f0f",
    "axes.facecolor":   "#1a1a1a",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "grid.color":       "#2a2a2a",
    "font.family":      "sans-serif",
})

VISUALS_PATH = os.path.join("..", "..", "visuals")


def load() -> pd.DataFrame:
    path = os.path.join("..", "..", "data", "processed", "clean_titles.csv")
    df   = pd.read_csv(path)
    df["year"]         = pd.to_numeric(df["year"],         errors="coerce")
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["popularity"]   = pd.to_numeric(df["popularity"],   errors="coerce")
    return df


def plot_summary_dashboard(df: pd.DataFrame):
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor("#0a0a0a")

    # Title banner
    fig.text(0.5, 0.97,
             "Netflix vs Prime Video — Strategic Analysis Dashboard",
             ha="center", va="top", fontsize=22, fontweight="bold",
             color="white")
    fig.text(0.5, 0.945,
             "Data: Watchmode API + TMDb API  |  500 titles  |  2026",
             ha="center", va="top", fontsize=11, color="#888888")

    gs = gridspec.GridSpec(
        3, 3,
        figure=fig,
        hspace=0.55,
        wspace=0.38,
        top=0.91, bottom=0.06,
        left=0.06, right=0.97,
    )

    # ── Row 1: KPI scorecards ─────────────────────────────────────────────────
    kpis = [
        ("Total Titles",      "250",   "250",   "equal"),
        ("Avg Rating",        "7.49",  "7.40",  "netflix"),
        ("Avg Popularity",    "18.1",  "19.5",  "prime"),
        ("International %",  "19.2%", "6.0%",  "netflix"),
        ("Animation Titles",  "29",    "15",    "netflix"),
    ]

    for col, (label, nval, pval, winner) in enumerate(kpis[:3]):
        ax = fig.add_subplot(gs[0, col])
        ax.set_facecolor("#111111")
        ax.axis("off")

        n_color = NETFLIX_COLOR if winner in ("netflix", "equal") else "#666"
        p_color = PRIME_COLOR   if winner in ("prime",   "equal") else "#666"

        ax.text(0.5, 0.82, label,
                ha="center", va="center", fontsize=12,
                color="#aaaaaa", transform=ax.transAxes)
        ax.text(0.25, 0.42, nval,
                ha="center", va="center", fontsize=26,
                fontweight="bold", color=n_color,
                transform=ax.transAxes)
        ax.text(0.75, 0.42, pval,
                ha="center", va="center", fontsize=26,
                fontweight="bold", color=p_color,
                transform=ax.transAxes)
        ax.text(0.25, 0.12, "Netflix",
                ha="center", va="center", fontsize=10,
                color=NETFLIX_COLOR, transform=ax.transAxes)
        ax.text(0.75, 0.12, "Prime",
                ha="center", va="center", fontsize=10,
                color=PRIME_COLOR, transform=ax.transAxes)

        # Divider line
        ax.plot([0.5, 0.5], [0.1, 0.9], color="#333", linewidth=1,
                transform=ax.transAxes)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333333")
            spine.set_visible(True)

    # ── Row 2 left: Content per year ──────────────────────────────────────────
    ax1 = fig.add_subplot(gs[1, 0:2])
    yearly = (
        df[df["year"] >= 2015]
        .groupby(["year", "platform"])
        .size()
        .reset_index(name="count")
    )
    for platform, color in COLOR_MAP.items():
        d = yearly[yearly["platform"] == platform]
        ax1.plot(d["year"], d["count"], marker="o",
                 label=platform, color=color,
                 linewidth=2, markersize=5)
        ax1.fill_between(d["year"], d["count"], alpha=0.08, color=color)

    ax1.set_title("Content Added Per Year (2015+)", fontsize=12, pad=8)
    ax1.set_xlabel("Year", fontsize=9)
    ax1.set_ylabel("Titles", fontsize=9)
    ax1.legend(fontsize=9)
    ax1.tick_params(labelsize=8)

    # ── Row 2 right: International share ─────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 2])
    platforms  = ["Netflix", "Prime Video"]
    intl_pcts  = [19.2, 6.0]
    colors     = [NETFLIX_COLOR, PRIME_COLOR]
    bars = ax2.bar(platforms, intl_pcts, color=colors, alpha=0.85, width=0.5)
    for bar, val in zip(bars, intl_pcts):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.4,
                 f"{val}%", ha="center", fontsize=13,
                 fontweight="bold", color="white")
    ax2.set_title("International Content %", fontsize=12, pad=8)
    ax2.set_ylabel("% of Library", fontsize=9)
    ax2.tick_params(labelsize=8)
    ax2.set_ylim(0, 28)

    # ── Row 3 left: Ratings over time ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2, 0:2])
    yearly_r = (
        df[df["year"] >= 2015]
        .groupby(["year", "platform"])["vote_average"]
        .mean()
        .reset_index()
    )
    for platform, color in COLOR_MAP.items():
        d = yearly_r[yearly_r["platform"] == platform]
        ax3.plot(d["year"], d["vote_average"], marker="o",
                 label=platform, color=color,
                 linewidth=2, markersize=5)
        ax3.fill_between(d["year"], d["vote_average"],
                         alpha=0.08, color=color)

    ax3.set_title("Avg Content Rating Over Time (2015+)", fontsize=12, pad=8)
    ax3.set_xlabel("Year", fontsize=9)
    ax3.set_ylabel("Avg TMDb Rating", fontsize=9)
    ax3.set_ylim(5.5, 9)
    ax3.legend(fontsize=9)
    ax3.tick_params(labelsize=8)

    # ── Row 3 right: Top genres ───────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[2, 2])
    top_genres = ["Drama", "Comedy", "Animation", "Action", "Crime"]
    n_vals = [df[(df["platform"] == "Netflix") &
                 (df["primary_genre"] == g)].shape[0] for g in top_genres]
    p_vals = [df[(df["platform"] == "Prime Video") &
                 (df["primary_genre"] == g)].shape[0] for g in top_genres]

    x          = np.arange(len(top_genres))
    bar_width  = 0.35
    ax4.bar(x - bar_width/2, n_vals, bar_width,
            label="Netflix",     color=NETFLIX_COLOR, alpha=0.85)
    ax4.bar(x + bar_width/2, p_vals, bar_width,
            label="Prime Video", color=PRIME_COLOR,   alpha=0.85)
    ax4.set_xticks(x)
    ax4.set_xticklabels(top_genres, fontsize=8, rotation=15)
    ax4.set_title("Top 5 Genres Comparison", fontsize=12, pad=8)
    ax4.set_ylabel("Titles", fontsize=9)
    ax4.legend(fontsize=8)
    ax4.tick_params(labelsize=8)

    # ── Footer ────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.02,
             "Key finding: Netflix is investing 3x more in international content "
             "and shows a widening quality gap vs Prime Video since 2022.",
             ha="center", fontsize=11, color="#cccccc",
             style="italic")

    path = os.path.join(VISUALS_PATH, "00_summary_dashboard.png")
    plt.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  Saved → {path}")
    plt.show()


if __name__ == "__main__":
    print("Loading clean data...")
    df = load()

    print("Building summary dashboard...")
    plot_summary_dashboard(df)
    print("\nSummary dashboard complete.")
    print("This is your LinkedIn hero image — visuals/00_summary_dashboard.png")