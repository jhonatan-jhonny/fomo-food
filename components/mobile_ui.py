from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp { background:
            radial-gradient(circle at 80% 0%, rgba(255,104,70,.10), transparent 28rem),
            #090b0f;
        }
        .block-container {
            max-width: 760px;
            padding: 1rem 1rem 4rem;
        }
        header[data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer { visibility: hidden; }
        h1, h2, h3 { letter-spacing: -.025em; }
        h1 { font-size: clamp(2.15rem, 9vw, 4.2rem) !important; line-height: .98 !important; }
        h2 { font-size: clamp(1.55rem, 6vw, 2.15rem) !important; }
        div[data-testid="stSelectbox"] > label,
        div[data-testid="stRadio"] > label { color: #aeb6c2; }
        .hero-kicker {
            color: #ff795b; font-size: .76rem; font-weight: 800;
            letter-spacing: .18em; text-transform: uppercase; margin-bottom: .65rem;
        }
        .hero-copy { color: #bbc1ca; font-size: 1.05rem; line-height: 1.55; max-width: 650px; }
        .data-card {
            background: linear-gradient(145deg, rgba(25,29,37,.98), rgba(16,19,25,.98));
            border: 1px solid rgba(255,255,255,.08); border-radius: 22px;
            padding: 1.15rem 1.15rem 1.05rem; margin: .7rem 0;
            box-shadow: 0 14px 38px rgba(0,0,0,.24);
        }
        .data-card.primary {
            border-color: rgba(255,104,70,.4);
            background: linear-gradient(145deg, rgba(58,29,25,.98), rgba(22,19,22,.98));
        }
        .data-card.positive { border-color: rgba(66,196,138,.32); }
        .card-label { color: #aeb6c2; font-size: .73rem; font-weight: 800;
            text-transform: uppercase; letter-spacing: .1em; }
        .card-value { color: #f8f9fb; font-weight: 800; line-height: 1.03;
            font-size: clamp(2rem, 10vw, 3.65rem); margin: .7rem 0 .35rem; overflow-wrap: anywhere; }
        .data-card:not(.primary) .card-value { font-size: clamp(1.75rem, 8vw, 2.8rem); }
        .card-unit { color: #ff795b; font-weight: 700; font-size: .92rem; }
        .card-note { color: #89919e; font-size: .78rem; line-height: 1.45; margin-top: .65rem; }
        .source-strip { border-left: 3px solid #ff6846; padding: .75rem .9rem;
            background: rgba(255,104,70,.06); color: #c6cbd2; border-radius: 0 12px 12px 0;
            margin: 1rem 0; font-size: .84rem; }
        .eyebrow { color: #ff795b; text-transform: uppercase; letter-spacing: .14em;
            font-size: .72rem; font-weight: 800; margin-top: 2rem; }
        .unavailable { color: #d2a64f; }
        div.stButton > button, div.stDownloadButton > button {
            min-height: 48px; border-radius: 13px; width: 100%;
        }
        div[data-baseweb="select"] > div { min-height: 48px; border-radius: 13px; }
        div[data-testid="stPlotlyChart"] { border: 1px solid rgba(255,255,255,.07);
            border-radius: 18px; overflow: hidden; }
        @media (max-width: 430px) {
            .block-container { padding-left: .75rem; padding-right: .75rem; padding-top: .65rem; }
            .data-card { padding: 1rem; border-radius: 18px; }
            .hero-copy { font-size: .96rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown('<div class="hero-kicker">Observatório de dados</div>', unsafe_allow_html=True)
    st.title("Fome & desperdício")
    st.markdown(
        '<p class="hero-copy">Enquanto milhões de pessoas enfrentam insegurança '
        "alimentar, enormes quantidades de alimentos são perdidas ou desperdiçadas todos "
        "os dias.</p>",
        unsafe_allow_html=True,
    )


def section_intro(kicker: str, title: str, text: str = "") -> None:
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.header(title)
    if text:
        st.caption(text)

