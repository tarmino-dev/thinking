"""Unit tests for core._build_suggestions and core._fits_in_gap.

Everything here runs on hand-built Gap/Event objects and fake 2D
embeddings — no calendar, no Ticketmaster, no TinyBERT.
"""

from datetime import datetime, timedelta, timezone

from calendar_module.gaps import Gap
from classifier_module.feedback_model import train_feedback_model
from classifier_module.ranking import RankedEvent
from core import DEFAULT_EVENT_DURATION_MINUTES, _apply_feedback_model, _build_suggestions, _fits_in_gap
from events_module.client import Event
from feedback_module.store import FeedbackRow

TZ = timezone.utc


def _dt(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, day, hour, minute, tzinfo=TZ)


def _make_gap(day: int, start_hour: int, end_hour: int) -> Gap:
    return Gap(start=_dt(day, start_hour), end=_dt(day, end_hour))


def _make_event(
    id_: str,
    day: int,
    hour: int,
    minute: int = 0,
    duration_minutes: float | None = 60,
    classification: str | None = None,
) -> Event:
    return Event(
        id=id_,
        name=f"Event {id_}",
        start=_dt(day, hour, minute),
        duration_minutes=duration_minutes,
        classification=classification,
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


# --- _apply_feedback_model ------------------------------------------------------


def _ranked(id_: str, score: float, classification: str | None = None) -> RankedEvent:
    return RankedEvent(event=_make_event(id_, 20, 10, classification=classification), score=score)


def _trained_feedback_model():
    # Same pattern as tests/test_feedback_model.py's _varied_rows(): enough
    # rows, both classes, and a real learnable pattern (Music liked, Sports
    # disliked) regardless of the recorded cosine_score.
    liked_music = [
        FeedbackRow("m", "Music Event", _dt(1, 19), 0.1 + 0.01 * i, True, "Music, Jazz, Vocal Jazz")
        for i in range(10)
    ]
    disliked_sports = [
        FeedbackRow("s", "Sports Event", _dt(1, 19), 0.1 + 0.01 * i, False, "Sports, Golf, PGA Tour")
        for i in range(10)
    ]
    return train_feedback_model(liked_music + disliked_sports)


def test_apply_feedback_model_returns_unchanged_when_model_is_none():
    ranked = [_ranked("a", 0.9), _ranked("b", 0.1)]

    result = _apply_feedback_model(ranked, None)

    assert result == ranked


def test_apply_feedback_model_rescoves_and_resorts():
    model = _trained_feedback_model()
    # Pure cosine similarity ranks the Sports event first — the feedback
    # model, having learned "Music good, Sports bad", should flip this.
    ranked = [
        _ranked("sports_event", 0.9, "Sports, Basketball, NBA"),
        _ranked("music_event", 0.2, "Music, Rock, Alternative Rock"),
    ]

    result = _apply_feedback_model(ranked, model)

    assert [r.event.id for r in result] == ["music_event", "sports_event"]


def test_build_suggestions_feedback_model_can_promote_an_event_past_max_per_gap_cutoff():
    # The core correctness property discussed while designing this step:
    # re-scoring must happen BEFORE the max_per_gap cut, not after —
    # otherwise an event the feedback model would rank #1 could already be
    # gone if it only ranked, say, #4 on pure cosine similarity.
    gap = _make_gap(20, 9, 12)
    # 3 mediocre-but-not-Music/Sports events that beat the real Music event
    # on pure cosine similarity, plus the Music event trailing behind them.
    filler_events = [_make_event(f"filler{i}", 20, 10) for i in range(3)]
    music_event = _make_event("music_event", 20, 10, classification="Music, Rock, Alternative Rock")
    events = [*filler_events, music_event]
    # Fillers score higher (closer to the interest direction) than the
    # Music event on pure cosine similarity alone.
    event_embeddings = [[0.9, 0.1]] * 3 + [[0.2, 0.8]]
    interest_embeddings = [[1, 0]]
    model = _trained_feedback_model()

    result = _build_suggestions([gap], events, event_embeddings, interest_embeddings, model, max_per_gap=1)

    [(_, ranked)] = result
    assert [r.event.id for r in ranked] == ["music_event"]
