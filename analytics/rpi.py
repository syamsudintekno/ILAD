"""Relative Performance Index calculation for prepared EDOM datasets."""

from collections.abc import Mapping, Sequence

import pandas as pd
from scipy import stats

from config.schema import (
    DEFAULT_RPI_WEIGHTS,
    DIMENSION_COLUMNS,
    RPI_COLUMN,
)

__all__ = ["calculate_rpi"]

_BLOM_CONSTANT = 0.375
_T_SCORE_MEAN = 50.0
_T_SCORE_STANDARD_DEVIATION = 10.0


def calculate_rpi(
    df: pd.DataFrame,
    dimension_columns: Sequence[str] | None = None,
    weights: Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """Append RPI scores calculated from EDOM competency dimensions.

    The calculation follows the reference methodology: average-rank ties,
    Blom rankit transformation, inverse-normal transformation, equal-weighted
    dimension combination, and T-score scaling.

    Args:
        df: Prepared lecturer-level EDOM dataset.
        dimension_columns: Competency columns used for RPI calculation.
        weights: Weights keyed by competency column. They must sum to one.

    Returns:
        A copy of ``df`` with one additional RPI column.

    Raises:
        TypeError: If ``df`` is not a pandas DataFrame.
        ValueError: If dimensions and weights do not match or weights do not sum
            to one.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    columns = tuple(dimension_columns or DIMENSION_COLUMNS)
    resolved_weights = _resolve_weights(columns, weights)
    dimension_z_scores = _calculate_dimension_z_scores(df, columns)
    rpi_z_scores = _combine_weighted_z_scores(dimension_z_scores, resolved_weights)
    result = df.copy()
    result[RPI_COLUMN] = _scale_to_rpi(rpi_z_scores)
    return result


def _calculate_dimension_z_scores(
    df: pd.DataFrame,
    dimension_columns: Sequence[str],
) -> pd.DataFrame:
    """Calculate rankit Z-scores for each selected competency dimension."""
    return pd.DataFrame(
        {
            column: _rankit_z_scores(df[column])
            for column in dimension_columns
        },
        index=df.index,
    )


def _rankit_z_scores(values: pd.Series) -> pd.Series:
    """Apply average ranks, Blom plotting positions, and inverse normal CDF."""
    sample_size = len(values)
    ranks = stats.rankdata(values, method="average")
    probabilities = (ranks - _BLOM_CONSTANT) / (
        sample_size - 2 * _BLOM_CONSTANT + 1
    )
    return pd.Series(stats.norm.ppf(probabilities), index=values.index)


def _combine_weighted_z_scores(
    dimension_z_scores: pd.DataFrame,
    weights: Mapping[str, float],
) -> pd.Series:
    """Combine dimension Z-scores using the configured RPI weights."""
    return sum(
        weights[column] * dimension_z_scores[column]
        for column in dimension_z_scores.columns
    )


def _scale_to_rpi(rpi_z_scores: pd.Series) -> pd.Series:
    """Scale composite Z-scores to the reference RPI T-score scale."""
    return _T_SCORE_MEAN + _T_SCORE_STANDARD_DEVIATION * rpi_z_scores


def _resolve_weights(
    dimension_columns: Sequence[str],
    weights: Mapping[str, float] | None,
) -> Mapping[str, float]:
    """Return validated weights for the dimensions included in RPI."""
    resolved_weights = DEFAULT_RPI_WEIGHTS if weights is None else weights
    if set(resolved_weights) != set(dimension_columns):
        raise ValueError("weights must contain exactly the selected dimensions")
    if abs(sum(resolved_weights.values()) - 1.0) >= 1e-6:
        raise ValueError("weights must sum to one")
    return resolved_weights
