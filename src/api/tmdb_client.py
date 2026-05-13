"""
TMDb API client
Fetches detailed metadata for each title using tmdb_id
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def fetch_details(tmdb_id: int, tmdb_type: str) -> dict:
    """Fetch full details for one title using its TMDb ID."""
    kind = "movie" if tmdb_type == "movie" else "tv"
    url  = f"{BASE_URL}/{kind}/{tmdb_id}"

    params   = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    return {}


def extract_fields(data: dict, tmdb_type: str) -> dict:
    """Pull only the fields we need from a TMDb response."""

    # Genres — stored as list of dicts
    genres = [g["name"] for g in data.get("genres", [])]

    # Countries — stored as list of dicts
    countries = [c["iso_3166_1"] for c in data.get("production_countries", [])]

    # Runtime differs between movies and TV
    runtime = data.get("runtime")
    if not runtime and tmdb_type != "movie":
        episodes = data.get("episode_run_time", [])
        runtime  = episodes[0] if episodes else None

    return {
        "vote_average":          data.get("vote_average"),
        "vote_count":            data.get("vote_count"),
        "popularity":            data.get("popularity"),
        "runtime_min":           runtime,
        "genres":                "|".join(genres),
        "original_language":     data.get("original_language"),
        "overview":              data.get("overview"),
        "production_countries":  "|".join(countries),
        "poster_path":           data.get("poster_path"),
    }


if __name__ == "__main__":
    # Quick test — fetch Citadel (Prime Video show we saw in the sample)
    data   = fetch_details(114922, "tv")
    fields = extract_fields(data, "tv")

    print("Test fetch — Citadel:")
    for k, v in fields.items():
        print(f"  {k}: {v}")