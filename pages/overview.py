"""Streamlit Dashboard Overview presentation page."""

from collections.abc import Mapping, MutableMapping

import pandas as pd
import plotly.express as px
import streamlit as st

from application.controller import (
    ANALYTICS_RESULT_SESSION_KEY,
    AnalyticsController,
    AnalyticsRunResult,
    DatasetValidationError,
)
from components.footer import render_footer
from config.schema import (
    LECTURER_NAME_COLUMN,
    QUARTILE_COLUMN,
    PREPARED_COLUMNS,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)
from ui.theme import PRIMARY_TURQUOISE, apply_theme, render_brand_header, render_section_header

PREPARED_DATA_SESSION_KEY = "prepared_data"
UPLOADED_FILENAME_SESSION_KEY = "uploaded_filename"


def render_overview() -> None:
    """Render the CSV-uploaded institutional Dashboard Overview."""
    apply_theme()
    render_brand_header("Dashboard Overview")
    result = st.session_state.get(ANALYTICS_RESULT_SESSION_KEY)
    if isinstance(result, AnalyticsRunResult):
        _render_cached_overview(result)
        render_footer()
        return

    st.caption("Upload a synthetic EDOM CSV dataset to generate institutional insights.")
    uploaded_file = st.file_uploader("Upload EDOM CSV", type="csv")
    if uploaded_file is None:
        st.info("Upload a synthetic CSV dataset to view the dashboard overview.")
        render_footer()
        return

    try:
        with st.spinner("Generating institutional analytics..."):
            result = AnalyticsController().run_uploaded_csv(uploaded_file)
    except DatasetValidationError as error:
        _render_validation_errors(error.validation_result.errors)
        render_footer()
        return
    except (ValueError, OSError, pd.errors.ParserError) as error:
        st.error("The uploaded dataset could not be processed. Please verify the ILAD EDOM template.")
        render_footer()
        return
    except Exception:
        st.error("The uploaded dataset could not be processed. Please upload it again.")
        render_footer()
        return

    _store_processed_dataset(st.session_state, result, uploaded_file.name)
    _render_cached_overview(result)
    render_footer()


def _render_cached_overview(result: AnalyticsRunResult) -> None:
    """Render a completed dashboard result retained in the current session."""
    uploaded_filename = st.session_state.get(UPLOADED_FILENAME_SESSION_KEY, "dataset")
    st.success("Dashboard generated successfully.")
    st.caption(f"Loaded dataset: {uploaded_filename}")
    _render_kpis(result.kpis)
    _render_quartile_distribution(result.kpis["quartile_distribution"])
    _render_top_lecturers(result.analytics_data)


def _store_processed_dataset(
    session_state: MutableMapping[str, object],
    result: AnalyticsRunResult,
    uploaded_filename: str,
) -> None:
    """Persist processed data and metadata without retaining an upload object."""
    session_state[PREPARED_DATA_SESSION_KEY] = result.analytics_data.loc[
        :, list(PREPARED_COLUMNS)
    ].copy()
    session_state[ANALYTICS_RESULT_SESSION_KEY] = result
    session_state[UPLOADED_FILENAME_SESSION_KEY] = uploaded_filename


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
    if "missing_columns" in errors:
        st.error("The uploaded dataset does not follow the ILAD EDOM template.")
    if "invalid_score_counts" in errors:
        st.error(
            "Some questionnaire responses contain values outside the expected range (1–5)."
        )
    if "missing_values" in errors:
        st.error("Some questionnaire responses are incomplete.")
    if "duplicate_row_count" in errors:
        st.error("The uploaded dataset contains duplicate records.")
    st.error("Please correct the dataset and upload it again.")


def _render_quartile_distribution(distribution: Mapping[str, int]) -> None:
    """Render institutional quartile counts in a simple Plotly bar chart."""
    render_section_header("Quartile Distribution")
    chart_data = pd.DataFrame(
        {"Quartile": list(distribution), "Lecturers": list(distribution.values())}
    )
    figure = px.bar(
        chart_data,
        x="Quartile",
        y="Lecturers",
        color_discrete_sequence=[PRIMARY_TURQUOISE],
    )
    st.plotly_chart(figure, use_container_width=True)


def _render_top_lecturers(analytics_data: pd.DataFrame) -> None:
    """Render the top ten ranked lecturers from completed analytics data."""
    render_section_header("Top 10 Lecturers")
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


if __name__ == "__main__":
    render_overview()
