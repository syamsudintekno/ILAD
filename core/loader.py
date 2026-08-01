"""CSV loading utilities for the Data Processing Layer."""

from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd


PathLike = Union[str, Path]
CsvSource = Union[PathLike, BinaryIO]


class CsvFileNotFoundError(FileNotFoundError):
    """Raised when the requested EDOM CSV file does not exist."""


class EmptyCsvFileError(ValueError):
    """Raised when an EDOM CSV file contains no data."""


def load_csv(file_source: CsvSource) -> pd.DataFrame:
    """Load an EDOM CSV file into a DataFrame.

    Args:
        file_source: Path or binary file-like object containing CSV data.

    Returns:
        The contents of the CSV file.

    Raises:
        CsvFileNotFoundError: If a path source does not identify an existing file.
        EmptyCsvFileError: If the file is empty or has no CSV columns.
        IsADirectoryError: If ``file_path`` identifies a directory.
        pandas.errors.ParserError: If pandas cannot parse the CSV content.
    """
    if isinstance(file_source, (str, Path)):
        path = Path(file_source)
        _ensure_readable_file(path)
        source = path
    else:
        source = file_source

    try:
        return pd.read_csv(source)
    except pd.errors.EmptyDataError as error:
        raise EmptyCsvFileError("CSV file is empty") from error


def _ensure_readable_file(path: Path) -> None:
    """Check whether a path identifies a non-empty regular file.

    Args:
        path: Path to validate before reading.

    Raises:
        CsvFileNotFoundError: If the path does not exist.
        IsADirectoryError: If the path is a directory.
        EmptyCsvFileError: If the file has zero bytes.
    """
    if not path.exists():
        raise CsvFileNotFoundError(f"CSV file was not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"CSV path is a directory: {path}")
    if path.stat().st_size == 0:
        raise EmptyCsvFileError(f"CSV file is empty: {path}")
