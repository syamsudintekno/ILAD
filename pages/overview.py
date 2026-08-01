"""Streamlit Dashboard Overview presentation page."""

from collections.abc import Mapping

import pandas as pd
import plotly.express as px
import streamlit as st

from application.controller import (
    ANALYTICS_RESULT_SESSION_KEY,
    AnalyticsController,
    DatasetValidationError,
)
from config.schema import (
    LECTURER_NAME_COLUMN,
    QUARTILE_COLUMN,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)


def render_overview() -> None:
    """Render the CSV-uploaded institutional Dashboard Overview."""
    st.title("Institutional Learning Analytics Dashboard")
    st.caption("Upload a synthetic EDOM CSV dataset to generate institutional insights.")
    uploaded_file = st.file_uploader("Upload EDOM CSV", type="csv")
    if uploaded_file is None:
        st.info("Upload a synthetic CSV dataset to view the dashboard overview.")
        return

    try:
        result = AnalyticsController().run_uploaded_csv(uploaded_file)
    except DatasetValidationError as error:
        _render_validation_errors(error.validation_result.errors)
        return
    except (ValueError, OSError, pd.errors.ParserError) as error:
        st.error(str(error))
        return
    except Exception:
        st.error("The uploaded dataset could not be processed.")
        return

    st.session_state[ANALYTICS_RESULT_SESSION_KEY] = result
    st.success("Dashboard generated successfully.")
    _render_kpis(result.kpis)
    _render_quartile_distribution(result.kpis["quartile_distribution"])
    _render_top_lecturers(result.analytics_data)


def _render_kpis(kpis: dict[str, float | int | dict[str, int]]) -> None:
    """Render the approved institutional KPI metrics."""
    cards = st.columns(5)
    cards[0].metric("Total Lecturers", int(kpis["lecturer_count"]))
    cards[1].metric("Total Study Programs", int(kpis["study_program_count"]))
    cards[2].metric("Average RPI", f"{float(kpis['average_rpi']):.2f}")
    cards[3].metric("Highest RPI", f"{float(kpis['highest_rpi']):.2f}")
    cards[4].metric("Lowest RPI", f"{float(kpis['lowest_rpi']):.2f}")


def _render_validation_errors(errors: Mapping[str, object]) -> None:
    """Render data-validation issues without exposing Python tracebacks."""
    st.error("The uploaded dataset has validation issues.")
    for category, detail in errors.items():
        label = category.replace("_", " ").capitalize()
        st.error(f"{label}: {detail}")


def _render_quartile_distribution(distribution: Mapping[str, int]) -> None:
    """Render institutional quartile counts in a simple Plotly bar chart."""
    st.subheader("Quartile Distribution")
    chart_data = pd.DataFrame(
        {"Quartile": list(distribution), "Lecturers": list(distribution.values())}
    )
    figure = px.bar(chart_data, x="Quartile", y="Lecturers")
    st.plotly_chart(figure, use_container_width=True)


def _render_top_lecturers(analytics_data: pd.DataFrame) -> None:
    """Render the top ten ranked lecturers from completed analytics data."""
    st.subheader("Top 10 Lecturers")
    top_lecturers = _prepare_top_lecturer_table(analytics_data)
    st.dataframe(top_lecturers, hide_index=True, use_container_width=True)


def _prepare_top_lecturer_table(analytics_data: pd.DataFrame) -> pd.DataFrame:
    """Return the formatted top-ten lecturer table for dashboard display."""
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
    return (
        analytics_data.sort_values(
            by=RPI_COLUMN,
            ascending=False,
            kind="mergesort",
        )
        .loc[:, columns]
        .head(10)
        .rename(columns=labels)
    )
