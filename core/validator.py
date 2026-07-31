"""Non-mutating validation utilities for EDOM datasets."""

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import pandas as pd


IDENTITY_COLUMNS: tuple[str, ...] = (
    "lecturer_name",
    "study_program",
    "faculty",
)
INDICATOR_COLUMNS: tuple[str, ...] = tuple(f"P{number}" for number in range(1, 21))
REQUIRED_COLUMNS: tuple[str, ...] = IDENTITY_COLUMNS + INDICATOR_COLUMNS


@dataclass(frozen=True)
class ValidationResult:
    """Structured issues found while checking an EDOM dataset.

    The fields are intentionally additive so later pipeline stages can consume
    validation metadata without changing the validator's non-mutating contract.

    Attributes:
        missing_columns: Required columns absent from the dataset.
        duplicate_row_count: Number of rows that duplicate an earlier row.
        missing_values: Count of missing values by present column.
        invalid_score_counts: Invalid P1--P20 values by present indicator.
    """

    missing_columns: tuple[str, ...] = ()
    duplicate_row_count: int = 0
    missing_values: Mapping[str, int] = field(default_factory=dict)
    invalid_score_counts: Mapping[str, int] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Return whether the dataset contains no detected validation issues."""
        return not (
            self.missing_columns
            or self.duplicate_row_count
            or self.missing_values
            or self.invalid_score_counts
        )


def validate_dataset(
    dataset: pd.DataFrame,
    required_columns: Sequence[str] = REQUIRED_COLUMNS,
) -> ValidationResult:
    """Validate an EDOM dataset without changing it.

    Args:
        dataset: Dataset to inspect.
        required_columns: Columns that must be present for downstream processing.

    Returns:
        A structured description of the detected issues.

    Raises:
        TypeError: If ``dataset`` is not a pandas DataFrame.
    """
    if not isinstance(dataset, pd.DataFrame):
        raise TypeError("dataset must be a pandas DataFrame")

    missing_columns = tuple(
        column for column in required_columns if column not in dataset.columns
    )
    return ValidationResult(
        missing_columns=missing_columns,
        duplicate_row_count=int(dataset.duplicated().sum()),
        missing_values=_find_missing_values(dataset),
        invalid_score_counts=_find_invalid_scores(dataset),
    )


def _find_missing_values(dataset: pd.DataFrame) -> dict[str, int]:
    """Return missing-value counts for columns that contain missing data."""
    counts = dataset.isna().sum()
    return {column: int(count) for column, count in counts.items() if count > 0}


def _find_invalid_scores(dataset: pd.DataFrame) -> dict[str, int]:
    """Return counts of non-missing P1--P20 values outside the 1--5 range."""
    invalid_counts: dict[str, int] = {}
    for column in INDICATOR_COLUMNS:
        if column not in dataset.columns:
            continue
        numeric_scores = pd.to_numeric(dataset[column], errors="coerce")
        invalid = dataset[column].notna() & (
            numeric_scores.isna() | ~numeric_scores.between(1, 5)
        )
        invalid_count = int(invalid.sum())
        if invalid_count:
            invalid_counts[column] = invalid_count
    return invalid_counts
