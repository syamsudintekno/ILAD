"""Regression tests for the CSV-to-Overview adapter."""

import json
from io import BytesIO, StringIO

import pandas as pd
import pytest
from pandas.errors import ParserError

from application.controller import AnalyticsController, DatasetValidationError
from application.web_overview import build_web_overview
from config.schema import (
    FACULTY_COLUMN,
    INDICATOR_COLUMNS,
    LECTURER_NAME_COLUMN,
    REQUIRED_COLUMNS,
    STUDY_PROGRAM_COLUMN,
)
from core.loader import EmptyCsvFileError
from pages.analytics import _prepare_statistics_table
from pages.distribution import _prepare_statistics_table as _prepare_distribution_table
from pages.lecturer import _prepare_dimension_summary


def make_csv(scores: list[float]) -> bytes:
    """Create a canonical CSV with one synthetic lecturer per score."""
    rows = [
        {
            LECTURER_NAME_COLUMN: f"Dosen sintetis {index:02d}",
            STUDY_PROGRAM_COLUMN: "Program sintetis",
            FACULTY_COLUMN: "Fakultas sintetis",
            **dict.fromkeys(INDICATOR_COLUMNS, score),
        }
        for index, score in enumerate(scores)
    ]
    buffer = StringIO()
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def test_web_overview_serializes_cohort_kpis_and_top_ten() -> None:
    """Return the full cohort count and preserve tied ranks in the top ten."""
    scores = [1.0 + index / 4 for index in range(10)] + [5.0, 5.0]

    payload = build_web_overview(make_csv(scores))
    overview = payload["overview"]
    top_lecturers = overview["top_lecturers"]

    assert payload["cohort_size"] == 12
    assert overview["kpis"]["lecturer_count"] == 12
    assert len(top_lecturers) == 10
    assert [entry["rank"] for entry in top_lecturers[:3]] == [1, 1, 3]
    assert top_lecturers[0]["overall_score"] == 5.0
    assert top_lecturers[0]["rpi"] == overview["kpis"]["highest_rpi"]
    json.dumps(payload, allow_nan=False)


def test_institutional_analytics_matches_streamlit_cohort() -> None:
    """Match the Streamlit table and account for every RPI including tied scores."""
    csv = make_csv([5.0, 4.0, 4.0])
    payload = build_web_overview(csv)
    reference = AnalyticsController().run_uploaded_csv(BytesIO(csv))
    expected = _prepare_statistics_table(reference.statistics).rename(columns={
        "Score": "score", "Mean": "mean", "Median": "median",
        "Standard Deviation": "standard_deviation", "Variance": "variance",
        "Minimum": "minimum", "Maximum": "maximum",
    })
    institutional = payload["institutional_analytics"]
    pd.testing.assert_frame_equal(pd.DataFrame(institutional["statistics"]), expected)
    histogram = institutional["rpi_histogram"]
    assert [item["count"] for item in histogram] == [2, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    assert histogram[0]["lower"] == reference.analytics_data["rpi"].min()
    assert histogram[-1]["upper"] == reference.analytics_data["rpi"].max()
    assert payload["overview"]["kpis"]["quartile_distribution"] == {"Q1": 1, "Q2": 2, "Q3": 0, "Q4": 0}


def test_distribution_matches_streamlit_statistics_and_score_ranges() -> None:
    """Check both variables against the same cohort used by Streamlit."""
    csv = make_csv([5.0, 4.0, 4.0, 3.0, 3.0])
    payload = build_web_overview(csv)
    reference = AnalyticsController().run_uploaded_csv(BytesIO(csv))
    table = _prepare_distribution_table(reference.distribution_comparison)
    for key, label in (("edom", "Overall Score"), ("rpi", "RPI")):
        series = payload["distribution"][key]
        for metric, expected in zip(table["Metric"], table[label], strict=True):
            assert series["statistics"][metric.lower().replace(" ", "_")] == pytest.approx(expected)
        assert sum(interval["count"] for interval in series["histogram"]) == 5
        assert series["histogram"][0]["lower"] == table.loc[4, label]
        assert series["histogram"][-1]["upper"] == table.loc[5, label]
        assert series["boxplot"]["median"] == table.loc[1, label]
    assert payload["distribution"]["edom"]["boxplot"]["q1"] == 3.0
    assert payload["distribution"]["edom"]["boxplot"]["q3"] == 4.0


def test_lecturer_profiles_match_streamlit_beyond_top_ten() -> None:
    """Preserve the cohort ranking and all four dimensions for each profile."""
    csv = make_csv([1.0 + index / 4 for index in range(10)] + [5.0, 5.0])
    profiles = build_web_overview(csv)["lecturer_profiles"]
    reference = AnalyticsController().run_uploaded_csv(BytesIO(csv)).analytics_data
    assert len(profiles) == len(reference) == 12
    assert build_web_overview(csv)["analytics_csv"] == reference.to_csv(index=False)
    for profile, (_, lecturer) in zip(profiles, reference.iterrows(), strict=True):
        for field in ("lecturer_name", "study_program", "rpi", "rank", "quartile"):
            assert profile[field] == lecturer[field]
        dimensions = _prepare_dimension_summary(lecturer)
        assert [profile[column.lower()] for column in dimensions["Dimension"]] == dimensions["Score"].tolist()


def test_analytics_csv_escapes_spreadsheet_formulas_in_text_fields() -> None:
    """Protect spreadsheet users while preserving labels in the application."""
    csv = make_csv([4.0]).replace(b"Dosen sintetis 00", b" =1+1")
    payload = build_web_overview(csv)
    assert payload["lecturer_profiles"][0]["lecturer_name"] == " =1+1"
    exported = pd.read_csv(StringIO(payload["analytics_csv"]))
    assert exported.loc[0, "lecturer_name"] == "' =1+1"


def test_web_overview_preserves_structured_validation_errors() -> None:
    """Surface invalid indicator counts without creating a result."""
    with pytest.raises(DatasetValidationError) as captured:
        build_web_overview(make_csv([5.5]))

    assert captured.value.validation_result.errors["invalid_score_counts"] == dict.fromkeys(
        INDICATOR_COLUMNS, 1
    )


@pytest.mark.parametrize("csv_bytes", [b"", make_csv([])])
def test_web_overview_rejects_empty_uploads(csv_bytes: bytes) -> None:
    """Classify empty bodies and header-only files as input errors."""
    with pytest.raises(EmptyCsvFileError):
        build_web_overview(csv_bytes)


def test_web_overview_rejects_non_utf8_input() -> None:
    """Classify unsupported encoding as a CSV parse error."""
    with pytest.raises(ParserError, match="UTF-8"):
        build_web_overview(b"\xff")
