from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BG = "rgba(0,0,0,0)"
GRID = "rgba(185,205,232,.09)"
TEXT = "#DCE4EE"
MUTED = "#9EABBC"
ACCENT = "#8FB7FF"
CYAN = "#7ED7D1"
LILAC = "#B7A7FF"
ALERT = "#FF8E7A"


def _finish(fig: go.Figure, y_title: str = "") -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font={"color": TEXT, "size": 12, "family": "Inter, Segoe UI, sans-serif"},
        margin={"l": 12, "r": 12, "t": 48, "b": 18},
        height=390,
        legend={"orientation": "h", "y": -0.2, "title": "", "font": {"color": MUTED}},
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=GRID, title="", linecolor="rgba(255,255,255,.08)")
    fig.update_yaxes(gridcolor=GRID, title=y_title, linecolor="rgba(255,255,255,.08)")
    return fig


def line_chart(frame: pd.DataFrame, title: str, y_title: str, color: str = ACCENT) -> go.Figure:
    fig = px.line(frame, x="year", y="value", markers=True, title=title)
    fig.update_traces(line={"color": color, "width": 3}, marker={"size": 7})
    return _finish(fig, y_title)


def multi_line_chart(
    frame: pd.DataFrame,
    title: str,
    y_title: str,
    color_column: str = "entity",
) -> go.Figure:
    fig = px.line(
        frame,
        x="year",
        y="value",
        color=color_column,
        markers=True,
        title=title,
        color_discrete_sequence=[ACCENT, CYAN, LILAC, ALERT, "#6E8FC6"],
    )
    fig.update_traces(line={"width": 2.5})
    return _finish(fig, y_title)


def grouped_bar(
    frame: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    y_title: str,
) -> go.Figure:
    fig = px.bar(
        frame,
        x=x,
        y=y,
        color=color,
        barmode="group",
        title=title,
        color_discrete_sequence=[ACCENT, CYAN, LILAC, ALERT],
    )
    return _finish(fig, y_title)


def horizontal_bar(frame: pd.DataFrame, title: str, x_title: str) -> go.Figure:
    ordered = frame.sort_values("value")
    fig = px.bar(
        ordered,
        x="value",
        y="entity",
        orientation="h",
        title=title,
        color="value",
        color_continuous_scale=["#172235", "#355986", ACCENT, "#DCE8FF"],
    )
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    return _finish(fig, x_title)
