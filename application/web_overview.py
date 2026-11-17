"""Adapt uploaded CSV analytics for the ILAD web Overview."""

from io import BytesIO
from math import isfinite
from typing import TypedDict

import numpy as np
from pandas.errors import ParserError

from application.controller import AnalyticsController
from config.schema import (
    ANALYTIC_SCORE_COLUMNS,
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
    institutional_analytics: dict[str, object]


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
    statistics = result.statistics
    metrics = {
        "mean": statistics.mean,
        "median": statistics.median,
        "standard_deviation": statistics.standard_deviation,
        "variance": statistics.variance,
        "minimum": statistics.minimum,
        "maximum": statistics.maximum,
    }
    counts, edges = np.histogram(analytics_data[RPI_COLUMN], bins=10)
    return {
        "cohort_size": len(analytics_data),
        "overview": {
            "kpis": result.kpis,
            "top_lecturers": analytics_data.loc[:, list(_OVERVIEW_COLUMNS)]
            .head(10)
            .to_dict(orient="records"),
        },
        "institutional_analytics": {
            "statistics": [
                {
                    "score": score,
                    **{
                        metric: values[score] if isfinite(values[score]) else None
                        for metric, values in metrics.items()
                    },
                }
                for score in ANALYTIC_SCORE_COLUMNS
            ],
            "rpi_histogram": [
                {"lower": float(lower), "upper": float(upper), "count": int(count)}
                for lower, upper, count in zip(edges[:-1], edges[1:], counts, strict=True)
            ],
        },
    }
