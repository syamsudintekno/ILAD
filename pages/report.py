"""Streamlit Reporting presentation page for completed ILAD analytics."""

from datetime import datetime
import json

import pandas as pd
import streamlit as st

from application.controller import ANALYTICS_RESULT_SESSION_KEY, AnalyticsRunResult
from components.footer import render_footer
from config.schema import (
    LECTURER_NAME_COLUMN,
    QUARTILE_COLUMN,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)
from ui.theme import apply_theme, render_brand_header, render_section_header


def render_report() -> None:
    """Render the cached institutional report and its approved exports."""
    apply_theme()
    render_brand_header("Institutional Report")
    result = st.session_state.get(ANALYTICS_RESULT_SESSION_KEY)
    if not isinstance(result, AnalyticsRunResult):
        st.info("Upload a valid synthetic EDOM CSV on the Dashboard Overview page first.")
        render_footer()
        return

    st.caption(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _render_summary(result.kpis)
    _render_top_lecturers(result.analytics_data)
    _render_quartile_summary(result.kpis["quartile_distribution"])
    _render_downloads(result)
    render_footer()


def _render_summary(kpis: dict[str, float | int | dict[str, int]]) -> None:
    """Display existing institutional KPIs in compact report cards."""
    render_section_header("Institution Summary")
    cards = st.columns(5)
    cards[0].metric("Total Lecturers", int(kpis["lecturer_count"]))
    cards[1].metric("Total Study Programs", int(kpis["study_program_count"]))
    cards[2].metric("Average RPI", f"{float(kpis['average_rpi']):.2f}")
    cards[3].metric("Highest RPI", f"{float(kpis['highest_rpi']):.2f}")
    cards[4].metric("Lowest RPI", f"{float(kpis['lowest_rpi']):.2f}")


def _render_top_lecturers(analytics_data: pd.DataFrame) -> None:
    """Display the highest twenty completed analytics records."""
    render_section_header("Top 20 Lecturers")
    columns = [
        RANK_COLUMN,
        LECTURER_NAME_COLUMN,
        STUDY_PROGRAM_COLUMN,
        RPI_COLUMN,
        QUARTILE_COLUMN,
    ]
    labels = {
        RANK_COLUMN: "Rank",
        LECTURER_NAME_COLUMN: "Lecturer Name",
        STUDY_PROGRAM_COLUMN: "Study Program",
        RPI_COLUMN: "RPI",
        QUARTILE_COLUMN: "Quartile",
    }
    table = analytics_data.sort_values(
        by=RPI_COLUMN,
        ascending=False,
        kind="mergesort",
    ).loc[:, columns].head(20).rename(columns=labels)
    st.dataframe(table, hide_index=True, use_container_width=True)


def _render_quartile_summary(distribution: dict[str, int]) -> None:
    """Display the already computed number of lecturers in each quartile."""
    render_section_header("Quartile Summary")
    cards = st.columns(4)
    for card, quartile in zip(cards, ("Q1", "Q2", "Q3", "Q4")):
        card.metric(quartile, distribution[quartile])


def _render_downloads(result: AnalyticsRunResult) -> None:
    """Offer unmodified analytics CSV and institutional KPI JSON downloads."""
    render_section_header("Downloads")
    csv_column, json_column = st.columns(2)
    csv_column.download_button(
        "Download Analytics CSV",
        data=result.analytics_data.to_csv(index=False).encode("utf-8"),
        file_name="ilad_analytics.csv",
        mime="text/csv",
        use_container_width=True,
    )
    json_column.download_button(
        "Download KPI Summary",
        data=json.dumps(result.kpis, indent=2),
        file_name="ilad_kpi_summary.json",
        mime="application/json",
        use_container_width=True,
    )


if __name__ == "__main__":
    render_report()
