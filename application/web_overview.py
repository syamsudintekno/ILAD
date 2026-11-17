"""Adapt uploaded CSV analytics for the ILAD web Overview."""

from dataclasses import asdict
from io import BytesIO
from math import isfinite
from typing import TypedDict

import numpy as np
from pandas import Series
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
    distribution: dict[str, object]


def _histogram(scores: Series) -> list[dict[str, float | int]]:
    """Count the cohort scores in ten intervals."""
    counts, edges = np.histogram(scores, bins=10)
    return [
        {"lower": float(lower), "upper": float(upper), "count": int(count)}
        for lower, upper, count in zip(edges[:-1], edges[1:], counts, strict=True)
    ]


def _boxplot(scores: Series) -> dict[str, float | int]:
    """Summarize quartiles, whiskers, and the number of outliers."""
    q1, median, q3 = np.quantile(scores, [0.25, 0.5, 0.75])
    iqr = q3 - q1
    inside = scores[(scores >= q1 - 1.5 * iqr) & (scores <= q3 + 1.5 * iqr)]
    # With very small samples, interpolation may leave a fence between observations.
    lower = min(float(inside.min()), float(q1))
    upper = max(float(inside.max()), float(q3))
    return {
        "q1": float(q1), "median": float(median), "q3": float(q3),
        "lower_whisker": lower, "upper_whisker": upper,
        "outlier_count": len(scores) - len(inside),
    }


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
    rpi_histogram = _histogram(analytics_data[RPI_COLUMN])
    comparison = result.distribution_comparison
    assert comparison is not None  # The CSV controller always computes both summaries.
    distribution = {}
    for key, column, summary in (
        ("edom", OVERALL_SCORE_COLUMN, comparison.raw),
        ("rpi", RPI_COLUMN, comparison.transformed),
    ):
        scores = analytics_data[column]
        distribution[key] = {
            "histogram": rpi_histogram if key == "rpi" else _histogram(scores),
            "boxplot": _boxplot(scores),
            "statistics": {
                metric: value if isfinite(value) else None
                for metric, value in asdict(summary).items()
            },
        }
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
            "rpi_histogram": rpi_histogram,
        },
        "distribution": distribution,
    }
