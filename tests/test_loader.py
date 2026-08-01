"""Tests for CSV loading."""

import pandas as pd
import pytest
from io import BytesIO

from core.loader import CsvFileNotFoundError, EmptyCsvFileError, load_csv


def test_load_csv_returns_dataframe(tmp_path) -> None:
    """Load a valid CSV into a DataFrame."""
    csv_file = tmp_path / "edom.csv"
    csv_file.write_text("lecturer_name,P1\nDr. Ani,5\n", encoding="utf-8")

    result = load_csv(csv_file)

    assert isinstance(result, pd.DataFrame)
    assert result.to_dict("records") == [{"lecturer_name": "Dr. Ani", "P1": 5}]


def test_load_csv_raises_for_missing_file(tmp_path) -> None:
    """Report a missing CSV with a specific exception."""
    with pytest.raises(CsvFileNotFoundError):
        load_csv(tmp_path / "absent.csv")


def test_load_csv_raises_for_empty_file(tmp_path) -> None:
    """Report a zero-byte CSV with a specific exception."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(EmptyCsvFileError):
        load_csv(csv_file)


def test_load_csv_reads_binary_file_like_object() -> None:
    """Load uploaded CSV content without requiring a local path."""
    uploaded_content = BytesIO(b"lecturer_name,P1\nDr. Ani,5\n")

    result = load_csv(uploaded_content)

    assert result.to_dict("records") == [{"lecturer_name": "Dr. Ani", "P1": 5}]
