from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BG = "#101319"
GRID = "rgba(255,255,255,.08)"
TEXT = "#dfe3e8"
ACCENT = "#ff6846"
GREEN = "#42c48a"


def _finish(fig: go.Figure, y_title: str = "") -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font={"color": TEXT, "size": 12},
        margin={"l": 12, "r": 12, "t": 48, "b": 18},
        height=390,
        legend={"orientation": "h", "y": -0.2, "title": ""},
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=GRID, title="")
    fig.update_yaxes(gridcolor=GRID, title=y_title)
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
        color_discrete_sequence=[ACCENT, GREEN, "#f3bd52", "#668dff", "#c478ff"],
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
        color_discrete_sequence=[ACCENT, "#f3bd52", GREEN, "#668dff"],
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
        color_continuous_scale=["#562d28", ACCENT],
    )
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    return _finish(fig, x_title)

