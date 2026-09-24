from __future__ import annotations

from html import escape

import streamlit as st

from data.models import Indicator
from utils.formatting import format_date_br


def metric_card(
    label: str,
    value: str,
    unit: str = "",
    note: str = "",
    variant: str = "",
) -> None:
    safe_variant = variant if variant in {"primary", "positive"} else ""
    unavailable = value == "Dado não disponível"
    value_class = "card-value unavailable" if unavailable else "card-value"
    st.markdown(
        f"""
        <div class="data-card {safe_variant}">
          <div class="card-label">{escape(label)}</div>
          <div class="{value_class}">{escape(value)}</div>
          {f'<div class="card-unit">{escape(unit)}</div>' if unit else ''}
          {f'<div class="card-note">{escape(note)}</div>' if note else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def calculation_details(indicator: Indicator, title: str = "Como este número foi calculado?") -> None:
    with st.expander(title):
        st.markdown(
            f"""
**Fonte:** [{indicator.source}]({indicator.source_url})  
**Indicador:** {indicator.indicator}  
**Período do dado:** {indicator.year or 'não informado'}  
**Valor original:** {indicator.original_value or 'não informado'}  
**Fórmula:** {indicator.formula}  
**Consulta:** {format_date_br(indicator.consulted_at)}  

{indicator.note}
            """
        )


def availability_notice(message: str = "Dado não disponível para este país/período.") -> None:
    st.info(message, icon="ℹ️")


def source_status(name: str, period: str, consulted: str, fallback: bool = False) -> None:
    suffix = " · último cache válido" if fallback else ""
    st.markdown(
        f"""
        <div class="source-status">
          <strong>{escape(name)}</strong><br>
          Último período disponível: {escape(period)}<br>
          Consultado em: {escape(consulted + suffix)}
        </div>
        """,
        unsafe_allow_html=True,
    )
