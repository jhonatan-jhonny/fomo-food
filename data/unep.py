from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from data.models import Indicator
from utils.constants import CACHE_TTL_SECONDS, SNAPSHOT_DIR


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def global_food_waste() -> Indicator:
    """Lê um recorte versionado dos principais resultados do UNEP 2024."""
    payload = json.loads(
        (SNAPSHOT_DIR / "official_global_indicators.json").read_text(encoding="utf-8")
    )["food_waste"]
    tonnes = float(payload["value_tonnes"])
    return Indicator(
        key="global_food_waste",
        label="Alimentos desperdiçados",
        value=tonnes * 1_000,
        unit="kg/ano",
        year=int(payload["reference_year"]),
        source=payload["source"],
        source_url=payload["source_url"],
        indicator=payload["indicator"],
        consulted_at=datetime.now(timezone.utc),
        original_value=f"{tonnes:,.0f} toneladas/ano",
        formula=(
            "toneladas × 1.000 = kg (cálculo interno); toneladas ÷ 31.536.000 "
            "= taxa média em toneladas/s"
        ),
        note=payload["note"],
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def environmental_facts() -> dict:
    payload = json.loads(
        (SNAPSHOT_DIR / "official_global_indicators.json").read_text(encoding="utf-8")
    )
    return payload["environment"]
