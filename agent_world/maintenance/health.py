from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from agent_world.orchestrator.engine import SimEngine


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class HealthMonitor:
    def __init__(self, check_interval: int = 5, stuck_threshold: int = 10):
        self.check_interval = check_interval
        self.stuck_threshold = stuck_threshold
        self._status_streak: Dict[str, int] = defaultdict(int)
        self._zero_energy_streak: Dict[str, int] = defaultdict(int)
        self._last_tick: Dict[str, int] = defaultdict(int)
        self._handlers: List[Callable] = []

    def register(self, handler: Callable) -> None:
        self._handlers.append(handler)

    def check(self, engine: "SimEngine") -> List[Dict[str, Any]]:
        tick = engine.world.tick
        if tick % self.check_interval != 0:
            return []

        events = []
        for agent in engine.agents:
            aid = agent.agent_id
            state = engine.states[aid]

            # STUCK: same status for > stuck_threshold ticks
            if state.status == getattr(self, f"_last_status_{aid}", None):
                self._status_streak[aid] += self.check_interval
            else:
                self._status_streak[aid] = 0
            setattr(self, f"_last_status_{aid}", state.status)

            if self._status_streak[aid] > self.stuck_threshold:
                events.append(self._event("STUCK", aid, "WARNING",
                                          f"status={state.status.value} for {self._status_streak[aid]} ticks", tick))

            # FROZEN: current_tick hasn't advanced
            if state.current_tick == self._last_tick[aid] and tick > 0:
                events.append(self._event("FROZEN", aid, "CRITICAL",
                                          f"current_tick frozen at {state.current_tick}", tick))
            self._last_tick[aid] = state.current_tick

            # OVERDRAINED: energy at 0 for > 5 ticks
            from agent_world.models.agent import AgentStatus
            if state.energy <= 0.0:
                self._zero_energy_streak[aid] += self.check_interval
            else:
                self._zero_energy_streak[aid] = 0
            if self._zero_energy_streak[aid] > 5:
                events.append(self._event("OVERDRAINED", aid, "CRITICAL",
                                          f"energy=0 for {self._zero_energy_streak[aid]} ticks", tick))

            # NEGATIVE_BALANCE
            if state.balance < 0.0:
                events.append(self._event("NEGATIVE_BALANCE", aid, "WARNING",
                                          f"balance={state.balance:.2f}", tick))

        for e in events:
            for h in self._handlers:
                h(e)
        return events

    def _event(self, check_type: str, agent_id: str, severity: str, detail: str, tick: int) -> Dict[str, Any]:
        return {
            "check_type": check_type,
            "agent_id": agent_id,
            "severity": severity,
            "detail": detail,
            "tick": tick,
            "timestamp": _utcnow(),
        }
