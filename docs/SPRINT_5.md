# SPRINT 5

## Advanced Institutional Analytics

Project:
Institutional Learning Analytics Dashboard (ILAD)

Status:
Planning

---

# Goal

Sprint 5 extends ILAD from a reporting dashboard into a research-oriented decision support system.

The objective is to provide deeper institutional analytics while preserving the existing layered architecture.

No Data Layer redesign.

No Analytics Layer redesign.

Only extend analytics using existing processed data.

---

# Architecture

Current pipeline

CSV
↓

Data Layer

↓

Application Layer

↓

Analytics Layer

↓

Presentation Layer

Sprint 5 extends only the Analytics Layer and Presentation Layer.

---

# Design Principles

Sprint 5 must follow these rules.

• Do not modify the existing RPI algorithm.

• Do not modify preprocessing.

• Do not duplicate calculations.

• Every new page must consume Application Layer outputs.

• Business logic belongs inside Analytics Layer.

• Presentation Layer renders only.

---

# Sprint 5 Roadmap

Sprint 5.1
Distribution Analysis

Purpose

Visualize institutional score distributions before and after RPI transformation.

Outputs

• Histogram (Overall Score)

• Histogram (RPI)

• Density Plot

• Box Plot

• Distribution summary

New analytics

None.

Use existing processed data.

---

Sprint 5.2
Ceiling Effect Analysis

Purpose

Provide empirical evidence that RPI restores distributional characteristics.

Metrics

Before RPI

• Mean

• Median

• Variance

• Standard Deviation

• Skewness

• Kurtosis

After RPI

• Mean

• Median

• Variance

• Standard Deviation

• Skewness

• Kurtosis

Visualizations

Before vs After comparison.

No recalculation of RPI.

Only statistical comparison.

---

Sprint 5.3
Program Study Analytics

Purpose

Compare study programs using lecturer RPI.

Outputs

Per study program

• Average RPI

• Highest RPI

• Lowest RPI

• Standard deviation

• Lecturer count

Charts

• Bar chart

• Radar chart

• Boxplot

Future support

Faculty aggregation.

---

Sprint 5.4
Faculty Analytics

Purpose

Aggregate analytics by faculty.

Outputs

Faculty comparison dashboard.

Note

Only implemented when faculty information exists.

---

Sprint 5.5
Lecturer Benchmark

Purpose

Compare an individual lecturer against institutional averages.

Outputs

Selected lecturer

↓

Institution average

↓

Study program average

Charts

• Radar

• Difference plot

• Percentile indicator

---

Sprint 5.6
Interactive Filtering

Purpose

Allow institutional exploration.

Filters

• Study Program

• Quartile

• RPI Range

• Lecturer Name

Filtering affects presentation only.

No analytics recalculation.

---

Sprint 5.7
Research Method Validation

Purpose

Demonstrate the scientific contribution of Relative Performance Index.

Sections

Overall Score Distribution

↓

RPI Distribution

↓

Distribution Restoration

↓

Interpretation

Metrics

Variance

Skewness

Kurtosis

Ceiling compression

Visual comparison

This page is intended for publications and grant demonstrations.

---

Sprint 5.8
Dataset Quality Dashboard

Purpose

Provide institutional data quality assessment.

Metrics

Missing values

Duplicate rows

Question completeness

Number of lecturers

Number of study programs

Distribution of responses

No preprocessing modifications.

---

Sprint 5.9
Research Appendix

Purpose

Document the implemented methodology.

Contents

Pipeline

Architecture

RPI methodology

Statistical methodology

Quartile methodology

Institutional KPI definition

No calculations.

Static documentation only.

---

Sprint 5.10
Research Report Generator

Purpose

Generate downloadable institutional reports.

Future outputs

CSV

JSON

PDF (future)

DOCX (future)

Current sprint

Planning only.

---

# Coding Rules

Every Sprint 5 implementation must satisfy:

✓ Existing tests remain passing.

✓ No modification of Data Layer.

✓ No modification of Application Layer API.

✓ No duplication of RPI calculations.

✓ No direct analytics imports inside Streamlit pages.

✓ All analytics accessed through the Controller.

---

# Deliverables

At the end of Sprint 5 ILAD should provide:

✓ Institutional Dashboard

✓ Lecturer Dashboard

✓ Institutional Distribution Analysis

✓ Ceiling Effect Validation

✓ Program Study Comparison

✓ Benchmark Dashboard

✓ Interactive Filtering

✓ Research Documentation

without changing the underlying analytics engine.

---

End of Sprint 5 Planning
