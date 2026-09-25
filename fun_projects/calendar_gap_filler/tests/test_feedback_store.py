"""Unit tests for feedback_module.store.

Unlike every other I/O-touching module in this project, SQLite needs
neither credentials nor a network call — so these run against a real
temporary database (pytest's tmp_path), not a fake or a mock.
"""

import os
import sqlite3
from datetime import datetime, timezone

import pytest

from feedback_module.store import FeedbackRow, get_all_feedback, init_db, record_feedback

TZ = timezone.utc


def _db_path(tmp_path) -> str:
    return str(tmp_path / "feedback.db")


def _fetch_all(db_path: str) -> list[tuple]:
    with sqlite3.connect(db_path) as connection:
        return connection.execute(
            "SELECT event_id, event_name, event_start, score, liked FROM feedback ORDER BY id"
        ).fetchall()


def _fetch_all_with_classification(db_path: str) -> list[tuple]:
    with sqlite3.connect(db_path) as connection:
        return connection.execute(
            "SELECT event_id, event_name, event_start, score, liked, classification FROM feedback ORDER BY id"
        ).fetchall()


# --- init_db ----------------------------------------------------------------------


def test_init_db_creates_feedback_table(tmp_path):
    db_path = _db_path(tmp_path)

    init_db(db_path)

    with sqlite3.connect(db_path) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "feedback" in tables


def test_init_db_is_idempotent(tmp_path):
    db_path = _db_path(tmp_path)

    init_db(db_path)
    init_db(db_path)  # must not raise, table already exists

    with sqlite3.connect(db_path) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "feedback" in tables


# --- record_feedback ----------------------------------------------------------------


def test_record_feedback_creates_db_and_table_when_missing(tmp_path):
    db_path = _db_path(tmp_path)  # file doesn't exist yet; init_db() is never called directly

    record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        db_path=db_path,
    )

    assert _fetch_all(db_path) == [("evt-1", "Jazz Night", "2026-08-20T19:00:00+00:00", 0.27, 1)]


def test_record_feedback_returns_incrementing_row_ids(tmp_path):
    db_path = _db_path(tmp_path)

    first_id = record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        db_path=db_path,
    )
    second_id = record_feedback(
        event_id="evt-2",
        event_name="Board Games Meetup",
        event_start=datetime(2026, 8, 21, 10, 0, tzinfo=TZ),
        score=0.15,
        liked=False,
        db_path=db_path,
    )

    assert (first_id, second_id) == (1, 2)
    assert len(_fetch_all(db_path)) == 2


def test_record_feedback_stores_liked_true_as_1(tmp_path):
    db_path = _db_path(tmp_path)

    record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        db_path=db_path,
    )

    assert _fetch_all(db_path)[0][4] == 1


def test_record_feedback_stores_liked_false_as_0(tmp_path):
    db_path = _db_path(tmp_path)

    record_feedback(
        event_id="evt-1",
        event_name="Not For Me",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.05,
        liked=False,
        db_path=db_path,
    )

    assert _fetch_all(db_path)[0][4] == 0


def test_record_feedback_raises_for_naive_datetime(tmp_path):
    db_path = _db_path(tmp_path)

    with pytest.raises(ValueError):
        record_feedback(
            event_id="evt-1",
            event_name="Jazz Night",
            event_start=datetime(2026, 8, 20, 19, 0),  # naive
            score=0.27,
            liked=True,
            db_path=db_path,
        )


def test_record_feedback_stores_classification(tmp_path):
    db_path = _db_path(tmp_path)

    record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        classification="Music, Jazz, Vocal Jazz",
        db_path=db_path,
    )

    assert _fetch_all_with_classification(db_path)[0][5] == "Music, Jazz, Vocal Jazz"


def test_record_feedback_classification_defaults_to_none(tmp_path):
    # Older callers (or events with no classification at all — Ticketmaster
    # doesn't always provide one) shouldn't be forced to supply it.
    db_path = _db_path(tmp_path)

    record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        db_path=db_path,
    )

    assert _fetch_all_with_classification(db_path)[0][5] is None


def test_record_feedback_naive_datetime_leaves_no_trace(tmp_path):
    # The tzinfo check runs before any connection is opened, so a rejected
    # call shouldn't even create the database file, let alone a table.
    db_path = _db_path(tmp_path)

    with pytest.raises(ValueError):
        record_feedback(
            event_id="evt-1",
            event_name="Jazz Night",
            event_start=datetime(2026, 8, 20, 19, 0),
            score=0.27,
            liked=True,
            db_path=db_path,
        )

    assert not os.path.exists(db_path)


# --- get_all_feedback --------------------------------------------------------------


def test_get_all_feedback_returns_empty_list_when_nothing_recorded(tmp_path):
    db_path = _db_path(tmp_path)  # file doesn't exist yet

    assert get_all_feedback(db_path) == []


def test_get_all_feedback_returns_stored_rows(tmp_path):
    db_path = _db_path(tmp_path)
    record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        classification="Music, Jazz, Vocal Jazz",
        db_path=db_path,
    )
    record_feedback(
        event_id="evt-2",
        event_name="Golf Championship",
        event_start=datetime(2026, 8, 21, 10, 0, tzinfo=TZ),
        score=-0.05,
        liked=False,
        classification="Sports, Golf, PGA Tour",
        db_path=db_path,
    )

    rows = get_all_feedback(db_path)

    assert rows == [
        FeedbackRow(
            event_id="evt-1",
            event_name="Jazz Night",
            event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
            score=0.27,
            liked=True,
            classification="Music, Jazz, Vocal Jazz",
        ),
        FeedbackRow(
            event_id="evt-2",
            event_name="Golf Championship",
            event_start=datetime(2026, 8, 21, 10, 0, tzinfo=TZ),
            score=-0.05,
            liked=False,
            classification="Sports, Golf, PGA Tour",
        ),
    ]


def test_get_all_feedback_classification_none_round_trips(tmp_path):
    db_path = _db_path(tmp_path)
    record_feedback(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        score=0.27,
        liked=True,
        db_path=db_path,
    )

    assert get_all_feedback(db_path)[0].classification is None
