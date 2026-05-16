# AGENT WORLD — Experiment Log
**Running record of all simulation experiments, parameter changes, and observations**
*Maintained by: Spence | Started: May 2026*

---

> **Log Protocol**
> Each entry must include: date, experiment ID, phase, tick range or duration, config snapshot reference, and structured observations. Findings are descriptive — interpretation belongs in RESULTS_LOG.md.

---

## EXP-001 | Phase 1 Validation Run
**Date:** TBD
**Status:** Planned
**Phase:** 1 (Post 1.5 completion)
**Duration:** 100 ticks
**Population:** 8 agents
**Config Snapshot:** `exports/configs/exp001_config.json`

### Objective
Validate that the full Phase 1 stack (agents, world, orchestrator, maintenance, tracking) operates correctly end-to-end before GUI development begins.

### Setup
| Parameter | Value |
|---|---|
| Population Size | 8 |
| Ticks Per Cycle | 10 |
| Max Concurrent Workers | 4 |
| Base Pay Per Tick | 5.0 |
| Scarcity Mode | normal |
| Random Seed | TBD |

### Observations
*(To be filled during run)*

### Anomalies
*(To be filled during run)*

### Outcome
- [ ] All 8 agents completed 100 ticks without HARD_FAIL
- [ ] Ledger totals match expected range
- [ ] At least one health check event fired and was recovered
- [ ] KPI export produced valid CSV

---

## EXP-002 | Phase 1 GUI Live Run
**Date:** TBD
**Status:** Planned
**Phase:** 1 (Post 1.6 completion)
**Duration:** 200 ticks
**Population:** 8 agents
**Config Snapshot:** `exports/configs/exp002_config.json`

### Objective
First live run with the observer GUI active. Validate real-time display, WebSocket reliability, and agent detail drawer accuracy.

### Setup
| Parameter | Value |
|---|---|
| Population Size | 8 |
| Simulation Speed | 500ms/tick (observable pace) |
| Scarcity Mode | normal |

### Observations
*(To be filled during run)*

### GUI Verification Checklist
- [ ] Population grid updates without full page reload
- [ ] World clock advances correctly each tick
- [ ] Agent detail drawer shows correct transaction history
- [ ] Pay period notification fires at correct intervals
- [ ] Alerts appear in sidebar when thresholds breached
- [ ] CSV export from GUI produces valid file

---

## EXP-003 | Phase 2 Job Integration Stress Test
**Date:** TBD
**Status:** Planned
**Phase:** 2 (Post 2.3 completion)
**Duration:** 100 ticks
**Population:** 10 agents
**Config Snapshot:** `exports/configs/exp003_config.json`

### Objective
Validate agent-job integration under load. Confirm that all 3 job types are selected, completed, and paid correctly across the population.

### Setup
*(To be filled before run)*

### Observations
*(To be filled during run)*

---

## EXP-004 | Phase 3 Week Run — Production
**Date:** TBD
**Status:** Planned
**Phase:** 3
**Duration:** 7 days (continuous)
**Population:** 10–20 agents
**Machine:** TBD (standalone)
**Config Snapshot:** `exports/configs/exp004_config.json`

### Objective
First sustained autonomous run. Observe behavioral patterns, earnings trends, and system stability over 7 days without intervention.

### Daily Observation Log
| Day | Date | Notes | Alerts Fired | Recoveries |
|---|---|---|---|---|
| 1 | TBD | | | |
| 2 | TBD | | | |
| 3 | TBD | | | |
| 4 | TBD | | | |
| 5 | TBD | | | |
| 6 | TBD | | | |
| 7 | TBD | | | |

---

## EXP-005 | Phase 3 Month Run — Production
**Date:** TBD
**Status:** Planned
**Phase:** 3
**Duration:** 30 days (continuous)
**Population:** TBD (based on week run findings)
**Machine:** TBD (standalone)
**Config Snapshot:** `exports/configs/exp005_config.json`

### Objective
Full month-long production run. Primary data collection experiment for research findings.

### Weekly Summary Log
| Week | Dates | Key Observations | Population Profit | Gini | Notes |
|---|---|---|---|---|---|
| 1 | TBD | | | | |
| 2 | TBD | | | | |
| 3 | TBD | | | | |
| 4 | TBD | | | | |

---

## Parameter Change Log

*Any mid-experiment parameter adjustment is logged here, not in individual experiment entries.*

| Date | Experiment | Parameter | Old Value | New Value | Reason |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## Anomaly Registry

*Unexpected behaviors logged here for cross-experiment pattern analysis.*

| Date | Experiment | Tick | Agent(s) | Anomaly Type | Description | Resolved |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

---

*This log is append-only. Do not edit past entries. Add new experiments at the bottom.*
