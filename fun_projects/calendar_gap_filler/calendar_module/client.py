"""Google Calendar API client.

Authenticates via OAuth2 and fetches busy periods (existing events) so that
calendar_module.gaps can compute free time slots. This module only reads
calendar data (scope: calendar.readonly, see config.py) and never modifies
the calendar.
"""

import os
from dataclasses import dataclass
from datetime import datetime

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GOOGLE_CALENDAR_SCOPES, GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE


@dataclass
class BusyBlock:
    """A single existing calendar event, reduced to just its time boundaries.

    We don't need the event's title or description to find gaps — only when
    it starts and ends.
    """

    start: datetime
    end: datetime


def get_busy_periods(date_from: datetime, date_to: datetime) -> list[BusyBlock]:
    """Fetch events from the user's primary Google Calendar between
    date_from and date_to, returning only their start/end times.

    Both date_from and date_to must be timezone-aware — the Google Calendar
    API requires an explicit timezone for its time range filters.
    """
    if date_from.tzinfo is None or date_to.tzinfo is None:
        raise ValueError("date_from and date_to must be timezone-aware")

    credentials = _load_credentials()
    service = build("calendar", "v3", credentials=credentials)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=date_from.isoformat(),
            timeMax=date_to.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return [
        BusyBlock(start=_parse_event_time(event["start"]), end=_parse_event_time(event["end"]))
        for event in events_result.get("items", [])
    ]


def _load_credentials() -> Credentials:
    """Load cached OAuth credentials from GOOGLE_TOKEN_FILE, refreshing them
    if expired, or running the one-time browser login flow if none exist yet.
    """
    credentials = None
    if os.path.exists(GOOGLE_TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except RefreshError as error:
                # Expected roughly weekly: while the OAuth consent screen is
                # in "Testing" status, Google expires refresh tokens after
                # 7 days no matter how often they're used. Not a bug — just
                # delete the token file and log in again via the browser.
                raise RuntimeError(
                    f"Google refresh token is no longer valid ({error}). This is expected "
                    f"about once a week while the app is in OAuth 'Testing' mode. Delete "
                    f"{GOOGLE_TOKEN_FILE} and run again to log in via the browser."
                ) from error
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, GOOGLE_CALENDAR_SCOPES)
            credentials = flow.run_local_server(port=0)

        with open(GOOGLE_TOKEN_FILE, "w") as token_file:
            token_file.write(credentials.to_json())

    return credentials


def _parse_event_time(time_field: dict) -> datetime:
    """Google Calendar gives either a precise 'dateTime' (timed events) or
    just a 'date' (all-day events). Normalize both to a datetime so gap
    logic doesn't need to care about the difference.
    """
    if "dateTime" in time_field:
        return datetime.fromisoformat(time_field["dateTime"])
    return datetime.fromisoformat(time_field["date"])
