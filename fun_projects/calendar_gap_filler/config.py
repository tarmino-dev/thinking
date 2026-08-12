"""Project-wide configuration constants."""

import os

from dotenv import load_dotenv

# Loads variables from a local .env file (if present) into the process
# environment. On a real deployment, env vars would just be set directly by
# the hosting platform instead — load_dotenv() is a no-op if there's no
# .env file, so this is safe either way.
load_dotenv()

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
