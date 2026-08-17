"""Pure ranking logic for classifier_module.

Given precomputed embeddings (from classifier_module.embeddings), scores and
sorts candidate events by how well they match the user's interests. No
model, no network — everything here works on plain lists of floats, which
is what makes it unit-testable without downloading TinyBERT.
"""

import math
from dataclasses import dataclass

from events_module.client import Event


@dataclass
class RankedEvent:
    """An event paired with its relevance score against the user's
    interests. Higher score = more relevant.
    """

    event: Event
    score: float


def rank_events(
    events: list[Event],
    event_embeddings: list[list[float]],
    interest_embeddings: list[list[float]],
) -> list[RankedEvent]:
    """Score each event by its best match among the user's interests, and
    return them sorted from most to least relevant.

    "Best match" is the MAX cosine similarity across all interest
    embeddings, not the average — an event should count as relevant if it
    matches ANY one of the user's interests well, not just if it's a
    middling match against all of them blended together.
    """
    if len(events) != len(event_embeddings):
        raise ValueError("events and event_embeddings must have the same length")
    if not interest_embeddings:
        raise ValueError("interest_embeddings must not be empty")

    ranked = [
        RankedEvent(event=event, score=_best_match_score(event_embedding, interest_embeddings))
        for event, event_embedding in zip(events, event_embeddings)
    ]
    return sorted(ranked, key=lambda ranked_event: ranked_event.score, reverse=True)


def _best_match_score(event_embedding: list[float], interest_embeddings: list[list[float]]) -> float:
    return max(_cosine_similarity(event_embedding, interest) for interest in interest_embeddings)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Measure how similar two embedding vectors are in *direction*,
    ignoring their length.

    Geometrically, this is the cosine of the angle between vectors a and b:
    1.0 means they point the same way (as similar in meaning as it gets for
    this model), 0.0 means they're unrelated (perpendicular), and -1.0
    means they point in opposite directions. We use this instead of e.g.
    raw distance because embedding *direction* is what encodes meaning —
    two texts about the same topic point the same way even if one
    embedding happens to have a larger magnitude than the other.

    Formula: cos(angle) = (a . b) / (|a| * |b|)
    where "a . b" is the dot product and "|a|", "|b|" are the vectors'
    lengths (Euclidean norms).
    """
    # Dot product: multiply matching components pairwise, then sum them up.
    dot_product = sum(x * y for x, y in zip(a, b))

    # Euclidean norm (length) of each vector: sqrt of the sum of squared components.
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    # Dividing the dot product by both lengths cancels out magnitude,
    # leaving only the directional (angular) similarity.
    return dot_product / (norm_a * norm_b)
