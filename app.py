"""Streamlit entry point for the ILAD Dashboard Overview."""

import streamlit as st

from pages.overview import render_overview


def main() -> None:
    """Configure Streamlit and render the Dashboard Overview page."""
    st.set_page_config(page_title="ILAD Dashboard", layout="wide")
    render_overview()


if __name__ == "__main__":
    main()
