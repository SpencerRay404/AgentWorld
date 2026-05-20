# AGENT WORLD — Experiment Log
**Running record of all simulation experiments, parameter changes, and observations**
*Maintained by: Spence | Started: May 2026*

---

> **Log Protocol**
> Each entry must include: date, experiment ID, phase, tick range or duration, config snapshot reference, and structured observations. Findings are descriptive — interpretation belongs in RESULTS_LOG.md.

---

## EXP-001 | Phase 1 Validation Run
**Date:** 2026-05-20
**Status:** Complete
**Phase:** 1 (Post 1.5 completion)
**Duration:** 100 ticks / 10 cycles
**Population:** 8 agents (7 survived; 1 terminated)
**Config Snapshot:** in-memory run, config matches `config.json` defaults

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
| Scarcity Multiplier | 1.0 |
| Health Check Interval | 5 |
| Stuck Threshold | 10 |
| Max Recoveries | 3 |

### Observations

**Economy:**
- Population total profit: $1,295.00
- Earnings range: $130–$205 across 8 agents
- Mean earnings per agent: $161.88 (std $22.77)
- Gini coefficient: 0.0787 — near-equal distribution at this tick count

**Agent behavior:**
- Work/rest/play ratios were roughly 35% work / 42% rest / 23% play across the population
- Fatigue indexes very low (0.003–0.036), indicating agents are not being over-exploited
- Efficiency scores clustered around 0.42–0.45 earn/energy-unit across roles

**Agent breakdown (surviving agents, sorted by earnings):**
| Agent | Role | Earned | Balance | Energy | Final Status |
|---|---|---|---|---|---|
| Ulla | WORKER | $180 | $15 | 90.0 | WORKING |
| Xen | BALANCED | $170 | $85 | 70.0 | WORKING |
| Vex | EXPLORER | $170 | $115 | 90.0 | WORKING |
| Blaze | BALANCED | $155 | $40 | 45.0 | RESTING |
| Flux | EXPLORER | $145 | $30 | 40.0 | WORKING |
| Zap | WORKER | $140 | $45 | 15.0 | WORKING |
| Grit | WORKER | $130 | $10 | 80.0 | WORKING |
| Drift | (any) | $205 | — | — | TERMINATED |

### Anomalies

**Agent Drift — terminated at max_recoveries:**
- Drift was STUCK in WORKING status for 15+ consecutive ticks (health check fired at T25 twice)
- STUCK events continued (T30 20 ticks, T35, T40, T45) across different statuses
- After 3 recovery attempts, recovery manager terminated Drift at T~50
- Despite termination, Drift had accumulated the highest earnings ($205) of all agents before failing
- This is a notable paradox: the highest earner was also the most unstable

**9 health events total — all STUCK type:**
- T25: 2×STUCK (WORKING status, 15 ticks each)
- T30: STUCK (WORKING, 20 ticks) 
- T35: STUCK (RESTING, 15 ticks)
- T40: STUCK (RESTING, 20 ticks)
- T45: 2×STUCK (RESTING, 25 and 15 ticks)
- T80: STUCK (RESTING, 15 ticks)
- T85: STUCK (RESTING, 20 ticks)

No FROZEN, OVERDRAINED, or NEGATIVE_BALANCE events in this run.

### Outcome
- [x] All 8 agents ran for 100 ticks; 7 completed without HARD_FAIL; 1 terminated by recovery system
- [x] Ledger totals match expected range ($1295 at $5/tick × ~4 workers × 10 cycles ≈ $1600 max; 81% efficiency)
- [x] Health check system fired 9 events; recovery manager engaged and eventually terminated Drift
- [x] KPI export produced valid CSV — 7 rows, correct columns confirmed

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
