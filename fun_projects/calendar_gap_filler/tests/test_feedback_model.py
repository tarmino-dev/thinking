"""Unit tests for classifier_module.feedback_model.

Pure logic, no I/O — sklearn's LogisticRegression runs locally and
deterministically enough for these tests (no network, no real TinyBERT
model), so unlike calendar_module/events_module this doesn't need mocking
or a "verify manually on the real thing" script to be meaningfully tested.
"""

from events_module.client import Event
from classifier_module.feedback_model import (
    MIN_FEEDBACK_FOR_MODEL,
    predict_score,
    train_feedback_model,
)
from feedback_module.store import FeedbackRow
from datetime import datetime, timezone

TZ = timezone.utc


def _feedback_row(liked: bool, classification: str | None, score: float = 0.2) -> FeedbackRow:
    return FeedbackRow(
        event_id="evt",
        event_name="Some Event",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=score,
        liked=liked,
        classification=classification,
    )


def _event(classification: str | None) -> Event:
    return Event(
        id="evt",
        name="Some Event",
        start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        duration_minutes=60.0,
        classification=classification,
        description=None,
        venue_name=None,
        url=None,
    )


# --- train_feedback_model: cold start / not-enough-data guards --------------------


def test_returns_none_when_fewer_rows_than_minimum():
    rows = [_feedback_row(True, "Music, Jazz, Vocal Jazz") for _ in range(MIN_FEEDBACK_FOR_MODEL - 1)]

    assert train_feedback_model(rows) is None


def test_returns_none_when_all_feedback_is_liked():
    # Enough rows, but only one class present — logistic regression can't
    # learn a decision boundary from a single class.
    rows = [_feedback_row(True, "Music, Jazz, Vocal Jazz") for _ in range(MIN_FEEDBACK_FOR_MODEL)]

    assert train_feedback_model(rows) is None


def test_returns_none_when_all_feedback_is_disliked():
    rows = [_feedback_row(False, "Sports, Golf, PGA Tour") for _ in range(MIN_FEEDBACK_FOR_MODEL)]

    assert train_feedback_model(rows) is None


# --- train_feedback_model + predict_score: real behavior --------------------------


def _varied_rows() -> list[FeedbackRow]:
    # Enough rows, both classes, and a real pattern to learn: "Music"
    # events liked, "Sports" events disliked, regardless of cosine_score.
    liked_music = [_feedback_row(True, "Music, Jazz, Vocal Jazz", score=0.1 + 0.01 * i) for i in range(10)]
    disliked_sports = [_feedback_row(False, "Sports, Golf, PGA Tour", score=0.1 + 0.01 * i) for i in range(10)]
    return liked_music + disliked_sports


def test_trains_successfully_with_enough_varied_data():
    model = train_feedback_model(_varied_rows())

    assert model is not None
    assert model.known_segments == ["Music", "Sports"]


def test_predict_score_is_a_probability():
    model = train_feedback_model(_varied_rows())

    score = predict_score(model, _event("Music, Rock, Alternative Rock"), cosine_score=0.15)

    assert 0.0 <= score <= 1.0


def test_predict_score_favors_previously_liked_segment():
    model = train_feedback_model(_varied_rows())

    music_score = predict_score(model, _event("Music, Rock, Alternative Rock"), cosine_score=0.15)
    sports_score = predict_score(model, _event("Sports, Basketball, NBA"), cosine_score=0.15)

    # Same cosine_score, different segment — the model should have learned
    # the segment matters, using the exact pattern in _varied_rows().
    assert music_score > sports_score


def test_predict_score_handles_unseen_segment_without_crashing():
    model = train_feedback_model(_varied_rows())

    # "Arts & Theatre" never appeared in training — _featurize() should
    # produce an all-zero one-hot block for it rather than raising.
    score = predict_score(model, _event("Arts & Theatre, Comedy, Stand-Up"), cosine_score=0.15)

    assert 0.0 <= score <= 1.0


def test_predict_score_handles_missing_classification():
    model = train_feedback_model(_varied_rows())

    score = predict_score(model, _event(None), cosine_score=0.15)

    assert 0.0 <= score <= 1.0
