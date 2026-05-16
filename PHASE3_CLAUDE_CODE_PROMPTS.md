# Agent World — Claude Code Prompts
## Phase 3: First Production Run
*Ready-to-paste prompts for Claude Code. Run each subphase in sequence.*

---

## SUBPHASE 3.1 — Standalone Environment Prep

```
Continuing "Agent World" — Phase 3, Subphase 3.1: preparing the full stack for standalone deployment.

Context: Phases 1 and 2 are fully complete. We have:
- Full Python backend: SimEngine, Scheduler, Orchestrator, JobSelector, ProfitCalculator, PayoutPipeline
- All analytics layers: KPIEngine, TrackingPipeline, Exporter, AlertEngine, JobAnalytics
- FastAPI server with WebSocket live updates and all analytics endpoints
- React GUI with live population grid, job analytics, charts, and control panel
- SQLite for all persistence (agent_world.db)
- All tests passing

The system runs correctly in dev mode. Now prepare it for a sustained, unattended production run on a standalone machine. This means: containerized deployment, remote monitoring access, automated checkpointing, and a run configuration system.

1. **Docker Compose Setup**
   Create `docker-compose.yml` in the project root:

   ```yaml
   version: '3.9'

   services:
     backend:
       build:
         context: .
         dockerfile: Dockerfile.backend
       container_name: agent_world_backend
       volumes:
         - ./agent_world.db:/app/agent_world.db
         - ./logs:/app/logs
         - ./checkpoints:/app/checkpoints
         - ./exports:/app/exports
         - ./config.json:/app/config.json
       ports:
         - "8000:8000"
       environment:
         - PYTHONUNBUFFERED=1
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 10s

     frontend:
       build:
         context: ./gui
         dockerfile: Dockerfile.frontend
       container_name: agent_world_frontend
       ports:
         - "3000:80"
       depends_on:
         - backend
       restart: unless-stopped
   ```

   Create `Dockerfile.backend`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["uvicorn", "agent_world.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

   Create `Dockerfile.frontend` (in `gui/`):
   ```dockerfile
   FROM node:20-slim AS builder
   WORKDIR /app
   COPY package*.json .
   RUN npm ci
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/dist /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   EXPOSE 80
   ```

   Create `gui/nginx.conf`:
   ```nginx
   server {
       listen 80;
       root /usr/share/nginx/html;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://backend:8000/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }

       location /ws/ {
           proxy_pass http://backend:8000/ws/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

2. **Health Endpoint**
   Add to `agent_world/api/server.py`:
   ```python
   @app.get("/health")
   async def health_check():
       """Used by Docker healthcheck and remote monitoring."""
       return {
           "status": "healthy",
           "tick": engine.world.tick if engine else 0,
           "uptime_seconds": (datetime.now() - start_time).total_seconds(),
           "db_size_mb": os.path.getsize("agent_world.db") / 1_000_000,
           "checkpoint_count": len(checkpoint_manager.list_checkpoints()),
           "kill_switch_active": False,   # placeholder for Phase 3.2+ monitoring
       }
   ```

3. **Experiment Run Configuration**
   Create `runs/` directory with run config files. Each run is a named JSON file describing the experiment:

   ```json
   // runs/week_run_01.json
   {
       "run_id": "week_run_01",
       "description": "First 7-day run — baseline behavior with 10 agents, default job mix",
       "started_at": null,
       "ended_at": null,
       "status": "planned",   // planned | running | completed | failed

       "simulation": {
           "population_size": 10,
           "target_ticks": 10080,
           "ticks_per_cycle": 10,
           "max_concurrent_workers": 4,
           "simulation_speed_delay": 0.1,    // 0.1s between ticks = ~1000 ticks/min real-time

           "job_mix": {
               "data_entry": true,
               "market_analysis": true,
               "crypto_arbitrage": true
           },

           "scarcity_mode": "normal",
           "scarcity_multiplier": 1.0
       },

       "checkpointing": {
           "interval_ticks": 100,
           "max_checkpoints_to_keep": 50
       },

       "alerts": {
           "fatigue_alert_threshold": 0.75,
           "earnings_variance_alert": 2.0,
           "zero_earner_cycles": 2,
           "population_profit_drop": 0.3
       },

       "analysis": {
           "export_interval_cycles": 10,
           "export_path": "exports/week_run_01/"
           "daily_summary_enabled": true
       }
   }
   ```

   Create `scripts/start_run.py`:
   ```bash
   python scripts/start_run.py --run runs/week_run_01.json
   ```
   This script: loads the run config, validates it, sets SimConfig from it, records started_at, and launches the simulation.

4. **Automated Daily Snapshots**
   Update `CheckpointManager` to support automatic export on a schedule:

   Add to `agent_world/maintenance/checkpoint.py`:
   ```python
   def save_daily_export(self, exporter, run_id: str, cycle: int) -> str:
       """
       At the end of each simulated day (configurable tick threshold), auto-exports:
       - agent_summary.csv
       - tick_history.csv
       - population_report.json
       All saved to exports/{run_id}/day_{N}/
       Returns path to export directory.
       """
   ```

   Wire into SimEngine: every `export_interval_cycles` pay periods, call `save_daily_export()`.

5. **Remote Monitoring Access**
   Document two access methods:

   **Option A — Local Network (same WiFi):**
   - `docker-compose up` on the host machine
   - Access from any device on same network: `http://[host-machine-ip]:3000`
   - Find host IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`

   **Option B — Tailscale (remote access):**
   - Install Tailscale on both the host machine and your laptop
   - Access via Tailscale IP: `http://[tailscale-ip]:3000`
   - Add setup instructions to `README.md`

   Create `scripts/get_access_url.sh`:
   ```bash
   #!/bin/bash
   LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
   echo "Local network URL: http://${LOCAL_IP}:3000"
   echo "API: http://${LOCAL_IP}:8000"
   ```

6. **Hardware Target Spec**
   Create `docs/HARDWARE_SPEC.md`:
   ```markdown
   # Hardware Requirements — Agent World Production Run

   ## Minimum (7-day run, 10 agents)
   - CPU: 2 cores (any modern x86_64)
   - RAM: 2 GB
   - Storage: 10 GB free (DB + logs + exports grow over time)
   - OS: macOS, Linux, or Windows with WSL2
   - Network: Required for remote GUI access only (simulation runs offline)

   ## Recommended (30-day run, 20+ agents)
   - CPU: 4 cores
   - RAM: 4 GB
   - Storage: 50 GB free (SQLite DB can reach 5–10 GB over 30 days)
   - Always-on power: UPS or laptop plugged in

   ## Tested Configurations
   - MacBook Pro M1, 16 GB RAM — runs comfortably at 10 agents
   - Raspberry Pi 4, 4 GB RAM — viable for 10 agents at slower tick speed
   ```

7. **README Update**
   Rewrite `README.md` for production use:
   - Quick start: clone → `docker-compose up` → open http://localhost:3000
   - How to configure a run (edit runs/week_run_01.json)
   - How to monitor: GUI access, daily export location
   - How to safely stop and resume from checkpoint
   - How to export data for analysis

8. **Tests**
   Write `tests/test_deployment.py`:
   - `docker-compose.yml` is valid YAML with required services
   - Health endpoint returns 200 with expected fields
   - `start_run.py` correctly applies run config to SimConfig
   - Daily export creates correct directory structure with all expected files
   - Checkpoint restore after simulated restart produces matching world state

Deliverables:
- `docker-compose.yml` (project root)
- `Dockerfile.backend`
- `gui/Dockerfile.frontend`
- `gui/nginx.conf`
- `runs/week_run_01.json` — week run configuration
- `runs/month_run_01.json` — month run configuration (same structure, 43200 ticks)
- `scripts/start_run.py`
- `scripts/get_access_url.sh`
- Updated `agent_world/maintenance/checkpoint.py` — daily export
- Updated `agent_world/api/server.py` — /health endpoint
- Updated `README.md`
- `docs/HARDWARE_SPEC.md`
- `tests/test_deployment.py`

Verification: Run `docker-compose up` locally. Open http://localhost:3000 and confirm the GUI loads and shows live simulation data. Run `python scripts/start_run.py --run runs/week_run_01.json` and confirm it starts correctly. Stop with Ctrl+C, restart with `docker-compose up`, confirm the simulation resumes from the last checkpoint.
```

---

## SUBPHASE 3.2 — Week-Long Run

```
Continuing "Agent World" — Phase 3, Subphase 3.2: running and analyzing the first 7-day experiment.

Context: Subphase 3.1 is complete. The full stack is containerized and accessible remotely. Run configs are defined.

This subphase is operational, not code-heavy. The goal is to:
1. Launch the 7-day run
2. Build monitoring tooling for daily observation
3. Run end-of-week analysis

1. **Pre-Run Checklist**
   Before launching, verify:
   - [ ] docker-compose up starts cleanly (both backend + frontend healthy)
   - [ ] GUI loads at localhost:3000 and shows live agent data
   - [ ] Run config `runs/week_run_01.json` has correct parameters (10 agents, 10080 ticks)
   - [ ] Checkpoint interval set to 100 ticks (saves every ~100 ticks)
   - [ ] Export interval set to 10 cycles (auto-export every 10 pay periods)
   - [ ] All alert thresholds configured
   - [ ] Storage available: > 10 GB free

2. **Launch Script**
   Create `scripts/launch_week_run.sh`:
   ```bash
   #!/bin/bash
   echo "Launching Agent World — Week Run 01"
   echo "Target: 10080 ticks (~7 days simulated at 0.1s/tick)"
   echo "Population: 10 agents | Jobs: DATA_ENTRY, MARKET_ANALYSIS, CRYPTO_ARBITRAGE"
   echo ""

   # Start containers
   docker-compose up -d

   # Wait for backend to be healthy
   echo "Waiting for backend..."
   until curl -sf http://localhost:8000/health > /dev/null; do sleep 2; done
   echo "Backend healthy."

   # Start the simulation run
   python scripts/start_run.py --run runs/week_run_01.json

   echo "Run started. Monitor at http://localhost:3000"
   ```

3. **Daily Observer Interface**
   Create `scripts/daily_summary.py` — run this each day to get a mid-run status report:
   ```bash
   python scripts/daily_summary.py --run week_run_01
   ```

   Output:
   ```
   ═══════════════════════════════════════════
   AGENT WORLD — Daily Summary
   Run: week_run_01 | Day 3 of 7
   Ticks: 4,320 / 10,080 (42.9%)
   ═══════════════════════════════════════════

   POPULATION OVERVIEW
   ─────────────────────────────────────────
   Active agents:   10 / 10
   Recoveries today: 2 (agent_004 x1, agent_007 x1)
   Terminated:      0

   KPI SNAPSHOT (Last 5 Cycles)
   ─────────────────────────────────────────
   Population total profit:    $2,847.50
   Avg earnings/agent/cycle:   $28.48
   Earnings Gini coefficient:  0.31 (moderate inequality)
   Fatigue index (avg):        0.42

   TOP EARNERS
   ─────────────────────────────────────────
   1. aria_explorer    $412.30  (VOLATILE: 67% of ticks)
   2. bob_balanced     $387.10  (SKILLED: 54% of ticks)
   3. cal_worker       $351.20  (SKILLED: 48% of ticks)

   JOB PERFORMANCE
   ─────────────────────────────────────────
   DATA_ENTRY:      8.4 agents avg/tick | $4.1 avg/tick/agent
   MARKET_ANALYSIS: 1.8 agents avg/tick | $9.2 avg/tick/agent
   CRYPTO_ARBITRAGE: 0.9 agents avg/tick | $7.1 avg/tick/agent (high variance: σ=11.2)

   ALERTS SINCE YESTERDAY
   ─────────────────────────────────────────
   [WARNING] agent_004 fatigue index: 0.81 (threshold: 0.75) — Cycle 44
   [INFO]    Population profit drop: -18% cycle 40→41 (below 30% threshold)

   BEHAVIORAL OBSERVATIONS
   ─────────────────────────────────────────
   Preference drift detected: agent_007 shifting STABLE → VOLATILE (cycles 40–45)
   3 agents showing specialization (>60% time on one job type)

   Next export: Cycle 50 → exports/week_run_01/day_03/
   ═══════════════════════════════════════════
   ```

   Implement this by querying SQLite directly (read-only) and calling KPIEngine, JobAnalytics.

4. **Mid-Run Observation Protocol**
   Create `docs/OBSERVATION_LOG.md` — a template for recording daily notes:

   ```markdown
   # Week Run 01 — Observation Log

   ## Day 1 (Ticks 0–1440)
   **Date:** [date]
   **Observer:** Spence

   ### What I noticed:
   -

   ### Surprising behaviors:
   -

   ### Agents to watch:
   -

   ### Parameter adjustments (if any):
   - (Note: only adjust between cycles, not mid-cycle)

   ---

   ## Day 2 (Ticks 1440–2880)
   ...
   ```

5. **End-of-Week Analysis Script**
   Create `scripts/week_analysis.py`:
   ```bash
   python scripts/week_analysis.py --run week_run_01 --output reports/week_run_01_analysis.md
   ```

   Generates a full Markdown analysis report covering:
   - Run summary: total ticks, agents, duration, total profit
   - Agent performance rankings with full KPI table
   - Job type comparison: total earnings, avg/tick, occupancy, completion rates
   - Behavioral findings: specialization count, drift events, recovery events
   - KPI time series: earnings per cycle (all agents), state distribution over time
   - Anomaly log: all alerts with severity and resolution
   - Gini coefficient trend over the week
   - Research question responses (from RESULTS_LOG.md RQ1–RQ6) with preliminary evidence
   - Open questions surfaced during the run
   - Recommended parameter adjustments for month run

6. **Parameter Review After Week Run**
   After the week run completes and analysis is reviewed, document any parameter changes for the month run in `runs/month_run_01.json`:

   Common adjustments to consider:
   - Scarcity mode: if agents accumulated too much balance, try `"scarce"` for the month run
   - Population size: increase to 15–20 if system was stable
   - Job capacity: if MARKET_ANALYSIS was always at capacity, increase max_concurrent_workers
   - Energy curves: if agents were too frequently exhausted, reduce energy costs

7. **Tests / Validation**
   Write `scripts/validate_week_run.py` — post-run integrity checker:
   ```bash
   python scripts/validate_week_run.py --run week_run_01
   ```

   Checks:
   - [ ] Total ticks in DB matches expected (±2% tolerance for any restarts)
   - [ ] All agent IDs present throughout the run (no silent disappearances)
   - [ ] Ledger totals match AgentState.balance for all agents
   - [ ] No occupancy violations in job_assignments (max_concurrent_workers respected)
   - [ ] All checkpoints are valid JSON and loadable
   - [ ] No gaps > 10 ticks in the event log (would indicate silent failure)
   - [ ] Exports directory has the expected number of daily snapshots

Deliverables:
- `scripts/launch_week_run.sh`
- `scripts/daily_summary.py`
- `scripts/week_analysis.py`
- `scripts/validate_week_run.py`
- `docs/OBSERVATION_LOG.md` (template)
- `runs/week_run_01.json` (finalized config)
- `reports/week_run_01_analysis.md` (generated after run)
- Updated `docs/OBSERVATION_LOG.md` (filled in during run)

Phase 3.2 exit criteria:
- [ ] 7-day run completes without manual intervention
- [ ] Performance data collected across full run period
- [ ] `validate_week_run.py` passes all checks
- [ ] Week analysis report generated
- [ ] Month run parameters decided (document in runs/month_run_01.json)
```

---

## SUBPHASE 3.3 — Month-Long Run

```
Continuing "Agent World" — Phase 3, Subphase 3.3: the first 30-day production run.

Context: Subphase 3.2 is complete. The 7-day run finished successfully. You have:
- A validated simulation stack running without manual intervention
- Week run analysis revealing behavioral patterns and parameter refinements
- An updated month run config (runs/month_run_01.json) incorporating week-run learnings

This subphase is primarily operational. The code additions are: weekly automated reporting, a stability monitor, and the final research summary generator.

1. **Month Run Configuration**
   Finalize `runs/month_run_01.json` based on week-run learnings:
   - population_size: 15 (increased from 10 if system was stable)
   - target_ticks: 43200 (30 days × 1440 ticks/day)
   - simulation_speed_delay: 0.1 (same as week run for consistent real-time pacing)
   - Scarcity and energy parameters refined from week-run observations

2. **Weekly Auto-Report**
   Create `scripts/weekly_report_job.py` — runs every 7 simulated days (10080 ticks):

   Wire into SimEngine: every 10080 ticks, call:
   ```python
   weekly_report_job.generate(
       run_id="month_run_01",
       week_number=current_week,
       output_path=f"reports/month_run_01/week_{current_week}.md"
   )
   ```

   Each weekly report includes:
   - Population health: active agents, recoveries, terminations this week
   - Earnings trend: population total profit, week-over-week change
   - Job preference summary: dominant job per agent, any preference shifts
   - Top/bottom performers this week
   - Alert summary
   - Research question updates (annotate against RESULTS_LOG.md)

3. **Stability Monitor**
   Create `agent_world/maintenance/stability.py` with a `StabilityMonitor` class:

   Runs alongside the simulation and flags systemic instability:

   ```python
   class StabilityMonitor:

       def check(self, engine, current_tick: int) -> list[StabilityAlert]:
           """
           Runs these checks every 500 ticks:

           - POPULATION_COLLAPSE: < 50% of initial agents active
           - EARNINGS_STAGNATION: population total profit unchanged for 20+ cycles
           - SINGLE_JOB_MONOPOLY: >80% of all work ticks concentrated on one job
           - INFINITE_REST_LOOP: >3 agents stuck in RESTING for 30+ consecutive ticks
           - LEDGER_DRIFT: sum of all agent balances diverges from total Ledger credits by >1%

           Returns list of StabilityAlert dicts.
           """
   ```

   Publish stability alerts to EventBus and log to `logs/stability.jsonl`.
   If POPULATION_COLLAPSE or LEDGER_DRIFT: auto-pause simulation and send critical alert.

4. **Research Annotations**
   Update `RESULTS_LOG.md` with a running research annotation format:

   Each research question (RQ1–RQ6 from Phase 1) gets a running evidence log:
   ```markdown
   ## RQ1: Do agents develop consistent behavioral patterns (specialization)?

   ### Evidence Log
   | Run | Week | Finding | Confidence |
   |-----|------|---------|-----------|
   | week_run_01 | Week 1 | 3 of 10 agents showed >60% job concentration | Medium |
   | month_run_01 | Week 2 | Specialization stabilized — same 3 agents, same jobs | High |
   ...

   ### Current Working Answer (updated each week):
   Preliminary yes — ...
   ```

   Create `scripts/annotate_results.py` — generates RQ evidence rows from current run data and appends to RESULTS_LOG.md.

5. **Final Research Report Generator**
   Create `scripts/generate_final_report.py`:
   ```bash
   python scripts/generate_final_report.py --run month_run_01 --output reports/PHASE3_RESEARCH_SUMMARY.md
   ```

   Generates a comprehensive Markdown research report:

   ```markdown
   # Agent World — Phase 3 Research Summary
   **Run:** month_run_01 | **Duration:** 30 days | **Population:** 15 agents

   ## Executive Summary
   [2–3 paragraph summary of key findings]

   ## Methodology
   [Stack, parameters, job types, monitoring approach]

   ## Research Question Findings

   ### RQ1: Agent Specialization
   **Verdict:** [CONFIRMED | PARTIAL | NOT_CONFIRMED]
   **Evidence:** [quantitative summary]
   **Chart reference:** exports/month_run_01/week_4/agent_job_preference_timeseries.csv

   [Repeat for RQ2–RQ6]

   ## Behavioral Highlights
   [Top 3–5 specific interesting behaviors observed with tick references]

   ## Statistical Summary
   | Metric | Week 1 | Week 2 | Week 3 | Week 4 |
   |--------|--------|--------|--------|--------|
   | Population total profit | ... | | | |
   | Earnings Gini | ... | | | |
   | Avg fatigue index | ... | | | |

   ## Anomaly Log
   [All critical/warning alerts that fired, with resolution]

   ## Parameter Sensitivity Analysis
   [What changed between week run → month run, observed impact]

   ## Open Questions for Future Experiments
   [EXP-006 through whatever new questions emerged]

   ## Recommended Next Steps
   [Phase 4 ideas: new job types, adversarial agents, multi-population, real API integration]
   ```

6. **Month Run Launch**
   Create `scripts/launch_month_run.sh` (same pattern as week run):
   ```bash
   #!/bin/bash
   echo "Launching Agent World — Month Run 01"
   echo "Target: 43200 ticks (~30 days simulated)"
   echo "Population: 15 agents | Jobs: 3 types"
   docker-compose up -d
   until curl -sf http://localhost:8000/health > /dev/null; do sleep 2; done
   python scripts/start_run.py --run runs/month_run_01.json
   echo "Run started. Weekly reports auto-generate to reports/month_run_01/"
   ```

7. **Post-Run Validation**
   Extend `scripts/validate_week_run.py` into `scripts/validate_run.py` (works for any run):
   ```bash
   python scripts/validate_run.py --run month_run_01
   ```

   Additional checks for month run:
   - [ ] 4 weekly report files generated (week_1.md through week_4.md)
   - [ ] Stability monitor logged no POPULATION_COLLAPSE or LEDGER_DRIFT events
   - [ ] All 6 research questions have at least 4 evidence rows each
   - [ ] Export directory has 4 weekly subdirectories with complete CSV sets
   - [ ] DB size is within hardware spec limits (< 10 GB)

Deliverables:
- `runs/month_run_01.json` (finalized)
- `scripts/launch_month_run.sh`
- `scripts/weekly_report_job.py`
- `scripts/annotate_results.py`
- `scripts/generate_final_report.py`
- `scripts/validate_run.py`
- `agent_world/maintenance/stability.py` — StabilityMonitor
- Updated `RESULTS_LOG.md` (template + running evidence log)
- `reports/PHASE3_RESEARCH_SUMMARY.md` (generated after 30-day run)
- `reports/month_run_01/week_1.md` through `week_4.md` (auto-generated during run)

Phase 3 exit criteria:
- [ ] 30-day run completes without manual intervention
- [ ] Performance data collected across full 30-day period
- [ ] 4 weekly reports generated automatically
- [ ] `validate_run.py` passes all checks
- [ ] Research summary report generated and covers all 6 RQs
- [ ] Findings documented and ready for review or external publication
```

---

*Phase 3 is primarily an operational phase. Code in 3.1 enables production deployment; 3.2 and 3.3 are mostly observation, analysis, and reporting. The real output is the research data and findings that emerge from sustained autonomous operation.*

*Document Owner: Spence | Agent World Project | Phase 3 Prompts v1.0*
