"""Tests for Dashboard Overview presentation data preparation."""

import pandas as pd

from application.controller import AnalyticsRunResult
from config.schema import (
    LECTURER_NAME_COLUMN,
    QUARTILE_COLUMN,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)
from pages.overview import (
    ANALYTICS_RESULT_SESSION_KEY,
    PREPARED_DATA_SESSION_KEY,
    UPLOADED_FILENAME_SESSION_KEY,
    _prepare_top_lecturer_table,
    _store_processed_dataset,
)


def test_prepare_top_lecturer_table_sorts_and_limits_display_rows() -> None:
    """Order the visible lecturer table by RPI and retain required columns."""
    rows = [
        {
            RANK_COLUMN: index + 1,
            LECTURER_NAME_COLUMN: f"Lecturer {index}",
            STUDY_PROGRAM_COLUMN: "Informatics",
            RPI_COLUMN: float(index),
            QUARTILE_COLUMN: "Q1",
        }
        for index in range(11)
    ]

    result = _prepare_top_lecturer_table(pd.DataFrame(rows))

    assert len(result) == 10
    assert result.columns.tolist() == [
        "Rank",
        "Lecturer Name",
        "Study Program",
        "RPI",
        "Quartile",
    ]
    assert result["RPI"].tolist() == list(range(10, 0, -1))


def test_store_processed_dataset_retains_only_processed_session_values() -> None:
    """Persist prepared data, analytics result, and filename without uploads."""
    analytics_data = pd.DataFrame(
        {
            LECTURER_NAME_COLUMN: ["Dr. Ani"],
            STUDY_PROGRAM_COLUMN: ["Informatics"],
            "pedagogic": [4.0],
            "professional": [4.0],
            "personality": [4.0],
            "social": [4.0],
            "overall_score": [4.0],
            RPI_COLUMN: [50.0],
            RANK_COLUMN: [1],
            QUARTILE_COLUMN: ["Q1"],
        }
    )
    analytics_result = AnalyticsRunResult(
        analytics_data=analytics_data,
        statistics=None,
        kpis={},
    )
    session_state: dict[str, object] = {}

    _store_processed_dataset(session_state, analytics_result, "synthetic.csv")

    assert session_state[ANALYTICS_RESULT_SESSION_KEY] is analytics_result
    assert session_state[UPLOADED_FILENAME_SESSION_KEY] == "synthetic.csv"
    assert session_state[PREPARED_DATA_SESSION_KEY].columns.tolist() == [
        LECTURER_NAME_COLUMN,
        STUDY_PROGRAM_COLUMN,
        "pedagogic",
        "professional",
        "personality",
        "social",
        "overall_score",
    ]
