"""Orchestrator: the single place that wires calendar_module, events_module,
profile_module, and classifier_module together into one pipeline.

Deliberately not a "service layer" — just one composition point, split into
a pure function (_build_suggestions, easy to unit test) and the real
end-to-end entry point (suggest_events, which actually talks to Google
Calendar, Ticketmaster, and TinyBERT).
"""

from datetime import datetime, timedelta

from calendar_module.client import get_busy_periods
from calendar_module.gaps import Gap, find_gaps
from classifier_module.embeddings import embed_texts
from classifier_module.ranking import RankedEvent, event_text, rank_events
from config import USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM
from events_module.client import Event, search_events
from profile_module.profile import load_profile

DAYS_AHEAD = 7
MAX_SUGGESTIONS_PER_GAP = 3

# Conservative fallback for events where Ticketmaster didn't provide an end
# time (see events_module.client — this happens a lot). 2 hours is a
# reasonable guess for "average concert/show length" — good enough to avoid
# suggesting something that obviously can't fit, without being so cautious
# that we throw away most real candidates (see architecture.md decision on
# this trade-off).
DEFAULT_EVENT_DURATION_MINUTES = 120


def suggest_events(days_ahead: int = DAYS_AHEAD) -> list[tuple[Gap, list[RankedEvent]]]:
    """Real end-to-end pipeline: load the profile, find this week's free
    time slots, fetch nearby events once, embed everything once, and rank
    candidates per gap.
    """
    if USER_LATITUDE is None or USER_LONGITUDE is None:
        raise RuntimeError(
            "USER_LATITUDE and USER_LONGITUDE are not set. Add them to .env — see README.md."
        )

    profile = load_profile()

    today = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    window_start = today.replace(hour=profile.waking_hours_start)
    window_end = (today + timedelta(days=days_ahead)).replace(hour=profile.waking_hours_end)

    # One API call for busy periods and one for events, covering the whole
    # window — same trick as in scripts/check_gaps.py and
    # scripts/check_events.py, just combined here into a single pipeline.
    busy_periods = get_busy_periods(window_start, window_end)
    events = search_events(USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM, window_start, window_end)

    gaps = []
    for day_offset in range(days_ahead + 1):
        day = today + timedelta(days=day_offset)
        day_start = day.replace(hour=profile.waking_hours_start)
        day_end = day.replace(hour=profile.waking_hours_end)
        gaps.extend(find_gaps(busy_periods, day_start, day_end))

    if not events or not gaps:
        return [(gap, []) for gap in gaps]

    # Embed every event's text and every interest exactly once, up front —
    # not once per gap. TinyBERT inference isn't free, and the event pool
    # and interest list don't change between gaps in the same run.
    event_embeddings = embed_texts([event_text(event) for event in events])
    interest_embeddings = embed_texts(profile.interests)

    return _build_suggestions(gaps, events, event_embeddings, interest_embeddings)


def _build_suggestions(
    gaps: list[Gap],
    events: list[Event],
    event_embeddings: list[list[float]],
    interest_embeddings: list[list[float]],
    max_per_gap: int = MAX_SUGGESTIONS_PER_GAP,
) -> list[tuple[Gap, list[RankedEvent]]]:
    """Pure composition: for each gap, keep only the events that actually
    fit (by time), rank the survivors against the interest profile, and
    keep the top few. No I/O — everything needed is passed in already
    computed, which is what makes this testable without touching any real
    API or the TinyBERT model.
    """
    event_embedding_by_id = dict(zip((event.id for event in events), event_embeddings))

    suggestions = []
    for gap in gaps:
        fitting_events = [event for event in events if _fits_in_gap(event, gap)]

        if not fitting_events:
            suggestions.append((gap, []))
            continue

        fitting_embeddings = [event_embedding_by_id[event.id] for event in fitting_events]
        ranked = rank_events(fitting_events, fitting_embeddings, interest_embeddings)
        suggestions.append((gap, ranked[:max_per_gap]))

    return suggestions


def _fits_in_gap(event: Event, gap: Gap) -> bool:
    """An event fits in a gap only if it's actually scheduled to happen
    during that gap: it can't start before the gap does, and it can't run
    (using its real duration, or DEFAULT_EVENT_DURATION_MINUTES if unknown)
    past the gap's end. A concert on Friday night doesn't help fill a gap
    on Tuesday afternoon, no matter how short it is.
    """
    duration = event.duration_minutes if event.duration_minutes is not None else DEFAULT_EVENT_DURATION_MINUTES
    event_end = event.start + timedelta(minutes=duration)
    return event.start >= gap.start and event_end <= gap.end
