"""Tests for Lecturer Profile presentation data preparation."""

import pandas as pd

from config.schema import DIMENSION_COLUMNS
from pages.lecturer import _prepare_dimension_summary


def test_prepare_dimension_summary_uses_configured_dimension_scores() -> None:
    """Return direct competency values with presentation labels."""
    lecturer = pd.Series(
        {
            "pedagogic": 4.0,
            "professional": 3.5,
            "personality": 4.5,
            "social": 3.0,
        }
    )

    result = _prepare_dimension_summary(lecturer)

    assert result.to_dict("records") == [
        {"Dimension": column.title(), "Score": float(lecturer[column])}
        for column in DIMENSION_COLUMNS
    ]
