from __future__ import annotations

from datetime import datetime, timezone
from io import StringIO

import pandas as pd
import requests
import streamlit as st

from data.cache_store import load_json, save_json
from data.http_client import get
from data.models import SeriesResult
from utils.constants import CACHE_TTL_SECONDS, OWID_DATASETS, OWID_GRAPHS


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.rename(
        columns={"Entity": "entity", "Code": "code", "Year": "year"}
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_grapher(dataset_key: str) -> SeriesResult:
    """Baixa somente o CSV pequeno necessário da API Grapher documentada."""
    consulted_at = datetime.now(timezone.utc)
    slug = OWID_DATASETS[dataset_key]
    url = f"{OWID_GRAPHS}/{slug}.csv"
    error = None
    from_fallback = False

    try:
        response = get(
            url,
            params={
                "v": 1,
                "csvType": "full",
                "useColumnShortNames": "false",
            },
        )
        frame = _normalise_columns(pd.read_csv(StringIO(response.text)))
        save_json("owid", slug, frame.to_dict(orient="records"))
    except (requests.RequestException, ValueError, UnicodeError) as exc:
        records = load_json("owid", slug) or []
        frame = _normalise_columns(pd.DataFrame(records))
        error = f"Fonte temporariamente indisponível: {exc}"
        from_fallback = bool(records)

    labels = {
        "food_waste": "Desperdício de alimentos por pessoa e setor",
        "meat_production": "Produção de carne",
        "beef_production": "Produção de carne bovina e de búfalo",
        "pork_production": "Produção de carne suína",
        "poultry_production": "Produção de carne de aves",
        "food_loss_index": "Índice de perda de alimentos",
    }
    return SeriesResult(
        data=frame,
        source="Our World in Data (dados originais FAO/UNEP)",
        source_url=f"{OWID_GRAPHS}/{slug}",
        indicator=labels[dataset_key],
        consulted_at=consulted_at,
        error=error,
        from_fallback=from_fallback,
    )


def country_rows(result: SeriesResult, code: str) -> pd.DataFrame:
    if result.data.empty or "code" not in result.data.columns:
        return pd.DataFrame()
    return result.data[result.data["code"] == code].copy().sort_values("year")
