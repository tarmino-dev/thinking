"""
Configuration module for Spotify API credentials.

This script loads Spotify API credentials from a .env file located three levels above this file.
Ensure the .env file contains:
    SPOTIPY_CLIENT_ID=your_client_id
    SPOTIPY_CLIENT_SECRET=your_client_secret
    SPOTIPY_REDIRECT_URI=your_redirect_uri
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the .env file in the project root
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Validate environment variables
if not all([SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI]):
    raise EnvironmentError("Missing one or more required Spotify environment variables.")
