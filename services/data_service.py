from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from data.models import Indicator, SeriesResult, unavailable_indicator
from data.owid import country_rows, fetch_grapher
from data.world_bank import fetch_indicator, latest_value
from services.calculations import percent_to_people
from utils.constants import WORLD_BANK_INDICATORS


def _population_for_year(series: SeriesResult, year: int | None) -> float | None:
    if year is None or series.data.empty:
        return None
    exact = series.data[series.data["year"] == year]
    if exact.empty:
        return None
    return float(exact.iloc[-1]["value"])


def country_dashboard(code: str) -> dict[str, Indicator | SeriesResult]:
    """Monta indicadores nacionais mantendo ausências como ausências, nunca como zero."""
    consulted_at = datetime.now(timezone.utc)
    series: dict[str, SeriesResult] = {
        key: fetch_indicator(code, item["code"])
        for key, item in WORLD_BANK_INDICATORS.items()
    }
    indicators: dict[str, Indicator | SeriesResult] = {"series": series}

    for key, result in series.items():
        definition = WORLD_BANK_INDICATORS[key]
        value, year = latest_value(result)
        if value is None:
            indicators[key] = unavailable_indicator(
                key,
                definition["label"],
                result.source,
                result.source_url,
                definition["label"],
                consulted_at,
            )
            continue
        indicators[key] = Indicator(
            key=key,
            label=definition["label"],
            value=value,
            unit=definition["unit"],
            year=year,
            source=result.source,
            source_url=result.source_url,
            indicator=definition["label"],
            consulted_at=result.consulted_at,
            original_value=f"{value} {definition['unit']}",
            formula="Sem transformação.",
            note=("Série recuperada do último cache válido." if result.from_fallback else ""),
        )

    waste_result = fetch_grapher("food_waste")
    waste_rows = country_rows(waste_result, code)
    if waste_rows.empty:
        indicators["food_waste"] = unavailable_indicator(
            "food_waste",
            "Desperdício de alimentos",
            waste_result.source,
            waste_result.source_url,
            waste_result.indicator,
            consulted_at,
        )
    else:
        latest = waste_rows.iloc[-1]
        year = int(latest["year"])
        sector_columns = [
            column
            for column in ("Retail", "Out-of-home consumption", "Household")
            if column in waste_rows.columns
        ]
        per_capita = float(latest[sector_columns].sum())
        indicators["food_waste"] = Indicator(
            key="food_waste",
            label="Desperdício de alimentos por pessoa",
            value=per_capita,
            unit="kg/pessoa/ano",
            year=year,
            source=waste_result.source,
            source_url=waste_result.source_url,
            indicator=waste_result.indicator,
            consulted_at=waste_result.consulted_at,
            original_value=" + ".join(
                f"{column}: {float(latest[column]):.2f} kg" for column in sector_columns
            ),
            formula="varejo + alimentação fora do lar + domicílios",
            note="Estimativa nacional UNEP; alguns valores são extrapolados e têm diferentes níveis de confiança.",
        )
        population_same_year = _population_for_year(series["population"], year)
        total_tonnes = (
            per_capita * population_same_year / 1_000
            if population_same_year is not None
            else None
        )
        if total_tonnes is None:
            indicators["food_waste_total"] = unavailable_indicator(
                "food_waste_total",
                "Desperdício anual estimado",
                waste_result.source,
                waste_result.source_url,
                waste_result.indicator,
                consulted_at,
            )
        else:
            indicators["food_waste_total"] = Indicator(
                key="food_waste_total",
                label="Desperdício anual estimado",
                value=total_tonnes,
                unit="toneladas/ano",
                year=year,
                source=waste_result.source,
                source_url=waste_result.source_url,
                indicator="Desperdício per capita × população do mesmo ano",
                consulted_at=waste_result.consulted_at,
                original_value=(
                    f"{per_capita:.2f} kg/pessoa/ano × "
                    f"{population_same_year:.0f} pessoas"
                ),
                formula="kg por pessoa/ano × população ÷ 1.000 = toneladas/ano",
                note="Estimativa derivada; conserva as incertezas do valor per capita modelado pelo UNEP.",
            )
    if "food_waste_total" not in indicators:
        indicators["food_waste_total"] = unavailable_indicator(
            "food_waste_total",
            "Desperdício anual estimado",
            waste_result.source,
            waste_result.source_url,
            waste_result.indicator,
            consulted_at,
        )
    indicators["waste_series"] = waste_rows

    under = indicators["undernourishment"]
    if isinstance(under, Indicator) and under.available:
        population_same_year = _population_for_year(series["population"], int(under.year))
        indicators["undernourished_people"] = percent_to_people(
            under.value, population_same_year
        )
    else:
        indicators["undernourished_people"] = None
    return indicators


def production_by_category(code: str) -> tuple[pd.DataFrame, list[str]]:
    """Retorna séries de produção; não as confunde com perdas ou desperdício."""
    category_keys = {
        "beef_production": "Bovina e búfalo",
        "pork_production": "Suína",
        "poultry_production": "Frango/aves",
    }
    frames = []
    errors = []
    for dataset_key, category in category_keys.items():
        result = fetch_grapher(dataset_key)
        subset = country_rows(result, code)
        if subset.empty:
            if result.error:
                errors.append(result.error)
            continue
        value_columns = [
            column
            for column in subset.columns
            if column not in {"entity", "code", "year"}
        ]
        if not value_columns:
            continue
        part = subset[["year", value_columns[0]]].rename(
            columns={value_columns[0]: "value"}
        )
        part["category"] = category
        frames.append(part)
    if not frames:
        return pd.DataFrame(columns=["year", "value", "category"]), errors

    return pd.concat(frames, ignore_index=True), errors
