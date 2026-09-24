from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from services.calculations import estimate_since_midnight, rate_per_second
from utils.constants import APP_TIMEZONE


def seconds_since_midnight(now: datetime | None = None) -> float:
    zone = ZoneInfo(APP_TIMEZONE)
    current = now.astimezone(zone) if now else datetime.now(zone)
    midnight = current.replace(hour=0, minute=0, second=0, microsecond=0)
    return (current - midnight).total_seconds()


def counter_values(annual_value: float, now: datetime | None = None) -> dict[str, float]:
    elapsed = seconds_since_midnight(now)
    return {
        "today": estimate_since_midnight(annual_value, elapsed),
        "per_second": rate_per_second(annual_value),
        "elapsed_seconds": elapsed,
    }

