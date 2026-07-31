"""Executive-oriented quartile classification for performance scores."""

import pandas as pd

from config.schema import QUARTILE_COLUMN, QUARTILE_LABELS, RPI_COLUMN

__all__ = ["calculate_quartiles"]


def calculate_quartiles(
    df: pd.DataFrame,
    score_column: str = RPI_COLUMN,
) -> pd.DataFrame:
    """Append executive-oriented quartile labels from institutional scores.

    Q1 contains the highest scores and Q4 contains the lowest. Scores tied at a
    percentile boundary remain in the higher-performing quartile.

    Args:
        df: Analytics dataset containing the score to classify.
        score_column: Existing column used for institution-wide classification.

    Returns:
        A new DataFrame with a replaced quartile column.

    Raises:
        TypeError: If ``df`` is not a pandas DataFrame.
        ValueError: If ``score_column`` is not present in ``df``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if score_column not in df.columns:
        raise ValueError(f"Required score column is missing: {score_column}")

    lower, median, upper = _calculate_boundaries(df[score_column])
    result = df.copy()
    result[QUARTILE_COLUMN] = _assign_quartiles(
        result[score_column],
        lower,
        median,
        upper,
    )
    return result


def _calculate_boundaries(scores: pd.Series) -> tuple[float, float, float]:
    """Calculate linear 25th, 50th, and 75th percentile boundaries."""
    quartiles = scores.quantile([0.25, 0.5, 0.75], interpolation="linear")
    return float(quartiles.iloc[0]), float(quartiles.iloc[1]), float(quartiles.iloc[2])


def _assign_quartiles(
    scores: pd.Series,
    lower: float,
    median: float,
    upper: float,
) -> pd.Series:
    """Assign Q1--Q4 without splitting tied scores at score boundaries."""
    labels = pd.Series(QUARTILE_LABELS[-1], index=scores.index, dtype="object")
    labels.loc[scores >= lower] = QUARTILE_LABELS[-2]
    labels.loc[scores >= median] = QUARTILE_LABELS[-3]
    labels.loc[scores >= upper] = QUARTILE_LABELS[0]
    return labels
