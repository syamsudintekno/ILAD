"""Tests for the Application Layer analytics controller."""

from dataclasses import FrozenInstanceError
from io import BytesIO

import pandas as pd
import pytest

from application.controller import AnalyticsController, AnalyticsRunResult
from config.schema import QUARTILE_COLUMN, RANK_COLUMN, RPI_COLUMN


def make_prepared_dataset() -> pd.DataFrame:
    """Create synthetic lecturer-level data for the controller workflow."""
    return pd.DataFrame(
        {
            "lecturer_name": ["Dr. Ani", "Dr. Budi", "Dr. Citra"],
            "study_program": ["Informatics", "Informatics", "Information Systems"],
            "pedagogic": [1.0, 3.0, 5.0],
            "professional": [1.0, 3.0, 5.0],
            "personality": [1.0, 3.0, 5.0],
            "social": [1.0, 3.0, 5.0],
            "overall_score": [1.0, 3.0, 5.0],
        }
    )


def test_run_analytics_orchestrates_completed_analytics_pipeline() -> None:
    """Return analytics data, descriptive statistics, and KPIs together."""
    prepared_data = make_prepared_dataset()

    result = AnalyticsController().run_analytics(prepared_data)

    assert isinstance(result, AnalyticsRunResult)
    assert {RPI_COLUMN, RANK_COLUMN, QUARTILE_COLUMN}.issubset(
        result.analytics_data.columns
    )
    assert result.kpis["lecturer_count"] == len(prepared_data)
    assert result.statistics.mean["overall_score"] == 3.0
    pd.testing.assert_frame_equal(prepared_data, make_prepared_dataset())


def test_analytics_run_result_is_frozen() -> None:
    """Prevent reassignment of completed application-level outputs."""
    result = AnalyticsController().run_analytics(make_prepared_dataset())

    with pytest.raises(FrozenInstanceError):
        result.kpis = {}


def test_run_uploaded_csv_delegates_data_and_analytics_pipeline() -> None:
    """Process a synthetic upload through Data and Analytics Layer services."""
    row = {
        "lecturer_name": "Dr. Ani",
        "study_program": "Informatics",
        "faculty": "Engineering",
    }
    row.update({f"P{number}": 4 for number in range(1, 21)})
    uploaded_file = BytesIO(pd.DataFrame([row]).to_csv(index=False).encode("utf-8"))

    result = AnalyticsController().run_uploaded_csv(uploaded_file)

    assert result.kpis["lecturer_count"] == 1
    assert {RPI_COLUMN, RANK_COLUMN, QUARTILE_COLUMN}.issubset(
        result.analytics_data.columns
    )
