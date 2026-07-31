# DATA_CONTRACT.md

# Institutional Learning Analytics Dashboard (ILAD)

## Purpose

This document defines the data contract between the Data Processing Layer, Analytics Layer, and Presentation Layer.

The objective is to ensure that every module exchanges data using a consistent structure without relying on implementation details.

---

# Data Flow

```
Raw CSV

↓

Loader

↓

Validator

↓

Preprocessing

↓

Prepared Dataset

↓

Analytics Engine

↓

Dashboard
```

---

# Contract 1

## Loader Output

Module

```
core/loader.py
```

Input

```
CSV file
```

Output

```
pandas.DataFrame
```

Guarantees

- CSV successfully loaded
- Original column names preserved
- No modification performed
- Original row count preserved

---

# Contract 2

## Validator Output

Module

```
core/validator.py
```

Input

```
Raw DataFrame
```

Output

```
ValidationResult
```

ValidationResult contains

- is_valid
- errors
- warnings
- summary

Guarantees

- DataFrame is NOT modified
- Validation only reports issues

---

# Contract 3

## Preprocessing Output

Module

```
core/preprocessing.py
```

Input

Validated DataFrame

Output

Prepared DataFrame

The Prepared DataFrame MUST contain the following columns.

| Column        | Type   | Nullable | Description                           |
| ------------- | ------ | -------- | ------------------------------------- |
| lecturer_name | string | No       | Lecturer name                         |
| study_program | string | No       | Study program                         |
| pedagogic     | float  | No       | Mean score of pedagogic indicators    |
| professional  | float  | No       | Mean score of professional indicators |
| personality   | float  | No       | Mean score of personality indicators  |
| social        | float  | No       | Mean score of social indicators       |
| overall_score | float  | No       | Mean score of all indicators          |

Notes

- One row represents one lecturer.
- Indicator columns (P1–P20) are no longer required after preprocessing.
- All scores remain in the original Likert scale (1–5).
- No ranking is performed.

---

# Contract 4

## Analytics Input

Analytics Layer assumes:

- One row = one lecturer
- No duplicated lecturers
- All competency scores are numeric
- No missing competency values
- All required columns exist

Analytics Layer MUST NOT:

- Load CSV
- Validate schema
- Clean data

These responsibilities belong to previous layers.

---

# Contract 5

## Analytics Output

Analytics Engine returns

| Column        | Description                |
| ------------- | -------------------------- |
| lecturer_name | Lecturer                   |
| study_program | Program                    |
| pedagogic     | Mean                       |
| professional  | Mean                       |
| personality   | Mean                       |
| social        | Mean                       |
| overall_score | Mean                       |
| rpi           | Relative Performance Index |
| percentile    | Percentile                 |
| quartile      | Q1–Q4                      |

This output becomes the input for the Dashboard.

---

# Contract 6

## Dashboard Input

Dashboard pages receive only the Analytics Output.

Dashboard modules must never:

- load CSV
- preprocess data
- calculate statistics
- calculate RPI

Dashboard only visualizes data.

---

# Data Ownership

| Layer         | Owns                |
| ------------- | ------------------- |
| Loader        | File access         |
| Validator     | Data quality        |
| Preprocessing | Data transformation |
| Analytics     | KPI calculation     |
| Dashboard     | Visualization       |

Each layer owns exactly one responsibility.

---

# Future Compatibility

Future versions may replace

CSV

with

- PostgreSQL
- MySQL
- REST API

without changing the Analytics Layer or Dashboard.

Only the Loader implementation should change.

---

# Version

Current Version

```
v1.0
```

Last Updated

```
Sprint 2
```
