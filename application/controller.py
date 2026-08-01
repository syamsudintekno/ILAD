"""Application-layer orchestration for the institutional analytics workflow."""

from dataclasses import dataclass
from typing import BinaryIO

import pandas as pd

from analytics.kpi import calculate_institutional_kpis
from analytics.quartile import calculate_quartiles
from analytics.ranking import calculate_ranking
from analytics.rpi import calculate_rpi
from analytics.statistics import StatisticsResult, calculate_descriptive_statistics
from core.loader import load_csv
from core.preprocessing import preprocess_dataset
from core.validator import ValidationResult, validate_dataset

__all__ = [
    "ANALYTICS_RESULT_SESSION_KEY",
    "AnalyticsController",
    "AnalyticsRunResult",
    "DatasetValidationError",
]

ANALYTICS_RESULT_SESSION_KEY = "analytics_run_result"


@dataclass(frozen=True)
class AnalyticsRunResult:
    """Completed analytics outputs supplied to the presentation layer.

    Attributes:
        analytics_data: Lecturer-level data after RPI, ranking, and quartiles.
        statistics: Descriptive statistics for the prepared input dataset.
        kpis: Institution-wide performance indicators.
    """

    analytics_data: pd.DataFrame
    statistics: StatisticsResult
    kpis: dict[str, float | int | dict[str, int]]


class DatasetValidationError(ValueError):
    """Raised when an uploaded EDOM dataset fails validation."""

    def __init__(self, validation_result: ValidationResult) -> None:
        """Initialize the error with structured data-quality findings.

        Args:
            validation_result: Validation findings for the uploaded dataset.
        """
        self.validation_result = validation_result
        super().__init__("Uploaded dataset failed validation")


class AnalyticsController:
    """Run the Analytics Layer for a prepared lecturer dataset."""

    def run_analytics(self, prepared_data: pd.DataFrame) -> AnalyticsRunResult:
        """Run the documented analytics pipeline for prepared EDOM data.

        Args:
            prepared_data: Lecturer-level output from the Data Processing Layer.

        Returns:
            Completed analytics data, descriptive statistics, and institutional
            KPIs for the presentation layer.
        """
        statistics = calculate_descriptive_statistics(prepared_data)
        scored_data = calculate_rpi(prepared_data)
        ranked_data = calculate_ranking(scored_data)
        classified_data = calculate_quartiles(ranked_data)
        kpis = calculate_institutional_kpis(classified_data)
        return AnalyticsRunResult(
            analytics_data=classified_data,
            statistics=statistics,
            kpis=kpis,
        )

    def run_uploaded_csv(self, uploaded_file: BinaryIO) -> AnalyticsRunResult:
        """Run the complete dashboard workflow for an uploaded CSV file.

        Args:
            uploaded_file: Binary CSV content supplied by the presentation layer.

        Returns:
            Completed analytics outputs for a valid uploaded dataset.

        Raises:
            DatasetValidationError: If the uploaded dataset has validation issues.
            CsvFileNotFoundError: If a path-based upload source is unavailable.
            EmptyCsvFileError: If the uploaded CSV contains no data.
        """
        raw_data = load_csv(uploaded_file)
        validation_result = validate_dataset(raw_data)
        if not validation_result.is_valid:
            raise DatasetValidationError(validation_result)
        prepared_data = preprocess_dataset(raw_data)
        return self.run_analytics(prepared_data)
