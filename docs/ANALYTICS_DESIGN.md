# ANALYTICS_DESIGN.md

# Institutional Learning Analytics Dashboard (ILAD)

## Purpose

This document defines the architecture of the Analytics Layer.

The Analytics Layer transforms the prepared lecturer dataset into institutional performance indicators that can be consumed directly by the dashboard.

The Analytics Layer does NOT perform:

- CSV loading
- Data validation
- Data cleaning
- Visualization

Those responsibilities belong to other layers.

---

# Analytics Pipeline

```
Prepared Dataset

↓

Descriptive Statistics

↓

Relative Performance Index (RPI)

↓

Ranking

↓

Quartile Classification

↓

Institutional KPI

↓

Analytics Dataset
```

---

# Analytics Modules

```
analytics/

statistics.py

rpi.py

ranking.py

quartile.py

kpi.py
```

Each module has exactly one responsibility.

---

# Module Responsibilities

## statistics.py

Purpose

Calculate descriptive statistics from the prepared dataset.

Output

- mean
- median
- standard deviation
- minimum
- maximum
- variance

Future Extension

- skewness
- kurtosis

No ranking.

No RPI.

---

## rpi.py

Purpose

Calculate Relative Performance Index (RPI).

Input

Prepared Dataset

Output

Additional column

```
rpi
```

No ranking.

No visualization.

---

## ranking.py

Purpose

Sort lecturers according to RPI.

Output

Additional column

```
rank
```

Ranking depends only on RPI.

---

## quartile.py

Purpose

Assign quartile labels.

Output

Additional column

```
quartile
```

Possible values

- Q1
- Q2
- Q3
- Q4

---

## kpi.py

Purpose

Generate institutional performance indicators.

Examples

- Average RPI
- Highest RPI
- Lowest RPI
- Number of lecturers
- Number of study programs

Output

Dictionary

```
{
    "average_rpi": ...,
    "highest_rpi": ...,
    ...
}
```

---

# Analytics Dataset

After all analytics modules finish, the dataset should contain

| Column        |
| ------------- |
| lecturer_name |
| study_program |
| pedagogic     |
| professional  |
| personality   |
| social        |
| overall_score |
| rpi           |
| rank          |
| quartile      |

This dataset becomes the input for the Dashboard.

---

# Dependency Rules

Allowed

```
statistics

↓

rpi

↓

ranking

↓

quartile

↓

kpi
```

Forbidden

- ranking calculates RPI
- quartile calculates RPI
- dashboard calculates analytics

Each module must consume outputs from previous modules.

---

# Design Principles

- Single Responsibility Principle
- Layered Architecture
- Modular Design
- Testable Components
- No Streamlit dependency

---

# Future Extensions

The architecture supports future additions without modifying existing modules.

Examples

- Faculty Ranking
- Department KPI
- Semester Comparison
- Trend Analysis
- Benchmark Analysis

```

---

Version

```

v1.0

```

Last Updated

```

Sprint 3

```

```

RPI Engine

Raw Score

↓

Ranking

↓

Rankit Transformation

↓

Inverse Normal Transformation

↓

T-score Scaling

↓

Relative Performance Index
