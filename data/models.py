from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class Indicator:
    """Um valor publicado e todos os metadados necessários para auditá-lo."""

    key: str
    label: str
    value: float | None
    unit: str
    year: int | str | None
    source: str
    source_url: str
    indicator: str
    consulted_at: datetime
    original_value: str = ""
    formula: str = "Sem transformação."
    note: str = ""
    available: bool = True


@dataclass
class SeriesResult:
    """Série temporal que pode falhar sem derrubar o restante da aplicação."""

    data: pd.DataFrame
    source: str
    source_url: str
    indicator: str
    consulted_at: datetime
    error: str | None = None
    from_fallback: bool = False

    @property
    def available(self) -> bool:
        return not self.data.empty


def unavailable_indicator(
    key: str,
    label: str,
    source: str,
    source_url: str,
    indicator: str,
    consulted_at: datetime,
    note: str = "Dado não disponível para este país/período.",
) -> Indicator:
    return Indicator(
        key=key,
        label=label,
        value=None,
        unit="",
        year=None,
        source=source,
        source_url=source_url,
        indicator=indicator,
        consulted_at=consulted_at,
        note=note,
        available=False,
    )
