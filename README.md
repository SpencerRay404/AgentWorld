# 🌐 Agent World

> **A controlled virtual economy for studying AI agent behavior and earning potential at population scale.**

![Status](https://img.shields.io/badge/status-Phase%201%20Active-00E5CC?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square)
![React](https://img.shields.io/badge/react-18+-61DAFB?style=flat-square&logo=react)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## What Is This?

Agent World is an open research project that builds a simulated virtual economy populated by AI agents. Each agent has needs, makes decisions, earns money, and interacts with the environment over time. The goal is to study what emerges.

Agents can:
- **Work** — complete virtual jobs that generate profit, at the cost of energy
- **Rest** — recharge energy, enabling sustained work over time  
- **Play** — spend earnings, which resets readiness and incentivizes earning

The system tracks every decision, every transaction, and every state change — giving researchers a rich dataset of agent behavioral dynamics.

---

## Research Questions

1. Do agents develop consistent behavioral patterns (specialization)?
2. Does population-level profit stabilize, grow, or degrade over time?
3. What work/rest/play ratio emerges vs. what is prescribed?
4. Do high-risk agents outperform over long horizons?
5. Can the system self-sustain economically without parameter adjustment?
6. What failure modes appear unsupervised that don't appear supervised?

---

## Architecture

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

## Project Status

| Phase | Title | Status | Target |
|---|---|---|---|
| Phase 1 | Lab Construction | 🟡 In Progress | Week 6 |
| Phase 2 | Virtual Jobs | ⚪ Planned | Week 11 |
| Phase 3 | Production Run | ⚪ Planned | Week 18 |

---

## Quick Start

```bash
git clone https://github.com/SpencerRay404/AgentWorld.git
cd AgentWorld
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m agent_world.db.schema
./run.sh
```

Open [http://localhost:3000](http://localhost:3000) for the observer GUI.

---

## Documentation

| Document | Purpose |
|---|---|
| [Project Plan](PROJECT_PLAN.md) | Full phase/subphase breakdown with milestones |
| [Dev Plan](DEV_PLAN.md) | Technical stack, structure, coding standards |
| [Governance](GOVERNANCE.md) | Decision framework, versioning, data standards |
| [Experiment Log](EXPERIMENT_LOG.md) | Running log of all simulation experiments |
| [Results Log](RESULTS_LOG.md) | Interpreted findings and research conclusions |
| [Phase 1 Claude Code Prompts](PHASE1_CLAUDE_CODE_PROMPTS.md) | Ready-to-paste prompts for building Phase 1 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Logic | Python 3.11+ / asyncio |
| Persistence | SQLite |
| API | FastAPI + uvicorn |
| GUI | React + Recharts |
| Logging | Structured JSONL |
| Deployment | Docker Compose |
| Analysis | pandas + matplotlib |

---

*Built with Python, React, and Claude · Open research · May 2026*
