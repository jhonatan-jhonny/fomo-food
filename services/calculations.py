from __future__ import annotations

from utils.constants import SECONDS_PER_YEAR


def rate_per_second(annual_value: float) -> float:
    """Converte um fluxo anual em taxa média por segundo (ano de 365 dias)."""
    if annual_value < 0:
        raise ValueError("O valor anual não pode ser negativo.")
    return annual_value / SECONDS_PER_YEAR


def estimate_since_midnight(annual_value: float, elapsed_seconds: float) -> float:
    """Estima o acumulado diário sem sugerir medição evento a evento."""
    if elapsed_seconds < 0:
        raise ValueError("Os segundos decorridos não podem ser negativos.")
    return rate_per_second(annual_value) * min(elapsed_seconds, 86_400)


def percent_to_people(percent: float | None, population: float | None) -> float | None:
    if percent is None or population is None:
        return None
    return population * percent / 100


def tonnes_to_kg(tonnes: float) -> float:
    return tonnes * 1_000

