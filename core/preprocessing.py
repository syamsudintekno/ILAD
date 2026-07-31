"""EDOM dataset preparation for the Analytics Layer."""

import pandas as pd

from config.schema import (
    COMPETENCY_COLUMNS,
    COMPETENCY_MAPPING,
    INDICATOR_COLUMNS,
    LECTURER_NAME_COLUMN,
    OVERALL_SCORE_COLUMN,
    PREPARED_COLUMNS,
    REQUIRED_COLUMNS,
    STUDY_PROGRAM_COLUMN,
)


def preprocess_dataset(dataset: pd.DataFrame) -> pd.DataFrame:
    """Standardize, enrich, and aggregate an EDOM dataset by lecturer.

    Args:
        dataset: Validated EDOM records to prepare for analytics.

    Returns:
        A lecturer-level dataset containing study program, competency
        dimensions, and overall scores.

    Raises:
        TypeError: If ``dataset`` is not a pandas DataFrame.
        ValueError: If required EDOM columns are absent after normalization.
    """
    standardized = standardize_column_names(dataset)
    _ensure_required_columns(standardized)
    enriched = map_competency_dimensions(standardized)
    return aggregate_by_lecturer(enriched)


def standardize_column_names(dataset: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with canonical EDOM column names.

    Args:
        dataset: Dataset whose column labels require normalization.

    Returns:
        A copy with whitespace-trimmed identity columns and uppercase P columns.

    Raises:
        TypeError: If ``dataset`` is not a pandas DataFrame.
        ValueError: If normalization creates duplicate column names.
    """
    _ensure_dataframe(dataset)
    standardized = dataset.copy()
    standardized.columns = [_normalize_column_name(column) for column in dataset.columns]
    if standardized.columns.duplicated().any():
        raise ValueError("Column normalization created duplicate column names")
    return standardized


def map_competency_dimensions(dataset: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with dimension and overall EDOM scores.

    Args:
        dataset: Dataset containing all canonical P1--P20 indicator columns.

    Returns:
        A copy enriched with competency-dimension and overall-score columns.

    Raises:
        TypeError: If ``dataset`` is not a pandas DataFrame.
        ValueError: If any indicator column is absent.
    """
    _ensure_dataframe(dataset)
    _ensure_columns(dataset, INDICATOR_COLUMNS)
    enriched = dataset.copy()
    for competency, indicators in COMPETENCY_MAPPING.items():
        enriched[competency] = enriched.loc[:, list(indicators)].mean(axis=1)
    enriched[OVERALL_SCORE_COLUMN] = enriched.loc[
        :, list(INDICATOR_COLUMNS)
    ].mean(axis=1)
    return enriched


def aggregate_by_lecturer(dataset: pd.DataFrame) -> pd.DataFrame:
    """Aggregate EDOM records to one row per lecturer.

    Args:
        dataset: Enriched EDOM records with canonical identity and score columns.

    Returns:
        A prepared dataset with one row per lecturer and the columns required by
        the Analytics Layer.

    Raises:
        TypeError: If ``dataset`` is not a pandas DataFrame.
        ValueError: If an aggregation, indicator, or competency column is absent.
    """
    _ensure_dataframe(dataset)
    required_columns = (LECTURER_NAME_COLUMN, STUDY_PROGRAM_COLUMN)
    _ensure_columns(dataset, required_columns + COMPETENCY_COLUMNS)
    _ensure_columns(dataset, (OVERALL_SCORE_COLUMN,))
    score_columns = COMPETENCY_COLUMNS + (OVERALL_SCORE_COLUMN,)
    aggregations = {STUDY_PROGRAM_COLUMN: "first"}
    aggregations.update({column: "mean" for column in score_columns})
    prepared_dataset = (
        dataset.groupby(LECTURER_NAME_COLUMN, as_index=False, dropna=False)
        .agg(aggregations)
        .reset_index(drop=True)
    )
    return prepared_dataset.loc[:, list(PREPARED_COLUMNS)]


def _normalize_column_name(column: object) -> str:
    """Convert a source label to its canonical EDOM schema form."""
    normalized = str(column).strip().lower().replace(" ", "_")
    if normalized.startswith("p") and normalized[1:].isdigit():
        return f"P{normalized[1:]}"
    return normalized


def _ensure_dataframe(dataset: pd.DataFrame) -> None:
    """Raise a TypeError unless an object is a DataFrame."""
    if not isinstance(dataset, pd.DataFrame):
        raise TypeError("dataset must be a pandas DataFrame")


def _ensure_required_columns(dataset: pd.DataFrame) -> None:
    """Raise a ValueError if canonical required columns are absent."""
    _ensure_columns(dataset, REQUIRED_COLUMNS)


def _ensure_columns(dataset: pd.DataFrame, columns: tuple[str, ...]) -> None:
    """Raise a ValueError when one or more expected columns are absent."""
    missing_columns = [column for column in columns if column not in dataset.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")
