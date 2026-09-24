from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from data.models import Indicator
from utils.constants import CACHE_TTL_SECONDS, SNAPSHOT_DIR


def _snapshot_indicator(
    key: str, formula: str = "Sem transformação; estimativa publicada pela fonte."
) -> Indicator:
    payload = json.loads(
        (SNAPSHOT_DIR / "official_global_indicators.json").read_text(encoding="utf-8")
    )[key]
    return Indicator(
        key=key,
        label=payload["label"],
        value=float(payload["value"]),
        unit=payload["unit"],
        year=payload["reference_year"],
        source=payload["source"],
        source_url=payload["source_url"],
        indicator=payload["indicator"],
        consulted_at=datetime.now(timezone.utc),
        original_value=payload["original_value"],
        formula=formula,
        note=payload["note"],
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def protein_energy_malnutrition_deaths() -> Indicator:
    return _snapshot_indicator(
        "protein_energy_malnutrition_deaths",
        "total anual estimado ÷ 31.536.000 = taxa média por segundo; taxa × segundos desde 00:00 = estimativa de hoje",
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def malnutrition_associated_deaths() -> Indicator:
    return _snapshot_indicator(
        "malnutrition_deaths",
        "mortes anuais associadas ÷ 31.536.000 = média estatística por segundo",
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def child_nutrition_indicators() -> tuple[Indicator, ...]:
    return tuple(
        _snapshot_indicator(key)
        for key in (
            "child_stunting",
            "child_wasting",
            "child_severe_wasting",
            "child_minimum_dietary_diversity",
        )
    )
