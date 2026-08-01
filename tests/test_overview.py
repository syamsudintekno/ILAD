"""Tests for Dashboard Overview presentation data preparation."""

import pandas as pd

from config.schema import (
    LECTURER_NAME_COLUMN,
    QUARTILE_COLUMN,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)
from pages.overview import _prepare_top_lecturer_table


def test_prepare_top_lecturer_table_sorts_and_limits_display_rows() -> None:
    """Order the visible lecturer table by RPI and retain required columns."""
    rows = [
        {
            RANK_COLUMN: index + 1,
            LECTURER_NAME_COLUMN: f"Lecturer {index}",
            STUDY_PROGRAM_COLUMN: "Informatics",
            RPI_COLUMN: float(index),
            QUARTILE_COLUMN: "Q1",
        }
        for index in range(11)
    ]

    result = _prepare_top_lecturer_table(pd.DataFrame(rows))

    assert len(result) == 10
    assert result.columns.tolist() == [
        "Rank",
        "Lecturer Name",
        "Study Program",
        "RPI",
        "Quartile",
    ]
    assert result["RPI"].tolist() == list(range(10, 0, -1))
