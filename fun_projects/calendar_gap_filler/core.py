"""Orchestrator: the single place that wires calendar_module, events_module,
profile_module, and classifier_module together into one pipeline.

Deliberately not a "service layer" — just one composition point, split into
a pure function (_build_suggestions, easy to unit test) and the real
end-to-end entry point (suggest_events, which actually talks to Google
Calendar, Ticketmaster, and TinyBERT).
"""

import logging
from datetime import datetime, timedelta

from calendar_module.client import get_busy_periods
from calendar_module.gaps import Gap, find_gaps
from classifier_module.embeddings import embed_texts
from classifier_module.feedback_model import FeedbackModel, predict_score, train_feedback_model
from classifier_module.ranking import RankedEvent, event_text, rank_events
from config import USER_LATITUDE, USER_LONGITUDE, USER_SEARCH_RADIUS_KM
from events_module.client import Event, search_events
from feedback_module.store import get_all_feedback
from profile_module.profile import load_profile

logger = logging.getLogger(__name__)

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

    logger.info("Running suggestion pipeline for the next %d day(s)", days_ahead)
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

    logger.info("Found %d gap(s) and %d candidate event(s) this week", len(gaps), len(events))

    if not events or not gaps:
        return [(gap, []) for gap in gaps]

    # Embed every event's text and every interest exactly once, up front —
    # not once per gap. TinyBERT inference isn't free, and the event pool
    # and interest list don't change between gaps in the same run.
    event_embeddings = embed_texts([event_text(event) for event in events])
    interest_embeddings = embed_texts(profile.interests)

    # Same "compute once per run, not once per gap" reasoning as the
    # embeddings above (Phase 10 step 3, decision #12) — trains fresh on
    # every call from whatever's in feedback.db right now; returns None
    # (handled by _build_suggestions/_apply_feedback_model) when there
    # isn't enough feedback yet to trust a model over plain cosine ranking.
    feedback_model = train_feedback_model(get_all_feedback())

    suggestions = _build_suggestions(gaps, events, event_embeddings, interest_embeddings, feedback_model)
    total_suggested = sum(len(ranked) for _, ranked in suggestions)
    logger.info("Built %d suggestion(s) across %d gap(s)", total_suggested, len(gaps))
    return suggestions


def _build_suggestions(
    gaps: list[Gap],
    events: list[Event],
    event_embeddings: list[list[float]],
    interest_embeddings: list[list[float]],
    feedback_model: FeedbackModel | None = None,
    max_per_gap: int = MAX_SUGGESTIONS_PER_GAP,
) -> list[tuple[Gap, list[RankedEvent]]]:
    """Pure composition: for each gap, keep only the events that actually
    fit (by time), rank the survivors against the interest profile, adjust
    with the feedback model if one is available, and keep the top few. No
    I/O — everything needed is passed in already computed, which is what
    makes this testable without touching any real API, the TinyBERT model,
    or scikit-learn's training.
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
        # Re-score with feedback (if trained) and re-sort *before* cutting
        # to max_per_gap — otherwise an event the feedback model would
        # have promoted to #1 could already be discarded for scoring #4
        # on pure cosine similarity alone.
        ranked = _apply_feedback_model(ranked, feedback_model)
        suggestions.append((gap, ranked[:max_per_gap]))

    return suggestions


def _apply_feedback_model(
    ranked: list[RankedEvent], feedback_model: FeedbackModel | None
) -> list[RankedEvent]:
    """Re-score ranked (already sorted by pure cosine similarity) using the
    feedback-trained model, and re-sort by the new scores.

    Returns ranked unchanged when feedback_model is None — not enough
    feedback yet to trust one over plain cosine ranking, see
    classifier_module.feedback_model.MIN_FEEDBACK_FOR_MODEL — so callers
    don't need an if/else at every call site.
    """
    if feedback_model is None:
        return ranked

    adjusted = [
        RankedEvent(event=ranked_event.event, score=predict_score(feedback_model, ranked_event.event, ranked_event.score))
        for ranked_event in ranked
    ]
    return sorted(adjusted, key=lambda ranked_event: ranked_event.score, reverse=True)


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
