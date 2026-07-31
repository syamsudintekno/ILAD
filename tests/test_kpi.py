"""Tests for institutional KPI generation."""

import pandas as pd
import pytest

from analytics.kpi import calculate_institutional_kpis
from config.schema import QUARTILE_COLUMN, RPI_COLUMN, STUDY_PROGRAM_COLUMN


def make_analytics_dataset() -> pd.DataFrame:
    """Create a synthetic completed analytics dataset."""
    return pd.DataFrame(
        {
            "lecturer_name": ["Dr. Ani", "Dr. Budi", "Dr. Citra"],
            STUDY_PROGRAM_COLUMN: ["Informatics", "Informatics", "Information Systems"],
            RPI_COLUMN: [40.0, 50.0, 70.0],
            QUARTILE_COLUMN: ["Q4", "Q2", "Q1"],
        }
    )


def test_calculate_institutional_kpis_returns_expected_summaries() -> None:
    """Return unrounded RPI summaries, institutional counts, and quartiles."""
    result = calculate_institutional_kpis(make_analytics_dataset())

    assert result == {
        "average_rpi": pytest.approx(160 / 3),
        "highest_rpi": 70.0,
        "lowest_rpi": 40.0,
        "lecturer_count": 3,
        "study_program_count": 2,
        "quartile_distribution": {"Q1": 1, "Q2": 1, "Q3": 0, "Q4": 1},
    }


def test_calculate_institutional_kpis_rejects_an_empty_dataset() -> None:
    """Require at least one lecturer for institutional KPI generation."""
    dataset = pd.DataFrame(
        columns=[STUDY_PROGRAM_COLUMN, RPI_COLUMN, QUARTILE_COLUMN]
    )

    with pytest.raises(ValueError, match="empty dataset"):
        calculate_institutional_kpis(dataset)


def test_calculate_institutional_kpis_rejects_missing_required_columns() -> None:
    """Report required analytics fields that are not available."""
    dataset = pd.DataFrame({RPI_COLUMN: [50.0]})

    with pytest.raises(ValueError, match="Required KPI column is missing"):
        calculate_institutional_kpis(dataset)
