# Institutional Learning Analytics Dashboard (ILAD)

A research-oriented web-based dashboard prototype for institutional learning analytics and lecturer performance evaluation in higher education.

> Developed as part of the 2026 Interdisciplinary Research Grant.

---

## Overview

Institutional Learning Analytics Dashboard (ILAD) is a research prototype designed to support university quality assurance through multidimensional analysis of Student Evaluation of Teaching (EDOM) data.

Unlike conventional dashboards that rely solely on raw average scores, ILAD integrates a Relative Performance Index (RPI) methodology to mitigate ceiling effects commonly observed in teaching evaluation datasets.

The project follows a modular software architecture and Design Science Research Methodology (DSRM).

---
## Related Publications

- Syamsudin, et al. (2026). *Restoring Distributional Properties of Ceiling-Compressed Student Evaluation of Teaching Data via Relative Performance Indexing.* (Submitted)

- Development of an Institutional Learning Analytics Dashboard Prototype for Lecturer Performance Evaluation. (In Progress)
---
## Research Objectives

- Analyze institutional EDOM data
- Restore discriminatory power of ceiling-compressed evaluation scores
- Provide fair lecturer performance comparison
- Support evidence-based quality assurance
- Develop a reusable institutional analytics platform

---

## Current Features

### Data Processing

- CSV Loader
- Data Validation
- Data Preprocessing
- Lecturer-level Aggregation

### Analytics Engine

- Descriptive Statistics
- Relative Performance Index (RPI)
- Lecturer Ranking
- Quartile Classification
- Institutional KPI Summary

### Software Engineering

- Modular Architecture
- Unit Testing
- Configuration-driven Design

---

## Project Structure

```text
ilad/

├── analytics/
├── config/
├── core/
├── pages/
├── tests/
├── docs/
├── assets/
├── data/
└── app.py
```

---

## Development Status

| Sprint | Status |
|---------|--------|
| Sprint 0 | ✅ Architecture |
| Sprint 1 | ✅ Project Setup |
| Sprint 2 | ✅ Data Layer |
| Sprint 3 | ✅ Analytics Engine |
| Sprint 4 | ⏳ Dashboard UI |
| Sprint 5 | ⏳ Reporting |
| Sprint 6 | ⏳ Evaluation |

---

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- SciPy
- Plotly
- Matplotlib
- OpenPyXL
- Pytest

---

## Architecture

```text
CSV Dataset

↓

Loader

↓

Validator

↓

Preprocessing

↓

Statistics

↓

Relative Performance Index (RPI)

↓

Ranking

↓

Quartile Classification

↓

Institutional KPI

↓

Streamlit Dashboard
```

---

## Testing

Run all tests

```bash
pytest
```

Current status

```
31 tests passed
```

---

## Research Methodology

This project follows the Design Science Research Methodology (DSRM):

1. Problem Identification
2. Objective Definition
3. Design
4. Prototype Development
5. Demonstration
6. Evaluation
7. Communication

---

## Project Status

Current Version

```
v0.1.0
```

Current milestone

> Analytics Engine Completed

---

## Future Development

- Interactive Streamlit Dashboard
- Faculty-level Analytics
- PDF Report Generation
- Excel Export
- User Authentication
- Institutional Benchmarking

---

## License

This repository is intended for academic research and prototype development.

---

## Author

Syamsudin

Department of Informatics

UIN Syekh Wasil Kediri

Indonesia
