"""Thin wrapper around the TinyBERT sentence-embedding model.

Turns text into vectors so classifier_module.ranking can compare events to
the user's interests by meaning, not just keyword overlap. Not unit tested
here — encoding real text requires the actual model, the same reason
calendar_module.client isn't unit tested either. Verified manually instead
(scripts/check_ranking.py, once it exists).
"""

from sentence_transformers import SentenceTransformer

from config import TINYBERT_MODEL_NAME

# Loaded lazily on first use, then reused — loading the model from disk is
# slow (real work: reading weights, building the network), so we only want
# to pay that cost once per process, not once per embed_texts() call.
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(TINYBERT_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Encode a list of strings into embedding vectors, one per input text,
    in the same order.
    """
    model = _get_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()
