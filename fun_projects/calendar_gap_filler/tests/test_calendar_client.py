"""Unit tests for calendar_module.client — currently only covers the Phase
10 hardening added to get_busy_periods() (wrapping a live Google Calendar
API failure into a RuntimeError). _load_credentials()'s OAuth flow itself
needs a real browser login or a real cached token to exercise meaningfully,
which is why this module has no broader test coverage yet.
"""

from datetime import datetime, timezone

import pytest
from googleapiclient.errors import HttpError

from calendar_module.client import get_busy_periods


class _FakeHttpResponse:
    """Minimal stand-in for the httplib2.Response HttpError expects —
    only .status and .reason are ever read when the error is just being
    raised and caught, not inspected in detail.
    """

    status = 500
    reason = "Internal Server Error"


class _FakeEventsList:
    def list(self, **kwargs):
        return self

    def execute(self):
        raise HttpError(resp=_FakeHttpResponse(), content=b'{"error": "boom"}')


class _FakeService:
    def events(self):
        return _FakeEventsList()


def test_get_busy_periods_raises_runtime_error_on_http_error(monkeypatch):
    # A live failure of the Google Calendar API (quota, transient outage,
    # ...) used to propagate as a raw googleapiclient.errors.HttpError all
    # the way to api/main.py instead of the 503 every other "can't fulfill
    # this request right now" case gets.
    monkeypatch.setattr("calendar_module.client._load_credentials", lambda: object())
    monkeypatch.setattr("calendar_module.client.build", lambda *args, **kwargs: _FakeService())

    aware_from = datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc)
    aware_to = datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(RuntimeError):
        get_busy_periods(aware_from, aware_to)


def test_get_busy_periods_raises_for_naive_datetime():
    naive = datetime(2026, 8, 10, 9, 0)
    aware = datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        get_busy_periods(naive, aware)
