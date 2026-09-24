from __future__ import annotations

import json
from datetime import datetime, timezone

import streamlit as st

from data.models import Indicator
from utils.constants import CACHE_TTL_SECONDS, SNAPSHOT_DIR


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def malnutrition_associated_deaths() -> Indicator:
    payload = json.loads(
        (SNAPSHOT_DIR / "official_global_indicators.json").read_text(encoding="utf-8")
    )["malnutrition_deaths"]
    return Indicator(
        key="malnutrition_deaths",
        label=payload["label"],
        value=float(payload["value"]),
        unit="mortes/ano",
        year=int(payload["reference_year"]),
        source=payload["source"],
        source_url=payload["source_url"],
        indicator=payload["indicator"],
        consulted_at=datetime.now(timezone.utc),
        original_value=payload["original_value"],
        formula="mortes anuais associadas ÷ 31.536.000 = média estimada por segundo",
        note=payload["note"],
    )

