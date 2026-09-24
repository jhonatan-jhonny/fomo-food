from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from data.models import Indicator, SeriesResult
from utils.constants import CACHE_TTL_SECONDS, SNAPSHOT_DIR


def _global_indicator(key: str) -> Indicator:
    payload = json.loads(
        (SNAPSHOT_DIR / "official_global_indicators.json").read_text(encoding="utf-8")
    )[key]
    return Indicator(
        key=key,
        label=payload["label"],
        value=float(payload["value"]),
        unit=payload["unit"],
        year=int(payload["reference_year"]),
        source=payload["source"],
        source_url=payload["source_url"],
        indicator=payload["indicator"],
        consulted_at=datetime.now(timezone.utc),
        original_value=payload["original_value"],
        formula="Sem transformação; estimativa central publicada pela fonte.",
        note=payload["note"],
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def global_undernourishment() -> Indicator:
    return _global_indicator("undernourishment")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def global_food_insecurity() -> Indicator:
    return _global_indicator("food_insecurity")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def global_healthy_diet_unaffordable() -> Indicator:
    return _global_indicator("healthy_diet_unaffordable")


@st.cache_data(show_spinner=False)
def load_official_csv(path: str, value_column: str) -> SeriesResult:
    """Adaptador para novos downloads oficiais FAOSTAT quando não houver API adequada."""
    consulted_at = datetime.now(timezone.utc)
    try:
        frame = pd.read_csv(Path(path), usecols=["Area", "Year", value_column])
        frame = frame.rename(
            columns={"Area": "entity", "Year": "year", value_column: "value"}
        )
        error = None
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        frame = pd.DataFrame(columns=["entity", "year", "value"])
        error = f"Arquivo oficial indisponível ou incompatível: {exc}"
    return SeriesResult(
        data=frame,
        source="FAOSTAT — arquivo oficial fornecido localmente",
        source_url="https://www.fao.org/faostat/en/#data",
        indicator=value_column,
        consulted_at=consulted_at,
        error=error,
    )
