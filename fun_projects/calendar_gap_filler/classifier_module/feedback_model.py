"""Feedback-based ranking adjustment (Phase 10 step 3, decision #12).

Trains a small logistic regression on accumulated user feedback
(feedback_module.store) to predict P(liked) for a candidate event, meant to
replace the plain cosine-similarity score once there's enough feedback to
make that worth trusting. Below that threshold, the caller should leave
ranking untouched — an undertrained model is worse than no model at all
(same reasoning as decision #3's honesty about cosine-similarity's narrow
real-world range: don't over-trust a number just because it came out of
"real ML").

Retrains from scratch on every call rather than persisting a model file:
with feedback likely staying in the tens or low hundreds of rows for a
single-user app, training takes milliseconds, and persistence would add
versioning/staleness complexity for no real benefit at this scale.
"""

import logging
from dataclasses import dataclass

from sklearn.linear_model import LogisticRegression

from events_module.client import Event
from feedback_module.store import FeedbackRow

logger = logging.getLogger(__name__)

# Below this many labeled examples, a logistic regression has nothing
# meaningful to learn from — it would just memorize noise and produce
# confident-looking but arbitrary predictions. A round, conservative
# number chosen up front; revisit once real usage shows what a sensible
# amount of data actually looks like for this app.
MIN_FEEDBACK_FOR_MODEL = 15


@dataclass
class FeedbackModel:
    """A trained model plus the fixed list of classification segments it
    was trained on. predict_score() needs that same segment list (in the
    same order) to build a feature vector for a new event that lines up
    with what the model was actually trained on.
    """

    model: LogisticRegression
    known_segments: list[str]


def _segment(classification: str | None) -> str:
    """The first, coarse component of a classification string (e.g.
    "Music" from "Music, Jazz, Vocal Jazz"). Matching on the full string
    would be too specific to ever repeat across different real events —
    see decision #12 for the concrete example that ruled that out.
    """
    if not classification:
        return ""
    return classification.split(",")[0].strip()


def _featurize(cosine_score: float, segment: str, known_segments: list[str]) -> list[float]:
    """One feature vector: the cosine score, plus a one-hot flag per known
    segment. A segment never seen during training (including "" for a
    missing classification) contributes an all-zero one-hot block —
    logistic regression handles that fine, it just means none of the
    segment weights apply to this particular example.
    """
    one_hot = [1.0 if segment == known else 0.0 for known in known_segments]
    return [cosine_score, *one_hot]


def train_feedback_model(feedback_rows: list[FeedbackRow]) -> FeedbackModel | None:
    """Train a fresh logistic regression on all feedback collected so far.

    Returns None if there isn't enough of it yet to trust (too few rows,
    or only one class represented so far — logistic regression requires
    both to fit at all, and one-sided feedback this early tells us nothing
    about what the *other* choice would have looked like).
    """
    if len(feedback_rows) < MIN_FEEDBACK_FOR_MODEL:
        logger.info(
            "Skipping feedback model: %d row(s) recorded, need at least %d",
            len(feedback_rows),
            MIN_FEEDBACK_FOR_MODEL,
        )
        return None

    labels = [1 if row.liked else 0 for row in feedback_rows]
    if len(set(labels)) < 2:
        logger.info("Skipping feedback model: all recorded feedback is the same (all liked or all disliked)")
        return None

    known_segments = sorted({_segment(row.classification) for row in feedback_rows} - {""})
    features = [_featurize(row.score, _segment(row.classification), known_segments) for row in feedback_rows]

    model = LogisticRegression()
    model.fit(features, labels)
    logger.info(
        "Trained feedback model on %d example(s) across %d segment(s)", len(feedback_rows), len(known_segments)
    )
    return FeedbackModel(model=model, known_segments=known_segments)


def predict_score(feedback_model: FeedbackModel, event: Event, cosine_score: float) -> float:
    """Predicted probability that the user would like this event, given
    its content-based cosine_score and classification segment.
    """
    features = [_featurize(cosine_score, _segment(event.classification), feedback_model.known_segments)]
    return float(feedback_model.model.predict_proba(features)[0][1])
