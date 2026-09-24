from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st

from data.cache_store import load_json, save_json
from data.http_client import get
from data.models import SeriesResult
from utils.constants import (
    CACHE_TTL_SECONDS,
    WORLD_BANK_API,
    WORLD_BANK_DOCS,
    WORLD_BANK_INDICATORS,
)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_indicator(
    country_code: str,
    indicator_code: str,
    start_year: int = 2000,
    end_year: int = 2026,
) -> SeriesResult:
    """Busca uma série na API v2 oficial e recorre ao último cache em disco."""
    consulted_at = datetime.now(timezone.utc)
    cache_key = f"{country_code}-{indicator_code}-{start_year}-{end_year}"
    url = f"{WORLD_BANK_API}/country/{country_code}/indicator/{indicator_code}"
    from_fallback = False
    error = None

    try:
        payload = get(
            url,
            params={
                "format": "json",
                "date": f"{start_year}:{end_year}",
                "per_page": 100,
                "source": 2,
            },
        ).json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError("Formato inesperado retornado pela API do Banco Mundial.")
        rows = payload[1] or []
        save_json("world-bank", cache_key, rows)
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        rows = load_json("world-bank", cache_key) or []
        from_fallback = bool(rows)
        error = f"Fonte temporariamente indisponível: {exc}"

    records = [
        {
            "year": int(row["date"]),
            "value": float(row["value"]),
            "country": row.get("country", {}).get("value", country_code),
        }
        for row in rows
        if row.get("value") is not None and str(row.get("date", "")).isdigit()
    ]
    frame = pd.DataFrame(records, columns=["year", "value", "country"])
    if not frame.empty:
        frame = frame.sort_values("year").reset_index(drop=True)

    definition = next(
        (
            item
            for item in WORLD_BANK_INDICATORS.values()
            if item["code"] == indicator_code
        ),
        {"label": indicator_code, "provider": "Banco Mundial"},
    )
    return SeriesResult(
        data=frame,
        source=definition["provider"],
        source_url=WORLD_BANK_DOCS,
        indicator=definition["label"],
        consulted_at=consulted_at,
        error=error,
        from_fallback=from_fallback,
    )


def latest_value(result: SeriesResult) -> tuple[float | None, int | None]:
    if result.data.empty:
        return None, None
    row = result.data.iloc[-1]
    return float(row["value"]), int(row["year"])
