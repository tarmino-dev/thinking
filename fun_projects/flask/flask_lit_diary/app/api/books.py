import requests
from flask import Blueprint, jsonify, request

books_bp = Blueprint("books_api", __name__, url_prefix="/api")

_OPEN_LIBRARY_SEARCH = "https://openlibrary.org/search.json"
_MAX_RESULTS = 10
_MIN_QUERY_LEN = 2
_TIMEOUT_S = 10


def _doc_title(doc: dict) -> str:
    raw = doc.get("title")
    if isinstance(raw, list) and raw:
        return str(raw[0]).strip()
    if isinstance(raw, str):
        return raw.strip()
    return ""


def _doc_author(doc: dict) -> str:
    names = doc.get("author_name")
    if isinstance(names, list) and names:
        return str(names[0]).strip()
    if isinstance(names, str):
        return names.strip()
    return ""


@books_bp.get("/books/search")
def search_books():
    q = request.args.get("q", "").strip()
    if len(q) < _MIN_QUERY_LEN:
        return (
            jsonify(
                {
                    "error": "validation error",
                    "message": f"parameter 'q' must be at least {_MIN_QUERY_LEN} characters",
                }
            ),
            400,
        )

    try:
        resp = requests.get(
            _OPEN_LIBRARY_SEARCH,
            params={"q": q, "limit": _MAX_RESULTS},
            timeout=_TIMEOUT_S,
            headers={"User-Agent": "FlaskLitDiary/1.0 (book search; contact: local dev)"},
        )
        resp.raise_for_status()
    except requests.RequestException:
        return (
            jsonify(
                {
                    "error": "upstream error",
                    "message": "Open Library request failed",
                    "results": [],
                }
            ),
            502,
        )

    try:
        payload = resp.json()
    except ValueError:
        return (
            jsonify(
                {
                    "error": "upstream error",
                    "message": "invalid JSON from Open Library",
                    "results": [],
                }
            ),
            502,
        )

    docs = payload.get("docs") or []
    results: list[dict[str, str]] = []
    for doc in docs[:_MAX_RESULTS]:
        if not isinstance(doc, dict):
            continue
        title = _doc_title(doc)
        if not title:
            continue
        author = _doc_author(doc)
        display = f"{title} — {author}" if author else title
        results.append({"title": title, "author": author, "display": display})

    return jsonify({"results": results})
