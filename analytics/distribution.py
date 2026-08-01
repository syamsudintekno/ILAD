"""Pure distribution comparison utilities for research validation."""

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

import numpy as np
from scipy import stats


class StatisticsLike(Protocol):
    """Describe the statistical mappings required for comparison."""

    mean: Mapping[str, float]
    median: Mapping[str, float]
    minimum: Mapping[str, float]
    maximum: Mapping[str, float]
    variance: Mapping[str, float]
    standard_deviation: Mapping[str, float]
    skewness: Mapping[str, float]
    kurtosis: Mapping[str, float]


@dataclass(frozen=True)
class DistributionSummary:
    """Descriptive distribution metrics for one score variable."""

    mean: float
    median: float
    variance: float
    standard_deviation: float
    minimum: float
    maximum: float
    skewness: float
    kurtosis: float


@dataclass(frozen=True)
class DistributionComparison:
    """Comparison of raw and transformed score distributions."""

    raw: DistributionSummary
    transformed: DistributionSummary
    interpretations: tuple[str, ...]


def calculate_skewness(values: Sequence[float]) -> float:
    """Calculate Fisher-Pearson skewness using the reference methodology.

    Args:
        values: Numeric observations to summarize.

    Returns:
        The distribution skewness.
    """
    return float(stats.skew(np.asarray(values, dtype=float)))


def calculate_kurtosis(values: Sequence[float]) -> float:
    """Calculate Fisher excess kurtosis using the reference methodology.

    Args:
        values: Numeric observations to summarize.

    Returns:
        The distribution excess kurtosis.
    """
    return float(stats.kurtosis(np.asarray(values, dtype=float)))


def compare_distributions(
    raw_statistics: StatisticsLike,
    transformed_statistics: StatisticsLike,
    raw_column: str,
    transformed_column: str,
) -> DistributionComparison:
    """Build a raw-versus-transformed comparison from precomputed statistics.

    Args:
        raw_statistics: Precomputed descriptive statistics for raw scores.
        transformed_statistics: Precomputed descriptive statistics for RPI.
        raw_column: Raw-score column key in ``raw_statistics``.
        transformed_column: RPI column key in ``transformed_statistics``.

    Returns:
        Structured distribution summaries and deterministic interpretations.
    """
    raw = _build_summary(raw_statistics, raw_column)
    transformed = _build_summary(transformed_statistics, transformed_column)
    return DistributionComparison(
        raw=raw,
        transformed=transformed,
        interpretations=_build_interpretations(raw, transformed),
    )


def _build_summary(statistics: StatisticsLike, column: str) -> DistributionSummary:
    """Extract one variable's metrics from a statistics result."""
    return DistributionSummary(
        mean=statistics.mean[column],
        median=statistics.median[column],
        variance=statistics.variance[column],
        standard_deviation=statistics.standard_deviation[column],
        minimum=statistics.minimum[column],
        maximum=statistics.maximum[column],
        skewness=statistics.skewness[column],
        kurtosis=statistics.kurtosis[column],
    )


def _build_interpretations(
    raw: DistributionSummary,
    transformed: DistributionSummary,
) -> tuple[str, ...]:
    """Generate deterministic research interpretations from metric changes."""
    variance_text = (
        "Variance increased after transformation."
        if transformed.variance > raw.variance
        else "Variance did not increase after transformation."
    )
    skewness_text = (
        "Distribution became more symmetric."
        if abs(transformed.skewness) < abs(raw.skewness)
        else "Distribution did not become more symmetric."
    )
    kurtosis_text = (
        "Kurtosis moved closer to a normal distribution."
        if abs(transformed.kurtosis) < abs(raw.kurtosis)
        else "Kurtosis did not move closer to a normal distribution."
    )
    return variance_text, skewness_text, kurtosis_text
