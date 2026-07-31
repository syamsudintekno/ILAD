# SPRINT_3.md

# Sprint 3 — Analytics Engine

Status

Planned

---

# Sprint Goal

Develop the Analytics Layer that transforms prepared lecturer data into institutional performance indicators.

The output of this sprint will become the primary data source for the dashboard.

---

# Learning Objectives

After completing Sprint 3, the developer should understand

- Analytics Layer Design
- Pipeline Processing
- Separation of Business Logic
- Statistical Programming
- Modular Analytics
- Unit Testing for Analytics Modules

---

# Coding Objectives

Implement

```
analytics/

statistics.py

rpi.py

ranking.py

quartile.py

kpi.py
```

---

# Development Strategy

Sprint 3 is divided into five micro-sprints.

---

## Sprint 3.1

statistics.py

Responsibilities

- mean
- median
- minimum
- maximum
- variance
- standard deviation

Output

StatisticsResult

---

## Sprint 3.2

rpi.py

Responsibilities

Implement Relative Performance Index.

Output

```
rpi
```

Uses only prepared dataset.

---

## Sprint 3.3

ranking.py

Responsibilities

Generate lecturer ranking.

Output

```
rank
```

Ranking is based only on RPI.

---

## Sprint 3.4

quartile.py

Responsibilities

Assign

- Q1
- Q2
- Q3
- Q4

based on RPI distribution.

---

## Sprint 3.5

kpi.py

Responsibilities

Generate dashboard KPIs.

Examples

- average RPI
- highest RPI
- lowest RPI
- lecturer count
- study program count

---

# Deliverables

Repository should contain

```
analytics/

statistics.py

rpi.py

ranking.py

quartile.py

kpi.py

tests/

test_statistics.py

test_rpi.py

test_ranking.py

test_quartile.py

test_kpi.py
```

---

# Acceptance Criteria

Statistics

- correct descriptive statistics
- tested

RPI

- calculated correctly
- unit tested

Ranking

- stable ranking
- deterministic

Quartile

- all lecturers assigned exactly one quartile

KPI

- returns expected institutional indicators

---

# Definition of Done

Sprint 3 is complete when

- all analytics modules implemented
- all unit tests pass
- no Streamlit dependency
- follows AI Developer Guide
- follows Analytics Design
- code reviewed
- committed to Git

---

# Out of Scope

Not included

- Dashboard
- Charts
- Streamlit pages
- PDF Export
- Excel Export
- User Interface

---

# Git Commit Recommendation

```
feat: implement descriptive statistics

feat: implement RPI engine

feat: implement ranking module

feat: implement quartile classification

feat: implement institutional KPI
```

---

# Sprint Exit Criteria

Analytics Dataset is ready for visualization.

No UI has been developed.
