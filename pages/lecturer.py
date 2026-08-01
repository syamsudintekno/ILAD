"""Streamlit Lecturer Profile presentation page."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from application.controller import ANALYTICS_RESULT_SESSION_KEY, AnalyticsRunResult
from config.schema import (
    DIMENSION_COLUMNS,
    LECTURER_NAME_COLUMN,
    QUARTILE_COLUMN,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)


def render_lecturer_profile() -> None:
    """Render the selected lecturer profile from completed analytics data."""
    st.title("Lecturer Profile")
    analytics_data = _get_analytics_data()
    if analytics_data is None:
        st.info("Upload a valid synthetic EDOM CSV on the Dashboard Overview page first.")
        return

    lecturer_name = st.selectbox(
        "Select Lecturer",
        analytics_data[LECTURER_NAME_COLUMN].tolist(),
    )
    lecturer = analytics_data.loc[
        analytics_data[LECTURER_NAME_COLUMN] == lecturer_name
    ].iloc[0]
    _render_identity(lecturer)
    _render_metrics(lecturer)
    _render_dimension_radar(lecturer)
    _render_dimension_summary(lecturer)


def _get_analytics_data() -> pd.DataFrame | None:
    """Return completed analytics data stored by the Overview page."""
    result = st.session_state.get(ANALYTICS_RESULT_SESSION_KEY)
    if not isinstance(result, AnalyticsRunResult):
        return None
    return result.analytics_data


def _render_identity(lecturer: pd.Series) -> None:
    """Display the selected lecturer's identity details."""
    st.subheader(str(lecturer[LECTURER_NAME_COLUMN]))
    st.write(f"Study Program: {lecturer[STUDY_PROGRAM_COLUMN]}")


def _render_metrics(lecturer: pd.Series) -> None:
    """Display RPI, institution rank, and quartile metrics."""
    cards = st.columns(3)
    cards[0].metric("RPI", f"{float(lecturer[RPI_COLUMN]):.2f}")
    cards[1].metric("Institution Rank", int(lecturer[RANK_COLUMN]))
    cards[2].metric("Quartile", str(lecturer[QUARTILE_COLUMN]))


def _render_dimension_radar(lecturer: pd.Series) -> None:
    """Display competency scores in a minimal Plotly radar chart."""
    dimensions = [column.title() for column in DIMENSION_COLUMNS]
    scores = [float(lecturer[column]) for column in DIMENSION_COLUMNS]
    figure = go.Figure(
        go.Scatterpolar(r=scores, theta=dimensions, fill="toself")
    )
    figure.update_layout(
        polar={"radialaxis": {"range": [1, 5]}},
        showlegend=False,
    )
    st.subheader("Competency Profile")
    st.plotly_chart(figure, use_container_width=True)


def _render_dimension_summary(lecturer: pd.Series) -> None:
    """Display the selected lecturer's competency scores as a table."""
    st.subheader("Dimension Summary")
    st.dataframe(_prepare_dimension_summary(lecturer), hide_index=True)


def _prepare_dimension_summary(lecturer: pd.Series) -> pd.DataFrame:
    """Build presentation data for the lecturer dimension summary table."""
    return pd.DataFrame(
        {
            "Dimension": [column.title() for column in DIMENSION_COLUMNS],
            "Score": [float(lecturer[column]) for column in DIMENSION_COLUMNS],
        }
    )


if __name__ == "__main__":
    render_lecturer_profile()
