"""Regression tests for the CSV-to-Overview adapter."""

import json
from io import StringIO

import pandas as pd
import pytest
from pandas.errors import ParserError

from application.controller import DatasetValidationError
from application.web_overview import build_web_overview
from config.schema import (
    FACULTY_COLUMN,
    INDICATOR_COLUMNS,
    LECTURER_NAME_COLUMN,
    REQUIRED_COLUMNS,
    STUDY_PROGRAM_COLUMN,
)
from core.loader import EmptyCsvFileError


def make_csv(scores: list[float]) -> bytes:
    """Create a canonical CSV with one synthetic lecturer per score."""
    rows = [
        {
            LECTURER_NAME_COLUMN: f"Dosen sintetis {index:02d}",
            STUDY_PROGRAM_COLUMN: "Program sintetis",
            FACULTY_COLUMN: "Fakultas sintetis",
            **dict.fromkeys(INDICATOR_COLUMNS, score),
        }
        for index, score in enumerate(scores)
    ]
    buffer = StringIO()
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def test_web_overview_serializes_cohort_kpis_and_top_ten() -> None:
    """Return the full cohort count and preserve tied ranks in the top ten."""
    scores = [1.0 + index / 4 for index in range(10)] + [5.0, 5.0]

    payload = build_web_overview(make_csv(scores))
    overview = payload["overview"]
    top_lecturers = overview["top_lecturers"]

    assert payload["cohort_size"] == 12
    assert overview["kpis"]["lecturer_count"] == 12
    assert len(top_lecturers) == 10
    assert [entry["rank"] for entry in top_lecturers[:3]] == [1, 1, 3]
    assert top_lecturers[0]["overall_score"] == 5.0
    assert top_lecturers[0]["rpi"] == overview["kpis"]["highest_rpi"]
    json.dumps(payload, allow_nan=False)


def test_web_overview_preserves_structured_validation_errors() -> None:
    """Surface invalid indicator counts without creating a result."""
    with pytest.raises(DatasetValidationError) as captured:
        build_web_overview(make_csv([5.5]))

    assert captured.value.validation_result.errors["invalid_score_counts"] == dict.fromkeys(
        INDICATOR_COLUMNS, 1
    )


@pytest.mark.parametrize("csv_bytes", [b"", make_csv([])])
def test_web_overview_rejects_empty_uploads(csv_bytes: bytes) -> None:
    """Classify empty bodies and header-only files as input errors."""
    with pytest.raises(EmptyCsvFileError):
        build_web_overview(csv_bytes)


def test_web_overview_rejects_non_utf8_input() -> None:
    """Classify unsupported encoding as a CSV parse error."""
    with pytest.raises(ParserError, match="UTF-8"):
        build_web_overview(b"\xff")
