"""Unit tests for api.main.

_to_response is tested directly — pure conversion logic, no HTTP involved.
The /suggestions endpoint is tested through FastAPI's TestClient with
core.suggest_events monkeypatched, the same way other tests in this project
stub out the thing they don't want to actually call (see
tests/test_profile.py) instead of reaching for a mocking library.
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
