import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

TMDB_API_SEARCH_MOVIE_URL = os.getenv("TMDB_API_SEARCH_MOVIE_URL")
TMDB_API_MOVIE_DETAILS_URL = os.getenv("TMDB_API_MOVIE_DETAILS_URL")
TMDB_API_READ_ACCESS_TOKEN = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
TMDB_API_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_READ_ACCESS_TOKEN}"
}