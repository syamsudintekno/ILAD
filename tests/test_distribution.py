"""Tests for pure raw-score and RPI distribution comparison utilities."""

import pytest

from analytics.distribution import (
    calculate_kurtosis,
    calculate_skewness,
    compare_distributions,
)
from analytics.statistics import StatisticsResult


def test_calculate_skewness_matches_symmetric_data() -> None:
    """Return zero skewness for symmetric observations."""
    assert calculate_skewness([1.0, 2.0, 3.0, 4.0, 5.0]) == pytest.approx(0.0)


def test_calculate_kurtosis_matches_reference_excess_kurtosis() -> None:
    """Return SciPy Fisher excess kurtosis for a simple numeric sequence."""
    assert calculate_kurtosis([1.0, 2.0, 3.0, 4.0, 5.0]) == pytest.approx(-1.3)


def test_compare_distributions_returns_metrics_and_rule_based_text() -> None:
    """Build a structured comparison from precomputed statistics mappings."""
    raw_statistics = StatisticsResult(
        mean={"overall_score": 4.0},
        median={"overall_score": 4.0},
        minimum={"overall_score": 3.0},
        maximum={"overall_score": 5.0},
        variance={"overall_score": 0.2},
        standard_deviation={"overall_score": 0.45},
        skewness={"overall_score": 1.0},
        kurtosis={"overall_score": 1.5},
    )
    rpi_statistics = StatisticsResult(
        mean={"rpi": 50.0},
        median={"rpi": 50.0},
        minimum={"rpi": 35.0},
        maximum={"rpi": 65.0},
        variance={"rpi": 25.0},
        standard_deviation={"rpi": 5.0},
        skewness={"rpi": 0.1},
        kurtosis={"rpi": 0.2},
    )

    result = compare_distributions(
        raw_statistics,
        rpi_statistics,
        "overall_score",
        "rpi",
    )

    assert result.raw.variance == 0.2
    assert result.transformed.mean == 50.0
    assert result.interpretations == (
        "Variance increased after transformation.",
        "Distribution became more symmetric.",
        "Kurtosis moved closer to a normal distribution.",
    )
