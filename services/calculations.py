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


def kg_to_tonnes(kg: float) -> float:
    return kg / 1_000


def estimate_feeding_potential(
    total_waste_kg: float,
    household_share: float,
    edible_share: float,
    meal_mass_kg: float,
    daily_kcal: float,
    meals_per_day: int,
) -> dict[str, float]:
    """Converte massa em equivalências alimentares, sem alegar recuperabilidade real.

    A parcela comestível é aplicada somente à fração domiciliar, em linha com o
    cenário conservador apresentado pelo UNEP. A densidade energética é implícita:
    calorias diárias / refeições por dia / massa de uma refeição.
    """
    if total_waste_kg < 0:
        raise ValueError("A massa desperdiçada não pode ser negativa.")
    if not 0 <= household_share <= 1 or not 0 <= edible_share <= 1:
        raise ValueError("As participações devem estar entre zero e um.")
    if meal_mass_kg <= 0 or daily_kcal <= 0 or meals_per_day <= 0:
        raise ValueError("Massa, energia e refeições devem ser positivas.")

    household_waste_kg = total_waste_kg * household_share
    edible_kg = household_waste_kg * edible_share
    meals = edible_kg / meal_mass_kg
    kcal_per_meal = daily_kcal / meals_per_day
    energy_density_kcal_kg = kcal_per_meal / meal_mass_kg
    potential_kcal = edible_kg * energy_density_kcal_kg
    person_days = potential_kcal / daily_kcal
    return {
        "total_waste_tonnes": kg_to_tonnes(total_waste_kg),
        "household_waste_tonnes": kg_to_tonnes(household_waste_kg),
        "edible_tonnes": kg_to_tonnes(edible_kg),
        "meals": meals,
        "person_days": person_days,
        "potential_kcal": potential_kcal,
        "energy_density_kcal_kg": energy_density_kcal_kg,
        "kcal_per_meal": kcal_per_meal,
    }
