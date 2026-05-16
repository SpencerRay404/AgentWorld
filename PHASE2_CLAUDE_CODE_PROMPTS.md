# Agent World — Claude Code Prompts
## Phase 2: Virtual Jobs & Agent-Job Integration
*Ready-to-paste prompts for Claude Code. Run each subphase in sequence — later prompts reference artifacts from earlier ones.*

---

## SUBPHASE 2.1 — Job Design Framework

```
Continuing "Agent World" — Phase 2, Subphase 2.1: building the job design framework.

Context: Phase 1 is fully complete. We have:
- `agent_world/models/agent.py` — Agent, AgentState dataclasses
- `agent_world/models/events.py` — LifecycleEvent, EventType enums
- `agent_world/db/schema.py` — SQLite tables: agents, agent_states, lifecycle_events, transactions, world_snapshots, kpi_snapshots
- `agent_world/db/agent_repo.py` — all agent CRUD helpers
- `agent_world/spawner.py` — spawn_agent, spawn_population
- `agent_world/world.py` — World class with tick engine, pay period logic, scarcity params
- `agent_world/ledger.py` — Ledger with full transaction tracking
- `agent_world/orchestrator/scheduler.py` — Scheduler (energy-aware action assignment)
- `agent_world/orchestrator/engine.py` — SimEngine (tick loop, pay period distribution)
- `agent_world/orchestrator/event_bus.py` — EventBus (pub/sub with asyncio.Queue)
- `agent_world/maintenance/` — HealthMonitor, RecoveryManager, SimLogger, CheckpointManager
- `agent_world/analytics/` — KPIEngine, TrackingPipeline, Exporter, AlertEngine
- `agent_world/api/server.py` — FastAPI with all Phase 1 endpoints + WebSocket
- `gui/` — React frontend with live population grid, charts, and control panel
- `config.json` — all simulation parameters
- All pytest suites passing

Now build the job design framework — the schema, types, and availability logic for virtual jobs.

1. **Job Schema**
   Create `agent_world/jobs/schema.py` with the following models:

   ```python
   from dataclasses import dataclass, field
   from enum import Enum
   from typing import Optional
   import uuid

   class JobType(Enum):
       STABLE = "stable"         # low risk, low reward — consistent and repeatable
       SKILLED = "skilled"       # medium risk, medium reward — requires timing/effort
       VOLATILE = "volatile"     # high risk, high reward — unpredictable payouts

   class JobStatus(Enum):
       AVAILABLE = "available"
       AT_CAPACITY = "at_capacity"
       COOLDOWN = "cooldown"
       DISABLED = "disabled"

   @dataclass
   class JobDefinition:
       job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
       name: str = ""
       job_type: JobType = JobType.STABLE
       description: str = ""

       # Capacity
       max_concurrent_workers: int = 3      # how many agents can work this job at once
       cooldown_ticks: int = 0              # ticks to wait after filling capacity before accepting new workers

       # Energy cost
       energy_cost_per_tick: float = 10.0   # overrides world default for this job
       min_energy_to_start: float = 30.0    # agent must have this energy to take the job

       # Payout model
       base_payout_per_tick: float = 5.0    # baseline earnings per tick worked
       payout_variance: float = 0.0         # standard deviation of payout (0 = deterministic)
       completion_bonus: float = 0.0        # one-time bonus paid when job fully completed
       completion_ticks_required: int = 0   # 0 = ongoing (no completion); >0 = must work N ticks for bonus

       # Performance modifiers
       efficiency_multiplier_enabled: bool = False   # whether agent efficiency_score affects payout
       streak_bonus_per_tick: float = 0.0            # extra pay per tick for consecutive work streaks
       max_streak_bonus: float = 0.0                 # cap on streak bonus

       # Availability
       available_from_tick: int = 0         # when job first becomes available in simulation
       available_until_tick: Optional[int] = None   # None = always available
   ```

   Create `agent_world/jobs/types.py` with three concrete job definitions:

   **STABLE — "Data Entry":**
   - Base payout: 4.0/tick, variance: 0.5, energy cost: 8.0/tick
   - Max concurrent workers: 4, no cooldown
   - No completion bonus, no streak bonuses
   - Always available
   - Description: "Steady, repetitive work. Low energy cost. Reliable but unspectacular pay."

   **SKILLED — "Market Analysis":**
   - Base payout: 7.0/tick, variance: 2.0, energy cost: 12.0/tick
   - Max concurrent workers: 2, cooldown: 3 ticks after reaching capacity
   - Completion bonus: 15.0 after 5 consecutive ticks (completion_ticks_required=5)
   - Streak bonus: 0.5/tick per consecutive tick worked (max 5.0 bonus/tick)
   - Min energy to start: 40.0
   - Description: "Requires focus and timing. Higher energy burn but completion bonuses reward consistency."

   **VOLATILE — "Crypto Arbitrage":**
   - Base payout: 3.0/tick, variance: 12.0, energy cost: 15.0/tick
   - Max concurrent workers: 1, cooldown: 5 ticks
   - No completion bonus, but efficiency_multiplier_enabled: True (efficient agents earn more)
   - Min energy to start: 50.0
   - Description: "High variance, high ceiling. Efficient agents can triple their pay — but crashes are common."

2. **Job Registry**
   Create `agent_world/jobs/registry.py` with a `JobRegistry` class:
   - Stores all available JobDefinitions in memory (loaded from config or hardcoded defaults)
   - `register(job: JobDefinition)` — adds a job to the registry
   - `get(job_id: str) -> JobDefinition` — retrieves a job by ID
   - `list_available(tick: int) -> list[JobDefinition]` — returns jobs where status is AVAILABLE at this tick (checks available_from_tick, available_until_tick)
   - `get_all() -> list[JobDefinition]` — returns all registered jobs regardless of availability

3. **Job Availability Logic**
   Create `agent_world/jobs/availability.py` with a `JobAvailabilityManager` class:
   - Tracks current occupancy for each job: how many agents are currently working it
   - `can_take_job(job: JobDefinition, agent: Agent, agent_state: AgentState, tick: int) -> tuple[bool, str]`
     - Returns (True, "") if eligible, or (False, "reason") if not
     - Checks: job capacity, agent energy >= min_energy_to_start, job is AVAILABLE (not COOLDOWN/DISABLED)
   - `assign_agent_to_job(agent_id: str, job_id: str, tick: int)` — occupancy tracking, status updates
   - `release_agent_from_job(agent_id: str, job_id: str, tick: int)` — decrement occupancy, trigger cooldown if needed
   - `get_job_status(job_id: str, tick: int) -> JobStatus` — returns current status
   - `get_occupancy(job_id: str) -> int` — current number of agents working this job
   - Persist occupancy and cooldown state to SQLite: `job_assignments(assignment_id, agent_id, job_id, started_tick, ended_tick, status)`

4. **Update SQLite Schema**
   Add two new tables to `agent_world/db/schema.py`:

   ```sql
   CREATE TABLE IF NOT EXISTS job_assignments (
       assignment_id TEXT PRIMARY KEY,
       agent_id TEXT NOT NULL,
       job_id TEXT NOT NULL,
       started_tick INTEGER,
       ended_tick INTEGER,
       consecutive_ticks INTEGER DEFAULT 0,
       status TEXT DEFAULT 'active',   -- active | completed | abandoned
       created_at TEXT
   );

   CREATE TABLE IF NOT EXISTS job_performance (
       perf_id TEXT PRIMARY KEY,
       job_id TEXT NOT NULL,
       tick INTEGER NOT NULL,
       agents_working INTEGER,
       total_payout_this_tick REAL,
       avg_payout_per_agent REAL,
       completion_count INTEGER DEFAULT 0,
       recorded_at TEXT
   );
   ```

5. **Update Config**
   Add to `config.json`:
   ```json
   "jobs": {
       "available_types": ["data_entry", "market_analysis", "crypto_arbitrage"],
       "job_selection_randomness": 0.2
   }
   ```

6. **Tests**
   Write `tests/test_jobs_schema.py`:
   - All three job types instantiate correctly with expected field values
   - JobRegistry registers and retrieves jobs by ID
   - `list_available()` respects `available_from_tick` and `available_until_tick`
   - `can_take_job()` returns False if agent has insufficient energy
   - `can_take_job()` returns False if job is at capacity
   - `assign_agent_to_job()` increments occupancy, `release_agent_from_job()` decrements it
   - Cooldown activates when job reaches capacity, releases after cooldown_ticks

Deliverables:
- `agent_world/jobs/__init__.py`
- `agent_world/jobs/schema.py` — JobDefinition, JobType, JobStatus
- `agent_world/jobs/types.py` — three concrete job definitions (DATA_ENTRY, MARKET_ANALYSIS, CRYPTO_ARBITRAGE)
- `agent_world/jobs/registry.py` — JobRegistry
- `agent_world/jobs/availability.py` — JobAvailabilityManager
- Updated `agent_world/db/schema.py` — new tables
- Updated `config.json`
- `tests/test_jobs_schema.py`

Demo: Print all registered jobs with their schemas. Show availability status at tick 0. Attempt to assign 3 agents to MARKET_ANALYSIS (capacity 2) and show that the third is rejected with a reason.
```

---

## SUBPHASE 2.2 — Profit Logic

```
Continuing "Agent World" — Phase 2, Subphase 2.2: building the profit calculation and reward system.

Context: Subphase 2.1 is complete. We have:
- `agent_world/jobs/schema.py` — JobDefinition with all payout fields
- `agent_world/jobs/types.py` — DATA_ENTRY, MARKET_ANALYSIS, CRYPTO_ARBITRAGE definitions
- `agent_world/jobs/registry.py` — JobRegistry
- `agent_world/jobs/availability.py` — JobAvailabilityManager with occupancy tracking
- SQLite tables: job_assignments, job_performance

Now build the profit calculation engine — the formulas that turn agent effort into earnings.

1. **Profit Calculator**
   Create `agent_world/jobs/profit.py` with a `ProfitCalculator` class.

   Implement this payout formula for each tick an agent works a job:

   ```
   tick_earnings = base_payout + variance_roll + streak_bonus + efficiency_bonus

   Where:
   - base_payout = job.base_payout_per_tick * world_scarcity_multiplier
   - variance_roll = random.gauss(0, job.payout_variance)   # can be negative
   - streak_bonus = min(consecutive_ticks * job.streak_bonus_per_tick, job.max_streak_bonus)
   - efficiency_bonus = 0 (if not efficiency_multiplier_enabled)
                      = base_payout * (agent.efficiency_score - 1.0) (if enabled)
                        where efficiency_score is from KPIEngine
   - Final: max(0, tick_earnings)  # earnings cannot go negative
   ```

   Methods:
   ```python
   def compute_tick_earnings(
       self,
       job: JobDefinition,
       agent: Agent,
       consecutive_ticks: int,
       world_scarcity_multiplier: float,
       efficiency_score: float = 1.0,
       seed: int | None = None,   # for deterministic testing
   ) -> dict:
       """
       Returns:
       {
           "gross_earnings": float,
           "base_payout": float,
           "variance_roll": float,
           "streak_bonus": float,
           "efficiency_bonus": float,
           "scarcity_adjusted": bool,
       }
       """

   def compute_completion_bonus(
       self,
       job: JobDefinition,
       agent: Agent,
       consecutive_ticks_completed: int,
   ) -> float:
       """
       Returns completion_bonus if agent has worked consecutive_ticks_required consecutive ticks.
       Returns 0.0 if job has no completion requirement or requirement not met.
       Resets streak tracking — agent starts fresh after collecting bonus.
       """

   def compute_payout_summary(
       self,
       job_id: str,
       tick: int,
       agent_payouts: dict[str, float],   # agent_id → earnings this tick
   ) -> dict:
       """
       Returns aggregate stats for logging to job_performance table:
       {
           "job_id": str,
           "tick": int,
           "agents_working": int,
           "total_payout": float,
           "avg_payout_per_agent": float,
           "min_payout": float,
           "max_payout": float,
       }
       """
   ```

2. **Payout Processing Pipeline**
   Create `agent_world/jobs/payout_pipeline.py` with a `PayoutPipeline` class.

   The payout pipeline runs once per tick inside SimEngine.run_tick(), after agent actions are assigned. It:

   1. Iterates all agents currently assigned to a job
   2. Calls `ProfitCalculator.compute_tick_earnings()` for each
   3. Calls `ProfitCalculator.compute_completion_bonus()` if consecutive_ticks_required is met
   4. Records earnings via `Ledger.record(agent_id, earnings, tx_type=EARNING, tick, cycle)`
   5. Updates `job_assignments.consecutive_ticks` for each agent
   6. Logs `job_performance` summary row for this tick
   7. Publishes a `JOB_PAYOUT` event to EventBus

   Methods:
   ```python
   def process_tick(
       self,
       tick: int,
       cycle: int,
       active_assignments: dict[str, str],   # agent_id → job_id
       agents: dict[str, tuple[Agent, AgentState]],
       world: World,
       ledger: Ledger,
       kpi_engine,   # for efficiency scores
   ) -> dict[str, float]:             # returns agent_id → earnings_this_tick
   ```

3. **Reward Signal (Success vs. Failure)**
   Add reward signal tracking to job_assignments:
   - A STABLE job tick is always a "success" (variance is low, rarely negative)
   - A SKILLED job tick is a "success" if tick_earnings > base_payout (beat the base)
   - A VOLATILE job tick is a "success" if tick_earnings > 0 (not a negative outcome)

   Add to `job_assignments` table: `success_ticks INTEGER DEFAULT 0`, `failure_ticks INTEGER DEFAULT 0`

   Update PayoutPipeline to classify and record success/failure per tick.

4. **Performance Bonuses Summary**
   Add to `agent_world/db/agent_repo.py`:
   ```python
   def get_agent_job_performance(
       agent_id: str,
       job_id: str | None = None
   ) -> dict:
       """
       Returns per-job performance summary for an agent:
       {
           "job_id": str,
           "total_ticks": int,
           "total_earnings": float,
           "success_rate": float,
           "completion_bonuses_earned": int,
           "avg_earnings_per_tick": float,
       }
       """
   ```

5. **Update SimEngine**
   Update `agent_world/orchestrator/engine.py` to integrate PayoutPipeline:
   - After scheduler assigns actions each tick, collect which agents are WORKING and their job_ids
   - Call `payout_pipeline.process_tick()` to compute and record earnings
   - Replace the Phase 1 stub payout (base_pay * ticks_worked * scarcity) with the full profit formula

6. **Tests**
   Write `tests/test_profit.py`:
   - STABLE job: 10 ticks worked, zero variance → earnings exactly base_payout × 10 × scarcity
   - MARKET_ANALYSIS: 5 consecutive ticks → completion_bonus fires exactly once at tick 5, streak resets
   - VOLATILE: efficiency_multiplier_enabled — agent with efficiency_score=1.5 earns 50% more base
   - Negative variance_roll: final earnings always >= 0 (floor at zero)
   - PayoutPipeline records Ledger entry for each agent each tick
   - Job performance summary rows are written to SQLite

Deliverables:
- `agent_world/jobs/profit.py` — ProfitCalculator
- `agent_world/jobs/payout_pipeline.py` — PayoutPipeline
- Updated `agent_world/orchestrator/engine.py` — PayoutPipeline integrated
- Updated `agent_world/db/schema.py` — success/failure columns on job_assignments
- `tests/test_profit.py`

Demo: Run a 30-tick simulation. For each agent, print: job they worked most, total earnings from that job, success rate, any completion bonuses earned. Compare earnings across the three job types.
```

---

## SUBPHASE 2.3 — Agent-Job Integration

```
Continuing "Agent World" — Phase 2, Subphase 2.3: connecting agent decision-making to job selection.

Context: Subphases 2.1 and 2.2 are complete. We have:
- Full job schema: DATA_ENTRY, MARKET_ANALYSIS, CRYPTO_ARBITRAGE
- JobRegistry, JobAvailabilityManager
- ProfitCalculator with variance, streak bonuses, efficiency bonuses
- PayoutPipeline integrated into SimEngine
- Ledger records all job earnings per tick

The current Scheduler assigns agents to WORKING/RESTING/PLAYING states but doesn't know about specific jobs — it just flips the status. Now we need to connect agent decision-making to actual job selection.

1. **Job Selection Heuristics**
   Create `agent_world/jobs/selector.py` with a `JobSelector` class.

   When an agent's scheduler assigns status = WORKING, the JobSelector determines which job they take:

   ```python
   def select_job(
       self,
       agent: Agent,
       agent_state: AgentState,
       available_jobs: list[JobDefinition],
       agent_history: dict,   # recent performance data per job
       config: dict,
   ) -> JobDefinition | None:
       """
       Job selection algorithm — energy-aware and balance-aware:

       1. Filter: remove jobs where agent can't meet min_energy_to_start
       2. Filter: remove jobs at capacity (not available)
       3. If no jobs available: return None (agent idles instead of working)

       4. Score each remaining job:
          score = (
              job.base_payout_per_tick * 0.4          # base earnings weight
            + prior_success_rate * 10 * 0.3           # historical success weight
            + (1 / energy_cost_per_tick) * 5 * 0.2   # energy efficiency weight
            + personality_fit_score * 0.1             # personality alignment weight
          )

          Where:
          - prior_success_rate = agent's historical success rate on this job (0–1), default 0.5 if unknown
          - personality_fit_score: STABLE fits balanced+conservative, VOLATILE fits risk-tolerant agents
            (computed from agent.personality_weights['risk_tolerance'])

       5. Apply randomness: with probability config['jobs']['job_selection_randomness'],
          pick a random job instead of the highest scorer (encourages exploration)

       6. Return highest-scored job
       """

   def compute_personality_fit(
       self,
       agent: Agent,
       job: JobDefinition,
   ) -> float:
       """
       Returns 0.0–1.0 score for how well this job matches agent personality.
       - STABLE: high score for agents with low risk_tolerance
       - SKILLED: high score for balanced agents
       - VOLATILE: high score for agents with high risk_tolerance
       """
   ```

2. **Update Scheduler**
   Update `agent_world/orchestrator/scheduler.py`:
   - Inject `JobSelector` and `JobAvailabilityManager` into Scheduler
   - When action is WORKING: call `JobSelector.select_job()` to get the specific job
   - If job is None (none available): redirect agent to RESTING instead
   - Call `JobAvailabilityManager.assign_agent_to_job()` on success
   - When action changes away from WORKING: call `JobAvailabilityManager.release_agent_from_job()`
   - Track current job_id on AgentState: add `current_job_id: str | None = None` field

3. **Update AgentState**
   Update `agent_world/models/agent.py`:
   ```python
   @dataclass
   class AgentState:
       # ... existing fields ...
       current_job_id: str | None = None          # active job, if WORKING
       consecutive_job_ticks: int = 0              # ticks on current job (streak tracking)
       total_ticks_by_job: dict = field(default_factory=dict)  # job_id → tick count
   ```

   Update `agent_repo.save_agent_state()` to persist these new fields.

4. **Stress Test**
   After integration, run a stress test:
   - Spawn 10 agents
   - Run 100 ticks
   - Validate:
     - Total job occupancy across all ticks never exceeds max_concurrent_workers per job
     - Every agent with WORKING status has a non-None current_job_id
     - Agent balances reflect job earnings (cross-check Ledger with AgentState.balance)
     - Some agents specialize naturally (> 60% of their work ticks on one job)
     - VOLATILE job shows higher earnings variance than STABLE job (std_dev > 2× STABLE)

5. **Energy Cost Tuning**
   Run the 100-tick stress test and observe:
   - Are agents spending too much time exhausted? (>20% of ticks in EXHAUSTED/RESTING forced)
   - Is any job draining agents too fast (VOLATILE at 15.0 energy/tick)?
   
   Adjust energy recovery and job costs in `config.json` to produce interesting behavior:
   - Agents should have meaningful choice between jobs
   - VOLATILE should be tempting but clearly riskier
   - Agents shouldn't be stuck in rest cycles more than 30% of total ticks

   Document the final tuned values in a comment block in `config.json`.

6. **Tests**
   Write `tests/test_job_integration.py`:
   - Agent with low energy (25.0) cannot take CRYPTO_ARBITRAGE (min 50.0)
   - Agent selects STABLE job when no higher-energy jobs available
   - High risk_tolerance agent scores VOLATILE higher than low risk_tolerance agent
   - Randomness flag causes occasional non-optimal selection
   - After 50 ticks, occupancy counts per job never exceed max_concurrent_workers
   - AgentState.current_job_id updates correctly on assign/release

Deliverables:
- `agent_world/jobs/selector.py` — JobSelector
- Updated `agent_world/orchestrator/scheduler.py` — job-aware scheduling
- Updated `agent_world/models/agent.py` — AgentState with job tracking fields
- Updated `agent_world/db/agent_repo.py` — persist new AgentState fields
- `tests/test_job_integration.py`
- Updated `config.json` with tuned energy parameters (documented)

Demo: Run a 100-tick simulation with 10 agents. Print a final table showing: each agent's name, role type, dominant job (most ticks), total earnings from each job, and success rate per job. Show that agents with different personality_weights gravitate toward different job types.
```

---

## SUBPHASE 2.4 — Job Analytics

```
Continuing "Agent World" — Phase 2, Subphase 2.4: adding job-level performance analytics.

Context: Subphases 2.1–2.3 are complete. The full job system is working:
- Agents select, execute, and are compensated for specific jobs
- Job earnings vary by type, streak, efficiency, and scarcity
- All earnings flow through Ledger and job_performance table
- AgentState tracks current_job_id and consecutive_job_ticks

Now build the job analytics layer — the analysis tools that turn job performance data into research insights.

1. **Job Analytics Module**
   Create `agent_world/analytics/jobs.py` with a `JobAnalytics` class:

   ```python
   class JobAnalytics:

       def job_profitability_ranking(self, cycle: int | None = None) -> list[dict]:
           """
           Ranks jobs by average earnings per agent per tick.
           Returns list sorted by avg_earnings_per_tick descending:
           [{"job_id": str, "job_name": str, "avg_earnings_per_tick": float,
             "total_payouts": float, "total_ticks_worked": int, "agent_count": int}]
           """

       def agent_job_preference_over_time(
           self,
           agent_id: str,
           cycle_window: int = 5
       ) -> dict:
           """
           Tracks which job each agent prefers over rolling windows.
           Returns: {"agent_id": str, "preferences_by_cycle": [{"cycle": int, "dominant_job": str, "pct": float}]}
           Useful for detecting specialization or drift.
           """

       def job_completion_rate(self, job_id: str, cycle: int | None = None) -> dict:
           """
           For jobs with completion_ticks_required > 0:
           Returns: {"job_id": str, "completion_attempts": int, "completions": int, "rate": float}
           """

       def job_selection_heatmap(self, tick_start: int, tick_end: int) -> dict:
           """
           Returns matrix of agent × job → tick count for visualization.
           {"agents": list[str], "jobs": list[str], "matrix": list[list[int]]}
           """

       def earnings_by_job_type(self, cycle: int | None = None) -> dict:
           """
           Aggregate earnings comparison across STABLE / SKILLED / VOLATILE.
           {"STABLE": {"total": float, "avg_per_tick": float, "agents_ever_used": int},
            "SKILLED": {...}, "VOLATILE": {...}}
           """

       def failure_pattern_analysis(self) -> list[dict]:
           """
           Identifies agents with high failure rates on specific jobs.
           Returns list of {"agent_id": str, "job_id": str, "failure_rate": float, "recommendation": str}
           where recommendation is: "avoid_job" | "adjust_personality" | "acceptable"
           """
   ```

2. **Preference Drift Detection**
   Add `detect_preference_drift(agent_id: str, lookback_cycles: int = 10) -> dict` to JobAnalytics:
   - Computes the agent's dominant job for each of the last N cycles
   - Returns: `{"drifted": bool, "from_job": str | None, "to_job": str | None, "drift_cycle": int | None}`
   - An agent "drifts" if their dominant job changes for more than 3 consecutive cycles

3. **Export Job Performance Dataset**
   Add to `agent_world/analytics/exporter.py`:
   ```python
   def export_job_performance_csv(self, path: str, cycle: int | None = None) -> None:
       """
       Exports per-job-per-tick performance summary.
       Columns: tick, cycle, job_id, job_name, job_type, agents_working, total_payout,
                avg_payout_per_agent, completion_count
       """

   def export_agent_job_summary_csv(self, path: str) -> None:
       """
       Exports per-agent-per-job lifetime performance.
       Columns: agent_id, agent_name, role_type, job_id, job_name, total_ticks,
                total_earnings, avg_earnings_per_tick, success_rate, completions
       """
   ```

4. **Wire into KPIEngine**
   Update `agent_world/analytics/kpis.py`:
   - Add `job_diversity_index(agent_id)` — entropy-based measure of how spread an agent's time is across jobs (0 = always one job, 1 = perfectly even spread)
   - Add `population_job_concentration(cycle=None)` — what fraction of total work ticks are on each job type (population-level)
   - Include both in the full KPI report from `compute_full_report()`

5. **Update API**
   Add new endpoints to `agent_world/api/server.py`:
   - `GET /jobs` — returns all job definitions with current occupancy and status
   - `GET /jobs/{job_id}/performance` — returns job_profitability_ranking for a specific job + time series
   - `GET /jobs/{job_id}/agents` — returns list of agents currently working this job
   - `GET /analytics/jobs/ranking` — returns job_profitability_ranking across all jobs
   - `GET /analytics/agents/{agent_id}/jobs` — returns agent's job preference history

6. **Update GUI**
   Add a Jobs Analytics section to the React dashboard:
   - Job performance table: one row per job, columns: name, type, avg earnings/tick, total agents ever, current occupancy
   - Job selection heatmap visualization (grid: agents × jobs, color = tick intensity)
   - Preference drift indicator per agent (badge in agent detail drawer: "Drifting toward VOLATILE")
   - Earnings by job type: grouped bar chart (STABLE vs SKILLED vs VOLATILE)

7. **Phase 2 Exit Gate Validation**
   Run a 200-tick simulation with 10 agents. Verify all exit criteria:

   **Required:**
   - [ ] All 3 job types active and generating earnings
   - [ ] No occupancy violations (max_concurrent_workers respected throughout)
   - [ ] Agent balances reflect job performance (cross-verify Ledger totals vs AgentState.balance)
   - [ ] Job completion bonuses fire for MARKET_ANALYSIS agents who maintain streaks
   - [ ] Observable differentiation across job types (VOLATILE variance >> STABLE variance in earnings)
   - [ ] Job performance data fully exportable to CSV with accurate figures
   - [ ] GUI shows live job occupancy and earnings

8. **Tests**
   Write `tests/test_job_analytics.py`:
   - job_profitability_ranking returns jobs sorted by avg_earnings_per_tick
   - agent_job_preference_over_time correctly identifies dominant job per cycle
   - preference drift detected when dominant job changes 3+ consecutive cycles
   - job_diversity_index returns 0 for agent who only works one job
   - export_job_performance_csv produces valid CSV with correct row count
   - API endpoint GET /jobs returns all 3 job definitions with occupancy counts

Deliverables:
- `agent_world/analytics/jobs.py` — JobAnalytics class
- Updated `agent_world/analytics/exporter.py` — job export functions
- Updated `agent_world/analytics/kpis.py` — job diversity KPIs
- Updated `agent_world/api/server.py` — new job analytics endpoints
- Updated `gui/` — jobs analytics panel and preference drift badges
- `tests/test_job_analytics.py`

Phase 2 exit criteria validation: After running the full 200-tick simulation:
1. Print job_profitability_ranking
2. Show earnings_by_job_type breakdown
3. Print failure_pattern_analysis results
4. Export both CSVs and confirm file sizes / row counts
5. Show any detected preference drifts
```

---

*These prompts are designed to run sequentially in Claude Code. Each subphase assumes all prior subphases are complete. Run them in order: 2.1 → 2.2 → 2.3 → 2.4.*

*Document Owner: Spence | Agent World Project | Phase 2 Prompts v1.0*
