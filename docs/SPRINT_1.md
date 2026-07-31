# SPRINT_1.md — Project Setup

**Status:** ✅ Complete (verified via repo screenshot — initial commit `feat: initial commit for sprint 1 project setup`)

## Sprint Goal
Stand up the `edom-dashboard/` skeleton per the module architecture in `ARCHITECTURE.md`, and prove the deployment path works end-to-end (public URL, not just localhost) before any real logic is written.

## Task
- Initialize git repo, `.gitignore`, initial `README.md`
- Create full folder skeleton (`core/`, `pages/`, `components/`, `assets/`, `tests/`, `docs/`, `data/`, `config/`)
- Stub every `core/*.py` file with function signatures + docstrings only — no logic
- Pin `requirements.txt`
- Minimal `app.py` runnable via `streamlit run app.py`, empty sidebar reflecting `pages/` structure, no real data
- `pytest` setup with one dummy test
- `Dockerfile` (base, for future non-Streamlit-Cloud hosting) + `.streamlit/config.toml`
- Deploy skeleton to a public URL (Streamlit Community Cloud)

## Acceptance Criteria
- [x] Git repository active with initial commit
- [x] Full folder structure matches `ARCHITECTURE.md` §3, including `Dockerfile` and `.streamlit/config.toml`
- [x] `streamlit run app.py` runs locally
- [x] Skeleton deployed and reachable via public URL
- [x] `requirements.txt` pinned, installs cleanly in deployment environment
- [x] `pytest` runs with at least one passing test
- [x] `README.md` documents local setup + deployment flow

## Explicitly Out of Scope (deferred)
- Real CSV loading/parsing (→ Sprint 2)
- Any statistics/RPI computation (→ Sprint 3–4)
- Radar/heatmap/visualization (→ Sprint 5)
- Real data deployment + per-role auth (→ near Sprint 8)

## Data Sensitivity Note
Public deployment at this stage uses **dummy data only**, per the hard rule in `PROJECT_CONTEXT.md` §6. Do not upload real EDOM CSVs to `data/` or to the public Streamlit instance until the Sprint 8 hosting decision is made.
