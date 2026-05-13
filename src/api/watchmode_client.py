"""
Watchmode API client
Fetches Netflix and Prime Video title catalogs
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("WATCHMODE_API_KEY")
BASE_URL = "https://api.watchmode.com/v1"

PLATFORMS = {
    "Netflix":     203,
    "Prime Video": 26,
}


def fetch_titles(source_id: int, platform_name: str) -> list[dict]:
    """Pull all titles for one platform, handling pagination."""
    titles = []
    page   = 1

    print(f"\nFetching {platform_name}...")

    while True:
        params = {
            "apiKey":     API_KEY,
            "source_ids": source_id,
            "types":      "movie,tv_series",
            "limit":      250,
            "page":       page,
        }

        response = requests.get(f"{BASE_URL}/list-titles/", params=params)

        if response.status_code != 200:
            print(f"  Error {response.status_code}: {response.text}")
            break

        data        = response.json()
        page_titles = data.get("titles", [])

        if not page_titles:
            break

        titles.extend(page_titles)
        total = data.get("total_results", "?")
        print(f"  Page {page} — {len(titles)} / {total} titles fetched")

        if data.get("more_pages"):
            page += 1
            time.sleep(0.5)   # be polite to the API
        else:
            break

    return titles


if __name__ == "__main__":
    for platform_name, source_id in PLATFORMS.items():
        titles = fetch_titles(source_id, platform_name)
        print(f"\n{platform_name}: {len(titles)} titles total")
        print("Sample:", titles[0] if titles else "No data returned")