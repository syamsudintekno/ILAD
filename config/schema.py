"""Canonical EDOM dataset schema definitions."""

LECTURER_NAME_COLUMN = "lecturer_name"
STUDY_PROGRAM_COLUMN = "study_program"
FACULTY_COLUMN = "faculty"
PEDAGOGIC_COLUMN = "pedagogic"
PROFESSIONAL_COLUMN = "professional"
PERSONALITY_COLUMN = "personality"
SOCIAL_COLUMN = "social"
OVERALL_SCORE_COLUMN = "overall_score"
RPI_COLUMN = "rpi"
RANK_COLUMN = "rank"
QUARTILE_COLUMN = "quartile"
QUARTILE_LABELS: tuple[str, ...] = ("Q1", "Q2", "Q3", "Q4")

IDENTITY_COLUMNS: tuple[str, ...] = (
    LECTURER_NAME_COLUMN,
    STUDY_PROGRAM_COLUMN,
    FACULTY_COLUMN,
)
INDICATOR_COLUMNS: tuple[str, ...] = tuple(f"P{number}" for number in range(1, 21))
COMPETENCY_MAPPING: dict[str, tuple[str, ...]] = {
    PEDAGOGIC_COLUMN: tuple(f"P{number}" for number in range(1, 7)),
    PROFESSIONAL_COLUMN: tuple(f"P{number}" for number in range(7, 12)),
    PERSONALITY_COLUMN: tuple(f"P{number}" for number in range(12, 17)),
    SOCIAL_COLUMN: tuple(f"P{number}" for number in range(17, 21)),
}
COMPETENCY_COLUMNS: tuple[str, ...] = tuple(COMPETENCY_MAPPING)
DIMENSION_COLUMNS: tuple[str, ...] = COMPETENCY_COLUMNS
DEFAULT_RPI_WEIGHTS: dict[str, float] = {
    column: 1 / len(DIMENSION_COLUMNS) for column in DIMENSION_COLUMNS
}
ANALYTIC_SCORE_COLUMNS: tuple[str, ...] = COMPETENCY_COLUMNS + (
    OVERALL_SCORE_COLUMN,
)
REQUIRED_COLUMNS: tuple[str, ...] = IDENTITY_COLUMNS + INDICATOR_COLUMNS
PREPARED_COLUMNS: tuple[str, ...] = (
    LECTURER_NAME_COLUMN,
    STUDY_PROGRAM_COLUMN,
) + COMPETENCY_COLUMNS + (OVERALL_SCORE_COLUMN,)
