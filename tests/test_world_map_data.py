import pandas as pd
import pytest

from services import world_map_data


@pytest.fixture
def sample_world_data() -> dict[str, object]:
    return {
        "catalog": pd.DataFrame(
            [
                {"iso3": "BRA", "country": "Brazil"},
                {"iso3": "USA", "country": "United States"},
            ]
        ),
        "population": pd.DataFrame(
            [
                {
                    "iso3": "BRA",
                    "population": 212_000_000,
                    "population_year": 2025,
                }
            ]
        ),
        "waste": pd.DataFrame(
            [
                {
                    "iso3": "BRA",
                    "year": 2022,
                    "waste_total": 30_000_000,
                    "waste_per_capita": 144.5,
                }
            ]
        ),
        "undernourishment": pd.DataFrame(
            [
                {
                    "iso3": "BRA",
                    "year": 2023,
                    "undernourished_people": 5_200_000,
                    "undernourishment_pct": 2.5,
                }
            ]
        ),
        "food_insecurity": pd.DataFrame(
            [
                {"iso3": "BRA", "year": 2023, "food_insecurity_pct": 13.5}
            ]
        ),
        "errors": {"catalog": None, "world_bank": None, "waste": None},
    }


def test_missing_map_values_remain_missing(monkeypatch, sample_world_data) -> None:
    monkeypatch.setattr(world_map_data, "load_world_data", lambda: sample_world_data)
    frame, _ = world_map_data.build_map_frame("waste_total", normalize=False)
    usa = frame[frame["iso3"] == "USA"].iloc[0]
    assert pd.isna(usa["value"])
    assert usa["value"] != 0


def test_population_normalization_uses_valid_existing_indicator(
    monkeypatch, sample_world_data
) -> None:
    monkeypatch.setattr(world_map_data, "load_world_data", lambda: sample_world_data)
    waste, waste_meta = world_map_data.build_map_frame("waste_total", normalize=True)
    hunger, hunger_meta = world_map_data.build_map_frame(
        "undernourished_people", normalize=True
    )
    assert waste_meta["unit"] == "kg/pessoa/ano"
    assert waste.loc[waste["iso3"] == "BRA", "value"].iloc[0] == 144.5
    assert hunger_meta["unit"] == "% da população"
    assert hunger.loc[hunger["iso3"] == "BRA", "value"].iloc[0] == 2.5


def test_country_details_keep_each_indicator_year(
    monkeypatch, sample_world_data
) -> None:
    monkeypatch.setattr(world_map_data, "load_world_data", lambda: sample_world_data)
    details = world_map_data.country_details("BRA")
    assert details["population"]["year"] == 2025
    assert details["waste_total"]["year"] == 2022
    assert details["undernourished_people"]["year"] == 2023
    assert details["mortality"]["value"] is None
