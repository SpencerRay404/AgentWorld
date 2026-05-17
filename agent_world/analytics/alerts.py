from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agent_world.analytics.kpis import KPIEngine

if TYPE_CHECKING:
    from agent_world.orchestrator.engine import SimEngine


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class AlertEngine:
    def __init__(self, engine: "SimEngine", log_path: str = "logs/alerts.jsonl"):
        self._engine = engine
        self._kpis = KPIEngine(engine.conn, engine.config)
        self._log_path = log_path
        self._zero_earner_streak: Dict[str, int] = {}
        self._prev_population_profit: Optional[float] = None
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def check_alerts(self, current_cycle: int) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        cfg = self._engine.config
        tick = self._engine.world.tick

        for agent in self._engine.agents:
            aid = agent.agent_id

            # Fatigue alert
            fi = self._kpis.fatigue_index(aid)
            if fi > cfg.fatigue_alert_threshold:
                alerts.append(self._alert(
                    "FATIGUE_HIGH", "WARNING", aid, tick,
                    f"fatigue_index={fi:.3f} > threshold={cfg.fatigue_alert_threshold}",
                ))

            # Zero earner streak
            cycle_earn = self._kpis.earnings_per_cycle(agent_id=aid, cycle=current_cycle)
            if cycle_earn == 0:
                self._zero_earner_streak[aid] = self._zero_earner_streak.get(aid, 0) + 1
            else:
                self._zero_earner_streak[aid] = 0
            if self._zero_earner_streak.get(aid, 0) >= cfg.zero_earner_cycles:
                alerts.append(self._alert(
                    "ZERO_EARNER", "WARNING", aid, tick,
                    f"earned $0 for {self._zero_earner_streak[aid]} consecutive cycles",
                ))

        # Earnings variance
        variance = self._kpis.earnings_variance(cycle=current_cycle)
        if variance["mean"] > 0:
            ratio = variance["std_dev"] / variance["mean"]
            if ratio > cfg.earnings_variance_alert:
                alerts.append(self._alert(
                    "HIGH_EARNINGS_VARIANCE", "INFO", None, tick,
                    f"std_dev/mean={ratio:.2f} > threshold={cfg.earnings_variance_alert}",
                ))

        # Population profit drop
        pop_profit = self._kpis.population_total_profit(cycle=current_cycle)
        if self._prev_population_profit is not None and self._prev_population_profit > 0:
            drop = (self._prev_population_profit - pop_profit) / self._prev_population_profit
            if drop > cfg.population_profit_drop:
                alerts.append(self._alert(
                    "POPULATION_PROFIT_DROP", "CRITICAL", None, tick,
                    f"profit dropped {drop*100:.1f}% cycle-over-cycle",
                ))
        self._prev_population_profit = pop_profit

        for alert in alerts:
            self._engine.event_bus.publish({"event_type": "ALERT", "agent_id": alert["agent_id"],
                                            "tick": tick, "payload": alert})
            with open(self._log_path, "a") as f:
                f.write(json.dumps(alert) + "\n")

        return alerts

    def _alert(self, alert_type: str, severity: str,
               agent_id: Optional[str], tick: int, message: str) -> Dict[str, Any]:
        return {
            "alert_type": alert_type,
            "severity": severity,
            "agent_id": agent_id,
            "message": message,
            "tick": tick,
            "timestamp": _utcnow(),
        }
