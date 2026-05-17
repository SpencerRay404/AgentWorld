from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agent_world.analytics.kpis import KPIEngine

if TYPE_CHECKING:
    from agent_world.orchestrator.engine import SimEngine


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrackingPipeline:
    def __init__(self, engine: "SimEngine"):
        self._engine = engine
        self._kpis = KPIEngine(engine.conn, engine.config)
        self._buffer: List[Dict[str, Any]] = []
        self.running_totals: Dict[str, float] = defaultdict(float)

    @property
    def kpis(self) -> KPIEngine:
        return self._kpis

    def on_tick(self, tick: int, agent_states: Dict[str, Any]) -> None:
        for agent_id, state in agent_states.items():
            self._buffer.append({
                "agent_id": agent_id,
                "tick": tick,
                "status": state.status.value,
                "energy": state.energy,
                "balance": state.balance,
            })

    def flush(self, cycle: int) -> None:
        if not self._buffer:
            return
        conn = self._engine.conn
        for entry in self._buffer:
            agent_id = entry["agent_id"]
            self.running_totals[agent_id] = self._kpis.earnings_per_cycle(agent_id=agent_id)
            conn.execute(
                """INSERT INTO kpi_snapshots (tick, cycle, agent_id, kpi_name, kpi_value, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (entry["tick"], cycle, agent_id, "balance", entry["balance"], _utcnow()),
            )
        conn.commit()
        self._buffer.clear()

    def compute_full_report(self, cycle: Optional[int] = None) -> Dict[str, Any]:
        agents = self._engine.agents
        report: Dict[str, Any] = {}
        for agent in agents:
            aid = agent.agent_id
            report[aid] = {
                "name": agent.name,
                "role_type": agent.role_type.value,
                "earnings": self._kpis.earnings_per_cycle(agent_id=aid, cycle=cycle),
                "work_rest_play": self._kpis.work_rest_play_ratio(aid),
                "fatigue_index": self._kpis.fatigue_index(aid),
                "efficiency_score": self._kpis.efficiency_score(aid, cycle=cycle),
                "recovery_rate": self._kpis.recovery_rate(agent_id=aid),
            }
        return report
