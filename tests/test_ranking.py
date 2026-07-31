"""Tests for institution-wide lecturer ranking."""

import pandas as pd
import pytest

from analytics.ranking import calculate_ranking
from config.schema import RANK_COLUMN, RPI_COLUMN


def make_analytics_dataset() -> pd.DataFrame:
    """Create a synthetic analytics dataset with tied RPI values."""
    return pd.DataFrame(
        {
            "lecturer_name": ["Dr. Ani", "Dr. Budi", "Dr. Citra", "Dr. Deni"],
            RPI_COLUMN: [70.0, 80.0, 80.0, 60.0],
        }
    )


def test_calculate_ranking_uses_competition_ranks_and_stable_sort() -> None:
    """Use minimum ranks and retain incoming tie order after sorting."""
    dataset = make_analytics_dataset()

    result = calculate_ranking(dataset)

    assert result["lecturer_name"].tolist() == [
        "Dr. Budi",
        "Dr. Citra",
        "Dr. Ani",
        "Dr. Deni",
    ]
    assert result[RANK_COLUMN].tolist() == [1, 1, 3, 4]
    assert RANK_COLUMN not in dataset.columns


def test_calculate_ranking_replaces_existing_rank_in_returned_copy() -> None:
    """Replace a stale rank column without changing the input DataFrame."""
    dataset = make_analytics_dataset()
    dataset[RANK_COLUMN] = [99, 99, 99, 99]
    original = dataset.copy(deep=True)

    result = calculate_ranking(dataset)

    assert result[RANK_COLUMN].tolist() == [1, 1, 3, 4]
    pd.testing.assert_frame_equal(dataset, original)


def test_calculate_ranking_accepts_an_explicit_score_column() -> None:
    """Allow callers to rank a completed alternative performance score."""
    dataset = make_analytics_dataset().assign(performance_score=[4.0, 3.0, 2.0, 1.0])

    result = calculate_ranking(dataset, score_column="performance_score")

    assert result["lecturer_name"].tolist() == [
        "Dr. Ani",
        "Dr. Budi",
        "Dr. Citra",
        "Dr. Deni",
    ]
    assert result[RANK_COLUMN].tolist() == [1, 2, 3, 4]


def test_calculate_ranking_rejects_a_missing_score_column() -> None:
    """Report a clear error when the requested score is absent."""
    with pytest.raises(ValueError, match="Required score column is missing"):
        calculate_ranking(make_analytics_dataset(), score_column="missing_score")
