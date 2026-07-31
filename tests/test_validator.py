"""Tests for non-mutating EDOM dataset validation."""

import pandas as pd

from core.validator import REQUIRED_COLUMNS, ValidationResult, validate_dataset


def make_valid_dataset() -> pd.DataFrame:
    """Create one valid synthetic EDOM row."""
    row = {
        "lecturer_name": "Dr. Ani",
        "study_program": "Informatics",
        "faculty": "Engineering",
    }
    row.update({column: 5 for column in REQUIRED_COLUMNS if column.startswith("P")})
    return pd.DataFrame([row])


def test_validate_dataset_returns_valid_typed_result() -> None:
    """Return a valid ValidationResult for a complete synthetic dataset."""
    result = validate_dataset(make_valid_dataset())

    assert isinstance(result, ValidationResult)
    assert result.is_valid


def test_validate_dataset_reports_issues_without_mutating_data() -> None:
    """Detect required issues while preserving the original DataFrame."""
    dataset = make_valid_dataset()
    dataset.loc[1] = dataset.loc[0]
    dataset.loc[0, "P1"] = 6
    dataset.loc[1, "P2"] = None
    original = dataset.copy(deep=True)

    result = validate_dataset(dataset)

    assert result.missing_columns == ()
    assert result.duplicate_row_count == 0
    assert result.missing_values == {"P2": 1}
    assert result.invalid_score_counts == {"P1": 1}
    pd.testing.assert_frame_equal(dataset, original)


def test_validate_dataset_reports_missing_columns_and_duplicates() -> None:
    """Detect absent schema columns and duplicated rows."""
    dataset = pd.DataFrame({"lecturer_name": ["Dr. Ani", "Dr. Ani"]})

    result = validate_dataset(dataset)

    assert result.duplicate_row_count == 1
    assert set(result.missing_columns) == set(REQUIRED_COLUMNS) - {"lecturer_name"}
