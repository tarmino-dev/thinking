"""Unit tests for api.main.

_to_response is tested directly — pure conversion logic, no HTTP involved.
The /suggestions and /feedback endpoints are tested through FastAPI's
TestClient with core.suggest_events / feedback_module.record_feedback
monkeypatched, the same way other tests in this project stub out the thing
they don't want to actually call (see tests/test_profile.py) instead of
reaching for a mocking library. /ui gets a thin test confirming the
StaticFiles mount actually serves something — its JS logic isn't tested
here at all (no JS test runner in this project); that got a one-off manual
check instead, see Phase 8.2/8.3.
"""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from api.main import _to_response, app
from calendar_module.gaps import Gap
from classifier_module.ranking import RankedEvent
from events_module.client import Event

client = TestClient(app)

TZ = timezone.utc


def _make_gap(start_hour: int, end_hour: int) -> Gap:
    return Gap(start=datetime(2026, 8, 20, start_hour, tzinfo=TZ), end=datetime(2026, 8, 20, end_hour, tzinfo=TZ))


def _make_event(id_: str = "1", **overrides) -> Event:
    fields = dict(
        id=id_,
        name=f"Event {id_}",
        start=datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        duration_minutes=60.0,
        classification="Music, Jazz",
        description="A show.",
        venue_name="Blue Note",
        url="https://example.com",
    )
    fields.update(overrides)
    return Event(**fields)


@pytest.fixture
def token_file_present(monkeypatch, tmp_path):
    """Points GOOGLE_TOKEN_FILE at a tmp file that exists, so the
    missing-token guard in get_suggestions() doesn't short-circuit tests
    that are about what happens *after* that guard passes. Without this,
    those tests would depend on whether a real token.json happens to sit
    in whatever directory pytest is run from — exactly the kind of ambient
    state tests/test_profile.py already avoids by using tmp_path instead of
    the real profile.json.
    """
    token_file = tmp_path / "token.json"
    token_file.write_text("{}")
    monkeypatch.setattr("api.main.GOOGLE_TOKEN_FILE", str(token_file))


# --- _to_response ---------------------------------------------------------------


def test_to_response_converts_gap_and_ranked_events():
    gap = _make_gap(18, 21)
    event = _make_event("1")

    result = _to_response(gap, [RankedEvent(event=event, score=0.42)])

    assert result.gap.start == gap.start
    assert result.gap.end == gap.end
    assert result.gap.duration_minutes == 180.0
    assert len(result.suggestions) == 1
    assert result.suggestions[0].event.id == "1"
    assert result.suggestions[0].event.venue_name == "Blue Note"
    assert result.suggestions[0].score == 0.42


def test_to_response_handles_event_with_all_optional_fields_none():
    # Ticketmaster frequently omits duration/classification/description/
    # venue/url (see events_module.client) — the response model has to
    # tolerate that shape, not just the fully-populated happy path.
    gap = _make_gap(18, 21)
    sparse_event = _make_event(
        "2", duration_minutes=None, classification=None, description=None, venue_name=None, url=None
    )

    result = _to_response(gap, [RankedEvent(event=sparse_event, score=0.1)])

    event_response = result.suggestions[0].event
    assert event_response.duration_minutes is None
    assert event_response.classification is None
    assert event_response.description is None
    assert event_response.venue_name is None
    assert event_response.url is None


def test_to_response_empty_suggestions_for_gap_with_no_matches():
    gap = _make_gap(18, 21)

    result = _to_response(gap, [])

    assert result.suggestions == []


# --- GET /suggestions -------------------------------------------------------------


def test_get_suggestions_returns_expected_shape(monkeypatch, token_file_present):
    gap = _make_gap(18, 21)
    event = _make_event("1")
    monkeypatch.setattr("api.main.suggest_events", lambda: [(gap, [RankedEvent(event=event, score=0.5)])])

    response = client.get("/suggestions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["gap"]["duration_minutes"] == 180.0
    assert body[0]["suggestions"][0]["event"]["id"] == "1"
    assert body[0]["suggestions"][0]["score"] == 0.5


def test_get_suggestions_empty_list_when_no_gaps(monkeypatch, token_file_present):
    monkeypatch.setattr("api.main.suggest_events", lambda: [])

    response = client.get("/suggestions")

    assert response.status_code == 200
    assert response.json() == []


def test_get_suggestions_returns_503_when_orchestrator_raises_runtime_error(monkeypatch, token_file_present):
    def _raise():
        raise RuntimeError("USER_LATITUDE and USER_LONGITUDE are not set.")

    monkeypatch.setattr("api.main.suggest_events", _raise)

    response = client.get("/suggestions")

    assert response.status_code == 503
    assert "USER_LATITUDE" in response.json()["detail"]


def test_get_suggestions_returns_503_when_token_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("api.main.GOOGLE_TOKEN_FILE", str(tmp_path / "token.json"))  # deliberately never created

    def _fail_if_called():
        raise AssertionError("suggest_events should not be called when token.json is missing")

    monkeypatch.setattr("api.main.suggest_events", _fail_if_called)

    response = client.get("/suggestions")

    assert response.status_code == 503
    assert "token.json" in response.json()["detail"]


# --- POST /feedback ---------------------------------------------------------------


def _valid_feedback_payload(**overrides) -> dict:
    payload = dict(
        event_id="evt-1",
        event_name="Jazz Night",
        event_start="2026-08-20T19:00:00+00:00",
        score=0.27,
        liked=True,
    )
    payload.update(overrides)
    return payload


def _fail_if_called(**kwargs):
    raise AssertionError("record_feedback should not be called when the request is invalid")


def test_post_feedback_returns_201_with_id(monkeypatch):
    captured = {}

    def _fake_record_feedback(**kwargs):
        captured.update(kwargs)
        return 7

    monkeypatch.setattr("api.main.record_feedback", _fake_record_feedback)

    response = client.post("/feedback", json=_valid_feedback_payload())

    assert response.status_code == 201
    assert response.json() == {"id": 7}
    # Also proves the request body was actually parsed into the right
    # Python types (e.g. the JSON string became a real datetime, "true"
    # became True), not just forwarded to record_feedback as raw JSON.
    assert captured == {
        "event_id": "evt-1",
        "event_name": "Jazz Night",
        "event_start": datetime(2026, 8, 20, 19, 0, tzinfo=TZ),
        "score": 0.27,
        "liked": True,
        "classification": None,
    }


def test_post_feedback_forwards_classification_when_provided(monkeypatch):
    captured = {}

    def _fake_record_feedback(**kwargs):
        captured.update(kwargs)
        return 7

    monkeypatch.setattr("api.main.record_feedback", _fake_record_feedback)

    response = client.post("/feedback", json=_valid_feedback_payload(classification="Music, Jazz, Vocal Jazz"))

    assert response.status_code == 201
    assert captured["classification"] == "Music, Jazz, Vocal Jazz"


def test_post_feedback_naive_event_start_returns_422(monkeypatch):
    monkeypatch.setattr("api.main.record_feedback", _fail_if_called)

    response = client.post("/feedback", json=_valid_feedback_payload(event_start="2026-08-20T19:00:00"))

    assert response.status_code == 422


def test_post_feedback_score_above_range_returns_422(monkeypatch):
    monkeypatch.setattr("api.main.record_feedback", _fail_if_called)

    response = client.post("/feedback", json=_valid_feedback_payload(score=1.5))

    assert response.status_code == 422


def test_post_feedback_score_below_range_returns_422(monkeypatch):
    monkeypatch.setattr("api.main.record_feedback", _fail_if_called)

    response = client.post("/feedback", json=_valid_feedback_payload(score=-1.5))

    assert response.status_code == 422


def test_post_feedback_score_boundary_values_are_valid(monkeypatch):
    # ge=-1.0/le=1.0 means the boundary itself must be accepted, not just
    # values safely inside it — this is exactly the kind of off-by-one
    # (ge vs gt) that "clearly out of range" tests alone wouldn't catch.
    monkeypatch.setattr("api.main.record_feedback", lambda **kwargs: 1)

    assert client.post("/feedback", json=_valid_feedback_payload(score=-1.0)).status_code == 201
    assert client.post("/feedback", json=_valid_feedback_payload(score=1.0)).status_code == 201


def test_post_feedback_missing_required_field_returns_422(monkeypatch):
    monkeypatch.setattr("api.main.record_feedback", _fail_if_called)

    payload = _valid_feedback_payload()
    del payload["liked"]

    response = client.post("/feedback", json=payload)

    assert response.status_code == 422


# --- GET /ui ----------------------------------------------------------------------


def test_get_ui_serves_index_html():
    # Thin on purpose (Развилка №4, Phase 8): this only confirms the
    # StaticFiles mount actually serves ui/index.html. The page's JS
    # (fetch calls, rendering, button behavior) has no test runner in
    # this project and was checked manually instead.
    response = client.get("/ui/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Calendar Gap Filler" in response.text


def test_get_ui_without_trailing_slash_redirects():
    # Not our code — Starlette's own Mount behavior — but worth pinning
    # down since it's exactly the URL someone would type by hand.
    response = client.get("/ui", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].endswith("/ui/")
