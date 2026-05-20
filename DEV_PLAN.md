# AGENT WORLD — Development Plan
**Technical Execution Roadmap**
*Version 1.0 | May 2026*

---

## Project Status
**Current phase:** Phase 1 — Lab Construction (in progress; subphases 1.1–1.5 built, 1.6 GUI scaffolded)
**Last updated:** 2026-05-19
**Next milestone:** EXP-001 (100-tick validation run) per EXPERIMENT_LOG.md, then complete Phase 1.6 GUI live run (EXP-002)
_Updated: 2026-05-19 — Weekly review. Confirmed in repo: full `agent_world/` package with `models/`, `db/` (schema.py, agent_repo.py), `orchestrator/` (engine.py, scheduler.py, event_bus.py), `maintenance/` (health, recovery, logger, errors, checkpoint), `analytics/` (kpis, pipeline, exporter, alerts), `api/` (server.py, schemas.py), plus `spawner.py`, `world.py`, `ledger.py`, `config.py`. Demos `demo_1_1.py`, `demo_1_2.py`, `demo_1_3.py` present. Tests cover agents, world, orchestrator, maintenance, analytics. `gui/` Vite/React scaffold with `src/components/`, `src/hooks/`, `src/styles/`, built `dist/`. SQLite `agent_world.db` populated; substantial event logs under `logs/` (test_analytics_events.jsonl ≈260 KB, test_events.jsonl ≈110 KB) confirm runs have executed. EXP-001 / EXP-002 still listed as "Planned" in EXPERIMENT_LOG.md and RESULTS_LOG has no findings yet — Phase 1 exit gate (validation run write-up) not yet documented._

---

## 1. Stack Decisions (Locked)

| Layer | Choice | Rationale |
|---|---|---|
| Agent Logic | Python 3.11+ with asyncio | Async-native for tick engine; wide ML ecosystem for Phase 2+ |
| State Persistence | SQLite (stdlib) | Zero infrastructure, fully portable, queryable, file-based for checkpointing |
| Orchestration | Custom engine + APScheduler | Full control over tick semantics; APScheduler for real-time Phase 3 |
| API | FastAPI + uvicorn | Async-native, auto-docs, WebSocket support built in |
| GUI | React (Vite) + Recharts | Fast dev loop, composable charts, WebSocket hooks straightforward |
| Logging | Structured JSONL | Human-readable, queryable with jq, no log infrastructure needed |
| Deployment | Docker Compose | Reproducible environment for Phase 3 standalone machine |
| Analysis | Python (pandas + matplotlib) | Standard research toolchain, CSV/JSON native |

---

## 2. Project Structure (Target)

```
agent-world/
├── agent_world/               # Core Python backend
│   ├── models/
│   │   ├── agent.py           # Agent, AgentState dataclasses
│   │   └── events.py          # LifecycleEvent, EventType enums
│   ├── db/
│   │   ├── schema.py          # Table definitions + init
│   │   └── agent_repo.py      # CRUD helpers
│   ├── orchestrator/
│   │   ├── engine.py          # SimEngine (tick loop)
│   │   ├── scheduler.py       # Action assignment per agent
│   │   └── event_bus.py       # Pub/sub event system
│   ├── maintenance/
│   │   ├── health.py          # HealthMonitor
│   │   ├── recovery.py        # RecoveryManager
│   │   ├── logger.py          # SimLogger (JSONL streams)
│   │   ├── errors.py          # Error classification
│   │   └── checkpoint.py      # CheckpointManager
│   ├── analytics/
│   │   ├── kpis.py            # KPIEngine
│   │   ├── pipeline.py        # TrackingPipeline
│   │   ├── exporter.py        # CSV/JSON export
│   │   └── alerts.py          # AlertEngine
│   ├── api/
│   │   ├── server.py          # FastAPI app
│   │   └── schemas.py         # Pydantic response models
│   └── config.py              # SimConfig + loader
├── gui/                       # React frontend
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── App.jsx
│       └── styles/
├── tests/                     # pytest suites
├── docs/                      # All governance + research docs
├── exports/                   # Committed CSVs and JSON exports
├── checkpoints/               # Auto-generated, gitignored
├── logs/                      # Auto-generated, gitignored
├── config.json                # Experiment configuration
├── docker-compose.yml         # Phase 3 deployment
├── requirements.txt
├── run.sh                     # Start API + GUI together
└── README.md
```

---

## 3. Development Sequence

### Phase 1 — Lab Construction

| Subphase | Module(s) Built | Key Dependency | Est. Effort |
|---|---|---|---|
| 1.1 Agent Population | models/, db/, spawner.py, config.py | None | 3–5 days |
| 1.2 Virtual Environment | world.py, ledger.py | 1.1 complete | 2–4 days |
| 1.3 Orchestration | orchestrator/ | 1.2 complete | 3–5 days |
| 1.4 Maintenance | maintenance/ | 1.3 complete | 3–4 days |
| 1.5 Performance Tracking | analytics/ | 1.4 complete | 3–4 days |
| 1.6 GUI | api/, gui/ | 1.5 complete | 5–7 days |

### Phase 2 — Virtual Jobs

| Subphase | Module(s) Built | Key Dependency | Est. Effort |
|---|---|---|---|
| 2.1 Job Framework | jobs/schema.py, jobs/types.py | Phase 1 complete | 3–4 days |
| 2.2 Profit Logic | jobs/profit.py | 2.1 complete | 2–3 days |
| 2.3 Agent-Job Integration | orchestrator updates | 2.2 complete | 3–5 days |
| 2.4 Job Analytics | analytics updates | 2.3 complete | 2–3 days |

### Phase 3 — Production Run

| Subphase | Deliverable | Key Dependency | Est. Effort |
|---|---|---|---|
| 3.1 Standalone Prep | docker-compose.yml, run configs | Phase 2 complete | 3–4 days |
| 3.2 Week Run | 7-day experiment + analysis | 3.1 complete | 7 days run + 1 day analysis |
| 3.3 Month Run | 30-day experiment + report | 3.2 findings | 30 days run + 3 days report |

---

## 4. Coding Standards

### Python
- Type hints on all function signatures
- Docstrings on all public classes and methods
- No global mutable state — everything passed explicitly or via SimConfig
- All DB access through `agent_repo.py` — no raw SQL outside of `db/`
- Exceptions must be caught at the engine level; agents should never crash the sim

### React
- Functional components only, hooks-based state
- No prop drilling beyond 2 levels — use context for shared state
- WebSocket state managed in `useWebSocket.js` hook
- All API calls centralized in `useSimData.js`
- CSS variables in `theme.css` — no hardcoded hex values in components

### Git
- Commit messages: `[subphase] verb: short description`
  - Example: `[1.3] feat: add event bus pub/sub system`
  - Example: `[1.5] fix: fatigue index division by zero on idle agents`
- No commits to `main` directly — PRs only (even solo)
- Each subphase gets its own feature branch

---

## 5. Testing Strategy

| Layer | Framework | Coverage Target |
|---|---|---|
| Models + DB | pytest | 100% of public methods |
| Orchestrator | pytest + asyncio | All state transitions |
| Maintenance | pytest | All failure modes + recovery paths |
| Analytics | pytest | All KPI formulas |
| API | pytest + httpx | All endpoints + WebSocket |
| GUI | Manual (Phase 1) | Visual verification |

Run tests: `pytest tests/ -v`
CI target (Phase 3): GitHub Actions on push to `dev`

---

## 6. Environment Setup

```bash
# Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize DB
python -m agent_world.db.schema

# Run simulation backend
uvicorn agent_world.api.server:app --reload --port 8000

# Run GUI (separate terminal)
cd gui && npm install && npm run dev

# Or run both together
./run.sh
```

---

## 7. Configuration Reference

All parameters live in `config.json`. No hardcoded values in source.

```json
{
  "population_size": 8,
  "db_path": "agent_world.db",
  "starting_energy": 100.0,
  "starting_balance": 0.0,
  "ticks_per_cycle": 10,
  "max_concurrent_workers": 4,
  "energy_regen_per_rest_tick": 15.0,
  "energy_cost_per_work_tick": 10.0,
  "play_cost_per_tick": 5.0,
  "play_energy_regen": 5.0,
  "play_minimum_balance": 5.0,
  "exhaustion_threshold": 20.0,
  "auto_rest_threshold": 15.0,
  "base_pay_per_tick": 5.0,
  "scarcity_mode": "normal",
  "scarcity_multiplier": 1.0,
  "simulation_speed_delay": 0.0,
  "event_log_path": "logs/events.jsonl",
  "checkpoint_interval": 20,
  "health_check_interval": 5,
  "stuck_threshold": 10,
  "max_recoveries": 3,
  "fatigue_alert_threshold": 0.75,
  "earnings_variance_alert": 2.0,
  "zero_earner_cycles": 2,
  "population_profit_drop": 0.3
}
```

---

*Document Owner: Spence | Agent World Project | DEV_PLAN v1.0*
