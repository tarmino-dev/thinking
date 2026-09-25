"""Unit tests for calendar_module.gaps.find_gaps.

Every test works with plain BusyBlock/Gap data — no real Google Calendar API
calls happen anywhere in this file, which is exactly why gaps.py was kept
free of I/O in the first place.
"""

from datetime import datetime, timezone

import pytest

from calendar_module.client import BusyBlock
from calendar_module.gaps import Gap, find_gaps

TZ = timezone.utc
DAY_START = datetime(2026, 8, 10, 9, 0, tzinfo=TZ)
DAY_END = datetime(2026, 8, 10, 18, 0, tzinfo=TZ)


def dt(hour: int, minute: int = 0) -> datetime:
    """Shorthand for a timezone-aware datetime on our fixed test day."""
    return datetime(2026, 8, 10, hour, minute, tzinfo=TZ)


def test_empty_calendar_returns_whole_day_as_one_gap():
    gaps = find_gaps([], DAY_START, DAY_END)

    assert gaps == [Gap(DAY_START, DAY_END)]


def test_back_to_back_meetings_produce_no_gap_between_them():
    busy = [BusyBlock(dt(10), dt(11)), BusyBlock(dt(11), dt(12))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [Gap(DAY_START, dt(10)), Gap(dt(12), DAY_END)]


def test_overlapping_meetings_are_merged():
    busy = [BusyBlock(dt(10), dt(12)), BusyBlock(dt(11), dt(13))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [Gap(DAY_START, dt(10)), Gap(dt(13), DAY_END)]


def test_gap_before_first_meeting_and_after_last_meeting():
    busy = [BusyBlock(dt(11), dt(16))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [Gap(DAY_START, dt(11)), Gap(dt(16), DAY_END)]


def test_short_gap_below_threshold_is_filtered_out():
    # 10-minute gap between the two meetings, threshold is 30 minutes.
    busy = [BusyBlock(dt(10), dt(12)), BusyBlock(dt(12, 10), dt(14))]

    gaps = find_gaps(busy, DAY_START, DAY_END, min_gap_minutes=30)

    assert gaps == [Gap(DAY_START, dt(10)), Gap(dt(14), DAY_END)]


def test_gap_exactly_at_threshold_is_kept():
    # Exactly a 30-minute gap, threshold is 30 minutes -> boundary is inclusive (>=, not >).
    busy = [BusyBlock(dt(10), dt(12)), BusyBlock(dt(12, 30), dt(14))]

    gaps = find_gaps(busy, DAY_START, DAY_END, min_gap_minutes=30)

    assert gaps == [Gap(DAY_START, dt(10)), Gap(dt(12), dt(12, 30)), Gap(dt(14), DAY_END)]


def test_naive_datetime_raises_value_error():
    naive_start = datetime(2026, 8, 10, 9, 0)  # no tzinfo

    with pytest.raises(ValueError):
        find_gaps([], naive_start, DAY_END)


def test_busy_period_covering_entire_day_leaves_no_gaps():
    busy = [BusyBlock(DAY_START, DAY_END)]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == []


def test_busy_period_outside_window_is_ignored():
    # A meeting the night before — entirely before day_start.
    busy = [BusyBlock(dt(3), dt(5))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [Gap(DAY_START, DAY_END)]


def test_busy_periods_extending_past_window_edges_are_clipped():
    # One meeting starts before day_start, another ends after day_end.
    busy = [BusyBlock(dt(6), dt(10)), BusyBlock(dt(16), dt(20))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [Gap(dt(10), dt(16))]


def test_multiple_separate_gaps_are_returned_in_chronological_order():
    busy = [BusyBlock(dt(10), dt(11)), BusyBlock(dt(13), dt(14)), BusyBlock(dt(16), dt(17))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [
        Gap(DAY_START, dt(10)),
        Gap(dt(11), dt(13)),
        Gap(dt(14), dt(16)),
        Gap(dt(17), DAY_END),
    ]


def test_unsorted_busy_periods_still_produce_correct_gaps():
    # Same meetings as the back-to-back test, but listed out of order.
    busy = [BusyBlock(dt(11), dt(12)), BusyBlock(dt(10), dt(11))]

    gaps = find_gaps(busy, DAY_START, DAY_END)

    assert gaps == [Gap(DAY_START, dt(10)), Gap(dt(12), DAY_END)]
