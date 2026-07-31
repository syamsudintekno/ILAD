# SPRINT_0.md — Architecture & Design

**Status:** ✅ Complete
**Output:** Decisions consolidated into `PROJECT_CONTEXT.md` and `ARCHITECTURE.md`.

## Sprint Goal
Define problem statement, stakeholders, requirements, and system architecture before any code is written.

## Key Decisions Made
- Architecture style: **Layered Architecture** (not MVC) — see `ARCHITECTURE.md`.
- Scoring service named **Performance Scoring Service**, current implementation RPI, to keep the algorithm swappable.
- 5 actors defined with distinct access levels (Admin QA, Kaprodi, Dekan, LPM, Rektor) — full detail in `PROJECT_CONTEXT.md` §4.
- Ceiling-effect analysis explicitly **excluded** from the main dashboard feature set (already solved in the paper via RPI); kept only as an optional QA/technical appendix feature.
- Data dictionary finalized (13 target columns, 4 competency dimensions, 20 indicators) — see `PROJECT_CONTEXT.md` §7.
- Use case scope deliberately reduced to a single `<<include>>` chain to keep diagrams reviewer-friendly (Q1 diagram hygiene).
- Module structure for `core/` finalized: loader, validator, preprocessing, statistics, rpi, ranking, quartile, insights, exporter.
- Non-functional constraints set: ≤10,000 records, <3s load, modular, no hardcoded paths.

## Acceptance Criteria (met)
- [x] Problem statement and research objective documented
- [x] Stakeholder table finalized
- [x] Functional + non-functional requirements listed
- [x] Layered architecture diagram (Figure 2 candidate for paper) finalized
- [x] Module architecture (Deliverable 7) finalized
- [x] Data dictionary finalized
- [x] DSRM mapping completed
- [x] Sprint backlog (Sprint 0–8) defined

## Notes for Future Sprints
Full deliverable text (stakeholder rationale, DSRM justification, UML narrative) is archived outside this handbook — do not re-paste it into sprint prompts. Reference `PROJECT_CONTEXT.md` / `ARCHITECTURE.md` instead.
