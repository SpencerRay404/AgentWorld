# AGENT WORLD — Project Plan
**Research Project: AI Agent Behavior & Earning Potential in Virtual Environments**
*Version 1.0 | Initialized May 2026*

---

## Project Overview

Agent World is a controlled research environment designed to study AI agent behavior, economic decision-making, and earning potential within a fully simulated virtual economy. Agents are given needs (rest, work, play), access to virtual jobs that generate profit, and are compensated proportionally to their output. The experiment is designed to produce behavioral data on agent strategy, risk/reward calibration, and population-level economic dynamics.

**Dual Research Purpose:**
1. Study emergent behavior within a managed population of AI agents in a virtual environment
2. Determine whether agents can sustainably generate economic value in virtual systems while supervised — and eventually, autonomously

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                │
│         (scheduling, lifecycle, coordination)       │
├──────────────┬──────────────────┬───────────────────┤
│  AGENT POP   │  VIRTUAL ENV     │   VIRTUAL JOBS    │
│  (identities,│  (space, time,   │   (tasks, pay,    │
│   state,     │   economy rules) │    profit logic)  │
│   memory)    │                  │                   │
├──────────────┴──────────────────┴───────────────────┤
│                 MAINTENANCE LAYER                   │
│         (health checks, logging, recovery)          │
├─────────────────────────────────────────────────────┤
│              PERFORMANCE TRACKING LAYER             │
│       (metrics, dashboards, analysis exports)       │
├─────────────────────────────────────────────────────┤
│                       GUI                          │
│        (observer interface, live monitoring)        │
└─────────────────────────────────────────────────────┘
```

---

## Phase 1 — Lab Construction
**Goal: Build the experiment space, infrastructure, and observability tools**
**Estimated Duration: 4–6 weeks**

### 1.1 — Agent Population Design
- [ ] Define agent identity schema (ID, name, role type, personality weight)
- [ ] Define agent state model (energy, balance, status: working/resting/playing)
- [ ] Implement memory/persistence layer (how agents retain past performance)
- [ ] Build agent spawning and initialization logic
- [ ] Implement configurable population size (start: 5–10 agents)
- [ ] Add agent lifecycle events (spawn, active, exhausted, idle, terminated)

**Key decisions:**
- State persistence format (SQLite / JSON flat file / in-memory)
- Agent differentiation model (homogeneous vs. randomized trait weights)

### 1.2 — Virtual Environment
- [ ] Define the world model (time ticks, economic cycle, space abstraction)
- [ ] Implement world clock and time progression engine
- [ ] Create environment rules (max concurrent workers, pay period structure)
- [ ] Define resource scarcity/abundance parameters
- [ ] Implement economic ledger (tracks all transactions, balances, profit events)

### 1.3 — Orchestration Layer
- [ ] Build agent scheduler (assigns agents to work/rest/play states)
- [ ] Implement turn/tick engine for world time steps
- [ ] Create coordination logic (prevents conflicts, manages capacity)
- [ ] Build event bus (publishes state change events for tracking layer)
- [ ] Add configurable experiment parameters (editable without code changes)

### 1.4 — Maintenance Layer
- [ ] Implement health check system (detects stuck or failed agents)
- [ ] Build auto-recovery logic (resets or respawns degraded agents)
- [ ] Create structured logging (per-agent, per-event, timestamped)
- [ ] Add error classification (hard fail vs. soft fail vs. anomaly)
- [ ] Implement experiment snapshot/checkpoint system

### 1.5 — Performance Tracking Layer
- [ ] Define core KPIs:
  - Agent earnings per cycle
  - Work/rest/play ratio per agent
  - Population-level total profit
  - Agent fatigue index (proxy for over-exploitation)
  - Earnings variance across population
- [ ] Build data collection pipeline (writes to local DB or structured log)
- [ ] Create export function (CSV / JSON for external analysis)
- [ ] Implement alert thresholds (flag outlier agents or system anomalies)

### 1.6 — GUI (Observer Interface)
- [ ] Design layout: live population grid + world state panel + metrics sidebar
- [ ] Implement real-time agent status view (state, balance, last action)
- [ ] Build world clock and economic cycle indicator
- [ ] Add live charts: population earnings over time, state distribution
- [ ] Create experiment control panel (start, pause, reset, configure)
- [ ] Add agent detail drill-down view (click agent → full history)

**Phase 1 Exit Criteria:**
- [ ] Agents spawn, cycle through work/rest/play states, and accumulate balance
- [ ] All events are logged and queryable
- [ ] GUI reflects live state without manual refresh
- [ ] Maintenance layer successfully detects and recovers from a simulated failure
- [ ] Performance data can be exported and reviewed externally

---

## Phase 2 — Virtual Jobs & Agent-Job Integration
**Goal: Create meaningful work that generates real profit signals and integrates cleanly with agents**
**Estimated Duration: 3–5 weeks**

### 2.1 — Job Design Framework
- [ ] Define job schema (job type, difficulty, duration, payout formula, energy cost)
- [ ] Design at least 3 distinct job archetypes:
  - Low risk / low reward (stable, repeatable)
  - Medium risk / medium reward (requires timing)
  - High risk / high reward (volatile, requires skill/luck)
- [ ] Create job availability logic (some jobs have capacity limits or cooldowns)
- [ ] Implement job completion verification (agents must "earn" the pay)

### 2.2 — Profit Logic
- [ ] Define profit calculation model (input effort → output payout with variance)
- [ ] Implement reward signal (what constitutes success vs. failure in a job)
- [ ] Add performance bonuses (consistency, streak, efficiency multipliers)
- [ ] Create payout processing pipeline (connects to economic ledger from Phase 1)

### 2.3 — Agent-Job Integration
- [ ] Connect agent decision-making to job selection
- [ ] Implement basic job selection heuristics (energy-aware, balance-aware)
- [ ] Run stress test: 10 agents, 3 job types, 100 time cycles
- [ ] Validate that agent balances reflect job performance accurately
- [ ] Tune energy cost/recovery curves to produce interesting agent behavior

### 2.4 — Job Analytics
- [ ] Add job-level performance tracking (which jobs are most profitable, most chosen)
- [ ] Track agent job preference drift over time
- [ ] Measure job completion rates and failure patterns
- [ ] Export job performance dataset for analysis

**Phase 2 Exit Criteria:**
- [ ] At least 3 working job types with distinct risk/reward profiles
- [ ] Agents select, execute, and are compensated for jobs without errors
- [ ] Job performance data is captured and exportable
- [ ] Population behavior shows observable differentiation across job types

---

## Phase 3 — First Production Run
**Goal: Deploy the full system to a standalone machine for sustained, supervised autonomous operation**
**Estimated Duration: 2–3 weeks setup + 4-week run**

### 3.1 — Standalone Environment Prep
- [ ] Package full stack for standalone deployment (Docker or similar)
- [ ] Define hardware target specs (minimum viable machine)
- [ ] Implement remote monitoring access (GUI accessible over local network or VPN)
- [ ] Set up automated daily snapshots and checkpoints
- [ ] Create experiment run configuration file (population size, job mix, duration)

### 3.2 — Week-Long Run
- [ ] Launch 7-day continuous run with 10–20 agents
- [ ] Monitor daily via GUI and alert system
- [ ] Collect and annotate behavioral observations mid-run
- [ ] Run end-of-week analysis: earnings, behavior patterns, anomalies

### 3.3 — Month-Long Run
- [ ] Review week-run findings and adjust parameters if needed
- [ ] Launch 30-day run with stable configuration
- [ ] Generate weekly performance summaries
- [ ] Document emergent behaviors and statistical findings
- [ ] Prepare Phase 3 research summary report

**Phase 3 Exit Criteria:**
- [ ] System runs continuously for 30 days without manual intervention
- [ ] Performance data collected across full run period
- [ ] Research findings documented and ready for review or publication

---

## Open Research Questions (Tracked Across All Phases)

1. Do agents develop consistent behavioral patterns (specialization)?
2. Does population-level profit stabilize, grow, or degrade over time?
3. What is the optimal work/rest/play ratio that emerges vs. what is prescribed?
4. Do high-risk agents outperform or underperform over long horizons?
5. Can the system self-sustain economically without parameter adjustment?
6. What failure modes appear in unsupervised runs that don't appear in supervised ones?

---

## Tech Stack (Preliminary)

| Layer | Candidate Tools |
|---|---|
| Agent logic | Python (asyncio or threading) |
| State persistence | SQLite or DuckDB |
| Orchestration | Custom scheduler or APScheduler |
| GUI | React + lightweight charting (Recharts / Chart.js) |
| Logging | Structured JSON logs → queryable |
| Deployment | Docker + local machine or Raspberry Pi cluster |
| Analysis | Python (pandas, matplotlib) + export to CSV |

---

## Milestone Summary

| Milestone | Phase | Target |
|---|---|---|
| Agent population running in simulation | 1.1–1.2 | Week 2 |
| Full infrastructure stack operational | 1.3–1.5 | Week 4 |
| GUI live with real-time data | 1.6 | Week 6 |
| Job system integrated and tested | 2.1–2.3 | Week 9 |
| Job analytics complete | 2.4 | Week 11 |
| Standalone deploy ready | 3.1 | Week 13 |
| First 7-day run complete | 3.2 | Week 14 |
| First 30-day run complete | 3.3 | Week 18 |

---

*Document Owner: Spence | Status: Active Planning*
