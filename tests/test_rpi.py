"""Tests for the notebook-based Relative Performance Index calculation."""

import pandas as pd
import pytest
from scipy import stats

from analytics.rpi import calculate_rpi
from config.schema import DEFAULT_RPI_WEIGHTS, DIMENSION_COLUMNS, RPI_COLUMN


def make_prepared_dataset() -> pd.DataFrame:
    """Create a synthetic prepared dataset with four competency dimensions."""
    return pd.DataFrame(
        {
            "lecturer_name": ["Dr. Ani", "Dr. Budi", "Dr. Citra"],
            "study_program": ["Informatics", "Informatics", "Information Systems"],
            "pedagogic": [1.0, 3.0, 5.0],
            "professional": [1.0, 3.0, 5.0],
            "personality": [1.0, 3.0, 5.0],
            "social": [1.0, 3.0, 5.0],
            "overall_score": [1.0, 3.0, 5.0],
        }
    )


def test_calculate_rpi_matches_blom_rankit_and_t_score_scaling() -> None:
    """Match the reference pipeline for identical dimension profiles."""
    dataset = make_prepared_dataset()

    result = calculate_rpi(dataset)

    ranks = stats.rankdata(dataset["pedagogic"], method="average")
    probabilities = (ranks - 0.375) / (len(dataset) - 2 * 0.375 + 1)
    expected_rpi = 50 + 10 * stats.norm.ppf(probabilities)
    assert result[RPI_COLUMN].tolist() == pytest.approx(expected_rpi.tolist())
    assert result.columns.tolist() == dataset.columns.tolist() + [RPI_COLUMN]
    pd.testing.assert_frame_equal(dataset, make_prepared_dataset())


def test_calculate_rpi_uses_average_ranks_for_tied_dimension_scores() -> None:
    """Assign tied competency values their average rank before rankit."""
    dataset = make_prepared_dataset()
    for column in DIMENSION_COLUMNS:
        dataset[column] = [2.0, 2.0, 5.0]

    result = calculate_rpi(dataset)

    tied_rank = 1.5
    probability = (tied_rank - 0.375) / (len(dataset) - 2 * 0.375 + 1)
    expected_tied_rpi = 50 + 10 * stats.norm.ppf(probability)
    assert result.loc[0, RPI_COLUMN] == pytest.approx(expected_tied_rpi)
    assert result.loc[1, RPI_COLUMN] == pytest.approx(expected_tied_rpi)


def test_calculate_rpi_combines_dimensions_with_custom_weights() -> None:
    """Use explicit weights when calculating the composite RPI Z-score."""
    dataset = make_prepared_dataset()
    dataset["professional"] = [5.0, 3.0, 1.0]
    weights = {
        "pedagogic": 0.4,
        "professional": 0.3,
        "personality": 0.2,
        "social": 0.1,
    }

    result = calculate_rpi(dataset, weights=weights)

    z_scores = {
        column: stats.norm.ppf(
            (stats.rankdata(dataset[column], method="average") - 0.375)
            / (len(dataset) - 2 * 0.375 + 1)
        )
        for column in DIMENSION_COLUMNS
    }
    expected = 50 + 10 * sum(weights[column] * z_scores[column] for column in weights)
    assert result[RPI_COLUMN].tolist() == pytest.approx(expected.tolist())


def test_calculate_rpi_uses_configured_defaults() -> None:
    """Use the four configured dimensions and equal default weights."""
    assert tuple(DEFAULT_RPI_WEIGHTS) == DIMENSION_COLUMNS
    assert tuple(DEFAULT_RPI_WEIGHTS.values()) == (0.25, 0.25, 0.25, 0.25)


def test_calculate_rpi_rejects_weights_that_do_not_sum_to_one() -> None:
    """Reject a manual weight scheme that differs from the methodology."""
    invalid_weights = {column: 0.3 for column in DIMENSION_COLUMNS}

    with pytest.raises(ValueError, match="weights must sum to one"):
        calculate_rpi(make_prepared_dataset(), weights=invalid_weights)
