from __future__ import annotations

import pandas as pd
import streamlit as st

from data.owid import fetch_grapher
from data.world_bank import fetch_country_catalog, fetch_global_indicators
from utils.constants import CACHE_TTL_SECONDS, WORLD_BANK_INDICATORS

POPULATION_CODE = WORLD_BANK_INDICATORS["population"]["code"]
UNDERNOURISHMENT_CODE = WORLD_BANK_INDICATORS["undernourishment"]["code"]
FOOD_INSECURITY_CODE = WORLD_BANK_INDICATORS["food_insecurity"]["code"]

MAP_INDICATORS = {
    "Desperdício total de alimentos — toneladas/ano": "waste_total",
    "Desperdício por habitante — kg/pessoa/ano": "waste_per_capita",
    "População subnutrida": "undernourished_people",
    "Insegurança alimentar": "food_insecurity",
}


def _latest(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    return (
        frame.dropna(subset=["value"])
        .sort_values(["iso3", "year"])
        .groupby("iso3", as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )


def _indicator_rows(frame: pd.DataFrame, code: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["iso3", "country", "year", "value"])
    return frame[frame["indicator"] == code][
        ["iso3", "country", "year", "value"]
    ].copy()


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_world_data() -> dict[str, object]:
    """Carrega e harmoniza fontes independentes sem transformar ausências em zero."""
    catalog_result = fetch_country_catalog()
    wb_result = fetch_global_indicators(
        (POPULATION_CODE, UNDERNOURISHMENT_CODE, FOOD_INSECURITY_CODE)
    )
    waste_result = fetch_grapher("food_waste")

    catalog = catalog_result.data.copy()
    waste = waste_result.data.copy()
    wb = wb_result.data.copy()
    if not waste.empty:
        waste = waste.rename(columns={"code": "iso3", "entity": "country"})
        waste = waste[waste["iso3"].astype(str).str.fullmatch(r"[A-Z]{3}", na=False)]
        waste_names = waste[["iso3", "country"]].drop_duplicates("iso3")
        catalog = pd.concat([catalog, waste_names], ignore_index=True)
    if not wb.empty:
        wb_names = wb[["iso3", "country"]].drop_duplicates("iso3")
        wb_names = wb_names[
            wb_names["iso3"].astype(str).str.fullmatch(r"[A-Z]{3}", na=False)
        ]
        catalog = pd.concat([catalog, wb_names], ignore_index=True)
    catalog = catalog.drop_duplicates("iso3").sort_values("country").reset_index(drop=True)

    population_all = _indicator_rows(wb, POPULATION_CODE)
    population_latest = _latest(population_all).rename(
        columns={"value": "population", "year": "population_year"}
    )

    if waste.empty:
        waste_latest = pd.DataFrame(
            columns=["iso3", "country", "year", "waste_per_capita"]
        )
    else:
        sector_columns = [
            column
            for column in ("Retail", "Out-of-home consumption", "Household")
            if column in waste.columns
        ]
        waste["waste_per_capita"] = waste[sector_columns].sum(
            axis=1, min_count=len(sector_columns)
        )
        waste_latest = (
            waste.dropna(subset=["waste_per_capita"])
            .sort_values(["iso3", "year"])
            .groupby("iso3", as_index=False)
            .tail(1)[["iso3", "country", "year", "waste_per_capita"]]
        )
        population_for_waste = population_all.rename(
            columns={"value": "population_for_waste"}
        )[["iso3", "year", "population_for_waste"]]
        waste_latest = waste_latest.merge(
            population_for_waste, on=["iso3", "year"], how="left"
        )
        waste_latest["waste_total"] = (
            waste_latest["waste_per_capita"]
            * waste_latest["population_for_waste"]
            / 1_000
        )

    under_prevalence = _latest(
        _indicator_rows(wb, UNDERNOURISHMENT_CODE)
    ).rename(columns={"value": "undernourishment_pct"})
    if not under_prevalence.empty:
        population_for_under = population_all.rename(
            columns={"value": "population_for_under"}
        )[["iso3", "year", "population_for_under"]]
        under_prevalence = under_prevalence.merge(
            population_for_under, on=["iso3", "year"], how="left"
        )
        under_prevalence["undernourished_people"] = (
            under_prevalence["undernourishment_pct"]
            * under_prevalence["population_for_under"]
            / 100
        )

    food_insecurity = _latest(
        _indicator_rows(wb, FOOD_INSECURITY_CODE)
    ).rename(columns={"value": "food_insecurity_pct"})

    return {
        "catalog": catalog,
        "population": population_latest,
        "waste": waste_latest,
        "undernourishment": under_prevalence,
        "food_insecurity": food_insecurity,
        "errors": {
            "catalog": catalog_result.error,
            "world_bank": wb_result.error,
            "waste": waste_result.error,
        },
    }


def build_map_frame(indicator_key: str, normalize: bool) -> tuple[pd.DataFrame, dict]:
    data = load_world_data()
    catalog = data["catalog"].copy()
    config = {
        "waste_total": {
            "table": "waste",
            "column": "waste_total",
            "unit": "toneladas/ano",
            "source": "UNEP 2024, processado por OWID; população do Banco Mundial",
            "normalized_key": "waste_per_capita",
            "title": "Desperdício total de alimentos",
        },
        "waste_per_capita": {
            "table": "waste",
            "column": "waste_per_capita",
            "unit": "kg/pessoa/ano",
            "source": "UNEP 2024, processado por Our World in Data",
            "normalized_key": None,
            "title": "Desperdício por habitante",
        },
        "undernourished_people": {
            "table": "undernourishment",
            "column": "undernourished_people",
            "unit": "pessoas",
            "source": "FAO via Banco Mundial",
            "normalized_key": "undernourishment_pct",
            "title": "População subnutrida",
        },
        "undernourishment_pct": {
            "table": "undernourishment",
            "column": "undernourishment_pct",
            "unit": "% da população",
            "source": "FAO via Banco Mundial",
            "normalized_key": None,
            "title": "Prevalência de subnutrição",
        },
        "food_insecurity": {
            "table": "food_insecurity",
            "column": "food_insecurity_pct",
            "unit": "% da população",
            "source": "FAO via Banco Mundial",
            "normalized_key": None,
            "title": "Insegurança alimentar moderada ou grave",
        },
    }
    selected_key = config[indicator_key].get("normalized_key") if normalize else None
    effective_key = selected_key or indicator_key
    selected = config[effective_key]
    source_frame = data[selected["table"]].copy()
    year_column = "year"
    columns = ["iso3", year_column, selected["column"]]
    source_frame = source_frame[columns].rename(
        columns={year_column: "year", selected["column"]: "value"}
    )
    frame = catalog.merge(source_frame, on="iso3", how="left")
    frame["unit"] = selected["unit"]
    frame["source"] = selected["source"]
    metadata = {
        **selected,
        "effective_key": effective_key,
        "normalization_applied": effective_key != indicator_key,
        "errors": data["errors"],
    }
    return frame, metadata


def country_details(iso3: str) -> dict[str, dict]:
    data = load_world_data()

    def row_for(table_name: str) -> pd.Series | None:
        frame = data[table_name]
        match = frame[frame["iso3"] == iso3]
        return None if match.empty else match.iloc[-1]

    population = row_for("population")
    waste = row_for("waste")
    under = row_for("undernourishment")
    insecurity = row_for("food_insecurity")
    return {
        "population": {
            "value": None if population is None else population.get("population"),
            "unit": "pessoas",
            "year": None if population is None else population.get("population_year"),
            "source": "Banco Mundial",
        },
        "waste_total": {
            "value": None if waste is None else waste.get("waste_total"),
            "unit": "toneladas/ano",
            "year": None if waste is None else waste.get("year"),
            "source": "UNEP 2024 / OWID + população do Banco Mundial",
        },
        "waste_per_capita": {
            "value": None if waste is None else waste.get("waste_per_capita"),
            "unit": "kg/pessoa/ano",
            "year": None if waste is None else waste.get("year"),
            "source": "UNEP 2024, processado por OWID",
        },
        "undernourished_people": {
            "value": None if under is None else under.get("undernourished_people"),
            "unit": "pessoas",
            "year": None if under is None else under.get("year"),
            "source": "FAO via Banco Mundial",
        },
        "food_insecurity": {
            "value": None if insecurity is None else insecurity.get("food_insecurity_pct"),
            "unit": "% da população",
            "year": None if insecurity is None else insecurity.get("year"),
            "source": "FAO via Banco Mundial",
        },
        "mortality": {
            "value": None,
            "unit": "",
            "year": None,
            "source": "OMS — sem série nacional comparável integrada",
        },
    }
