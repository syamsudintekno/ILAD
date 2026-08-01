"""Tests for Institutional Analytics presentation data preparation."""

from analytics.statistics import StatisticsResult
from pages.analytics import _prepare_statistics_table


def test_prepare_statistics_table_uses_precomputed_result_values() -> None:
    """Present all requested descriptive metrics without recomputation."""
    statistics = StatisticsResult(
        mean={"overall_score": 4.0},
        median={"overall_score": 4.0},
        minimum={"overall_score": 3.0},
        maximum={"overall_score": 5.0},
        variance={"overall_score": 0.5},
        standard_deviation={"overall_score": 0.71},
    )

    result = _prepare_statistics_table(statistics)

    assert result.to_dict("records") == [
        {
            "Score": "overall_score",
            "Mean": 4.0,
            "Median": 4.0,
            "Standard Deviation": 0.71,
            "Variance": 0.5,
            "Minimum": 3.0,
            "Maximum": 5.0,
        }
    ]
