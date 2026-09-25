"""Pure gap-finding logic for the Calendar Module.

No network calls here — this file only works with plain data (BusyBlock in,
Gap out), which is what makes it trivial to unit test without touching the
real Google Calendar API.
"""

from dataclasses import dataclass
from datetime import datetime

from .client import BusyBlock


@dataclass
class Gap:
    """A free time slot, long enough to potentially fit a suggested event."""

    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60


def find_gaps(
    busy_periods: list[BusyBlock],
    day_start: datetime,
    day_end: datetime,
    min_gap_minutes: int = 30,
) -> list[Gap]:
    """Find free time slots between day_start and day_end that aren't
    covered by any of the given busy_periods.

    Overlapping or back-to-back busy periods are merged first, so two
    meetings that touch at the edges don't produce a zero-length "gap"
    between them. Gaps shorter than min_gap_minutes are dropped — a 5-minute
    gap isn't useful for suggesting an event.
    """
    if day_start.tzinfo is None or day_end.tzinfo is None:
        raise ValueError("day_start and day_end must be timezone-aware")

    merged_busy = _merge_overlapping(busy_periods)

    gaps = []
    cursor = day_start

    for busy in merged_busy:
        if busy.end <= day_start or busy.start >= day_end:
            continue  # entirely outside the window we care about

        gap_end = min(busy.start, day_end)
        if gap_end > cursor:
            gaps.append(Gap(start=cursor, end=gap_end))

        cursor = max(cursor, busy.end)

    if cursor < day_end:
        gaps.append(Gap(start=cursor, end=day_end))

    return [gap for gap in gaps if gap.duration_minutes >= min_gap_minutes]


def _merge_overlapping(busy_periods: list[BusyBlock]) -> list[BusyBlock]:
    """Sort busy periods by start time and merge any that overlap or touch,
    so find_gaps never has to reason about overlaps itself.
    """
    if not busy_periods:
        return []

    sorted_periods = sorted(busy_periods, key=lambda b: b.start)
    merged = [sorted_periods[0]]

    for current in sorted_periods[1:]:
        last = merged[-1]
        if current.start <= last.end:
            merged[-1] = BusyBlock(start=last.start, end=max(last.end, current.end))
        else:
            merged.append(current)

    return merged
