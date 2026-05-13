"""Parses human-friendly schedule strings into APScheduler triggers.

Supported forms (all case-insensitive):

    "day at 7am"            → CronTrigger daily at 07:00
    "day at 7:30am"         → CronTrigger daily at 07:30
    "day at 23:00"          → CronTrigger daily at 23:00
    "monday at 9am"         → CronTrigger weekly Mon 09:00
    "every monday at 6pm"   → same (the leading 'every' is optional)
    "5 minutes"             → IntervalTrigger every 5 minutes
    "12 hours"              → IntervalTrigger every 12 hours
    "1 day"                 → IntervalTrigger every 1 day
    "0 7 * * *"             → CronTrigger from raw cron expression

All times are interpreted in the timezone from settings.timezone
(default: America/Lima).
"""
from __future__ import annotations

import re

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone

from server.config import settings


WEEKDAYS = {
    "monday": "mon",
    "tuesday": "tue",
    "wednesday": "wed",
    "thursday": "thu",
    "friday": "fri",
    "saturday": "sat",
    "sunday": "sun",
}

# "7am" → (7, 0). "7:30am" → (7, 30). "23:00" → (23, 0).
TIME_RE = re.compile(
    r"^(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<period>am|pm)?$",
    re.IGNORECASE,
)

# "5 minutes", "1 hour", "2 days"
INTERVAL_RE = re.compile(
    r"^(?P<n>\d+)\s+(?P<unit>minute|minutes|hour|hours|day|days)$",
    re.IGNORECASE,
)


def parse_trigger(expr: str):
    """Parse a schedule expression into an APScheduler trigger.

    Returns a CronTrigger or IntervalTrigger, both initialised with the
    configured timezone so 'day at 7am' means 7am local time.

    Raises ValueError if the expression cannot be parsed.
    """
    if not expr or not isinstance(expr, str):
        raise ValueError(f"Empty or non-string schedule: {expr!r}")

    tz = timezone(settings.timezone)
    expr = expr.strip().lower()

    # Strip leading 'every '
    if expr.startswith("every "):
        expr = expr[len("every "):]

    # 1. Try raw cron: "0 7 * * *" (5 fields)
    if len(expr.split()) == 5 and all(
        c in "0123456789*/,-" for c in expr.replace(" ", "")
    ):
        return CronTrigger.from_crontab(expr, timezone=tz)

    # 2. Try "day at HH" / "day at HHam" / "day at HH:MM"
    if expr.startswith("day at "):
        hour, minute = _parse_time(expr[len("day at "):])
        return CronTrigger(hour=hour, minute=minute, timezone=tz)

    # 3. Try "<weekday> at HH..."
    for long_name, short_name in WEEKDAYS.items():
        prefix = f"{long_name} at "
        if expr.startswith(prefix):
            hour, minute = _parse_time(expr[len(prefix):])
            return CronTrigger(
                day_of_week=short_name, hour=hour, minute=minute, timezone=tz
            )

    # 4. Try interval: "5 minutes", "1 hour", "2 days"
    m = INTERVAL_RE.match(expr)
    if m:
        n = int(m.group("n"))
        unit = m.group("unit").rstrip("s")
        kwargs = {f"{unit}s": n}
        return IntervalTrigger(**kwargs, timezone=tz)

    raise ValueError(f"Could not parse schedule expression: {expr!r}")


def _parse_time(time_str: str) -> tuple[int, int]:
    """Parse '7am', '7:30am', '23:00' → (hour, minute) in 24-hour form."""
    time_str = time_str.strip()
    m = TIME_RE.match(time_str)
    if not m:
        raise ValueError(f"Could not parse time: {time_str!r}")

    hour = int(m.group("hour"))
    minute = int(m.group("minute") or 0)
    period = (m.group("period") or "").lower()

    if period == "pm" and hour < 12:
        hour += 12
    elif period == "am" and hour == 12:
        hour = 0

    if not (0 <= hour <= 23):
        raise ValueError(f"Hour out of range: {hour}")
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute out of range: {minute}")

    return hour, minute
