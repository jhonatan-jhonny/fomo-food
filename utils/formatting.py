from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from utils.constants import APP_TIMEZONE


def format_number_br(value: float | None, decimals: int = 0) -> str:
    if value is None:
        return "Dado não disponível"
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_compact_br(value: float | None) -> str:
    if value is None:
        return "Dado não disponível"
    absolute = abs(float(value))
    scales = (
        (1_000_000_000_000, "trilhão", "trilhões"),
        (1_000_000_000, "bilhão", "bilhões"),
        (1_000_000, "milhão", "milhões"),
        (1_000, "mil", "mil"),
    )
    for divisor, singular, plural in scales:
        if absolute >= divisor:
            scaled = value / divisor
            label = singular if abs(scaled) < 2 else plural
            decimals = 0 if abs(scaled) >= 100 else 1
            return f"{format_number_br(scaled, decimals)} {label}"
    return format_number_br(value, 0)


def format_date_br(value: datetime) -> str:
    return value.astimezone(ZoneInfo(APP_TIMEZONE)).strftime("%d/%m/%Y %H:%M")


def format_value(value: float | None, unit: str, compact: bool = True) -> str:
    if value is None:
        return "Dado não disponível"
    if unit == "%":
        return f"{format_number_br(value, 1)}%"
    number = format_compact_br(value) if compact else format_number_br(value, 0)
    return f"{number} {unit}".strip()
