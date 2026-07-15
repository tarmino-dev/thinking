"""
Musical Time Machine
--------------------
A Python web-scraping and Spotify automation project that:
1. Scrapes Billboard Hot 100 songs for a given date.
2. Searches for each song on Spotify.
3. Creates a private Spotify playlist containing those songs.
"""

import logging
from datetime import datetime
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

# Configuration and Logging

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    )
}

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Core Functions

def get_date_input() -> Tuple[str, str, str]:
    """
    Prompt the user for a date and construct the Billboard URL.

    Returns:
        tuple: (date, year, url)
    """
    date = input("Enter a date (YYYY-MM-DD) to travel back to: ").strip()
    year = date.split("-")[0]
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    logger.info(f"Fetching Billboard Hot 100 for {date}")
    return date, year, url


def scrape_billboard_songs(url: str) -> List[str]:
    """
    Scrape Billboard Hot 100 songs for the given date.

    Args:
        url (str): Billboard URL for the selected date.

    Returns:
        list: List of song titles.
    """
    logger.debug(f"Requesting Billboard page: {url}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    song_elements = soup.select("li ul li h3")
    songs = [s.get_text(strip=True) for s in song_elements]

    logger.info(f"Found {len(songs)} songs.")
    return songs


def create_spotify_client() -> spotipy.Spotify:
    """
    Authenticate and create a Spotify client.

    Returns:
        spotipy.Spotify: Authorized Spotify API client.
    """
    logger.debug("Authenticating with Spotify...")
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI
        )
    )


def fetch_spotify_user_id(sp: spotipy.Spotify) -> str:
    """Return the current Spotify user ID."""
    user_id = sp.current_user()["id"]
    logger.debug(f"Spotify user ID: {user_id}")
    return user_id


def get_spotify_track_uris(sp: spotipy.Spotify, songs: List[str], year: str) -> List[str]:
    """
    Search Spotify for song URIs.

    Args:
        sp (spotipy.Spotify): Spotify client.
        songs (list): List of song titles.
        year (str): Year for refining search.

    Returns:
        list: Spotify track URIs.
    """
    uris = []
    logger.info("Searching Spotify for tracks...")
    for song in songs:
        query = f"track:{song} year:{year}"
        result = sp.search(q=query, type="track", limit=1)
        try:
            uri = result["tracks"]["items"][0]["uri"]
            uris.append(uri)
        except (IndexError, KeyError):
            logger.warning(f"'{song}' not found on Spotify — skipped.")
    logger.info(f"Retrieved {len(uris)} Spotify tracks.")
    return uris


def create_spotify_playlist(sp: spotipy.Spotify, user_id: str, date: str) -> dict:
    """Create a private Spotify playlist."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"{date} Billboard 100",
        public=False,
        description=f"Created automatically on {timestamp} via Python script."
    )
    logger.info(f"Created playlist: {playlist['name']}")
    return playlist


def add_tracks_to_playlist(sp: spotipy.Spotify, playlist_id: str, track_uris: List[str]) -> None:
    """Add tracks to the specified playlist."""
    if not track_uris:
        logger.warning("No tracks to add.")
        return
    sp.playlist_add_items(playlist_id, track_uris)
    logger.info(f"Added {len(track_uris)} tracks to playlist.")


# Main Workflow

def main():
    """Execute the Musical Time Machine workflow."""
    try:
        date, year, url = get_date_input()
        songs = scrape_billboard_songs(url)
        sp = create_spotify_client()
        user_id = fetch_spotify_user_id(sp)
        uris = get_spotify_track_uris(sp, songs, year)
        playlist = create_spotify_playlist(sp, user_id, date)
        add_tracks_to_playlist(sp, playlist["id"], uris)
        logger.info("Playlist successfully created!")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
