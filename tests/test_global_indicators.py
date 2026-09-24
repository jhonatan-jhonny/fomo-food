from __future__ import annotations

import json

from utils.constants import SNAPSHOT_DIR


def _snapshot() -> dict:
    return json.loads(
        (SNAPSHOT_DIR / "official_global_indicators.json").read_text(encoding="utf-8")
    )


def test_general_hunger_indicators_preserve_population_and_year() -> None:
    data = _snapshot()

    assert data["undernourishment"]["value"] == 645_000_000
    assert data["undernourishment"]["reference_year"] == 2025
    assert data["food_insecurity"]["value"] == 2_100_000_000
    assert data["healthy_diet_unaffordable"]["value"] == 2_690_000_000


def test_wasting_total_includes_severe_wasting_subset() -> None:
    data = _snapshot()
    wasting = data["child_wasting"]
    severe = data["child_severe_wasting"]

    assert wasting["reference_year"] == severe["reference_year"] == 2024
    assert wasting["value"] > severe["value"]
    assert "subconjunto" in severe["note"]


def test_mortality_indicator_is_all_ages_and_cause_specific() -> None:
    indicator = _snapshot()["protein_energy_malnutrition_deaths"]

    assert indicator["reference_year"] == 2021
    assert indicator["value"] == 196_555
    assert "all ages" in indicator["indicator"]
    assert "causa" in indicator["note"].lower()


def test_every_new_nutrition_indicator_has_auditable_metadata() -> None:
    data = _snapshot()
    keys = (
        "healthy_diet_unaffordable",
        "protein_energy_malnutrition_deaths",
        "malnutrition_deaths",
        "child_stunting",
        "child_wasting",
        "child_severe_wasting",
        "child_minimum_dietary_diversity",
    )

    for key in keys:
        assert data[key]["unit"]
        assert data[key]["reference_year"]
        assert data[key]["source"]
        assert data[key]["source_url"].startswith("https://")
        assert data[key]["indicator"]
