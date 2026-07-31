"""Institutional KPI generation for completed analytics datasets."""

import pandas as pd

from config.schema import (
    QUARTILE_COLUMN,
    QUARTILE_LABELS,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)

__all__ = ["calculate_institutional_kpis"]


def calculate_institutional_kpis(
    df: pd.DataFrame,
    score_column: str = RPI_COLUMN,
) -> dict[str, float | int | dict[str, int]]:
    """Calculate institutional KPIs from completed analytics data.

    Args:
        df: Analytics dataset with performance scores and quartile labels.
        score_column: Existing score column used for RPI summary KPIs.

    Returns:
        Institutional score summaries, counts, and quartile distribution.

    Raises:
        TypeError: If ``df`` is not a pandas DataFrame.
        ValueError: If the dataset is empty or required columns are missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        raise ValueError("Cannot calculate KPIs for an empty dataset")
    _ensure_required_columns(df, score_column)

    scores = df[score_column]
    return {
        "average_rpi": float(scores.mean()),
        "highest_rpi": float(scores.max()),
        "lowest_rpi": float(scores.min()),
        "lecturer_count": int(len(df)),
        "study_program_count": int(df[STUDY_PROGRAM_COLUMN].nunique()),
        "quartile_distribution": _calculate_quartile_distribution(df),
    }


def _ensure_required_columns(df: pd.DataFrame, score_column: str) -> None:
    """Raise a ValueError if a required KPI input column is absent."""
    required_columns = (score_column, STUDY_PROGRAM_COLUMN, QUARTILE_COLUMN)
    missing_columns = [column for column in required_columns if column not in df]
    if missing_columns:
        joined_columns = ", ".join(missing_columns)
        raise ValueError(f"Required KPI column is missing: {joined_columns}")


def _calculate_quartile_distribution(df: pd.DataFrame) -> dict[str, int]:
    """Return counts for every configured executive quartile label."""
    counts = df[QUARTILE_COLUMN].value_counts().reindex(
        QUARTILE_LABELS,
        fill_value=0,
    )
    return {label: int(count) for label, count in counts.items()}
