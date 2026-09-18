"""Unit tests for events_module.client.

No network calls anywhere in this file — the Ticketmaster HTTP request in
search_events() is only reached after validation that doesn't need one, and
every parsing helper works on hardcoded JSON shaped like real Discovery API
responses.
"""

from datetime import datetime, timezone

import pytest
import requests

from events_module.client import (
    _format_classification,
    _has_specific_start_time,
    _parse_datetime,
    _parse_event,
    search_events,
)

SAMPLE_EVENT_FULL = {
    "id": "abc123",
    "name": "WGC Cadillac Championship - Sunday Ticket",
    "url": "http://ticketmaster.com/event/0E0050681F51BA4C",
    "info": "Bring your own clubs.",
    "dates": {"start": {"localDate": "2016-03-06", "dateTime": "2016-03-06T18:00:00Z"}},
    "classifications": [
        {"primary": True, "segment": {"name": "Sports"}, "genre": {"name": "Golf"}, "subGenre": {"name": "PGA Tour"}}
    ],
    "_embedded": {"venues": [{"name": "Trump National Doral", "city": {"name": "Miami"}}]},
}

SAMPLE_EVENT_VENUE_WITHOUT_NAME = {
    "id": "venue001",
    "name": "Event At An Unnamed Venue",
    "dates": {"start": {"dateTime": "2016-03-06T18:00:00Z"}},
    # Real Ticketmaster data occasionally has a venue entry with no "name"
    # field at all — this used to crash _parse_event with a KeyError.
    "_embedded": {"venues": [{"city": {"name": "Miami"}}]},
}

SAMPLE_EVENT_TBA = {
    "id": "def456",
    "name": "TBA Show",
    "dates": {"start": {"localDate": "2016-03-07", "dateTBA": True}},
}

SAMPLE_EVENT_WITH_END = {
    "id": "jkl012",
    "name": "Concert With Known End",
    "dates": {"start": {"dateTime": "2016-03-06T18:00:00Z"}, "end": {"dateTime": "2016-03-06T21:30:00Z"}},
}

# No classifications, no _embedded, no info/pleaseNote, no url — the bare
# minimum a raw event could plausibly have.
SAMPLE_EVENT_MINIMAL = {
    "id": "min001",
    "name": "Minimal Event",
    "dates": {"start": {"dateTime": "2016-03-06T18:00:00Z"}},
}

SAMPLE_EVENT_PLEASE_NOTE_ONLY = {
    "id": "note001",
    "name": "Event With Note Only",
    "dates": {"start": {"dateTime": "2016-03-06T20:00:00Z"}},
    "pleaseNote": "Doors open at 7pm.",
}

SAMPLE_CLASSIFICATIONS_UNDEFINED_GENRE = [
    {"primary": True, "segment": {"name": "Miscellaneous"}, "genre": {"name": "Undefined"}, "subGenre": {"name": "Undefined"}}
]

SAMPLE_CLASSIFICATIONS_ALL_UNDEFINED = [
    {"primary": True, "segment": {"name": "Undefined"}, "genre": {"name": "Undefined"}, "subGenre": {"name": "Undefined"}}
]

SAMPLE_CLASSIFICATIONS_MULTIPLE = [
    {"primary": False, "segment": {"name": "Arts"}, "genre": {"name": "Theatre"}, "subGenre": {"name": "Drama"}},
    {"primary": True, "segment": {"name": "Music"}, "genre": {"name": "Rock"}, "subGenre": {"name": "Alternative Rock"}},
]


def test_has_specific_start_time_true_when_datetime_present():
    assert _has_specific_start_time(SAMPLE_EVENT_FULL) is True


def test_has_specific_start_time_false_when_date_is_tba():
    assert _has_specific_start_time(SAMPLE_EVENT_TBA) is False


def test_parse_event_extracts_basic_fields():
    event = _parse_event(SAMPLE_EVENT_FULL)

    assert event.id == "abc123"
    assert event.name == "WGC Cadillac Championship - Sunday Ticket"
    assert event.start == datetime(2016, 3, 6, 18, 0, tzinfo=timezone.utc)
    assert event.url == "http://ticketmaster.com/event/0E0050681F51BA4C"
    assert event.venue_name == "Trump National Doral"
    assert event.description == "Bring your own clubs."
    assert event.classification == "Sports, Golf, PGA Tour"


def test_parse_event_venue_name_is_none_when_venue_has_no_name():
    event = _parse_event(SAMPLE_EVENT_VENUE_WITHOUT_NAME)

    assert event.venue_name is None


def test_parse_event_duration_is_none_when_end_missing():
    event = _parse_event(SAMPLE_EVENT_FULL)

    assert event.duration_minutes is None


def test_parse_event_duration_is_computed_when_end_present():
    event = _parse_event(SAMPLE_EVENT_WITH_END)

    assert event.duration_minutes == 210.0


def test_parse_event_handles_missing_optional_fields_gracefully():
    event = _parse_event(SAMPLE_EVENT_MINIMAL)

    assert event.classification is None
    assert event.description is None
    assert event.venue_name is None
    assert event.url is None


def test_parse_event_description_falls_back_to_please_note():
    event = _parse_event(SAMPLE_EVENT_PLEASE_NOTE_ONLY)

    assert event.description == "Doors open at 7pm."


def test_parse_datetime_handles_z_suffix():
    assert _parse_datetime("2016-03-06T18:00:00Z") == datetime(2016, 3, 6, 18, 0, tzinfo=timezone.utc)


def test_format_classification_combines_segment_genre_subgenre():
    result = _format_classification(SAMPLE_EVENT_FULL["classifications"])

    assert result == "Sports, Golf, PGA Tour"


def test_format_classification_filters_undefined_values():
    result = _format_classification(SAMPLE_CLASSIFICATIONS_UNDEFINED_GENRE)

    assert result == "Miscellaneous"


def test_format_classification_returns_none_when_all_values_are_undefined():
    assert _format_classification(SAMPLE_CLASSIFICATIONS_ALL_UNDEFINED) is None


def test_format_classification_returns_none_for_empty_list():
    assert _format_classification([]) is None


def test_format_classification_picks_primary_entry_when_multiple():
    result = _format_classification(SAMPLE_CLASSIFICATIONS_MULTIPLE)

    assert result == "Music, Rock, Alternative Rock"


def test_search_events_raises_for_naive_datetime():
    naive = datetime(2026, 8, 10, 9, 0)
    aware = datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        search_events(50.45, 30.52, 20, naive, aware)


def test_search_events_raises_when_api_key_missing(monkeypatch):
    monkeypatch.setattr("events_module.client.TICKETMASTER_API_KEY", None)
    aware_from = datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc)
    aware_to = datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(RuntimeError):
        search_events(50.45, 30.52, 20, aware_from, aware_to)


def test_search_events_raises_runtime_error_on_connection_failure(monkeypatch):
    # Ticketmaster itself being unreachable (network down, DNS failure, ...)
    # — Phase 10 hardening: this used to propagate as a raw
    # requests.exceptions.ConnectionError all the way to api/main.py.
    monkeypatch.setattr("events_module.client.TICKETMASTER_API_KEY", "fake-key")

    def _raise_connection_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("boom")

    monkeypatch.setattr("events_module.client.requests.get", _raise_connection_error)
    aware_from = datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc)
    aware_to = datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(RuntimeError):
        search_events(50.45, 30.52, 20, aware_from, aware_to)


def test_search_events_raises_runtime_error_on_non_2xx_response(monkeypatch):
    # Ticketmaster reachable but erroring (rate limit, 5xx, ...) —
    # raise_for_status() raises HTTPError, a RequestException subclass,
    # which should be caught by the same handling as a connection failure.
    monkeypatch.setattr("events_module.client.TICKETMASTER_API_KEY", "fake-key")

    class _FailingResponse:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("500 Server Error")

    monkeypatch.setattr("events_module.client.requests.get", lambda *args, **kwargs: _FailingResponse())
    aware_from = datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc)
    aware_to = datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(RuntimeError):
        search_events(50.45, 30.52, 20, aware_from, aware_to)
