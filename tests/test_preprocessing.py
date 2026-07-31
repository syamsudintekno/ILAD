"""Tests for EDOM preprocessing."""

import pandas as pd
import pytest

from config.schema import (
    COMPETENCY_MAPPING,
    INDICATOR_COLUMNS,
    PREPARED_COLUMNS,
    REQUIRED_COLUMNS,
)
from core.preprocessing import (
    aggregate_by_lecturer,
    map_competency_dimensions,
    preprocess_dataset,
    standardize_column_names,
)


def make_raw_dataset() -> pd.DataFrame:
    """Create synthetic records for one lecturer."""
    first_row = {
        " Lecturer Name ": "Dr. Ani",
        "Study Program": "Informatics",
        "Faculty": "Engineering",
    }
    second_row = first_row.copy()
    first_row.update({column.lower(): 4 for column in INDICATOR_COLUMNS})
    second_row.update({column.lower(): 2 for column in INDICATOR_COLUMNS})
    return pd.DataFrame([first_row, second_row])


def test_standardize_column_names_uses_canonical_schema() -> None:
    """Normalize identity and indicator labels without mutating input data."""
    dataset = make_raw_dataset()

    result = standardize_column_names(dataset)

    assert tuple(result.columns) == REQUIRED_COLUMNS
    assert tuple(dataset.columns) != REQUIRED_COLUMNS


def test_map_competency_dimensions_uses_central_mapping() -> None:
    """Calculate each competency using the configured indicators."""
    dataset = standardize_column_names(make_raw_dataset())
    dataset.loc[0, "P1"] = 2

    result = map_competency_dimensions(dataset)

    assert result.loc[0, "pedagogic"] == pytest.approx(22 / 6)
    assert result.loc[0, "professional"] == 4
    assert result.loc[0, "personality"] == 4
    assert result.loc[0, "social"] == 4
    assert set(COMPETENCY_MAPPING) == {
        "pedagogic",
        "professional",
        "personality",
        "social",
    }


def test_preprocess_dataset_returns_lecturer_level_means() -> None:
    """Aggregate repeated synthetic records into one prepared lecturer row."""
    result = preprocess_dataset(make_raw_dataset())

    assert len(result) == 1
    assert tuple(result.columns) == PREPARED_COLUMNS
    assert result.loc[0, "lecturer_name"] == "Dr. Ani"
    assert result.loc[0, "P1"] == 3
    assert result.loc[0, "pedagogic"] == 3
    assert result.loc[0, "overall_score"] == 3


def test_preprocess_dataset_rejects_missing_required_columns() -> None:
    """Fail with a useful error when required data is absent."""
    dataset = make_raw_dataset().drop(columns=["p20"])

    with pytest.raises(ValueError, match="P20"):
        preprocess_dataset(dataset)


def test_aggregate_by_lecturer_requires_enriched_columns() -> None:
    """Require enrichment before performing lecturer-level aggregation."""
    dataset = standardize_column_names(make_raw_dataset())

    with pytest.raises(ValueError, match="pedagogic"):
        aggregate_by_lecturer(dataset)
