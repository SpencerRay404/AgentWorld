from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING

from agent_world.db.agent_repo import emit_lifecycle_event, load_latest_state, save_agent_state
from agent_world.ledger import TxType
from agent_world.models.agent import AgentState, AgentStatus
from agent_world.models.events import LifecycleEvent, LifecycleEventType

if TYPE_CHECKING:
    from agent_world.orchestrator.engine import SimEngine


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RecoveryManager:
    def __init__(self, max_recoveries: int = 3):
        self.max_recoveries = max_recoveries
        self._recovery_counts: Dict[str, int] = defaultdict(int)
        self._recovery_history: Dict[str, List[Dict]] = defaultdict(list)

    def handle(self, health_event: Dict[str, Any], engine: "SimEngine") -> None:
        check_type = health_event["check_type"]
        agent_id = health_event["agent_id"]
        tick = health_event["tick"]

        if agent_id not in {a.agent_id for a in engine.agents}:
            return

        state = engine.states[agent_id]

        # Check termination threshold
        self._recovery_counts[agent_id] += 1
        if self._recovery_counts[agent_id] > self.max_recoveries:
            self._terminate(agent_id, engine, tick)
            return

        if check_type == "STUCK":
            state.status = AgentStatus.IDLE
            state.consecutive_work_ticks = 0
            state.last_action = "recovery:unstuck"
            self._save_and_emit(engine, agent_id, state, tick, "STUCK→IDLE recovery")

        elif check_type == "FROZEN":
            reloaded = load_latest_state(engine.conn, agent_id)
            if reloaded:
                engine.states[agent_id] = reloaded
            else:
                # Respawn with reset state
                cfg = engine.config
                state.status = AgentStatus.IDLE
                state.energy = cfg.starting_energy
                state.balance = cfg.starting_balance
                state.consecutive_work_ticks = 0
                self._save_and_emit(engine, agent_id, state, tick, "FROZEN→respawn recovery")

        elif check_type == "OVERDRAINED":
            state.status = AgentStatus.RESTING
            state.energy = engine.config.exhaustion_threshold + 5.0
            state.last_action = "recovery:energy_restore"
            self._save_and_emit(engine, agent_id, state, tick, "OVERDRAINED→REST recovery")

        elif check_type == "NEGATIVE_BALANCE":
            state.balance = 0.0
            engine.ledger.record(agent_id, 0.0, TxType.ADJUSTMENT, tick,
                                  engine.world.cycle, notes="negative balance clamp")
            engine.event_bus.publish({
                "event_type": "ANOMALY_DETECTED",
                "agent_id": agent_id,
                "tick": tick,
                "payload": {"reason": "negative_balance_clamped"},
            })

        self._recovery_history[agent_id].append({
            "check_type": check_type, "tick": tick
        })

    def _save_and_emit(self, engine: "SimEngine", agent_id: str,
                       state: AgentState, tick: int, notes: str) -> None:
        state.current_tick = tick
        state.recorded_at = _utcnow()
        save_agent_state(engine.conn, state)
        emit_lifecycle_event(engine.conn, LifecycleEvent(
            agent_id=agent_id,
            event_type=LifecycleEventType.ACTIVATED,
            tick=tick,
            timestamp=_utcnow(),
            notes=notes,
        ))

    def _terminate(self, agent_id: str, engine: "SimEngine", tick: int) -> None:
        state = engine.states[agent_id]
        state.status = AgentStatus.TERMINATED
        state.current_tick = tick
        state.recorded_at = _utcnow()
        save_agent_state(engine.conn, state)
        emit_lifecycle_event(engine.conn, LifecycleEvent(
            agent_id=agent_id,
            event_type=LifecycleEventType.TERMINATED,
            tick=tick,
            timestamp=_utcnow(),
            notes=f"exceeded max_recoveries={self.max_recoveries}",
        ))
        engine.agents = [a for a in engine.agents if a.agent_id != agent_id]
