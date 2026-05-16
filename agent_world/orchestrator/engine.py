from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from agent_world.config import SimConfig
from agent_world.db.agent_repo import load_latest_state, save_agent_state
from agent_world.db.schema import init_db, save_world_snapshot
from agent_world.ledger import Ledger, TxType
from agent_world.models.agent import Agent, AgentState, AgentStatus
from agent_world.models.events import LifecycleEvent, LifecycleEventType
from agent_world.db.agent_repo import emit_lifecycle_event
from agent_world.orchestrator.event_bus import EventBus
from agent_world.orchestrator.scheduler import Scheduler
from agent_world.spawner import spawn_population
from agent_world.world import World, get_payout_multiplier

import sqlite3


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SimEngine:
    def __init__(self, conn: sqlite3.Connection, config: SimConfig):
        self.conn = conn
        self.config = config
        self.world = World(config)
        self.event_bus = EventBus(config.event_log_path)
        self.scheduler = Scheduler(config)
        self.ledger = Ledger(conn)
        self.agents: List[Agent] = []
        self.states: Dict[str, AgentState] = {}
        self._running = False
        self._paused = False

    def initialize(self) -> None:
        self.agents = spawn_population(self.conn, self.config.population_size, self.config)
        for agent in self.agents:
            state = load_latest_state(self.conn, agent.agent_id)
            self.states[agent.agent_id] = state

    def run_tick(self) -> None:
        self.world.advance_tick()
        tick = self.world.tick
        cycle = self.world.cycle

        # Snapshot work counts BEFORE assignments (which clears active_workers)
        cycle_work_snapshot = dict(self.scheduler.ticks_worked_this_cycle)

        assignments = self.scheduler.assign_actions(self.agents, self.states, self.world)

        for agent_id, new_status in assignments:
            state = self.states[agent_id]
            old_status = state.status

            # Apply energy / balance deltas
            if new_status == AgentStatus.WORKING:
                state.energy = max(0.0, state.energy - self.config.energy_cost_per_work_tick)
                state.consecutive_work_ticks += 1
                self.scheduler.record_work_tick(agent_id)
            elif new_status == AgentStatus.RESTING:
                state.energy = min(100.0, state.energy + self.config.energy_regen_per_rest_tick)
                state.consecutive_work_ticks = 0
            elif new_status == AgentStatus.PLAYING:
                state.balance = max(0.0, state.balance - self.config.play_cost_per_tick)
                state.energy = min(100.0, state.energy + self.config.play_energy_regen)
                state.consecutive_work_ticks = 0
            elif new_status == AgentStatus.EXHAUSTED:
                state.consecutive_work_ticks = 0

            state.status = new_status
            state.current_tick = tick
            state.last_action = new_status.value.lower()
            state.recorded_at = _utcnow()
            save_agent_state(self.conn, state)

            if old_status != new_status:
                self.event_bus.publish({
                    "event_type": "STATE_CHANGED",
                    "agent_id": agent_id,
                    "tick": tick,
                    "payload": {"from": old_status.value, "to": new_status.value},
                })

        # Anomaly detection
        for aid in self.scheduler.anomalies:
            self.event_bus.publish({
                "event_type": "ANOMALY_DETECTED",
                "agent_id": aid,
                "tick": tick,
                "payload": {"reason": "prolonged_exhaustion"},
            })

        # Pay period earnings — use snapshot taken before assignments
        if self.world.is_pay_period():
            multiplier = get_payout_multiplier(self.world)
            for agent_id, _ in assignments:
                ticks_worked = cycle_work_snapshot.get(agent_id, 0)
                if ticks_worked > 0:
                    payout = self.config.base_pay_per_tick * ticks_worked * multiplier
                    self.ledger.record(agent_id, payout, TxType.EARNING, tick, cycle,
                                       notes=f"{ticks_worked} ticks worked")
                    self.states[agent_id].balance += payout
            self.scheduler.ticks_worked_this_cycle.clear()

            self.event_bus.publish({
                "event_type": "PAY_PERIOD",
                "agent_id": None,
                "tick": tick,
                "payload": {"cycle": cycle},
            })

        save_world_snapshot(self.conn, tick, cycle, len(self.world.active_workers))

        self.event_bus.publish({
            "event_type": "TICK_COMPLETE",
            "agent_id": None,
            "tick": tick,
            "payload": self.world.get_world_state(),
        })
        self.event_bus.dispatch_all()

    def run(self, n_ticks: int) -> None:
        self._running = True
        for _ in range(n_ticks):
            if not self._running:
                break
            while self._paused:
                time.sleep(0.05)
            self.run_tick()
            if self.config.simulation_speed_delay > 0:
                time.sleep(self.config.simulation_speed_delay)
        self._running = False

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def stop(self) -> None:
        self._running = False
