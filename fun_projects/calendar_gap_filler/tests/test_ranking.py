"""Unit tests for classifier_module.ranking.

Everything here runs on hand-picked fake vectors — no TinyBERT, no network.
2D/3D vectors are used instead of real 768-dim embeddings because the
cosine similarity math is identical regardless of dimension, and small
vectors are easy to reason about by hand.
"""

from datetime import datetime, timezone

import pytest

from classifier_module.ranking import RankedEvent, _cosine_similarity, rank_events
from events_module.client import Event


def _make_event(id_: str) -> Event:
    return Event(
        id=id_,
        name=f"Event {id_}",
        start=datetime(2026, 8, 20, tzinfo=timezone.utc),
        duration_minutes=None,
        classification=None,
        description=None,
        venue_name=None,
        url=None,
    )


# --- _cosine_similarity -----------------------------------------------------


def test_cosine_similarity_identical_vectors_returns_one():
    assert _cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors_returns_zero():
    assert _cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors_returns_negative_one():
    assert _cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)


def test_cosine_similarity_ignores_magnitude():
    # [5, 0] points the same direction as [1, 0], just "longer" — similarity
    # should still be a perfect 1.0, since only direction encodes meaning.
    assert _cosine_similarity([1, 0], [5, 0]) == pytest.approx(1.0)


def test_cosine_similarity_raises_on_zero_vector():
    # A zero vector has no direction, so "how similar is this direction"
    # is undefined — this should fail loudly (division by zero), not
    # silently return a meaningless number.
    with pytest.raises(ZeroDivisionError):
        _cosine_similarity([0, 0], [1, 0])


# --- rank_events -------------------------------------------------------------


def test_rank_events_picks_max_similarity_not_average():
    # Event "1" matches interest A perfectly and interest B not at all.
    # MAX should score it 1.0; an average would unfairly score it 0.5.
    events = [_make_event("1")]
    event_embeddings = [[1, 0]]
    interest_embeddings = [[1, 0], [0, 1]]  # interest A, interest B

    ranked = rank_events(events, event_embeddings, interest_embeddings)

    assert ranked[0].score == pytest.approx(1.0)


def test_rank_events_returns_events_sorted_descending_by_score():
    events = [_make_event("low"), _make_event("high"), _make_event("mid")]
    event_embeddings = [[0, 1], [1, 0], [0.7, 0.7]]
    interest_embeddings = [[1, 0]]

    ranked = rank_events(events, event_embeddings, interest_embeddings)

    assert [r.event.id for r in ranked] == ["high", "mid", "low"]


def test_rank_events_preserves_original_order_for_tied_scores():
    # Both events match interest A equally (1.0) and interest B not at all
    # — same score, so their relative order from the input should survive
    # the sort untouched (Python's sort is stable).
    events = [_make_event("first"), _make_event("second")]
    event_embeddings = [[1, 0], [1, 0]]
    interest_embeddings = [[1, 0], [0, 1]]

    ranked = rank_events(events, event_embeddings, interest_embeddings)

    assert [r.event.id for r in ranked] == ["first", "second"]


def test_rank_events_raises_on_length_mismatch():
    events = [_make_event("1"), _make_event("2")]
    event_embeddings = [[1, 0]]  # one short
    interest_embeddings = [[1, 0]]

    with pytest.raises(ValueError):
        rank_events(events, event_embeddings, interest_embeddings)


def test_rank_events_raises_on_empty_interest_embeddings():
    events = [_make_event("1")]
    event_embeddings = [[1, 0]]

    with pytest.raises(ValueError):
        rank_events(events, event_embeddings, [])


def test_rank_events_with_empty_events_list_returns_empty_list():
    ranked = rank_events([], [], [[1, 0]])

    assert ranked == []
