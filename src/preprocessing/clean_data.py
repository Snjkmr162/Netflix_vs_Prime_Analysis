"""
Cleans enriched_titles.csv and engineers new features.
Input:  data/processed/enriched_titles.csv
Output: data/processed/clean_titles.csv
"""

import os
import pandas as pd
import numpy as np


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}\n")
    return df


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["title", "year", "platform"])
    print(f"Duplicates removed: {before - len(df)} rows dropped")
    return df


def fix_missing(df: pd.DataFrame) -> pd.DataFrame:
    # Runtime — fill with median per content type
    df["runtime_min"] = pd.to_numeric(df["runtime_min"], errors="coerce")
    df["runtime_min"] = df.groupby("type")["runtime_min"].transform(
        lambda x: x.fillna(x.median())
    )

    # Ratings — fill with platform + type median
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["vote_average"] = df.groupby(["platform", "type"])["vote_average"].transform(
        lambda x: x.fillna(x.median())
    )

    # vote_count
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)

    # Genres and countries
    df["genres"]               = df["genres"].fillna("Unknown")
    df["production_countries"] = df["production_countries"].fillna("Unknown")
    df["original_language"]    = df["original_language"].fillna("en")
    df["overview"]             = df["overview"].fillna("")

    print(f"Missing values handled")
    print(f"Remaining nulls:\n{df.isnull().sum()[df.isnull().sum() > 0]}\n")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    current_year = 2026

    # Year as numeric
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Decade
    df["decade"] = (df["year"] // 10 * 10).astype("Int64")

    # Content age
    df["content_age"] = current_year - df["year"]

    # Primary genre (first in the pipe-separated list)
    df["primary_genre"] = df["genres"].str.split("|").str[0].str.strip()

    # Genre count
    df["genre_count"] = df["genres"].apply(
        lambda x: len(x.split("|")) if x != "Unknown" else 0
    )

    # Rating category
    bins   = [0, 4, 6, 7.5, 10]
    labels = ["Poor", "Average", "Good", "Great"]
    df["rating_category"] = pd.cut(
        df["vote_average"], bins=bins, labels=labels
    )

    # Runtime bins (movies only)
    movie_mask = df["type"] == "movie"
    rt_bins    = [0, 60, 90, 120, 150, 999]
    rt_labels  = ["Short", "Standard", "Feature", "Long", "Epic"]
    df.loc[movie_mask, "runtime_bin"] = pd.cut(
        df.loc[movie_mask, "runtime_min"],
        bins=rt_bins, labels=rt_labels
    )

    # International flag
    df["is_international"] = df["original_language"] != "en"

    # Primary country
    df["primary_country"] = df["production_countries"].str.split("|").str[0].str.strip()

    print("Features engineered:")
    print("  decade, content_age, primary_genre, genre_count,")
    print("  rating_category, runtime_bin, is_international, primary_country\n")
    return df


def summary(df: pd.DataFrame):
    print("=== FINAL SUMMARY ===")
    print(f"Shape: {df.shape}")
    print(f"\nPlatform counts:\n{df['platform'].value_counts()}")
    print(f"\nContent types:\n{df['type'].value_counts()}")
    print(f"\nRating categories:\n{df['rating_category'].value_counts()}")
    print(f"\nTop 5 primary genres:\n{df['primary_genre'].value_counts().head()}")
    print(f"\nSample row:")
    print(df[["title", "platform", "year", "primary_genre",
              "vote_average", "rating_category", "is_international"]].head(3))


if __name__ == "__main__":
    in_path  = os.path.join("..", "..", "data", "processed", "enriched_titles.csv")
    out_path = os.path.join("..", "..", "data", "processed", "clean_titles.csv")

    if not os.path.exists(in_path):
        raise FileNotFoundError("Run enrich_tmdb.py first.")

    df = load(in_path)
    df = drop_duplicates(df)
    df = fix_missing(df)
    df = engineer_features(df)
    summary(df)

    df.to_csv(out_path, index=False)
    print(f"\nClean dataset saved → {out_path}")