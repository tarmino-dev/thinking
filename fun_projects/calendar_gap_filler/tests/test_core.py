"""Unit tests for core._build_suggestions and core._fits_in_gap.

Everything here runs on hand-built Gap/Event objects and fake 2D
embeddings — no calendar, no Ticketmaster, no TinyBERT.
"""

from datetime import datetime, timedelta, timezone

from calendar_module.gaps import Gap
from core import DEFAULT_EVENT_DURATION_MINUTES, _build_suggestions, _fits_in_gap
from events_module.client import Event

TZ = timezone.utc


def _dt(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, day, hour, minute, tzinfo=TZ)


def _make_gap(day: int, start_hour: int, end_hour: int) -> Gap:
    return Gap(start=_dt(day, start_hour), end=_dt(day, end_hour))


def _make_event(id_: str, day: int, hour: int, minute: int = 0, duration_minutes: float | None = 60) -> Event:
    return Event(
        id=id_,
        name=f"Event {id_}",
        start=_dt(day, hour, minute),
        duration_minutes=duration_minutes,
        classification=None,
        description=None,
        venue_name=None,
        url=None,
    )


# --- _fits_in_gap -------------------------------------------------------------


def test_fits_in_gap_true_when_event_starts_and_ends_within_gap():
    gap = _make_gap(20, 9, 12)
    event = _make_event("1", 20, 10, duration_minutes=60)  # 10:00-11:00

    assert _fits_in_gap(event, gap) is True


def test_fits_in_gap_true_at_exact_gap_start_boundary():
    gap = _make_gap(20, 9, 12)
    event = _make_event("1", 20, 9, duration_minutes=60)  # starts exactly when gap opens

    assert _fits_in_gap(event, gap) is True


def test_fits_in_gap_true_at_exact_gap_end_boundary():
    gap = _make_gap(20, 9, 12)
    event = _make_event("1", 20, 11, duration_minutes=60)  # ends exactly when gap closes (12:00)

    assert _fits_in_gap(event, gap) is True


def test_fits_in_gap_false_when_event_starts_before_gap():
    gap = _make_gap(20, 9, 12)
    event = _make_event("1", 20, 8, duration_minutes=30)  # starts an hour before the gap opens

    assert _fits_in_gap(event, gap) is False


def test_fits_in_gap_false_when_event_ends_after_gap():
    gap = _make_gap(20, 9, 10)
    event = _make_event("1", 20, 9, 30, duration_minutes=60)  # 9:30-10:30, gap closes at 10:00

    assert _fits_in_gap(event, gap) is False


def test_fits_in_gap_uses_default_duration_when_unknown():
    gap = _make_gap(20, 9, 12)
    # Starts at 10:00 with no known duration -> assumed DEFAULT_EVENT_DURATION_MINUTES
    # (120 min), so it's expected to end exactly at 12:00 — right at the gap's edge.
    event = _make_event("1", 20, 10, duration_minutes=None)

    assert DEFAULT_EVENT_DURATION_MINUTES == 120  # sanity check the assumption below still holds
    assert _fits_in_gap(event, gap) is True


def test_fits_in_gap_false_when_event_is_on_a_different_day():
    gap = _make_gap(20, 9, 12)
    event = _make_event("1", 19, 10, duration_minutes=30)  # the day before

    assert _fits_in_gap(event, gap) is False


# --- _build_suggestions --------------------------------------------------------


def test_build_suggestions_ranks_fitting_events_by_score():
    gap = _make_gap(20, 9, 12)
    events = [_make_event("low", 20, 10), _make_event("high", 20, 10)]
    event_embeddings = [[0, 1], [1, 0]]
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([gap], events, event_embeddings, interest_embeddings)

    [(returned_gap, ranked)] = result
    assert returned_gap == gap
    assert [r.event.id for r in ranked] == ["high", "low"]


def test_build_suggestions_gap_with_no_fitting_events_is_empty():
    gap = _make_gap(20, 9, 10)
    # Event exists but is on a completely different day — doesn't fit.
    events = [_make_event("1", 19, 10)]
    event_embeddings = [[1, 0]]
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([gap], events, event_embeddings, interest_embeddings)

    assert result == [(gap, [])]


def test_build_suggestions_truncates_to_max_per_gap():
    gap = _make_gap(20, 9, 12)
    events = [_make_event(str(i), 20, 10) for i in range(5)]
    event_embeddings = [[1, 0]] * 5
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([gap], events, event_embeddings, interest_embeddings, max_per_gap=2)

    [(_, ranked)] = result
    assert len(ranked) == 2


def test_build_suggestions_excludes_non_fitting_events_even_if_similar():
    gap = _make_gap(20, 9, 10)
    fitting = _make_event("fits", 20, 9, duration_minutes=30)
    not_fitting = _make_event("too_long", 20, 9, duration_minutes=120)  # runs past the gap's end
    events = [fitting, not_fitting]
    # Give the non-fitting event a *better* similarity score, to prove the
    # time filter runs before ranking rather than ranking deciding everything.
    event_embeddings = [[0.5, 0.5], [1, 0]]
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([gap], events, event_embeddings, interest_embeddings)

    [(_, ranked)] = result
    assert [r.event.id for r in ranked] == ["fits"]


def test_build_suggestions_gives_each_gap_its_own_candidate_set():
    morning_gap = _make_gap(20, 9, 11)
    evening_gap = _make_gap(20, 18, 20)
    morning_event = _make_event("morning", 20, 9, 30, duration_minutes=30)
    evening_event = _make_event("evening", 20, 18, 30, duration_minutes=30)
    events = [morning_event, evening_event]
    event_embeddings = [[1, 0], [1, 0]]
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([morning_gap, evening_gap], events, event_embeddings, interest_embeddings)

    result_by_gap = {gap.start.hour: [r.event.id for r in ranked] for gap, ranked in result}
    assert result_by_gap[9] == ["morning"]
    assert result_by_gap[18] == ["evening"]


def test_build_suggestions_no_gaps_returns_empty_list():
    events = [_make_event("1", 20, 10)]
    event_embeddings = [[1, 0]]
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([], events, event_embeddings, interest_embeddings)

    assert result == []


def test_build_suggestions_no_events_returns_empty_suggestions_per_gap():
    gap = _make_gap(20, 9, 12)
    interest_embeddings = [[1, 0]]

    result = _build_suggestions([gap], [], [], interest_embeddings)

    assert result == [(gap, [])]
