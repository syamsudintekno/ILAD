"""Tests for executive-oriented RPI quartile classification."""

import pandas as pd
import pytest

from analytics.quartile import calculate_quartiles
from config.schema import QUARTILE_COLUMN, RPI_COLUMN


def test_calculate_quartiles_assigns_highest_scores_to_q1() -> None:
    """Classify scores with explicit linear percentile boundaries."""
    dataset = pd.DataFrame({RPI_COLUMN: [10.0, 20.0, 30.0, 40.0]})

    result = calculate_quartiles(dataset)

    assert result[QUARTILE_COLUMN].tolist() == ["Q4", "Q3", "Q2", "Q1"]
    assert QUARTILE_COLUMN not in dataset.columns


def test_calculate_quartiles_does_not_split_tied_boundary_scores() -> None:
    """Keep all scores tied at the upper boundary in Q1."""
    dataset = pd.DataFrame({RPI_COLUMN: [10.0, 20.0, 20.0, 20.0]})

    result = calculate_quartiles(dataset)

    assert result.loc[result[RPI_COLUMN] == 20.0, QUARTILE_COLUMN].tolist() == [
        "Q1",
        "Q1",
        "Q1",
    ]


def test_calculate_quartiles_replaces_existing_column_in_returned_copy() -> None:
    """Replace stale quartile values without mutating the source data."""
    dataset = pd.DataFrame(
        {RPI_COLUMN: [10.0, 20.0, 30.0, 40.0], QUARTILE_COLUMN: ["Q1"] * 4}
    )
    original = dataset.copy(deep=True)

    result = calculate_quartiles(dataset)

    assert result[QUARTILE_COLUMN].tolist() == ["Q4", "Q3", "Q2", "Q1"]
    pd.testing.assert_frame_equal(dataset, original)


def test_calculate_quartiles_rejects_missing_score_column() -> None:
    """Report a clear error when the requested score is absent."""
    with pytest.raises(ValueError, match="Required score column is missing"):
        calculate_quartiles(pd.DataFrame({"other_score": [1.0]}))
