"""Adapt uploaded CSV analytics for the ILAD web Overview."""

from io import BytesIO
from typing import TypedDict

from pandas.errors import ParserError

from application.controller import AnalyticsController
from config.schema import (
    LECTURER_NAME_COLUMN,
    OVERALL_SCORE_COLUMN,
    QUARTILE_COLUMN,
    RANK_COLUMN,
    RPI_COLUMN,
    STUDY_PROGRAM_COLUMN,
)
from core.loader import EmptyCsvFileError

_OVERVIEW_COLUMNS = (
    LECTURER_NAME_COLUMN,
    STUDY_PROGRAM_COLUMN,
    OVERALL_SCORE_COLUMN,
    RPI_COLUMN,
    RANK_COLUMN,
    QUARTILE_COLUMN,
)


class OverviewPayload(TypedDict):
    """Analytics data returned by a successful web Overview run."""

    cohort_size: int
    overview: dict[str, object]


def build_web_overview(csv_bytes: bytes) -> OverviewPayload:
    """Calculate the pilot payload using the existing Streamlit controller.

    Raises:
        EmptyCsvFileError: The CSV contains no records.
        ParserError: The CSV cannot be decoded or parsed.
        DatasetValidationError: The input fails EDOM validation.
    """
    try:
        result = AnalyticsController().run_uploaded_csv(BytesIO(csv_bytes))
    except UnicodeDecodeError as error:
        raise ParserError("CSV must be encoded in UTF-8") from error
    analytics_data = result.analytics_data
    return {
        "cohort_size": len(analytics_data),
        "overview": {
            "kpis": result.kpis,
            "top_lecturers": analytics_data.loc[:, list(_OVERVIEW_COLUMNS)]
            .head(10)
            .to_dict(orient="records"),
        },
    }
