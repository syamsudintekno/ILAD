"""Institution-wide lecturer ranking for completed performance scores."""

import pandas as pd

from config.schema import RANK_COLUMN, RPI_COLUMN

__all__ = ["calculate_ranking"]


def calculate_ranking(
    df: pd.DataFrame,
    score_column: str = RPI_COLUMN,
) -> pd.DataFrame:
    """Sort lecturers by score and append competition-ranking positions.

    Args:
        df: Analytics dataset containing the score to rank.
        score_column: Existing column used for institution-wide ranking.

    Returns:
        A new DataFrame sorted by descending score with a replaced rank column.

    Raises:
        TypeError: If ``df`` is not a pandas DataFrame.
        ValueError: If ``score_column`` is not present in ``df``.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if score_column not in df.columns:
        raise ValueError(f"Required score column is missing: {score_column}")

    ranked = df.copy()
    ranked[RANK_COLUMN] = ranked[score_column].rank(
        ascending=False,
        method="min",
    ).astype(int)
    return ranked.sort_values(
        by=score_column,
        ascending=False,
        kind="mergesort",
    )
