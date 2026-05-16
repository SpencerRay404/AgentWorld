# AGENT WORLD — Project Governance
**Research Project: AI Agent Behavior & Earning Potential in Virtual Environments**
*Version 1.0 | Established May 2026*

---

## 1. Project Identity

| Field | Value |
|---|---|
| Project Name | Agent World |
| Project Type | Applied AI Research / Virtual Systems |
| Status | Active — Phase 1 |
| Owner | Spence |
| Repository | github.com/[owner]/agent-world |
| Initialized | May 2026 |
| Target Completion (Phase 3) | Q4 2026 |

---

## 2. Research Mandate

Agent World exists to answer two questions that current AI research has not fully addressed in controlled settings:

1. **Behavioral**: Can a population of AI agents develop distinct, stable behavioral strategies when given competing economic incentives (work vs. rest vs. play) within a virtual environment?
2. **Economic**: Can AI agents generate measurable, sustainable economic value in virtual systems — first under supervision, then autonomously?

All project decisions, technical choices, and experimental designs serve these two questions.

---

## 3. Roles & Responsibilities

| Role | Holder | Responsibilities |
|---|---|---|
| Principal Investigator | Spence | Research direction, final decisions, publication |
| Lead Developer | Spence | Architecture, code review, Claude Code prompts |
| AI Research Assistant | Claude | Prompt drafting, document authoring, code review support |
| External Reviewer | TBD | Phase 3 findings review |

---

## 4. Decision Framework

### 4.1 Architectural Decisions
Any change to the core stack (persistence layer, orchestration model, agent schema) requires:
- Written rationale documented in `docs/decisions/ADR_NNN.md` (Architecture Decision Record)
- Impact assessment on existing phases
- No retroactive changes to a completed phase without versioning

### 4.2 Experimental Parameter Changes
Changes to simulation parameters (population size, energy curves, pay rates) that occur **mid-experiment** must be:
- Logged as a parameter change event in the experiment log
- Accompanied by a note explaining the motivation
- Treated as a new experimental condition, not a correction

### 4.3 Phase Gating
No phase may begin until its predecessor's exit criteria are fully checked off and documented. Phase transitions require:
- Exit criteria sign-off (checklist in PROJECT_PLAN.md)
- A phase summary entry in EXPERIMENT_LOG.md
- A tagged GitHub release (e.g., `v1.0-phase1-complete`)

---

## 5. Versioning & Branching Strategy

```
main          ← stable, phase-complete only
dev           ← active development
feature/*     ← individual subphase work (e.g., feature/1.3-orchestrator)
experiment/*  ← experimental parameter variations (not merged to main)
```

**Tagging convention:**
- `v1.0-phase1-complete`
- `v1.1-phase2-complete`
- `v2.0-phase3-week1`
- `v2.1-phase3-month1`

---

## 6. Documentation Standards

All documents in this repository follow these conventions:

- Written in Markdown, stored in `docs/`
- Headers use sentence case (not ALL CAPS in body text)
- Dates in ISO format: `YYYY-MM-DD`
- Agent IDs in code blocks when referenced: `agent_a3f2`
- Experiment findings use neutral, descriptive language (no editorializing in logs)
- All claims in RESULTS_LOG.md must cite a tick range, cycle number, or export file

---

## 7. Data & Reproducibility Standards

- All simulation runs are reproducible via checkpoint files in `checkpoints/`
- Random seeds are logged at experiment start (see EXPERIMENT_LOG.md)
- No raw log files committed to GitHub (`.gitignore` covers `logs/` and `agent_world.db`)
- Exported CSVs and JSON summaries go to `exports/` and **are** committed
- Config snapshots (`config.json` at run start) are committed alongside each export

---

## 8. Ethical Considerations

This project studies AI agent behavior in a closed simulation. No real financial transactions occur. No real-world data is ingested. Agents are software constructs with no sentience or interests.

Research findings will be shared openly. Any extension of this work into real economic systems would require a separate ethics review.

---

## 9. Change Log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-05-14 | Initial governance document established |
