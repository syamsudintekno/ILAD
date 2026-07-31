"""Descriptive statistics for prepared EDOM datasets."""

from dataclasses import dataclass
from typing import Mapping, Sequence

import pandas as pd

from config.schema import ANALYTIC_SCORE_COLUMNS


@dataclass(frozen=True)
class StatisticsResult:
    """Population descriptive statistics keyed by score-column name.

    Attributes:
        mean: Arithmetic mean for each score column.
        median: Median for each score column.
        minimum: Smallest value for each score column.
        maximum: Largest value for each score column.
        variance: Population variance for each score column.
        standard_deviation: Population standard deviation for each score column.
    """

    mean: Mapping[str, float]
    median: Mapping[str, float]
    minimum: Mapping[str, float]
    maximum: Mapping[str, float]
    variance: Mapping[str, float]
    standard_deviation: Mapping[str, float]


def calculate_descriptive_statistics(
    dataset: pd.DataFrame,
    score_columns: Sequence[str] = ANALYTIC_SCORE_COLUMNS,
) -> StatisticsResult:
    """Calculate population descriptive statistics for prepared EDOM scores.

    Args:
        dataset: Prepared lecturer-level dataset from the Data Processing Layer.
        score_columns: Score columns to summarize.

    Returns:
        Population descriptive statistics keyed by selected score-column name.

    Raises:
        TypeError: If ``dataset`` is not a pandas DataFrame.
    """
    if not isinstance(dataset, pd.DataFrame):
        raise TypeError("dataset must be a pandas DataFrame")

    selected_scores = dataset.loc[:, list(score_columns)]
    return StatisticsResult(
        mean=_to_float_mapping(selected_scores.mean()),
        median=_to_float_mapping(selected_scores.median()),
        minimum=_to_float_mapping(selected_scores.min()),
        maximum=_to_float_mapping(selected_scores.max()),
        variance=_to_float_mapping(selected_scores.var(ddof=0)),
        standard_deviation=_to_float_mapping(selected_scores.std(ddof=0)),
    )


def _to_float_mapping(values: pd.Series) -> dict[str, float]:
    """Convert a statistics Series into a plain typed mapping."""
    return {str(column): float(value) for column, value in values.items()}
