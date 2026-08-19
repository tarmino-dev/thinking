"""Ticketmaster Discovery API client.

Fetches local events near the user's location and normalizes them into a
common Event shape. This module only searches for events (read-only) — it
never touches ticket purchasing or account data.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from config import TICKETMASTER_API_KEY

DISCOVERY_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


@dataclass
class Event:
    """A single local event, normalized to the fields we actually need:
    enough to describe it for later ranking (classifier_module) and enough
    to check whether it fits into a given time gap.
    """

    id: str
    name: str
    start: datetime
    duration_minutes: float | None  # None if Ticketmaster didn't provide an end time
    classification: str | None  # e.g. "Music, Rock, Alternative Rock"
    description: str | None
    venue_name: str | None
    url: str | None


def search_events(
    latitude: float,
    longitude: float,
    radius_km: float,
    date_from: datetime,
    date_to: datetime,
) -> list[Event]:
    """Search for local events within radius_km of (latitude, longitude),
    starting between date_from and date_to.

    Both date_from and date_to must be timezone-aware, for the same reason
    as calendar_module.client.get_busy_periods — an ambiguous time range
    would produce ambiguous results.
    """
    if date_from.tzinfo is None or date_to.tzinfo is None:
        raise ValueError("date_from and date_to must be timezone-aware")

    if not TICKETMASTER_API_KEY:
        raise RuntimeError(
            "TICKETMASTER_API_KEY is not set. Copy .env.example to .env and "
            "add your key — see README.md."
        )

    response = requests.get(
        DISCOVERY_API_URL,
        params={
            "apikey": TICKETMASTER_API_KEY,
            "latlong": f"{latitude},{longitude}",
            # Ticketmaster rejects non-integer radius values (error DIS1014:
            # "must be an integer value between 0 and 19,999"), even though
            # its own docs list this param as a generic String. round()
            # rather than int() so e.g. 20.6 becomes 21, not 20.
            "radius": round(radius_km),
            "unit": "km",
            "startDateTime": _format_for_api(date_from),
            "endDateTime": _format_for_api(date_to),
        },
        timeout=10,
    )
    response.raise_for_status()

    raw_events = response.json().get("_embedded", {}).get("events", [])
    return [_parse_event(raw) for raw in raw_events if _has_specific_start_time(raw)]


def _format_for_api(moment: datetime) -> str:
    """Ticketmaster expects UTC timestamps in 'yyyy-MM-ddTHH:mm:ssZ' format."""
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_specific_start_time(raw_event: dict) -> bool:
    """A handful of events only have a date, no specific time (dateTBA /
    dateTBD). We can't match those against a calendar gap, so we skip them
    instead of guessing a time.
    """
    return "dateTime" in raw_event.get("dates", {}).get("start", {})


def _parse_datetime(iso_string: str) -> datetime:
    """Parse a Ticketmaster timestamp and convert it to the local system
    timezone.

    Ticketmaster timestamps are always UTC and end in a literal 'Z' (e.g.
    "2016-07-27T23:30:00Z"). datetime.fromisoformat() only started accepting
    that suffix directly in Python 3.11, so we normalize it to an explicit
    "+00:00" offset first for portability.

    We then convert to local time so Event.start lines up with Gap.start /
    Gap.end, which are already built in local time (see calendar_module and
    core.py). Comparisons would be correct either way — Python compares
    aware datetimes by absolute instant, regardless of timezone — but
    mixing UTC and local timestamps makes anything we print to a human
    confusing, even when it isn't actually wrong.
    """
    utc_time = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return utc_time.astimezone()


def _parse_event(raw_event: dict) -> Event:
    start = _parse_datetime(raw_event["dates"]["start"]["dateTime"])

    duration_minutes = None
    end_date_time = raw_event.get("dates", {}).get("end", {}).get("dateTime")
    if end_date_time:
        duration_minutes = (_parse_datetime(end_date_time) - start).total_seconds() / 60

    venues = raw_event.get("_embedded", {}).get("venues", [])

    return Event(
        id=raw_event["id"],
        name=raw_event["name"],
        start=start,
        duration_minutes=duration_minutes,
        classification=_format_classification(raw_event.get("classifications", [])),
        description=raw_event.get("info") or raw_event.get("pleaseNote"),
        venue_name=venues[0].get("name") if venues else None,
        url=raw_event.get("url"),
    )


def _format_classification(classifications: list[dict]) -> str | None:
    """Combine segment/genre/subGenre into one readable string, e.g.
    'Music, Rock, Alternative Rock' — used later as descriptive text for the
    ML ranking step. Ticketmaster sometimes fills unset fields with the
    literal string "Undefined" instead of omitting them, so we filter that out.
    """
    if not classifications:
        return None

    primary = next((c for c in classifications if c.get("primary")), classifications[0])
    names = [
        primary.get("segment", {}).get("name"),
        primary.get("genre", {}).get("name"),
        primary.get("subGenre", {}).get("name"),
    ]
    names = [name for name in names if name and name != "Undefined"]
    return ", ".join(names) if names else None
