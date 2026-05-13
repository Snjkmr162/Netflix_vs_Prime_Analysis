"""
Pulls both platform catalogs from Watchmode and saves to data/raw/
Run this once to generate your raw CSVs
"""

import os
import pandas as pd
from watchmode_client import fetch_titles, PLATFORMS


def save_platform(titles: list[dict], platform_name: str) -> pd.DataFrame:
    df = pd.DataFrame(titles)
    df["platform"] = platform_name

    filename = platform_name.lower().replace(" ", "_") + "_titles.csv"
    path     = os.path.join("..", "..", "data", "raw", filename)

    df.to_csv(path, index=False)
    print(f"  Saved {len(df)} rows → {path}")
    return df


def main():
    all_dfs = []

    for platform_name, source_id in PLATFORMS.items():
        titles = fetch_titles(source_id, platform_name)
        df     = save_platform(titles, platform_name)
        all_dfs.append(df)

    # Merge into one master file
    combined = pd.concat(all_dfs, ignore_index=True)
    out_path = os.path.join("..", "..", "data", "raw", "streaming_titles_raw.csv")
    combined.to_csv(out_path, index=False)

    print(f"\nMaster file saved → {out_path}")
    print(f"Total rows: {len(combined)}")
    print(f"Columns: {list(combined.columns)}")
    print(f"\nSample:\n{combined.head(3)}")


if __name__ == "__main__":
    main()