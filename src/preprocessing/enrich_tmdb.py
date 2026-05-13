"""
Loops through streaming_titles_raw.csv,
fetches TMDb details for each title,
saves enriched_titles.csv to data/processed/
"""

import os
import sys
import time
import pandas as pd

# So we can import from src/api/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "api"))
from tmdb_client import fetch_details, extract_fields


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    enriched_rows = []
    total = len(df)

    for i, row in df.iterrows():
        if i % 50 == 0:
            print(f"  Progress: {i}/{total} titles enriched...")

        tmdb_data = {}

        if pd.notna(row.get("tmdb_id")):
            tmdb_data = fetch_details(int(row["tmdb_id"]), row.get("tmdb_type", "movie"))

        fields = extract_fields(tmdb_data, row.get("tmdb_type", "movie"))
        enriched_rows.append({**row.to_dict(), **fields})

        time.sleep(0.25)   # stay within TMDb rate limits

    return pd.DataFrame(enriched_rows)


if __name__ == "__main__":
    in_path  = os.path.join("..", "..", "data", "raw", "streaming_titles_raw.csv")
    out_path = os.path.join("..", "..", "data", "processed", "enriched_titles.csv")

    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Run save_raw.py first — {in_path} not found.")

    print(f"Loading {in_path}...")
    df = pd.read_csv(in_path)
    print(f"  {len(df)} titles loaded.\n")

    print("Starting TMDb enrichment — this takes ~2 mins for 500 titles...")
    enriched = enrich(df)

    enriched.to_csv(out_path, index=False)
    print(f"\nDone! Saved → {out_path}")
    print(f"Shape: {enriched.shape}")
    print(f"\nSample:")
    print(enriched[["title", "platform", "vote_average", "genres",
                     "production_countries"]].head(5))