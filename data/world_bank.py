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


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_global_indicators(
    indicator_codes: tuple[str, ...],
    start_year: int = 2015,
    end_year: int = 2026,
) -> SeriesResult:
    """Busca vários indicadores mundiais em uma única chamada documentada."""
    consulted_at = datetime.now(timezone.utc)
    joined_codes = ";".join(indicator_codes)
    cache_key = f"global-{joined_codes}-{start_year}-{end_year}"
    url = f"{WORLD_BANK_API}/country/all/indicator/{joined_codes}"
    from_fallback = False
    error = None

    try:
        payload = get(
            url,
            params={
                "format": "json",
                "date": f"{start_year}:{end_year}",
                "per_page": 20_000,
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
            "iso3": row.get("countryiso3code"),
            "country": row.get("country", {}).get("value", ""),
            "indicator": row.get("indicator", {}).get("id", ""),
            "year": int(row["date"]),
            "value": float(row["value"]),
        }
        for row in rows
        if row.get("value") is not None and str(row.get("date", "")).isdigit()
    ]
    frame = pd.DataFrame(
        records, columns=["iso3", "country", "indicator", "year", "value"]
    )
    return SeriesResult(
        data=frame,
        source="Banco Mundial WDI (inclui indicadores originais da FAO)",
        source_url=WORLD_BANK_DOCS,
        indicator=joined_codes,
        consulted_at=consulted_at,
        error=error,
        from_fallback=from_fallback,
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_country_catalog() -> SeriesResult:
    """Obtém o catálogo oficial usado para separar países de agregados regionais."""
    consulted_at = datetime.now(timezone.utc)
    cache_key = "country-catalog"
    url = f"{WORLD_BANK_API}/country"
    from_fallback = False
    error = None
    try:
        payload = get(url, params={"format": "json", "per_page": 400}).json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError("Catálogo de países em formato inesperado.")
        rows = payload[1] or []
        save_json("world-bank", cache_key, rows)
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        rows = load_json("world-bank", cache_key) or []
        from_fallback = bool(rows)
        error = f"Fonte temporariamente indisponível: {exc}"

    records = [
        {"iso3": row.get("id"), "country": row.get("name", "")}
        for row in rows
        if row.get("region", {}).get("id") != "NA"
        and len(str(row.get("id", ""))) == 3
    ]
    return SeriesResult(
        data=pd.DataFrame(records, columns=["iso3", "country"]),
        source="Banco Mundial — catálogo de países",
        source_url=WORLD_BANK_DOCS,
        indicator="Países e códigos ISO-3",
        consulted_at=consulted_at,
        error=error,
        from_fallback=from_fallback,
    )
