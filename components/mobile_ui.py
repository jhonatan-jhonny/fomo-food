from __future__ import annotations

from html import escape

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            --fomo-bg: #070B11;
            --fomo-surface: #0C1220;
            --fomo-glass: rgba(20, 28, 40, 0.52);
            --fomo-glass-soft: rgba(255, 255, 255, 0.055);
            --fomo-border: rgba(255, 255, 255, 0.105);
            --fomo-border-bright: rgba(143, 183, 255, 0.28);
            --fomo-text: #F4F7FB;
            --fomo-muted: #A9B4C3;
            --fomo-blue: #8FB7FF;
            --fomo-cyan: #7ED7D1;
            --fomo-lilac: #B7A7FF;
            --fomo-alert: #FF8E7A;
            --fomo-shadow: rgba(0, 0, 0, 0.38);
        }
        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                "Segoe UI", sans-serif;
        }
        .stApp {
            color: var(--fomo-text);
            background:
                radial-gradient(ellipse 85% 50% at 8% -5%, rgba(80, 125, 205, .18), transparent 62%),
                radial-gradient(ellipse 72% 44% at 96% 12%, rgba(136, 111, 210, .13), transparent 64%),
                radial-gradient(ellipse 58% 40% at 50% 78%, rgba(59, 143, 157, .075), transparent 70%),
                linear-gradient(180deg, #080D15 0%, var(--fomo-bg) 48%, #060910 100%);
            min-height: 100vh;
        }
        .block-container {
            max-width: 780px;
            padding: 1.15rem 1rem 5rem;
        }
        header[data-testid="stHeader"] { display: none !important; }
        #MainMenu, footer { visibility: hidden; }
        h1, h2, h3 {
            color: var(--fomo-text);
            letter-spacing: -.035em;
            text-wrap: balance;
        }
        h1 { font-size: clamp(2.35rem, 10vw, 4.5rem) !important; line-height: .96 !important; }
        h2 { font-size: clamp(1.65rem, 6vw, 2.25rem) !important; line-height: 1.08 !important; }
        h3 { font-size: clamp(1.25rem, 4.8vw, 1.55rem) !important; }
        p, li { color: #C2CBD7; line-height: 1.62; }
        a { color: var(--fomo-blue) !important; text-decoration-color: rgba(143,183,255,.4) !important; }
        hr { border-color: rgba(255,255,255,.08) !important; }
        div[data-testid="stSelectbox"] > label,
        div[data-testid="stRadio"] > label,
        div[data-testid="stToggle"] > label {
            color: var(--fomo-muted) !important;
            font-size: .9rem;
            font-weight: 600;
        }
        .hero-shell {
            position: relative;
            overflow: hidden;
            padding: 1.25rem 1.15rem 1.4rem;
            margin: .35rem 0 1rem;
            border: 1px solid var(--fomo-border);
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255,255,255,.075), rgba(255,255,255,.018) 46%),
                rgba(14, 21, 32, .54);
            box-shadow:
                0 24px 65px rgba(0,0,0,.34),
                inset 0 1px 0 rgba(255,255,255,.09),
                inset 0 -1px 0 rgba(143,183,255,.05);
            backdrop-filter: blur(22px) saturate(135%);
            -webkit-backdrop-filter: blur(22px) saturate(135%);
        }
        .hero-shell::before {
            content: "";
            position: absolute;
            width: 15rem; height: 15rem;
            right: -7rem; top: -8rem;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(143,183,255,.2), transparent 68%);
            pointer-events: none;
        }
        .hero-shell::after {
            content: "";
            position: absolute;
            left: 12%; right: 12%; top: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,.3), transparent);
            pointer-events: none;
        }
        .hero-kicker {
            display: flex; align-items: center; gap: .55rem;
            color: var(--fomo-blue); font-size: .78rem; font-weight: 750;
            letter-spacing: .16em; text-transform: uppercase; margin-bottom: 1rem;
        }
        .hero-kicker::before {
            content: ""; width: .52rem; height: .52rem; border-radius: 50%;
            background: var(--fomo-cyan);
            box-shadow: 0 0 0 5px rgba(126,215,209,.08), 0 0 18px rgba(126,215,209,.45);
        }
        .hero-title {
            position: relative; z-index: 1;
            color: var(--fomo-text);
            font-size: clamp(2.45rem, 12vw, 4.65rem);
            font-weight: 790;
            line-height: .93;
            letter-spacing: -.06em;
            margin: 0;
            text-wrap: balance;
        }
        .hero-title span {
            color: var(--fomo-blue);
            font-weight: 500;
            margin-left: .08em;
        }
        .hero-copy {
            position: relative; z-index: 1;
            color: #C4CEDA;
            font-size: clamp(1rem, 3.7vw, 1.12rem);
            line-height: 1.62;
            max-width: 650px;
            margin: 1.15rem 0 0;
        }
        .data-card {
            position: relative;
            isolation: isolate;
            overflow: hidden;
            background:
                linear-gradient(145deg, rgba(255,255,255,.07), rgba(255,255,255,.015) 58%),
                var(--fomo-glass);
            border: 1px solid var(--fomo-border);
            border-radius: 25px;
            padding: 1.3rem 1.25rem 1.2rem;
            margin: .8rem 0;
            box-shadow:
                0 18px 48px var(--fomo-shadow),
                inset 0 1px 0 rgba(255,255,255,.09),
                inset 0 -1px 0 rgba(255,255,255,.025);
            backdrop-filter: blur(20px) saturate(130%);
            -webkit-backdrop-filter: blur(20px) saturate(130%);
        }
        .data-card::before {
            content: "";
            position: absolute;
            z-index: -1;
            right: -3.5rem; top: -4.2rem;
            width: 10rem; height: 10rem; border-radius: 50%;
            background: radial-gradient(circle, rgba(143,183,255,.13), transparent 70%);
            pointer-events: none;
        }
        .data-card::after {
            content: "";
            position: absolute;
            left: 1.4rem; right: 1.4rem; top: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,.22), transparent);
            pointer-events: none;
        }
        .data-card.primary {
            border-color: rgba(143,183,255,.3);
            background:
                linear-gradient(145deg, rgba(143,183,255,.13), rgba(255,255,255,.025) 55%),
                rgba(14, 23, 38, .62);
            box-shadow:
                0 22px 55px rgba(0,0,0,.42),
                0 0 42px rgba(82,124,190,.07),
                inset 0 1px 0 rgba(255,255,255,.12);
        }
        .data-card.positive {
            border-color: rgba(126,215,209,.27);
            background:
                linear-gradient(145deg, rgba(126,215,209,.105), rgba(255,255,255,.018) 58%),
                rgba(13, 27, 35, .56);
        }
        .data-card.positive::before {
            background: radial-gradient(circle, rgba(126,215,209,.14), transparent 70%);
        }
        .card-label {
            color: #B9C5D4;
            font-size: .79rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: .115em;
            line-height: 1.4;
        }
        .card-value {
            color: var(--fomo-text);
            font-weight: 780;
            line-height: 1;
            letter-spacing: -.045em;
            font-variant-numeric: tabular-nums lining-nums;
            text-shadow: 0 0 28px rgba(143,183,255,.09);
            font-size: clamp(2.1rem, 10.5vw, 3.8rem);
            margin: .82rem 0 .42rem;
            overflow-wrap: anywhere;
        }
        .data-card:not(.primary) .card-value {
            font-size: clamp(1.9rem, 8.5vw, 3rem);
        }
        .card-unit {
            color: var(--fomo-blue);
            font-weight: 700;
            font-size: .98rem;
            line-height: 1.4;
        }
        .positive .card-unit { color: var(--fomo-cyan); }
        .card-note {
            color: var(--fomo-muted);
            font-size: .88rem;
            line-height: 1.56;
            margin-top: .78rem;
        }
        .source-strip {
            position: relative;
            border: 1px solid rgba(143,183,255,.16);
            border-left: 3px solid var(--fomo-blue);
            padding: .92rem 1rem;
            background: rgba(17, 26, 39, .48);
            color: #C9D2DE;
            border-radius: 7px 17px 17px 7px;
            margin: 1rem 0 1.2rem;
            font-size: .9rem;
            line-height: 1.55;
            box-shadow: 0 12px 32px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.04);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }
        .section-heading { margin: 2.35rem 0 1rem; }
        .section-title {
            color: var(--fomo-text);
            font-size: clamp(1.7rem, 6vw, 2.3rem);
            line-height: 1.08;
            letter-spacing: -.04em;
            margin: .38rem 0 .45rem;
            font-weight: 760;
        }
        .section-copy {
            color: var(--fomo-muted);
            font-size: .97rem;
            line-height: 1.58;
            margin: 0;
        }
        .eyebrow {
            color: var(--fomo-lilac);
            text-transform: uppercase;
            letter-spacing: .15em;
            font-size: .76rem;
            font-weight: 750;
        }
        .unavailable { color: var(--fomo-alert); text-shadow: none; }
        .source-status {
            padding: 1rem;
            margin: .65rem 0;
            border: 1px solid var(--fomo-border);
            border-radius: 17px;
            background: rgba(20,28,40,.4);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            color: var(--fomo-muted);
            font-size: .9rem;
            line-height: 1.55;
        }
        .source-status strong { color: var(--fomo-text); font-size: .96rem; }
        div.stButton > button, div.stDownloadButton > button {
            min-height: 50px;
            border-radius: 15px;
            width: 100%;
            color: var(--fomo-text);
            border: 1px solid var(--fomo-border-bright);
            background: linear-gradient(135deg, rgba(143,183,255,.14), rgba(255,255,255,.035));
            box-shadow: 0 10px 28px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.08);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }
        div.stButton > button:hover, div.stDownloadButton > button:hover {
            border-color: rgba(143,183,255,.5);
            color: #fff;
            background: linear-gradient(135deg, rgba(143,183,255,.2), rgba(183,167,255,.08));
        }
        div[data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] .react-aria-ComboBox > div {
            min-height: 50px;
            border-radius: 15px;
            color: var(--fomo-text);
            border-color: var(--fomo-border) !important;
            background: rgba(18, 26, 39, .62) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 10px 28px rgba(0,0,0,.15);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }
        div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stSelectbox"] .react-aria-ComboBox > div:focus-within {
            border-color: rgba(143,183,255,.55) !important;
            box-shadow: 0 0 0 3px rgba(143,183,255,.1);
        }
        div[data-baseweb="popover"] > div {
            background: rgba(12,18,32,.96) !important;
            border: 1px solid var(--fomo-border) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }
        div[data-testid="stSelectbox"] input {
            color: var(--fomo-text) !important;
            font-weight: 620;
            padding-left: .85rem;
        }
        div[data-testid="stExpander"] {
            border: 1px solid var(--fomo-border) !important;
            border-radius: 17px !important;
            background: rgba(18, 26, 39, .43);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.045), 0 12px 32px rgba(0,0,0,.14);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            overflow: hidden;
        }
        div[data-testid="stExpander"] summary {
            min-height: 52px;
            color: #DCE4EE;
            font-weight: 620;
        }
        div[data-testid="stAlert"] {
            border: 1px solid rgba(143,183,255,.18);
            border-radius: 16px;
            background: rgba(19, 29, 43, .62);
            color: #D8E0EA;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }
        div[data-testid="stPlotlyChart"] {
            border: 1px solid var(--fomo-border);
            border-radius: 22px;
            overflow: hidden;
            padding: .18rem;
            background: linear-gradient(145deg, rgba(255,255,255,.055), rgba(255,255,255,.012)),
                rgba(15, 22, 34, .46);
            box-shadow: 0 20px 50px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.07);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }
        div[data-testid="stCaptionContainer"] p {
            color: var(--fomo-muted) !important;
            font-size: .86rem;
            line-height: 1.5;
        }
        div[data-testid="stSpinner"] { color: var(--fomo-blue); }
        * { scrollbar-color: rgba(143,183,255,.3) transparent; scrollbar-width: thin; }
        ::selection { background: rgba(143,183,255,.28); color: #fff; }
        @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
            .data-card, .hero-shell, .source-strip, div[data-testid="stExpander"],
            div[data-testid="stPlotlyChart"] { background-color: #111A28; }
        }
        @media (max-width: 430px) {
            .block-container {
                padding-left: .72rem;
                padding-right: .72rem;
                padding-top: .7rem;
            }
            .hero-shell { padding: 1.12rem 1rem 1.25rem; border-radius: 23px; }
            .data-card { padding: 1.18rem 1.05rem 1.08rem; border-radius: 21px; margin: .7rem 0; }
            .card-note { font-size: .86rem; }
            .section-heading { margin-top: 2rem; }
            div[data-testid="stPlotlyChart"] { border-radius: 18px; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <section class="hero-shell">
          <div class="hero-kicker">Observatório humanitário de dados</div>
          <h1 class="hero-title">Fome <span>&amp;</span><br>desperdício</h1>
          <p class="hero-copy">Enquanto milhões de pessoas enfrentam insegurança
          alimentar, enormes quantidades de alimentos são perdidas ou desperdiçadas
          todos os dias.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_intro(kicker: str, title: str, text: str = "") -> None:
    copy = f'<p class="section-copy">{escape(text)}</p>' if text else ""
    st.markdown(
        f"""
        <div class="section-heading">
          <div class="eyebrow">{escape(kicker)}</div>
          <h2 class="section-title">{escape(title)}</h2>
          {copy}
        </div>
        """,
        unsafe_allow_html=True,
    )
