# AI_DEVELOPER_GUIDE.md

You are developing the **Institutional Learning Analytics Dashboard (ILAD)**, the MVP implementation of the Institutional Learning Analytics Architecture (ILAA) described in `ARCHITECTURE.md`.

Before implementing any task, read `PROJECT_CONTEXT.md` and `ARCHITECTURE.md`. Then read the relevant `SPRINT_N.md`. Do not ask for the full project background again — it lives in those files.

## Hard Rules

1. **Layering is non-negotiable.** `pages/` and `app.py` never import from `core/` computation modules directly for business logic — they go through the Application/Controller layer. `core/` modules never import `streamlit`.
2. **Single Responsibility Principle.** One module, one job. See the responsibility table in `ARCHITECTURE.md` §4 before adding a function anywhere — if it doesn't match that module's stated job, it belongs elsewhere.
3. **`app.py` is an entry point only.** No computation, no data loading, no business logic in it.
4. **PEP8** compliant code.
5. **Type hints** on every function signature (params and return).
6. **Google-style docstrings** on every public function/class.
7. **Functions under ~40 lines** where reasonably possible; split otherwise.
8. **No hardcoded paths.** Read paths/config from `config/`.
9. **Raise meaningful, specific exceptions** (not bare `except:` or generic `Exception`) — especially in `loader.py` and `validator.py`, where malformed EDOM data is expected input, not an edge case.
10. **Every module in `core/` must be unit-testable** without a running Streamlit session.
11. **Prefer composition over duplication** — if two modules need the same helper, extract it, don't copy it.
12. **Never commit real EDOM data.** Only synthetic/dummy CSVs go into `data/` or get used in public deployments, per the data-sensitivity rule in `PROJECT_CONTEXT.md` §6.
13. **Stay inside sprint scope.** If a task references functionality explicitly marked "not included" in the current `SPRINT_N.md`, stub it or flag it — do not implement ahead of schedule; that creates untested, unreviewed surface area.
14. **Terminology discipline.** Use "Performance Scoring Service," not "RPI Engine," in code comments, class/function names, and docs — RPI is the current algorithm, not the interface name (see `ARCHITECTURE.md` §2).

## When a Task Is Ambiguous

Stop and ask a specific clarifying question rather than guessing — e.g. "Should `validator.py` reject rows with any missing P1–P20 value, or only flag them?" A wrong assumption here compounds across every downstream module.

## Definition of Done for Any Task

- Code matches the module's stated responsibility (§ in `ARCHITECTURE.md`).
- Type hints + docstrings present.
- At least one `pytest` test added/updated in `tests/`.
- No `streamlit` import inside `core/`.
- No hardcoded paths.
- Confirms which sprint's Acceptance Criteria are satisfied.
