# Agent World — Claude Code Prompts
## Phase 1: Lab Construction
*Ready-to-paste prompts for Claude Code. Run each subphase in sequence — later prompts reference artifacts from earlier ones.*

---

## SUBPHASE 1.1 — Agent Population Design

```
I'm building a research simulation called "Agent World" — a virtual economy where AI agents live, work, rest, and play. This is Phase 1, Subphase 1.1: designing and implementing the agent population layer.

Project stack: Python backend, SQLite for persistence. Use asyncio for the agent runtime. Structure the project under an `agent_world/` directory.

Build the following:

1. **Agent Identity Schema**
   Create a dataclass or Pydantic model called `Agent` with these fields:
   - `agent_id` (UUID, auto-generated)
   - `name` (string, human-readable label)
   - `role_type` (enum: WORKER | BALANCED | EXPLORER — represents behavioral tendency)
   - `personality_weights` (dict with float values for keys: risk_tolerance, rest_preference, efficiency — all between 0.0 and 1.0, sum to 1.0)
   - `created_at` (datetime)

2. **Agent State Model**
   Create an `AgentState` dataclass tracking runtime state:
   - `status` (enum: IDLE | WORKING | RESTING | PLAYING | EXHAUSTED | TERMINATED)
   - `energy` (float 0.0–100.0, starts at 100.0)
   - `balance` (float, starts at 0.0)
   - `current_tick` (int, world tick counter)
   - `last_action` (string description of last action taken)
   - `consecutive_work_ticks` (int, used to detect overwork)

3. **Persistence Layer**
   Set up SQLite via the `sqlite3` stdlib module (no ORM). Create two tables:
   - `agents` — stores identity fields (insert once at spawn)
   - `agent_states` — append-only event log (insert a new row every time state changes, with a `recorded_at` timestamp). This gives us a full audit trail.
   Write helper functions: `save_agent()`, `save_agent_state()`, `load_agent()`, `load_latest_state(agent_id)`, `load_state_history(agent_id)`.

4. **Agent Spawning**
   Write a `spawn_agent(name, role_type, personality_weights=None)` function that:
   - Creates an Agent with a new UUID
   - Randomly generates personality_weights if not provided (normalized to sum to 1.0)
   - Initializes a fresh AgentState (IDLE, full energy, zero balance)
   - Persists both to SQLite
   - Emits a lifecycle event: `SPAWNED`
   Write a `spawn_population(n: int)` function that spawns N agents with randomized names and role types.

5. **Lifecycle Events**
   Create a simple `LifecycleEvent` dataclass with fields: `agent_id`, `event_type` (enum: SPAWNED | ACTIVATED | EXHAUSTED | IDLE | TERMINATED), `tick`, `timestamp`, `notes`.
   Log these to a `lifecycle_events` SQLite table.
   Write an `emit_lifecycle_event()` helper that inserts a row.

6. **Config**
   Create a `config.py` with a `SimConfig` dataclass containing:
   - `population_size: int = 8`
   - `db_path: str = "agent_world.db"`
   - `starting_energy: float = 100.0`
   - `starting_balance: float = 0.0`
   Load config from a `config.json` file if present, else use defaults.

7. **Tests**
   Write a `test_agents.py` using pytest that:
   - Spawns a single agent and verifies identity fields
   - Spawns a population of 5 and checks all were persisted
   - Verifies state history grows with each state update
   - Checks lifecycle events are logged correctly

Deliverables:
- `agent_world/models/agent.py` — Agent and AgentState models
- `agent_world/models/events.py` — LifecycleEvent model and enum
- `agent_world/db/schema.py` — table creation SQL and init function
- `agent_world/db/agent_repo.py` — all persistence helpers
- `agent_world/spawner.py` — spawn_agent and spawn_population
- `agent_world/config.py` — SimConfig and loader
- `tests/test_agents.py` — pytest suite
- `config.json` — default config file

At the end, print a summary showing all spawned agents and their initial states to confirm everything is wired.
```

---

## SUBPHASE 1.2 — Virtual Environment

```
Continuing "Agent World" — Phase 1, Subphase 1.2: building the virtual environment layer.

Context: Subphase 1.1 is complete. We have Agent/AgentState models, SQLite persistence under `agent_world/db/`, a spawner, lifecycle events, and a SimConfig in `config.py`. The DB is initialized via `agent_world/db/schema.py`.

Now build the virtual environment — the world the agents live in.

1. **World Model**
   Create a `World` class in `agent_world/world.py` with:
   - `tick` (int, starts at 0 — each tick is one unit of simulation time)
   - `cycle` (int — a pay period; every N ticks = 1 cycle, configurable)
   - `ticks_per_cycle` (int, default 10, from SimConfig)
   - `max_concurrent_workers` (int — capacity ceiling on how many agents can work at once)
   - `active_workers` (set of agent_ids currently working)
   - `world_time` (derived: tick / ticks_per_cycle gives fractional cycle position)
   - Methods: `advance_tick()`, `is_pay_period()` (returns True when a cycle completes), `get_world_state()` (returns a dict snapshot)

2. **World Clock**
   Implement `advance_tick()` to:
   - Increment `tick` by 1
   - Update `cycle` when a full cycle completes
   - Emit a `TICK` world event to the event bus (stub the event bus for now — just a list of dicts)
   - If it's a pay period, emit a `PAY_PERIOD` world event

3. **Environment Rules**
   Add these as fields on `World` or in SimConfig:
   - `max_concurrent_workers: int = 4` — no more than N agents can be in WORKING state simultaneously
   - `pay_period_length: int = 10` — ticks per cycle
   - `energy_regen_per_rest_tick: float = 15.0` — how much energy resting restores per tick
   - `energy_cost_per_work_tick: float = 10.0` — how much energy working drains per tick
   - `play_cost_per_tick: float = 5.0` — balance cost of playing per tick
   - `play_energy_regen: float = 5.0` — playing also slightly restores energy

4. **Resource Scarcity Parameters**
   Add to SimConfig:
   - `scarcity_mode: str = "normal"` — can be "normal", "scarce", "abundant"
   - `scarcity_multiplier: float = 1.0` — scales job payouts (< 1.0 = scarce, > 1.0 = abundant)
   - Write a `get_payout_multiplier(world: World) -> float` utility function that returns the current scarcity multiplier (for Phase 2 integration)

5. **Economic Ledger**
   Create `agent_world/ledger.py` with a `Ledger` class:
   - Backed by a SQLite table: `transactions(tx_id, agent_id, amount, tx_type, tick, cycle, timestamp, notes)`
   - `tx_type` is an enum: EARNING | PAYMENT | PENALTY | ADJUSTMENT
   - Methods:
     - `record(agent_id, amount, tx_type, tick, cycle, notes="")`
     - `get_balance(agent_id) -> float` (sum of all transactions for agent)
     - `get_cycle_earnings(agent_id, cycle) -> float`
     - `get_population_totals(cycle=None) -> dict` (total earnings per agent, optionally filtered by cycle)
     - `export_csv(path)` — exports full transaction log to CSV

6. **World State Persistence**
   Add a `world_snapshots` table to SQLite: `(snapshot_id, tick, cycle, active_workers_count, timestamp)`
   Call `save_snapshot()` at the end of each tick to record world state over time.

7. **Update SimConfig**
   Add all new world parameters to `config.py` and `config.json`:
   - `ticks_per_cycle`, `max_concurrent_workers`, `energy_regen_per_rest_tick`, `energy_cost_per_work_tick`, `play_cost_per_tick`, `play_energy_regen`, `scarcity_mode`, `scarcity_multiplier`

8. **Tests**
   Write `tests/test_world.py`:
   - World initializes with correct defaults
   - advance_tick() correctly increments tick and detects pay periods
   - Ledger records transactions and returns accurate balance
   - get_population_totals() returns correct aggregations
   - CSV export produces a valid file with correct headers

Deliverables:
- `agent_world/world.py` — World class
- `agent_world/ledger.py` — Ledger class
- Updated `agent_world/db/schema.py` — add transactions and world_snapshots tables
- Updated `agent_world/config.py` and `config.json`
- `tests/test_world.py`

At the end, run a demo: spawn 5 agents, advance the world 15 ticks, record a few sample ledger transactions, and print the world state + population totals.
```

---

## SUBPHASE 1.3 — Orchestration Layer

```
Continuing "Agent World" — Phase 1, Subphase 1.3: building the orchestration layer.

Context: We have:
- `agent_world/models/` — Agent, AgentState, LifecycleEvent models
- `agent_world/db/` — SQLite schema, agent_repo, transactions, world_snapshots tables
- `agent_world/world.py` — World class with tick engine, pay period logic, scarcity params
- `agent_world/ledger.py` — Ledger with full transaction tracking
- `agent_world/spawner.py` — spawn_agent, spawn_population
- `agent_world/config.py` — SimConfig with all world parameters

Now build the orchestration layer — the engine that drives the simulation tick by tick.

1. **Agent Scheduler**
   Create `agent_world/orchestrator/scheduler.py` with a `Scheduler` class:
   - Maintains a list of active Agent objects and their current AgentState
   - Each tick, evaluates each agent and decides its next action based on:
     - If energy < 20.0 → force RESTING (override any preference)
     - If energy >= 20.0 and balance < 10.0 → strong bias toward WORKING
     - Otherwise → use agent's `personality_weights` to probabilistically choose WORKING, RESTING, or PLAYING
   - Applies world capacity constraints: if `active_workers` is at `max_concurrent_workers`, new WORKING assignments are queued or redirected to RESTING
   - Returns a list of `(agent_id, new_status)` assignments for the tick

2. **Tick Engine**
   Create `agent_world/orchestrator/engine.py` with a `SimEngine` class:
   - Holds references to: World, Scheduler, Ledger, all agents
   - `run_tick()` method that:
     1. Calls `world.advance_tick()`
     2. Calls `scheduler.assign_actions()` → gets agent assignments
     3. For each assignment, applies energy changes (work costs energy, rest restores, play costs balance + slightly restores energy)
     4. Updates each agent's AgentState and persists via agent_repo
     5. Publishes events to the event bus
     6. On pay periods: distributes earnings to agents who worked this cycle (stub payout = base_pay * ticks_worked_this_cycle * scarcity_multiplier), records via Ledger
     7. Saves world snapshot
   - `run(n_ticks: int)` method that loops `run_tick()` N times with a configurable delay (default 0 for fast sim, supports real-time mode)
   - `pause()` / `resume()` / `stop()` controls using asyncio events

3. **Event Bus**
   Create `agent_world/orchestrator/event_bus.py` with an `EventBus` class:
   - Simple pub/sub system using asyncio.Queue
   - Event schema: `{ "event_type": str, "agent_id": str | None, "tick": int, "payload": dict, "timestamp": str }`
   - Event types: TICK_COMPLETE | STATE_CHANGED | PAY_PERIOD | AGENT_EXHAUSTED | AGENT_RECOVERED | ANOMALY_DETECTED
   - `publish(event)` — puts event on queue
   - `subscribe(handler_fn)` — registers a callback
   - `dispatch_all()` — drains queue and calls all handlers
   - Write a default `log_handler` that writes events to a JSON log file

4. **Coordination Logic**
   In the Scheduler, add:
   - `work_queue` — list of agents waiting to work when capacity opens up
   - Each tick, check if capacity is available and promote queued agents to WORKING
   - Track `ticks_worked_this_cycle` per agent (reset at pay period)
   - Flag agents that have been EXHAUSTED for more than 3 consecutive ticks as anomalies → publish ANOMALY_DETECTED event

5. **Configurable Experiment Parameters**
   Add to `config.json` (no code changes needed to adjust these):
   - `base_pay_per_tick: float = 5.0`
   - `play_minimum_balance: float = 5.0` (agent needs this balance to play)
   - `exhaustion_threshold: float = 20.0`
   - `auto_rest_threshold: float = 15.0`
   - `simulation_speed_delay: float = 0.0` (seconds between ticks; 0 = fast)
   - `event_log_path: str = "logs/events.jsonl"`

6. **Tests**
   Write `tests/test_orchestrator.py`:
   - Scheduler correctly routes low-energy agents to RESTING
   - Capacity cap prevents more than max_concurrent_workers agents from WORKING
   - Full 20-tick engine run produces correct state transitions
   - Pay period triggers earnings distribution
   - Event bus delivers events to registered handlers
   - Anomaly detection fires for prolonged EXHAUSTED agents

Deliverables:
- `agent_world/orchestrator/scheduler.py`
- `agent_world/orchestrator/engine.py`
- `agent_world/orchestrator/event_bus.py`
- Updated `config.json`
- `logs/` directory created on first run
- `tests/test_orchestrator.py`

Demo at the end: spawn 8 agents, run 30 ticks, print a tick-by-tick summary table showing each agent's status, energy, and balance per tick. Show final ledger totals.
```

---

## SUBPHASE 1.4 — Maintenance Layer

```
Continuing "Agent World" — Phase 1, Subphase 1.4: building the maintenance layer.

Context: The full simulation stack is running:
- Models, DB, World, Ledger, Spawner all complete
- Orchestrator: Scheduler, SimEngine, EventBus all wired
- Events publish to `logs/events.jsonl`
- SimConfig loaded from `config.json`

Now build the maintenance layer — the system that keeps the simulation healthy during long runs.

1. **Health Check System**
   Create `agent_world/maintenance/health.py` with a `HealthMonitor` class:
   - Runs as a background coroutine (asyncio), checks health every N ticks (configurable, default 5)
   - Checks each agent for these failure conditions:
     - STUCK: agent has been in the same status for more than `stuck_threshold` consecutive ticks (default 10) without state change — suggests the scheduler isn't updating it
     - FROZEN: `current_tick` on AgentState hasn't advanced in the last check window — suggests agent is no longer being processed
     - OVERDRAINED: energy has been at 0.0 for more than 5 ticks — agent should have auto-rested but didn't
     - NEGATIVE_BALANCE: balance has gone below 0.0
   - For each failure, emit a health event: `{ "check_type": str, "agent_id": str, "severity": "WARNING" | "CRITICAL", "detail": str }`
   - Publish to EventBus and log to a separate `logs/health.jsonl`

2. **Auto-Recovery Logic**
   Create `agent_world/maintenance/recovery.py` with a `RecoveryManager` class:
   - Subscribes to health events from EventBus
   - Recovery actions per failure type:
     - STUCK → force status to IDLE, reset `consecutive_work_ticks` to 0, emit AGENT_RECOVERED
     - FROZEN → attempt to reload agent state from DB; if corrupted, respawn with same identity and personality but reset energy/balance to starting values; emit AGENT_RECOVERED or SPAWNED
     - OVERDRAINED → force status to RESTING, restore energy to `exhaustion_threshold + 5`, emit AGENT_RECOVERED
     - NEGATIVE_BALANCE → clamp balance to 0.0, log as ADJUSTMENT in Ledger, emit anomaly
   - Track recovery history per agent (how many times recovered, what type)
   - If an agent is recovered more than `max_recoveries` times (default 3) in one cycle → mark as TERMINATED, remove from active pool, log final lifecycle event

3. **Structured Logging**
   Create `agent_world/maintenance/logger.py` with a `SimLogger` class:
   - All logs are structured JSON, one object per line (.jsonl format)
   - Three log streams:
     - `logs/events.jsonl` — all EventBus events
     - `logs/health.jsonl` — health check results
     - `logs/audit.jsonl` — agent state changes (one entry per state update: agent_id, old_status, new_status, energy_delta, balance_delta, tick, timestamp)
   - `SimLogger.log_event(event)`, `SimLogger.log_health(event)`, `SimLogger.log_audit(agent_id, old_state, new_state, tick)`
   - Rotate logs when file exceeds 10MB (rename to `.jsonl.1`, start fresh)
   - Wire SimLogger into SimEngine and RecoveryManager

4. **Error Classification**
   Create `agent_world/maintenance/errors.py`:
   - `ErrorClass` enum: HARD_FAIL | SOFT_FAIL | ANOMALY
   - `classify_error(error_type: str) -> ErrorClass`:
     - HARD_FAIL: FROZEN agent that can't be recovered from DB, DB write failure
     - SOFT_FAIL: STUCK, OVERDRAINED (recoverable with intervention)
     - ANOMALY: NEGATIVE_BALANCE, repeated recovery of same agent, unusual earnings spike
   - Wrap SimEngine's `run_tick()` in try/except; classify exceptions and log with appropriate severity; only halt simulation on HARD_FAIL

5. **Snapshot & Checkpoint System**
   Create `agent_world/maintenance/checkpoint.py` with a `CheckpointManager` class:
   - Every N ticks (configurable, default 20), save a full experiment checkpoint:
     - JSON file: `checkpoints/checkpoint_tick_{N}.json`
     - Contains: current tick, cycle, all agent identities + current states, ledger totals per agent, world config snapshot, event counts
   - `save_checkpoint(engine)` — serializes everything to JSON
   - `load_checkpoint(path) -> dict` — reads and validates checkpoint file
   - `list_checkpoints() -> list` — lists all checkpoint files sorted by tick
   - `restore_from_checkpoint(path, engine)` — rebuilds engine state from checkpoint (agent states, balances, tick counter)
   - Add `checkpoint_interval: int = 20` to `config.json`

6. **Tests**
   Write `tests/test_maintenance.py`:
   - Health monitor correctly flags a stuck agent after threshold
   - RecoveryManager successfully unsticks a stuck agent
   - An overdrained agent gets energy restored and status reset
   - An agent terminated after exceeding max_recoveries
   - Checkpoint saves and restores correctly (tick count matches, balances match)
   - Log rotation triggers when file hits size limit

Deliverables:
- `agent_world/maintenance/health.py`
- `agent_world/maintenance/recovery.py`
- `agent_world/maintenance/logger.py`
- `agent_world/maintenance/errors.py`
- `agent_world/maintenance/checkpoint.py`
- `checkpoints/` directory created on first run
- Updated `config.json` with checkpoint_interval and health check params
- `tests/test_maintenance.py`

Demo: Run a 50-tick simulation, intentionally inject a stuck agent at tick 25, show the health monitor detecting it and the recovery manager resolving it. Print the checkpoint file contents for the tick-40 checkpoint.
```

---

## SUBPHASE 1.5 — Performance Tracking Layer

```
Continuing "Agent World" — Phase 1, Subphase 1.5: building the performance tracking layer.

Context: Full simulation stack is operational including maintenance layer. We have:
- SimEngine running ticks with agent state transitions
- Ledger recording all transactions with tick and cycle metadata
- SimLogger writing to logs/events.jsonl, logs/health.jsonl, logs/audit.jsonl
- CheckpointManager saving snapshots every 20 ticks
- All structured data queryable from SQLite (agent_world.db)

Now build the performance tracking layer — the analytics engine that turns raw simulation data into research-grade insights.

1. **KPI Engine**
   Create `agent_world/analytics/kpis.py` with a `KPIEngine` class:
   Compute the following KPIs, all queryable by agent, by cycle, or across the full run:

   - `earnings_per_cycle(agent_id=None, cycle=None)` → float or dict
     Total earnings in a given cycle. If agent_id=None, returns dict of all agents.

   - `work_rest_play_ratio(agent_id, tick_start=None, tick_end=None)` → dict
     Proportion of ticks spent in each status. Returns `{"work": 0.4, "rest": 0.35, "play": 0.25}`.

   - `population_total_profit(cycle=None)` → float
     Sum of all agent earnings. Optional cycle filter.

   - `fatigue_index(agent_id, tick_start=None, tick_end=None)` → float
     Proxy for over-exploitation. Formula: `(avg_consecutive_work_ticks / ticks_per_cycle) * (1 - avg_energy/100)`. Higher = more fatigued.

   - `earnings_variance(cycle=None)` → dict
     Returns `{"mean": float, "std_dev": float, "min": float, "max": float, "gini": float}` across all agents.
     Implement Gini coefficient calculation to measure inequality.

   - `recovery_rate(agent_id=None)` → float or dict
     Number of recovery events per 10 ticks. Pulled from health logs.

   - `efficiency_score(agent_id, cycle=None)` → float
     Earnings divided by energy spent (ticks_worked * energy_cost_per_work_tick). Higher = more efficient.

2. **Data Collection Pipeline**
   Create `agent_world/analytics/pipeline.py` with a `TrackingPipeline` class:
   - Subscribes to EventBus
   - On every TICK_COMPLETE event: computes a lightweight snapshot of all KPIs and appends to an in-memory buffer
   - On every PAY_PERIOD event: flushes buffer to SQLite table `kpi_snapshots(snapshot_id, tick, cycle, agent_id, kpi_name, kpi_value, timestamp)`
   - On demand: `compute_full_report(cycle=None)` — returns a complete KPI dict for all agents over the specified period
   - Keeps an internal `running_totals` dict updated incrementally (avoids full DB scan every tick)

3. **Export Function**
   Create `agent_world/analytics/exporter.py` with an `Exporter` class:
   - `export_agent_summary_csv(path, cycle=None)` — one row per agent with all KPIs
     Columns: agent_id, name, role_type, total_earnings, avg_earnings_per_cycle, work_ratio, rest_ratio, play_ratio, fatigue_index, efficiency_score, recovery_count
   - `export_tick_history_csv(path, agent_id=None)` — one row per tick per agent
     Columns: tick, cycle, agent_id, status, energy, balance, earnings_this_tick
   - `export_population_report_json(path, cycle=None)` — full population snapshot as JSON
     Includes: run metadata, per-agent KPI dicts, population totals, variance stats
   - `export_kpi_timeseries_csv(path, kpi_name)` — time series of a single KPI across all ticks

4. **Alert Thresholds**
   Create `agent_world/analytics/alerts.py` with an `AlertEngine` class:
   - Configurable thresholds (all in config.json):
     - `fatigue_alert_threshold: float = 0.75` — alert if any agent's fatigue index exceeds this
     - `earnings_variance_alert: float = 2.0` — alert if std_dev / mean ratio exceeds this (high inequality)
     - `zero_earner_cycles: int = 2` — alert if any agent earns nothing for N consecutive cycles
     - `population_profit_drop: float = 0.3` — alert if population total drops >30% cycle-over-cycle
   - `check_alerts(kpi_engine, current_cycle)` — runs all threshold checks, returns list of alert dicts
   - Each alert: `{ "alert_type": str, "severity": "INFO" | "WARNING" | "CRITICAL", "agent_id": str | None, "message": str, "tick": int }`
   - Publish alerts to EventBus and log to `logs/alerts.jsonl`

5. **Wire into SimEngine**
   Update `SimEngine.run_tick()` to:
   - Call `TrackingPipeline.on_tick(tick, agent_states)` each tick
   - Call `AlertEngine.check_alerts()` each pay period
   - Make KPIEngine available as `engine.kpis` for external access

6. **Tests**
   Write `tests/test_analytics.py`:
   - earnings_per_cycle returns correct totals matching Ledger
   - work_rest_play_ratio sums to 1.0
   - fatigue_index produces values in expected range (0.0–1.0+)
   - Gini coefficient returns 0.0 for equal distribution, approaches 1.0 for unequal
   - CSV exports produce valid files with correct column counts
   - Alert fires correctly when fatigue threshold is breached
   - Zero earner alert triggers after N consecutive empty cycles

Deliverables:
- `agent_world/analytics/kpis.py`
- `agent_world/analytics/pipeline.py`
- `agent_world/analytics/exporter.py`
- `agent_world/analytics/alerts.py`
- Updated `agent_world/db/schema.py` — add kpi_snapshots table
- Updated `config.json` — add all alert thresholds
- `tests/test_analytics.py`

Demo: Run a 100-tick simulation with 8 agents, then:
1. Print the full KPI report for all agents
2. Export agent_summary.csv and show first 5 rows
3. Show any alerts that fired during the run
4. Print the Gini coefficient for earnings variance
```

---

## SUBPHASE 1.6 — GUI (Observer Interface)

```
Continuing "Agent World" — Phase 1, Subphase 1.6: building the observer GUI.

Context: The full Python backend is operational:
- SimEngine drives ticks with full agent lifecycle
- Ledger, KPIEngine, TrackingPipeline, AlertEngine all wired
- All data lives in SQLite (agent_world.db) and structured JSON logs
- SimEngine exposes: engine.agents, engine.world, engine.kpis, engine.ledger
- Config loaded from config.json

Now build the observer GUI — a React frontend that lets me watch the simulation live, drill into individual agents, and control the experiment.

**Backend API (FastAPI)**
First, create `agent_world/api/server.py` using FastAPI:

Endpoints:
- `GET /world` — returns current world state (tick, cycle, active_workers_count, scarcity_mode)
- `GET /agents` — returns all agents with their latest state (id, name, role_type, status, energy, balance, last_action)
- `GET /agents/{agent_id}` — returns full agent detail + state history (last 50 ticks) + lifecycle events
- `GET /agents/{agent_id}/transactions` — returns ledger history for agent
- `GET /kpis` — returns full KPI report for current cycle
- `GET /kpis/timeseries?kpi=earnings_per_cycle&cycles=5` — returns time series data
- `GET /alerts` — returns recent alerts (last 20)
- `GET /population` — returns population-level totals and variance stats
- `POST /control/start` — starts the simulation engine
- `POST /control/pause` — pauses
- `POST /control/resume` — resumes
- `POST /control/reset` — resets to initial state (re-spawns population)
- `GET /export/csv?type=agent_summary` — triggers CSV export, returns file download
- `WebSocket /ws/live` — streams live tick events (state changes, pay periods, alerts) as JSON

Run with uvicorn. Enable CORS for localhost:3000.

**React Frontend**
Create a React app in `gui/` using Vite. Use Recharts for charts. No external UI library — custom CSS only.

Design aesthetic: dark terminal/lab theme. Deep navy/charcoal background (#0A0E1A), monospace font (JetBrains Mono or similar), accent colors: teal (#00E5CC) for active/working, violet (#A78BFA) for resting, amber (#FB923C) for playing, red (#F87171) for alerts. Grid-based layout. Minimal chrome — data forward.

Layout (three-panel):

**Panel 1 — Population Grid (left, 40% width)**
- Grid of agent cards, one per agent
- Each card shows: agent name, role badge, status indicator (color-coded), energy bar, balance counter
- Status indicator pulses/animates when WORKING
- Clicking a card opens the agent detail drawer
- Cards sort by balance descending

**Panel 2 — World State (center top)**
- World clock: current tick + cycle displayed prominently
- Cycle progress bar (ticks_remaining_in_cycle / ticks_per_cycle)
- Economic cycle phase indicator: EARNING | PAY_PERIOD
- Status distribution donut chart (how many agents in each state right now)
- Scarcity mode badge

**Panel 3 — Metrics Sidebar (right, 25% width)**
- Population total profit (current cycle + all-time)
- Earnings variance stats (mean, std dev, Gini)
- Top earner + bottom earner this cycle
- Active alert count with severity breakdown
- Recent alerts list (last 5, color-coded by severity)
- Live scrolling event feed (last 10 EventBus events)

**Bottom Bar — Charts**
- Earnings over time: line chart, one line per agent, last 10 cycles
- State distribution over time: stacked area chart (work/rest/play proportions per cycle)
- Toggle between "by agent" and "population aggregate" views

**Agent Detail Drawer**
- Slides in from right when agent card is clicked
- Shows: full identity (id, role, personality weights as bar chart)
- State timeline: sparkline of energy over last 50 ticks
- Balance history: line chart
- Work/rest/play ratio: horizontal stacked bar
- Full transaction list: scrollable table (tick, type, amount, notes)
- Lifecycle events: timeline list
- Recovery history if any

**Experiment Control Panel**
- Fixed bottom strip: Start / Pause / Resume / Reset buttons
- Speed control: slider for simulation_speed_delay (0ms → 2000ms per tick)
- Population size input (applies on Reset)
- Scarcity mode dropdown (normal / scarce / abundant)
- All controls call the FastAPI /control/* endpoints

**Live Updates**
- Connect to WebSocket `/ws/live` on mount
- On TICK_COMPLETE: refresh agent cards and world clock (no full page reload)
- On PAY_PERIOD: flash a subtle pay period notification, refresh all charts
- On ALERT: show toast notification with severity color and message, increment alert badge

**Deliverables:**
- `agent_world/api/server.py` — FastAPI server
- `agent_world/api/schemas.py` — Pydantic response models
- `gui/` — full React app (Vite)
  - `gui/src/components/PopulationGrid.jsx`
  - `gui/src/components/AgentCard.jsx`
  - `gui/src/components/AgentDetailDrawer.jsx`
  - `gui/src/components/WorldState.jsx`
  - `gui/src/components/MetricsSidebar.jsx`
  - `gui/src/components/Charts.jsx`
  - `gui/src/components/ControlPanel.jsx`
  - `gui/src/hooks/useWebSocket.js`
  - `gui/src/hooks/useSimData.js`
  - `gui/src/App.jsx`
  - `gui/src/styles/theme.css`
- `requirements.txt` — updated with fastapi, uvicorn, websockets
- `gui/package.json`
- `run.sh` — starts both the FastAPI server and the Vite dev server together

End goal: I should be able to run `./run.sh`, open http://localhost:3000, see all 8 agents in the population grid, watch their statuses update in real time as ticks advance, click an agent to see their full history, and use the control panel to pause/resume/reset the simulation.
```

---

*These prompts are designed to be run in Claude Code sequentially. Each subphase assumes the prior one is complete. If you need to resume mid-subphase, paste the relevant context section from the prior prompt at the top of a new session.*

*Document Owner: Spence | Agent World Project | Phase 1 Prompts v1.0*
