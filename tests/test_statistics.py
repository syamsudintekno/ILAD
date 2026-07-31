"""Tests for descriptive analytics statistics."""

import math

import pandas as pd
import pytest

from analytics.statistics import StatisticsResult, calculate_descriptive_statistics
from config.schema import ANALYTIC_SCORE_COLUMNS


def make_prepared_dataset() -> pd.DataFrame:
    """Create a synthetic prepared dataset for descriptive statistics."""
    return pd.DataFrame(
        {
            "lecturer_name": ["Dr. Ani", "Dr. Budi", "Dr. Citra"],
            "study_program": ["Informatics", "Informatics", "Information Systems"],
            "pedagogic": [1.0, 3.0, 5.0],
            "professional": [2.0, 4.0, 5.0],
            "personality": [3.0, 3.0, 3.0],
            "social": [5.0, 4.0, 3.0],
            "overall_score": [2.75, 3.5, 4.0],
        }
    )


def test_calculate_descriptive_statistics_uses_all_default_scores() -> None:
    """Return population metrics for every configured analytic score."""
    result = calculate_descriptive_statistics(make_prepared_dataset())

    assert isinstance(result, StatisticsResult)
    assert tuple(result.mean) == ANALYTIC_SCORE_COLUMNS
    assert result.mean["pedagogic"] == 3.0
    assert result.median["professional"] == 4.0
    assert result.minimum["social"] == 3.0
    assert result.maximum["overall_score"] == 4.0


def test_calculate_descriptive_statistics_uses_population_dispersion() -> None:
    """Use ddof=0 for variance and standard deviation."""
    dataset = make_prepared_dataset()

    result = calculate_descriptive_statistics(dataset, score_columns=("pedagogic",))

    assert result.variance == {"pedagogic": pytest.approx(8 / 3)}
    assert result.standard_deviation == {
        "pedagogic": pytest.approx(math.sqrt(8 / 3))
    }


def test_calculate_descriptive_statistics_accepts_selected_score_columns() -> None:
    """Support focused summaries through the optional score-columns argument."""
    result = calculate_descriptive_statistics(
        make_prepared_dataset(),
        score_columns=("professional", "social"),
    )

    assert result.mean == {"professional": pytest.approx(11 / 3), "social": 4.0}
    assert set(result.median) == {"professional", "social"}


def test_calculate_descriptive_statistics_rejects_non_dataframe_input() -> None:
    """Reject programmer errors without duplicating Data Layer validation."""
    with pytest.raises(TypeError, match="pandas DataFrame"):
        calculate_descriptive_statistics([])
