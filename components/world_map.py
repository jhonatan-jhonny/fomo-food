from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.cards import metric_card
from components.mobile_ui import section_intro
from services.world_map_data import (
    MAP_INDICATORS,
    build_map_frame,
    country_details,
)
from utils.formatting import format_compact_br, format_number_br

MAP_HEIGHT = 440


def _display_value(value: float | None, unit: str) -> str:
    if value is None or pd.isna(value):
        return "Sem dados"
    numeric = float(value)
    if unit in {"pessoas", "toneladas/ano"}:
        return f"{format_compact_br(numeric)} {unit}"
    if unit.startswith("%"):
        return f"{format_number_br(numeric, 1)}%"
    return f"{format_number_br(numeric, 1)} {unit}"


def build_choropleth(frame: pd.DataFrame, title: str) -> object:
    visual = frame.copy()
    visual["display_value"] = visual.apply(
        lambda row: _display_value(row["value"], row["unit"]), axis=1
    )
    visual["display_year"] = visual["year"].apply(
        lambda value: "Sem dados" if pd.isna(value) else str(int(value))
    )
    fig = px.choropleth(
        visual,
        locations="iso3",
        color="value",
        hover_name="country",
        projection="natural earth",
        color_continuous_scale=["#3a211f", "#ad3f2d", "#ff795b", "#ffd0c5"],
        title=title,
        custom_data=["display_value", "display_year", "source", "iso3"],
    )
    fig.update_traces(
        marker_line_color="rgba(255,255,255,.16)",
        marker_line_width=0.35,
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Valor: %{customdata[0]}<br>"
            "Ano: %{customdata[1]}<br>"
            "Fonte: %{customdata[2]}<extra></extra>"
        ),
        selected_marker_opacity=1,
        unselected_marker_opacity=0.72,
    )
    fig.update_geos(
        bgcolor="#101319",
        showframe=False,
        showcoastlines=False,
        showland=True,
        landcolor="#292e37",
        showocean=True,
        oceancolor="#0c0f14",
        showcountries=True,
        countrycolor="rgba(255,255,255,.10)",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101319",
        plot_bgcolor="#101319",
        font={"color": "#dfe3e8", "size": 12},
        height=MAP_HEIGHT,
        margin={"l": 0, "r": 0, "t": 52, "b": 0},
        dragmode=False,
        coloraxis_colorbar={
            "title": "",
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.02,
            "len": 0.58,
            "thickness": 9,
            "tickfont": {"size": 9},
        },
    )
    return fig


def _selected_location(event: object) -> str | None:
    try:
        points = event.selection.points
    except (AttributeError, KeyError, TypeError):
        try:
            points = event.get("selection", {}).get("points", [])
        except AttributeError:
            return None
    if not points:
        return None
    point = points[0]
    location = point.get("location")
    if location:
        return str(location)
    customdata = point.get("customdata") or []
    return str(customdata[3]) if len(customdata) > 3 else None


def _detail_card(label: str, detail: dict) -> None:
    value = detail.get("value")
    year = detail.get("year")
    source = detail.get("source", "Fonte não informada")
    unit = detail.get("unit", "")
    if value is None or pd.isna(value):
        metric_card(
            label,
            "Dado não disponível",
            note=f"Fonte: {source}. Ausência de dado não significa zero.",
        )
        return
    metric_card(
        label,
        _display_value(float(value), unit),
        f"ano: {int(year)}" if year is not None and not pd.isna(year) else "ano não informado",
        f"Fonte: {source}",
    )


def render_world_map() -> None:
    section_intro(
        "Mapa mundial",
        "Explore os indicadores",
        "Toque em um país no mapa ou use o seletor para abrir os detalhes.",
    )
    indicator_label = st.selectbox("Indicador do mapa", list(MAP_INDICATORS))
    normalize = st.toggle("Normalizar por população", value=False)
    indicator_key = MAP_INDICATORS[indicator_label]

    with st.spinner("Preparando dados mundiais…"):
        frame, metadata = build_map_frame(indicator_key, normalize)

    if frame.empty:
        st.warning(
            "Não foi possível carregar o catálogo de países agora. As demais páginas "
            "continuam disponíveis."
        )
        return
    if normalize and not metadata["normalization_applied"]:
        st.caption("Este indicador já está normalizado ou não admite nova normalização.")
    if frame["value"].notna().sum() == 0:
        st.warning("Fonte temporariamente indisponível para este indicador.")

    fig = build_choropleth(frame, metadata["title"])
    event = st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False, "responsive": True, "scrollZoom": False},
        on_select="rerun",
        selection_mode="points",
        key="world_choropleth",
    )
    st.caption("Quanto mais intensa a cor, maior o valor do indicador selecionado.")
    st.caption(
        "Os dados representam os períodos mais recentes disponíveis para cada país e "
        "podem ter anos de referência diferentes. Países em cinza estão sem dados."
    )

    errors = [message for message in metadata["errors"].values() if message]
    if errors:
        st.warning(
            "Uma ou mais fontes estão temporariamente indisponíveis. Os demais "
            "indicadores continuam ativos e, quando possível, usam o último cache válido."
        )

    clicked_iso = _selected_location(event)
    countries = frame[["iso3", "country"]].drop_duplicates().sort_values("country")
    name_by_iso = dict(zip(countries["iso3"], countries["country"], strict=False))
    if clicked_iso in name_by_iso and st.session_state.get("last_map_click") != clicked_iso:
        st.session_state["map_country_selector"] = name_by_iso[clicked_iso]
        st.session_state["last_map_click"] = clicked_iso

    country_names = countries["country"].tolist()
    if "map_country_selector" not in st.session_state:
        st.session_state["map_country_selector"] = (
            "Brazil" if "Brazil" in country_names else country_names[0]
        )

    st.subheader("Detalhes do país")
    selected_country = st.selectbox(
        "País",
        country_names,
        key="map_country_selector",
    )
    selected_iso = countries.loc[
        countries["country"] == selected_country, "iso3"
    ].iloc[0]
    details = country_details(str(selected_iso))

    _detail_card("População", details["population"])
    _detail_card("Desperdício total", details["waste_total"])
    _detail_card("Desperdício por habitante", details["waste_per_capita"])
    _detail_card("Pessoas subnutridas", details["undernourished_people"])
    _detail_card("Insegurança alimentar", details["food_insecurity"])
    _detail_card("Mortalidade associada à desnutrição", details["mortality"])
