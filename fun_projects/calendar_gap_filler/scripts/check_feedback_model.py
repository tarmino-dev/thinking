"""Manual check: see whether there's enough feedback yet to train the
feedback-based ranking model (Phase 10 step 3, decision #12), and if so,
what it currently predicts for each classification segment it has seen.

This is not an automated test — it's a script you run by hand against your
real feedback.db to eyeball whether the model's learned effect per segment
makes sense (e.g. a segment you've consistently liked should predict higher
than one you've consistently disliked, at the same cosine_score). Run it
from the project root:

    PYTHONPATH=. python3 scripts/check_feedback_model.py
"""

from datetime import datetime, timezone

from classifier_module.feedback_model import MIN_FEEDBACK_FOR_MODEL, predict_score, train_feedback_model
from events_module.client import Event
from feedback_module.store import get_all_feedback

# Representative cosine_score values to show predictions at — picked to
# span the narrow real-world range these scores actually land in (decision
# #3: real TinyBERT cosine similarities cluster around 0.14-0.30, not the
# full [-1, 1] range), not spread across the whole mathematical range.
SAMPLE_COSINE_SCORES = [0.15, 0.22, 0.30]


def _dummy_event(segment: str) -> Event:
    # predict_score() only ever reads .classification off the event —
    # every other field here is just a placeholder to satisfy Event's
    # required fields, not something the prediction actually uses.
    return Event(
        id="dummy",
        name="dummy",
        start=datetime.now(timezone.utc),
        duration_minutes=None,
        classification=segment,
        description=None,
        venue_name=None,
        url=None,
    )


def main() -> None:
    feedback_rows = get_all_feedback()
    liked_count = sum(row.liked for row in feedback_rows)
    print(
        f"{len(feedback_rows)} feedback row(s) recorded "
        f"({liked_count} liked, {len(feedback_rows) - liked_count} disliked)."
    )

    model = train_feedback_model(feedback_rows)
    if model is None:
        print(
            f"Not enough data yet to train a model (need at least {MIN_FEEDBACK_FOR_MODEL} rows, "
            "with both liked and disliked represented) — ranking falls back to plain cosine similarity."
        )
        return

    print(f"\nModel trained across {len(model.known_segments)} known segment(s). Predicted P(liked) by segment:\n")
    for segment in model.known_segments:
        event = _dummy_event(segment)
        predictions = [predict_score(model, event, score) for score in SAMPLE_COSINE_SCORES]
        formatted = "  ".join(f"cosine={s:.2f} -> {p:.3f}" for s, p in zip(SAMPLE_COSINE_SCORES, predictions))
        print(f"  {segment:<20} {formatted}")


if __name__ == "__main__":
    main()
