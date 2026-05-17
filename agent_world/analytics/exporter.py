from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING

from agent_world.analytics.kpis import KPIEngine

if TYPE_CHECKING:
    from agent_world.orchestrator.engine import SimEngine


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Exporter:
    def __init__(self, engine: "SimEngine"):
        self._engine = engine
        self._kpis = KPIEngine(engine.conn, engine.config)

    def export_agent_summary_csv(self, path: str, cycle: Optional[int] = None) -> None:
        headers = [
            "agent_id", "name", "role_type", "total_earnings",
            "avg_earnings_per_cycle", "work_ratio", "rest_ratio", "play_ratio",
            "fatigue_index", "efficiency_score", "recovery_count",
        ]
        rows = []
        n_cycles = max(self._engine.world.cycle, 1)
        for agent in self._engine.agents:
            aid = agent.agent_id
            total = self._kpis.earnings_per_cycle(agent_id=aid)
            ratio = self._kpis.work_rest_play_ratio(aid)
            rec_row = self._engine.conn.execute(
                "SELECT COUNT(*) FROM lifecycle_events WHERE agent_id=? AND event_type='ACTIVATED'",
                (aid,),
            ).fetchone()
            rows.append([
                aid, agent.name, agent.role_type.value,
                round(total, 2),
                round(total / n_cycles, 2),
                ratio["work"], ratio["rest"], ratio["play"],
                self._kpis.fatigue_index(aid),
                self._kpis.efficiency_score(aid, cycle=cycle),
                rec_row[0],
            ])
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def export_tick_history_csv(self, path: str, agent_id: Optional[str] = None) -> None:
        q = """
            SELECT s.current_tick, w.cycle, s.agent_id, s.status, s.energy, s.balance,
                   COALESCE(t.amount, 0)
            FROM agent_states s
            LEFT JOIN world_snapshots w ON w.tick = s.current_tick
            LEFT JOIN transactions t ON t.agent_id = s.agent_id AND t.tick = s.current_tick
        """
        params: list = []
        if agent_id:
            q += " WHERE s.agent_id=?"
            params.append(agent_id)
        q += " ORDER BY s.id"
        rows = self._engine.conn.execute(q, params).fetchall()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tick", "cycle", "agent_id", "status", "energy", "balance", "earnings_this_tick"])
            writer.writerows(rows)

    def export_population_report_json(self, path: str, cycle: Optional[int] = None) -> None:
        var = self._kpis.earnings_variance(cycle=cycle)
        report: Dict[str, Any] = {
            "generated_at": _utcnow(),
            "tick": self._engine.world.tick,
            "cycle": self._engine.world.cycle,
            "population_total_profit": self._kpis.population_total_profit(cycle=cycle),
            "earnings_variance": var,
            "agents": {},
        }
        for agent in self._engine.agents:
            aid = agent.agent_id
            report["agents"][aid] = {
                "name": agent.name,
                "role_type": agent.role_type.value,
                "earnings": self._kpis.earnings_per_cycle(agent_id=aid, cycle=cycle),
                "work_rest_play": self._kpis.work_rest_play_ratio(aid),
                "fatigue_index": self._kpis.fatigue_index(aid),
                "efficiency_score": self._kpis.efficiency_score(aid, cycle=cycle),
            }
        with open(path, "w") as f:
            json.dump(report, f, indent=2)

    def export_kpi_timeseries_csv(self, path: str, kpi_name: str) -> None:
        rows = self._engine.conn.execute(
            "SELECT tick, cycle, agent_id, kpi_value FROM kpi_snapshots WHERE kpi_name=? ORDER BY tick, agent_id",
            (kpi_name,),
        ).fetchall()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tick", "cycle", "agent_id", kpi_name])
            writer.writerows(rows)
