"""Reusable Streamlit branding and layout utilities."""

from pathlib import Path

import streamlit as st

PRIMARY_TURQUOISE = "#00A8CC"
_LOGO_PATH = Path(__file__).resolve().parents[1] / "assets" / "logo_uin.png"


def apply_theme() -> None:
    """Apply shared ILAD CSS for consistent dashboard presentation."""
    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 1.5rem; padding-bottom: 2.5rem; }}
        div[data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid #DDE7E8;
            border-radius: 12px;
            padding: 0.8rem 1rem;
            box-shadow: 0 2px 8px rgba(30, 41, 59, 0.05);
        }}
        div[data-testid="stMetricValue"] {{ color: {PRIMARY_TURQUOISE}; font-weight: 700; }}
        .ilad-brand {{ margin-bottom: 1.25rem; }}
        .ilad-brand-title {{ color: #1E293B; font-size: 1.6rem; font-weight: 750; }}
        .ilad-brand-subtitle {{ color: #64748B; font-size: 0.9rem; margin-top: -0.3rem; }}
        .ilad-section {{
            color: #1E293B;
            font-size: 1.2rem;
            font-weight: 700;
            margin: 1.7rem 0 0.6rem;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid #DDE7E8;
            border-radius: 10px;
            padding: 0.35rem;
            background: #FFFFFF;
        }}
        .stButton > button, .stDownloadButton > button {{
            border-radius: 8px;
            border-color: {PRIMARY_TURQUOISE};
            color: {PRIMARY_TURQUOISE};
            font-weight: 600;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: {PRIMARY_TURQUOISE};
            color: #FFFFFF;
        }}
        a, a:visited {{ color: {PRIMARY_TURQUOISE}; }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {PRIMARY_TURQUOISE};
            border-bottom-color: {PRIMARY_TURQUOISE};
        }}
        [data-baseweb="select"] > div:focus-within {{
            border-color: {PRIMARY_TURQUOISE};
            box-shadow: 0 0 0 1px {PRIMARY_TURQUOISE};
        }}
        [data-testid="stSidebar"] {{ padding-top: 1rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header(page_title: str) -> None:
    """Render the ILAD logo, application identity, and current page title."""
    logo_column, title_column = st.columns([1, 12], vertical_alignment="center")
    with logo_column:
        st.image(str(_LOGO_PATH), width=52)
    with title_column:
        st.markdown(
            "<div class='ilad-brand'>"
            "<div class='ilad-brand-title'>ILAD</div>"
            "<div class='ilad-brand-subtitle'>"
            "Institutional Learning Analytics Dashboard<br>Research Prototype"
            "</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown(f"<div class='ilad-section'>{page_title}</div>", unsafe_allow_html=True)


def render_section_header(title: str) -> None:
    """Render a consistently styled section heading."""
    st.markdown(f"<div class='ilad-section'>{title}</div>", unsafe_allow_html=True)
