"""SQLite-backed storage for user feedback (like/dislike) on suggested
events.

No HTTP read path yet — see architecture.md decision #7 for why there's no
GET /feedback. Each row is a self-contained snapshot of the event at the
moment it was shown (name, start time, classification, the ranking score
it had), not just its id — no cache of fetched events exists anywhere else
in the app to look one back up by id later. `classification` was added in
Phase 10 step 3 (decision #12) specifically so classifier_module's
feedback-based ranking has a feature to train on; it's nullable because
events_module.client.Event.classification itself can be None.
"""

import contextlib
import logging
import sqlite3
from datetime import datetime

from config import FEEDBACK_DB_FILE

logger = logging.getLogger(__name__)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    event_name TEXT NOT NULL,
    event_start TEXT NOT NULL,
    score REAL NOT NULL,
    liked INTEGER NOT NULL,
    classification TEXT,
    created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
)
"""

_INSERT_FEEDBACK = """
INSERT INTO feedback (event_id, event_name, event_start, score, liked, classification)
VALUES (?, ?, ?, ?, ?, ?)
"""


def _connect(db_path: str) -> sqlite3.Connection:
    """Open a connection. Callers must pair this with contextlib.closing —
    sqlite3.Connection's own `with connection:` only wraps a transaction
    (commit on success, rollback on error), it does NOT close the
    connection afterwards. Easy to miss and easy to leak connections if
    you assume `with sqlite3.connect(...)` behaves like `with open(...)`.
    """
    return sqlite3.connect(db_path)


def init_db(db_path: str = FEEDBACK_DB_FILE) -> None:
    """Create the feedback table if it doesn't exist yet.

    Safe to call every time: CREATE TABLE IF NOT EXISTS is a no-op once
    the table is already there, and record_feedback() below calls this
    itself before every insert — for a single-user, low-volume app, that
    small repeated check is simpler and safer than requiring every caller
    to remember to initialize the database first.
    """
    with contextlib.closing(_connect(db_path)) as connection, connection:
        connection.execute(_CREATE_TABLE)


def record_feedback(
    event_id: str,
    event_name: str,
    event_start: datetime,
    score: float,
    liked: bool,
    classification: str | None = None,
    db_path: str = FEEDBACK_DB_FILE,
) -> int:
    """Store one feedback row and return its new row id.

    event_start must be timezone-aware, for the same reason as everywhere
    else in this app (calendar_module, events_module) — an ambiguous
    timestamp would make later analysis of the stored data unreliable.

    classification defaults to None (optional, not required) because it
    was added after event_id/event_name/etc. — see the module docstring —
    and older callers (before Phase 10 step 3) shouldn't be forced to
    supply something they may not have.
    """
    if event_start.tzinfo is None:
        raise ValueError("event_start must be timezone-aware")

    init_db(db_path)
    with contextlib.closing(_connect(db_path)) as connection, connection:
        cursor = connection.execute(
            _INSERT_FEEDBACK,
            (event_id, event_name, event_start.isoformat(), score, int(liked), classification),
        )
        logger.info("Recorded feedback: event_id=%s liked=%s score=%.3f", event_id, liked, score)
        return cursor.lastrowid
