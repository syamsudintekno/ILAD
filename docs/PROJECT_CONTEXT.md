# PROJECT_CONTEXT.md

## 1. Project Identity

**Name:** Institutional Learning Analytics Dashboard (ILAD)
**Conceptual architecture name:** Institutional Learning Analytics Architecture (ILAA)
**Type:** Prototype / MVP accompanying a Sinta 2 methodological paper (RPI framework)
**Repository:** `edom-dashboard/` (GitHub: syamsudinteknо/ILAD)

## 2. Project Goal

Build a prototype web dashboard that operationalizes the **Relative Performance Indexing (RPI)** method from the accompanying paper, so that raw Student Evaluation of Teaching (EDOM) data can be turned into actionable institutional intelligence for quality assurance — without requiring local installation (public URL from day one).

This is a research-grade MVP, not a production institutional system. Priorities, in order: **correctness of the analytics pipeline → clarity of architecture → usability → polish.**

## 3. Problem Being Solved

- EDOM results currently exist only as flat tables/spreadsheets.
- Aggregated averages are distorted by a **ceiling effect** (confirmed via Shapiro-Wilk in the paper).
- No visualization exists for leadership (Kaprodi / Dekan / LPM / Rektor).
- No system integrates RPI output into decision-making.

## 4. Actors & Access Level

| Actor | Scope |
|---|---|
| Admin QA | Upload dataset, run analytics, generate/export reports (only actor who triggers computation) |
| Head of Study Program | View dashboard filtered to their prodi, lecturer profiles, ranking |
| Dean | Faculty-level dashboard, compare study programs |
| Quality Assurance Office (LPM) | Institutional analytics, quartile distribution, KPI monitoring |
| Rector | Executive KPI summary only (no per-lecturer detail) |

Note: students are **not** an actor — the system consumes already-collected EDOM data, it is not a survey/collection tool.

## 5. Architecture (summary — see ARCHITECTURE.md for full detail)

Layered Architecture (chosen over MVC for analytics-heavy apps):

```
Presentation Layer   → Streamlit Dashboard (pages/)
Application Layer    → Navigation, Session, Filter, Report
Analytics Layer       → Statistics, RPI, Ranking, Quartile, Insights  (core/)
Data Layer            → CSV Loader, Validation, Preprocessing        (core/)
```

Design principle: the scoring method is named **Performance Scoring Service**, not "RPI Engine," so that RPI can later be swapped for TOPSIS/PROMETHEE/ML without changing the architecture.

## 6. Current Implementation Status

**Version:** Prototype 0.1 (Sprint 1 complete — skeleton only, no real logic yet)

| Aspect | Current | Future (not yet in scope) |
|---|---|---|
| Data source | Single CSV upload | Database / LMS / SIAKAD / Tracer Study |
| Scoring method | RPI (rankit-based) | Pluggable (TOPSIS, PROMETHEE, ML) |
| Auth | None (public demo, dummy data only) | Per-role authentication (Sprint 8) |
| Hosting | Streamlit Community Cloud (public skeleton) | Private hosting once real data is used |

**⚠️ Data sensitivity constraint (hard rule):** EDOM data contains lecturer names and individual scores. Public deployment is permitted **only** with dummy/synthetic data until Sprint 8 decides on private hosting. Never push `data/` with real records to a public repo or public Streamlit instance.

## 7. Data Dictionary (target schema after Sprint 2–3)

| Column | Type | Description |
|---|---|---|
| lecturer_name | string | Nama dosen |
| study_program | string | Program studi |
| faculty | string | Fakultas |
| P1–P20 | int (1–5) | Skor indikator EDOM |
| pedagogic | float | Rata-rata dimensi pedagogik (6 indikator) |
| professional | float | Rata-rata dimensi profesional (5 indikator) |
| personality | float | Rata-rata dimensi kepribadian (5 indikator) |
| social | float | Rata-rata dimensi sosial (4 indikator) |
| overall_score | float | Rata-rata keseluruhan |
| rpi | float | Relative Performance Index |
| percentile | float | Persentil |
| quartile | string | Q1–Q4 |
| rank | int | Peringkat dosen |

## 8. Coding Standard (summary — see AI_DEVELOPER_GUIDE.md for enforcement rules)

PEP8 · Type hints · Google-style docstrings · Single Responsibility Principle · no business logic in UI · modular architecture (`core/` has zero Streamlit imports).

## 9. Folder Structure

```
edom-dashboard/
├── app.py                # entry point ONLY — no logic here
├── config/
├── core/
│   ├── loader.py
│   ├── validator.py
│   ├── preprocessing.py
│   ├── statistics.py
│   ├── rpi.py
│   ├── ranking.py
│   ├── quartile.py
│   ├── insights.py
│   └── exporter.py
├── pages/                # Overview, Ranking, Lecturer Profile, Analytics, Report
├── components/
├── assets/
├── tests/
├── docs/                 # this handbook
├── data/                 # dummy/local only — never real EDOM data in git
├── requirements.txt
├── Dockerfile
└── .streamlit/config.toml
```

## 10. Sprint Roadmap

| Sprint | Target | Status |
|---|---|---|
| 0 | Architecture & Design | ✅ Done |
| 1 | Project Setup | ✅ Done |
| 2 | Data Layer (loader, validator, preprocessing) | ⏳ Next |
| 3 | Analytics Engine (statistics) | Pending |
| 4 | RPI Engine (performance scoring) | Pending |
| 5 | Visualization | Pending |
| 6 | Dashboard (pages) | Pending |
| 7 | Reporting (PDF/Excel export) | Pending |
| 8 | Evaluation (auth, private hosting, usability testing) | Pending |

## 11. How to Use This Handbook

For every new sprint prompt to Codex, reference this file plus `ARCHITECTURE.md` and `AI_DEVELOPER_GUIDE.md` by name — do not paste them in full. Example:

> "Read PROJECT_CONTEXT.md, ARCHITECTURE.md, and AI_DEVELOPER_GUIDE.md before implementing this task. Then implement Sprint 2.1 as described in SPRINT_2.md."

Do not repeat DSRM background, grant proposal narrative, or paper content in sprint prompts — that context lives here, once.
