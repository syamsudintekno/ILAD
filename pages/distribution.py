"""Research validation page for raw-score and RPI distributions."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from application.controller import ANALYTICS_RESULT_SESSION_KEY, AnalyticsRunResult
from components.footer import render_footer
from config.schema import OVERALL_SCORE_COLUMN, RPI_COLUMN
from ui.theme import PRIMARY_TURQUOISE, apply_theme, render_brand_header, render_section_header


def render_distribution_analysis() -> None:
    """Render cached raw-overall-score and RPI distribution comparisons."""
    apply_theme()
    render_brand_header("Distribution Validation")
    result = st.session_state.get(ANALYTICS_RESULT_SESSION_KEY)
    if not isinstance(result, AnalyticsRunResult) or result.distribution_comparison is None:
        st.info("Upload a valid synthetic EDOM CSV on the Dashboard Overview page first.")
        render_footer()
        return

    comparison = result.distribution_comparison
    _render_institution_summary(result)
    _render_distribution_comparison(result.analytics_data)
    _render_boxplot_comparison(result.analytics_data)
    _render_statistics_table(comparison)
    _render_ceiling_effect_analysis(comparison)
    _render_research_notes()
    render_footer()


def _render_institution_summary(result: AnalyticsRunResult) -> None:
    """Display existing institutional and raw-score summaries."""
    render_section_header("Institution Summary")
    cards = st.columns(4)
    cards[0].metric("Number of Lecturers", int(result.kpis["lecturer_count"]))
    cards[1].metric("Number of Study Programs", int(result.kpis["study_program_count"]))
    cards[2].metric(
        "Average Overall Score",
        f"{result.statistics.mean[OVERALL_SCORE_COLUMN]:.2f}",
    )
    cards[3].metric("Average RPI", f"{float(result.kpis['average_rpi']):.2f}")


def _render_distribution_comparison(analytics_data: pd.DataFrame) -> None:
    """Display raw overall-score and RPI histograms side by side."""
    render_section_header("Distribution Comparison")
    raw_column, rpi_column = st.columns(2)
    with raw_column:
        st.caption("Overall Score Distribution")
        st.plotly_chart(_histogram(analytics_data, OVERALL_SCORE_COLUMN), use_container_width=True)
    with rpi_column:
        st.caption("RPI Distribution")
        st.plotly_chart(_histogram(analytics_data, RPI_COLUMN), use_container_width=True)


def _histogram(analytics_data: pd.DataFrame, score_column: str) -> go.Figure:
    """Create a consistent histogram from existing analytics values."""
    return px.histogram(
        analytics_data,
        x=score_column,
        color_discrete_sequence=[PRIMARY_TURQUOISE],
    )


def _render_boxplot_comparison(analytics_data: pd.DataFrame) -> None:
    """Display paired boxplots to show existing score dispersion."""
    render_section_header("Boxplot Comparison")
    raw_column, rpi_column = st.columns(2)
    with raw_column:
        st.caption("Overall Score")
        st.plotly_chart(_boxplot(analytics_data, OVERALL_SCORE_COLUMN), use_container_width=True)
    with rpi_column:
        st.caption("RPI")
        st.plotly_chart(_boxplot(analytics_data, RPI_COLUMN), use_container_width=True)


def _boxplot(analytics_data: pd.DataFrame, score_column: str) -> go.Figure:
    """Create a simple boxplot from existing analytics values."""
    figure = go.Figure(go.Box(y=analytics_data[score_column], marker_color=PRIMARY_TURQUOISE))
    figure.update_layout(showlegend=False)
    return figure


def _render_statistics_table(comparison: object) -> None:
    """Display precomputed raw and RPI distribution statistics."""
    render_section_header("Distribution Statistics")
    st.dataframe(_prepare_statistics_table(comparison), hide_index=True, use_container_width=True)


def _prepare_statistics_table(comparison: object) -> pd.DataFrame:
    """Build a presentation comparison table without recomputing metrics."""
    raw = comparison.raw
    transformed = comparison.transformed
    metrics = (
        ("Mean", raw.mean, transformed.mean),
        ("Median", raw.median, transformed.median),
        ("Variance", raw.variance, transformed.variance),
        ("Standard Deviation", raw.standard_deviation, transformed.standard_deviation),
        ("Minimum", raw.minimum, transformed.minimum),
        ("Maximum", raw.maximum, transformed.maximum),
        ("Skewness", raw.skewness, transformed.skewness),
        ("Kurtosis", raw.kurtosis, transformed.kurtosis),
    )
    return pd.DataFrame(metrics, columns=["Metric", "Overall Score", "RPI"])


def _render_ceiling_effect_analysis(comparison: object) -> None:
    """Display rule-based precomputed ceiling-effect interpretations."""
    render_section_header("Ceiling Effect Analysis")
    before, after = st.columns(2)
    before.markdown("**Before RPI**")
    before.metric("Variance", f"{comparison.raw.variance:.3f}")
    before.metric("Skewness", f"{comparison.raw.skewness:.3f}")
    before.metric("Kurtosis", f"{comparison.raw.kurtosis:.3f}")
    after.markdown("**After RPI**")
    after.metric("Variance", f"{comparison.transformed.variance:.3f}")
    after.metric("Skewness", f"{comparison.transformed.skewness:.3f}")
    after.metric("Kurtosis", f"{comparison.transformed.kurtosis:.3f}")
    for interpretation in comparison.interpretations:
        st.write(f"- {interpretation}")


def _render_research_notes() -> None:
    """Display static research-method notes for institutional QA users."""
    with st.expander("Research Method"):
        st.write("Ceiling effect occurs when raw EDOM scores cluster near the top of the scale.")
        st.write("RPI compares lecturers relatively across the institution.")
        st.write("Rankit transformation converts ranks into inverse-normal scores.")
        st.write("Blom plotting position uses a 0.375 rank adjustment before inverse normalization.")
        st.write("T-score normalization centres the RPI scale at 50 with a standard deviation of 10.")


if __name__ == "__main__":
    render_distribution_analysis()
