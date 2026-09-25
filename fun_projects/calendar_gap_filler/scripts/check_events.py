"""Manual check: print local events near you for the next few days.

This is not an automated test — it's a script you run by hand to eyeball
that events_module.client works correctly against the real Ticketmaster API
and your configured location. Run it from the project root:

    PYTHONPATH=. python3 scripts/check_events.py
"""

from datetime import datetime, timedelta

from config import USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM
from events_module.client import search_events

DAYS_AHEAD = 7


def main() -> None:
    if USER_LATITUDE is None or USER_LONGITUDE is None:
        raise RuntimeError(
            "USER_LATITUDE and USER_LONGITUDE are not set. Add them to .env — see README.md."
        )

    date_from = datetime.now().astimezone()
    date_to = date_from + timedelta(days=DAYS_AHEAD)

    events = search_events(USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM, date_from, date_to)

    for event in sorted(events, key=lambda e: e.start):
        venue = f" @ {event.venue_name}" if event.venue_name else ""
        print(f"{event.start:%d.%m %H:%M} {event.name}{venue}")


if __name__ == "__main__":
    main()
