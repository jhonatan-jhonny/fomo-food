from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from services.calculations import (
    estimate_feeding_potential,
    estimate_since_midnight,
    kg_to_tonnes,
    percent_to_people,
    rate_per_second,
    tonnes_to_kg,
)
from services.counters import counter_values, seconds_since_midnight
from utils.constants import APP_TIMEZONE, SECONDS_PER_YEAR
from utils.formatting import format_compact_br, format_number_br


def test_annual_rate_and_daily_estimate() -> None:
    annual = float(SECONDS_PER_YEAR)
    assert rate_per_second(annual) == 1.0
    assert estimate_since_midnight(annual, 3_600) == 3_600


def test_counter_uses_sao_paulo_midnight() -> None:
    now = datetime(2026, 9, 24, 12, 30, tzinfo=ZoneInfo(APP_TIMEZONE))
    assert seconds_since_midnight(now) == 45_000
    assert counter_values(float(SECONDS_PER_YEAR), now)["today"] == 45_000


def test_invalid_negative_values_are_rejected() -> None:
    with pytest.raises(ValueError):
        rate_per_second(-1)
    with pytest.raises(ValueError):
        estimate_since_midnight(1, -1)


def test_conversions_do_not_turn_missing_data_into_zero() -> None:
    assert percent_to_people(None, 100) is None
    assert percent_to_people(12.5, 1_000) == 125
    assert tonnes_to_kg(1.5) == 1_500
    assert kg_to_tonnes(1_500) == 1.5


def test_unep_conservative_meal_equivalence_matches_report_scale() -> None:
    result = estimate_feeding_potential(
        total_waste_kg=1_052_000_000_000,
        household_share=0.60,
        edible_share=0.25,
        meal_mass_kg=0.420,
        daily_kcal=2_100,
        meals_per_day=3,
    )
    assert result["edible_tonnes"] == pytest.approx(157_800_000)
    assert result["meals"] == pytest.approx(375_714_285_714.2857)
    assert result["person_days"] == pytest.approx(result["meals"] / 3)
    assert result["energy_density_kcal_kg"] == pytest.approx(1_666.6667, rel=1e-5)


def test_feeding_estimate_rejects_invalid_assumptions() -> None:
    with pytest.raises(ValueError):
        estimate_feeding_potential(-1, 0.6, 0.25, 0.42, 2_100, 3)
    with pytest.raises(ValueError):
        estimate_feeding_potential(1, 1.2, 0.25, 0.42, 2_100, 3)


def test_brazilian_number_formatting() -> None:
    assert format_number_br(1_284_392_392) == "1.284.392.392"
    assert format_compact_br(735_000_000) == "735 milhões"
    assert format_compact_br(1_800_000) == "1,8 milhão"
