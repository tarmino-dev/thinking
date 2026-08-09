"""Project-wide configuration constants."""

# Google Calendar OAuth files (see README.md for how to obtain these).
# Both are gitignored — never commit real credentials.
GOOGLE_CREDENTIALS_FILE = "credentials.json"
GOOGLE_TOKEN_FILE = "token.json"

# Read-only scope: we only need to read events to find gaps, never modify the calendar.
GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
