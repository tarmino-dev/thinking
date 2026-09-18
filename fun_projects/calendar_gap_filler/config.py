"""Project-wide configuration constants."""

import logging
import os

from dotenv import load_dotenv

# Loads variables from a local .env file (if present) into the process
# environment. On a real deployment, env vars would just be set directly by
# the hosting platform instead — load_dotenv() is a no-op if there's no
# .env file, so this is safe either way.
load_dotenv()

# Phase 10 hardening: basic logging setup, done once here rather than in
# api/main.py, because config.py is the one module every entry point already
# imports first — both `uvicorn api.main:app` and every script in scripts/.
# Logging to stdout only (no log file): this is a personal, single-user app
# run via `uvicorn --reload` or `docker compose up`, and both already put
# stdout in front of you (docker compose up) or in `docker compose logs` —
# a log file would need its own volume mount in docker-compose.yml and a
# rotation policy for a benefit (log history surviving a container restart)
# nothing here actually needs yet. Doesn't configure uvicorn's own access
# logging — that already logs every HTTP request by default.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# Google Calendar OAuth files (see README.md for how to obtain these).
# Both are gitignored — never commit real credentials.
GOOGLE_CREDENTIALS_FILE = "credentials.json"
GOOGLE_TOKEN_FILE = "token.json"

# Read-only scope: we only need to read events to find gaps, never modify the calendar.
GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Ticketmaster Discovery API key (see README.md for how to obtain one).
# None if not set — events_module is responsible for failing loudly when it
# actually tries to use a missing key, not this module.
TICKETMASTER_API_KEY = os.environ.get("TICKETMASTER_API_KEY")


def _get_float_env(name: str) -> float | None:
    value = os.environ.get(name)
    return float(value) if value else None


# User's approximate home location, used to search for nearby events.
# Read from the environment (not hardcoded) for the same reason as the API
# keys above: this is personal data and the repo is public — it must never
# end up committed to git.
USER_LATITUDE = _get_float_env("USER_LATITUDE")
USER_LONGITUDE = _get_float_env("USER_LONGITUDE")
USER_SEARCH_RADIUS_KM = _get_float_env("USER_SEARCH_RADIUS_KM") or 20.0

# User interest profile (see profile.example.json for the shape and
# README.md for setup). Gitignored — never commit real values.
PROFILE_FILE = "profile.json"

# TinyBERT checkpoint used for ranking events against the interest profile.
# Downloaded from the Hugging Face Hub and cached locally on first use.
TINYBERT_MODEL_NAME = "sentence-transformers/paraphrase-TinyBERT-L6-v2"

# SQLite database file for user feedback (like/dislike on suggested events).
# Gitignored — it's local user data, same reasoning as profile.json.
FEEDBACK_DB_FILE = "feedback.db"
