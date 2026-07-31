# ARCHITECTURE.md

## 1. Architectural Style

**Layered Architecture**, chosen over MVC because the system is analytics-centric, not CRUD-centric. Each layer depends only on the layer directly below it. No layer may skip a level (e.g., `pages/` must never call `core/rpi.py` — it goes through the Analytics Service interface, not around it).

## 2. High-Level View (Institutional Learning Analytics Architecture — ILAA)

```
┌────────────────────────────────────────────┐
│ DATA ACQUISITION LAYER                      │  ← EDOM CSV (lecturer identity, prodi,
│                                              │    faculty, 20 indicators)
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ DATA MANAGEMENT LAYER                       │  ← CSV Loader, Validation, Cleaning,
│                                              │    Aggregation, Dimension Mapping
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ INSTITUTIONAL ANALYTICS ENGINE  ⭐ (novelty) │  ← Statistics → Performance Scoring
│                                              │    (current impl: RPI) → Ranking →
│                                              │    Quartile → Insight
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ DECISION SUPPORT & VISUALIZATION            │  ← KPI Dashboard, Lecturer Profile,
│                                              │    Ranking Dashboard, Competency
│                                              │    Analytics, Institutional Report
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ DECISION MAKERS                             │  ← Kaprodi, Dekan, LPM, Rektor
└────────────────────────────────────────────┘
```

**Design intent behind Layer 3's naming:** the scoring step is called "Performance Scoring Service," never "RPI Engine," in code, docs, and diagrams. RPI is today's implementation of that service; the interface must survive a future swap to TOPSIS, PROMETHEE, or a learned model without touching Layers 1, 2, 4, or 5.

## 3. Implementation-Level Component Map

```
Presentation Layer      Dashboard UI (pages/): Overview, Ranking, Lecturer Profile,
                         Analytics, Report — Streamlit only, zero computation.
        │
        ▼
Controller Layer         Session Manager, Navigation Controller, Request Handler
                         (Application Layer in app.py / components/)
        │
        ▼
Analytics Service Layer  Statistics Service, Performance Scoring Service (RPI),
                         Ranking Service, Quartile Service, Insight Service,
                         Report Service  → maps 1:1 to core/*.py
        │
        ▼
Data Processing Layer    CSV Loader, Validator, Preprocessor → core/loader.py,
                         core/validator.py, core/preprocessing.py
        │
        ▼
Data Source              CSV Dataset (data/)
```

## 4. Module Responsibilities (Single Responsibility Principle)

| Module | Responsibility | Explicitly forbidden |
|---|---|---|
| `core/loader.py` | Read CSV, return DataFrame | No validation logic, no Streamlit |
| `core/validator.py` | Check missing values, duplicates, invalid scores (1–5 range) | No cleaning/mutation of data |
| `core/preprocessing.py` | Normalize column names, map P1–P20 to dimensions, aggregate per lecturer | No statistics, no RPI |
| `core/statistics.py` | Mean, median, SD, distribution, Shapiro-Wilk / normality checks | No ranking, no export |
| `core/rpi.py` | Rankit transform + RPI composite score only | No PDF/Excel export, no charting, no CSV reading |
| `core/ranking.py` | Sort/rank lecturers by score | No quartile logic |
| `core/quartile.py` | Assign Q1–Q4 based on percentile/rank | No insight text generation |
| `core/insights.py` | Generate narrative/flag text from computed metrics | No file export |
| `core/exporter.py` | Serialize results to PDF/Excel | No computation |

Rule of thumb: if a function in `core/` imports `streamlit`, that is an architecture violation.

## 5. Analytics Pipeline (data flow, Sprint 2 → 4)

```
Raw CSV → Validation → Cleaning → Preprocessing → Dimension Aggregation
        → Statistical Analysis → Relative Performance Index → Ranking
        → Quartile Classification → Visualization → Institutional Insight
        → PDF/Excel Report
```

## 6. Use Case Scope (for reference, not for MVP scope creep)

Core chain (each step `<<include>>`s the next):
`Import EDOM Dataset → Validate → Run Analytics → Generate Statistics → Calculate RPI → Generate Ranking → Generate Dashboard → Generate Report → Export PDF/Excel`

Each actor (from PROJECT_CONTEXT.md §4) only reaches the presentation-layer views appropriate to their role; only Admin QA triggers the pipeline itself.

## 7. Non-Functional Constraints

- Dataset size ≤ 10,000 records; page load < 3s.
- Modular: adding a new analytics service must not require editing existing `core/` modules.
- No hardcoded file paths — everything through `config/`.
- Every `core/` module must be unit-testable in isolation (no Streamlit session state dependency).

## 8. Known Extension Points (do not build now, but do not architect them away)

- Data Acquisition Layer may later ingest LMS / SIAKAD / MBKM / Tracer Study sources — loader must stay swappable.
- Performance Scoring Service must stay swappable (see §2).
- Auth/per-role access control lands in Sprint 8 — do not hardcode "no auth" assumptions into page logic that would be painful to retrofit.
