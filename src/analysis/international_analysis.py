"""
Quantitative Analysis — International Content
Analyzes geographic diversity and language strategies
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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

# Readable country name map
COUNTRY_NAMES = {
    "US": "USA",       "GB": "UK",          "IN": "India",
    "JP": "Japan",     "KR": "South Korea", "FR": "France",
    "DE": "Germany",   "ES": "Spain",       "MX": "Mexico",
    "IT": "Italy",     "CA": "Canada",      "AU": "Australia",
    "BR": "Brazil",    "TR": "Turkey",      "TH": "Thailand",
    "DK": "Denmark",   "SE": "Sweden",      "NO": "Norway",
    "AR": "Argentina", "PL": "Poland",
}


def load() -> pd.DataFrame:
    path = os.path.join("..", "..", "data", "processed", "clean_titles.csv")
    df   = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


# ── Chart 1 — International vs English content ────────────────────────────────
def plot_international_share(df: pd.DataFrame):
    intl = (
        df.groupby(["platform", "is_international"])
        .size()
        .reset_index(name="count")
    )
    intl["label"] = intl["is_international"].map(
        {True: "International", False: "English"}
    )

    totals = intl.groupby("platform")["count"].transform("sum")
    intl["pct"] = (intl["count"] / totals * 100).round(1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    for ax, (platform, color) in zip(axes, COLOR_MAP.items()):
        data   = intl[intl["platform"] == platform].sort_values("label")
        colors = [color, "#555555"]
        wedges, texts, autotexts = ax.pie(
            data["pct"],
            labels=data["label"],
            autopct="%1.1f%%",
            colors=colors,
            textprops={"color": "white", "fontsize": 11},
            startangle=90,
            wedgeprops={"edgecolor": "#222", "linewidth": 1.5},
        )
        for at in autotexts:
            at.set_fontsize(12)
            at.set_color("white")
        ax.set_title(platform, fontsize=14, color=color, pad=15)

    plt.suptitle("International vs English Content Share", fontsize=16, y=1.02)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "10_international_share.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 2 — Top producing countries per platform ───────────────────────────
def plot_top_countries(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, (platform, color) in zip(axes, COLOR_MAP.items()):
        platform_df = df[df["platform"] == platform].copy()

        # Explode multi-country titles
        countries = (
            platform_df["production_countries"]
            .dropna()
            .str.split("|")
            .explode()
            .str.strip()
        )

        top = (
            countries
            .value_counts()
            .head(12)
            .reset_index()
        )
        top.columns   = ["code", "count"]
        top["country"] = top["code"].map(COUNTRY_NAMES).fillna(top["code"])
        top = top.sort_values("count")

        bars = ax.barh(top["country"], top["count"],
                       color=color, alpha=0.85)

        for bar, val in zip(bars, top["count"]):
            ax.text(bar.get_width() + 0.2,
                    bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=9, color="white")

        ax.set_title(f"{platform} — Top Producing Countries",
                     fontsize=14, color=color, pad=12)
        ax.set_xlabel("Number of Titles")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.suptitle("Content Production by Country", fontsize=16, y=1.02)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "11_top_countries.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Chart 3 — International content growth over time ─────────────────────────
def plot_international_growth(df: pd.DataFrame):
    recent = df[df["year"] >= 2015].copy()

    intl_yearly = (
        recent.groupby(["year", "platform", "is_international"])
        .size()
        .reset_index(name="count")
    )

    # Calculate % international per year per platform
    totals = intl_yearly.groupby(["year", "platform"])["count"].transform("sum")
    intl_yearly["pct"] = intl_yearly["count"] / totals * 100

    intl_only = intl_yearly[intl_yearly["is_international"] == True]

    fig, ax = plt.subplots(figsize=(12, 6))

    for platform, color in COLOR_MAP.items():
        data = intl_only[intl_only["platform"] == platform]
        ax.plot(data["year"], data["pct"],
                marker="o", label=platform,
                color=color, linewidth=2.5, markersize=6)
        ax.fill_between(data["year"], data["pct"],
                        alpha=0.1, color=color)

    ax.set_title("International Content Share Over Time (%)",
                 fontsize=16, pad=15)
    ax.set_xlabel("Year")
    ax.set_ylabel("% International Titles")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.legend(fontsize=12)
    plt.tight_layout()

    path = os.path.join(VISUALS_PATH, "12_international_growth.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.show()


# ── Console insights ──────────────────────────────────────────────────────────
def print_insights(df: pd.DataFrame):
    print("\n=== INTERNATIONAL INSIGHTS ===")

    for platform in ["Netflix", "Prime Video"]:
        p    = df[df["platform"] == platform]
        intl = p[p["is_international"] == True]

        # Top non-English language
        top_lang = (
            p[p["original_language"] != "en"]["original_language"]
            .value_counts()
            .head(3)
        )

        # Top non-US country
        countries = (
            p["production_countries"]
            .dropna()
            .str.split("|")
            .explode()
            .str.strip()
        )
        top_country = (
            countries[countries != "US"]
            .value_counts()
            .head(3)
        )

        print(f"\n{platform}:")
        print(f"  International share: {len(intl)/len(p)*100:.1f}%")
        print(f"  Top non-English languages: "
              f"{', '.join(top_lang.index.tolist())}")
        print(f"  Top non-US countries: "
              f"{', '.join([COUNTRY_NAMES.get(c,c) for c in top_country.index.tolist()])}")


if __name__ == "__main__":
    print("Loading clean data...")
    df = load()

    print("\nGenerating charts...")
    plot_international_share(df)
    plot_top_countries(df)
    plot_international_growth(df)

    print_insights(df)
    print("\nInternational analysis complete.")