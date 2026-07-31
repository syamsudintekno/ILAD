"""CSV loading utilities for the Data Processing Layer."""

from pathlib import Path
from typing import Union

import pandas as pd


PathLike = Union[str, Path]


class CsvFileNotFoundError(FileNotFoundError):
    """Raised when the requested EDOM CSV file does not exist."""


class EmptyCsvFileError(ValueError):
    """Raised when an EDOM CSV file contains no data."""


def load_csv(file_path: PathLike) -> pd.DataFrame:
    """Load an EDOM CSV file into a DataFrame.

    Args:
        file_path: Path to the CSV file to load.

    Returns:
        The contents of the CSV file.

    Raises:
        CsvFileNotFoundError: If ``file_path`` does not identify an existing file.
        EmptyCsvFileError: If the file is empty or has no CSV columns.
        IsADirectoryError: If ``file_path`` identifies a directory.
        pandas.errors.ParserError: If pandas cannot parse the CSV content.
    """
    path = Path(file_path)
    _ensure_readable_file(path)

    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError as error:
        raise EmptyCsvFileError(f"CSV file is empty: {path}") from error


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
