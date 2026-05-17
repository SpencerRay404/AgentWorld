from __future__ import annotations

import math
import sqlite3
from typing import Any, Dict, List, Optional


class KPIEngine:
    def __init__(self, conn: sqlite3.Connection, config: Any):
        self._conn = conn
        self._config = config

    def earnings_per_cycle(
        self, agent_id: Optional[str] = None, cycle: Optional[int] = None
    ) -> Any:
        if agent_id:
            q = "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE agent_id=?"
            params: list = [agent_id]
            if cycle is not None:
                q += " AND cycle=?"
                params.append(cycle)
            return float(self._conn.execute(q, params).fetchone()[0])
        else:
            if cycle is not None:
                rows = self._conn.execute(
                    "SELECT agent_id, COALESCE(SUM(amount),0) FROM transactions WHERE cycle=? GROUP BY agent_id",
                    (cycle,),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT agent_id, COALESCE(SUM(amount),0) FROM transactions GROUP BY agent_id"
                ).fetchall()
            return {r[0]: float(r[1]) for r in rows}

    def work_rest_play_ratio(
        self, agent_id: str, tick_start: int = 0, tick_end: Optional[int] = None
    ) -> Dict[str, float]:
        q = "SELECT status, COUNT(*) FROM agent_states WHERE agent_id=? AND current_tick>=?"
        params: list = [agent_id, tick_start]
        if tick_end is not None:
            q += " AND current_tick<=?"
            params.append(tick_end)
        q += " GROUP BY status"
        rows = self._conn.execute(q, params).fetchall()
        counts = {r[0]: r[1] for r in rows}
        active = (counts.get("WORKING", 0) + counts.get("RESTING", 0) + counts.get("PLAYING", 0))
        total = max(active, 1)
        return {
            "work": round(counts.get("WORKING", 0) / total, 4),
            "rest": round(counts.get("RESTING", 0) / total, 4),
            "play": round(counts.get("PLAYING", 0) / total, 4),
        }

    def population_total_profit(self, cycle: Optional[int] = None) -> float:
        if cycle is not None:
            row = self._conn.execute(
                "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE cycle=?", (cycle,)
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT COALESCE(SUM(amount),0) FROM transactions"
            ).fetchone()
        return float(row[0])

    def fatigue_index(
        self, agent_id: str, tick_start: int = 0, tick_end: Optional[int] = None
    ) -> float:
        q = "SELECT AVG(consecutive_work_ticks), AVG(energy) FROM agent_states WHERE agent_id=? AND current_tick>=?"
        params: list = [agent_id, tick_start]
        if tick_end is not None:
            q += " AND current_tick<=?"
            params.append(tick_end)
        row = self._conn.execute(q, params).fetchone()
        avg_consec = row[0] or 0.0
        avg_energy = row[1] or 100.0
        tpc = self._config.ticks_per_cycle or 1
        return round((avg_consec / tpc) * (1 - avg_energy / 100), 4)

    def earnings_variance(self, cycle: Optional[int] = None) -> Dict[str, float]:
        totals = list(self.earnings_per_cycle(cycle=cycle).values())
        if not totals:
            return {"mean": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0, "gini": 0.0}
        mean = sum(totals) / len(totals)
        variance = sum((x - mean) ** 2 for x in totals) / len(totals)
        std_dev = math.sqrt(variance)
        gini = self._gini(totals)
        return {
            "mean": round(mean, 4),
            "std_dev": round(std_dev, 4),
            "min": round(min(totals), 4),
            "max": round(max(totals), 4),
            "gini": round(gini, 4),
        }

    def recovery_rate(self, agent_id: Optional[str] = None) -> Any:
        # Count ACTIVATED lifecycle events (used as recovery markers) per 10 ticks
        if agent_id:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM lifecycle_events WHERE agent_id=? AND event_type='ACTIVATED'",
                (agent_id,),
            ).fetchone()
            total_ticks = self._conn.execute(
                "SELECT MAX(current_tick) FROM agent_states WHERE agent_id=?", (agent_id,)
            ).fetchone()[0] or 1
            return round(row[0] / total_ticks * 10, 4)
        else:
            agents = [r[0] for r in self._conn.execute("SELECT DISTINCT agent_id FROM agents").fetchall()]
            return {aid: self.recovery_rate(aid) for aid in agents}

    def efficiency_score(self, agent_id: str, cycle: Optional[int] = None) -> float:
        earned = self.earnings_per_cycle(agent_id=agent_id, cycle=cycle)
        if cycle is not None:
            tick_start = (cycle - 1) * self._config.ticks_per_cycle + 1
            tick_end = cycle * self._config.ticks_per_cycle
            q = ("SELECT COUNT(*) FROM agent_states WHERE agent_id=? AND status='WORKING'"
                 " AND current_tick>=? AND current_tick<=?")
            row = self._conn.execute(q, (agent_id, tick_start, tick_end)).fetchone()
        else:
            q = "SELECT COUNT(*) FROM agent_states WHERE agent_id=? AND status='WORKING'"
            row = self._conn.execute(q, (agent_id,)).fetchone()
        ticks_worked = row[0] or 0
        energy_spent = ticks_worked * self._config.energy_cost_per_work_tick
        if energy_spent == 0:
            return 0.0
        return round(earned / energy_spent, 4)

    @staticmethod
    def _gini(values: List[float]) -> float:
        if not values or sum(values) == 0:
            return 0.0
        n = len(values)
        s = sorted(values)
        cumsum = 0.0
        gini_num = 0.0
        for i, v in enumerate(s):
            cumsum += v
            gini_num += (2 * (i + 1) - n - 1) * v
        total = sum(s) * n
        return abs(gini_num / total) if total else 0.0
