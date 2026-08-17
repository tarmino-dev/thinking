"""Manual check: rank real local events against your real interest profile.

This is not an automated test — it's a script you run by hand to eyeball
whether TinyBERT-based ranking actually makes sense for your real interests
and real nearby events. Run it from the project root:

    PYTHONPATH=. python3 scripts/check_ranking.py
"""

from datetime import datetime, timedelta

from classifier_module.embeddings import embed_texts
from classifier_module.ranking import rank_events
from config import USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM
from events_module.client import Event, search_events
from profile_module.profile import load_profile

DAYS_AHEAD = 7


def _event_text(event: Event) -> str:
    """Build a single descriptive string per event to feed into the
    embedding model. Combines whatever fields happen to be available —
    name is the only one guaranteed to exist; classification and
    description are often missing (see events_module.client).

    NOTE: this will likely move into classifier_module once the
    orchestrator (Phase 5) needs the exact same text-building logic —
    kept here for now since this script is still its only user.
    """
    parts = [event.name, event.classification, event.description]
    return ". ".join(part for part in parts if part)


def main() -> None:
    if USER_LATITUDE is None or USER_LONGITUDE is None:
        raise RuntimeError(
            "USER_LATITUDE and USER_LONGITUDE are not set. Add them to .env — see README.md."
        )

    profile = load_profile()

    date_from = datetime.now().astimezone()
    date_to = date_from + timedelta(days=DAYS_AHEAD)
    events = search_events(USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM, date_from, date_to)

    if not events:
        print(f"No events found nearby in the next {DAYS_AHEAD} days — nothing to rank.")
        return

    event_embeddings = embed_texts([_event_text(event) for event in events])
    interest_embeddings = embed_texts(profile.interests)

    ranked = rank_events(events, event_embeddings, interest_embeddings)

    for ranked_event in ranked:
        event = ranked_event.event
        venue = f" @ {event.venue_name}" if event.venue_name else ""
        print(f"{ranked_event.score:.3f}  {event.start:%d.%m %H:%M}  {event.name}{venue}")


if __name__ == "__main__":
    main()
