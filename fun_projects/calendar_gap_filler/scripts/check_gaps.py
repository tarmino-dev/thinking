"""Manual check: print free time slots in your Google Calendar for the next
few days.

This is not an automated test — it's a script you run by hand to eyeball
that calendar_module.client and calendar_module.gaps work together
correctly against your real calendar. Run it from the project root:

    PYTHONPATH=. python3 scripts/check_gaps.py
"""

from datetime import datetime, timedelta

from calendar_module.client import get_busy_periods
from calendar_module.gaps import find_gaps
from profile_module.profile import load_profile

DAYS_AHEAD = 7


def main() -> None:
    profile = load_profile()

    today = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)

    first_day_start = today.replace(hour=profile.waking_hours_start)
    last_day_end = (today + timedelta(days=DAYS_AHEAD)).replace(hour=profile.waking_hours_end)

    # One API call for the whole window — find_gaps() below already clips
    # busy periods to each day's own start/end, so we don't need to fetch
    # per day.
    busy_periods = get_busy_periods(first_day_start, last_day_end)

    for day_offset in range(DAYS_AHEAD + 1):
        day = today + timedelta(days=day_offset)
        day_start = day.replace(hour=profile.waking_hours_start)
        day_end = day.replace(hour=profile.waking_hours_end)

        for gap in find_gaps(busy_periods, day_start, day_end):
            print(f"{gap.start:%d.%m %H:%M}–{gap.end:%H:%M}")


if __name__ == "__main__":
    main()
