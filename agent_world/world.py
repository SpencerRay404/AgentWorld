from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Set

from agent_world.config import SimConfig


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class World:
    def __init__(self, config: SimConfig):
        self.config = config
        self.tick: int = 0
        self.cycle: int = 0
        self.ticks_per_cycle: int = config.ticks_per_cycle
        self.max_concurrent_workers: int = config.max_concurrent_workers
        self.active_workers: Set[str] = set()
        self.event_bus: List[Dict[str, Any]] = []  # stub — replaced by EventBus in 1.3

    @property
    def world_time(self) -> float:
        return self.tick / self.ticks_per_cycle

    def advance_tick(self) -> None:
        self.tick += 1
        if self.is_pay_period():
            self.cycle += 1
            self._publish({"event_type": "PAY_PERIOD", "tick": self.tick, "cycle": self.cycle})
        self._publish({"event_type": "TICK", "tick": self.tick, "cycle": self.cycle})

    def is_pay_period(self) -> bool:
        return self.tick > 0 and self.tick % self.ticks_per_cycle == 0

    def get_world_state(self) -> Dict[str, Any]:
        return {
            "tick": self.tick,
            "cycle": self.cycle,
            "world_time": self.world_time,
            "active_workers_count": len(self.active_workers),
            "max_concurrent_workers": self.max_concurrent_workers,
            "scarcity_mode": self.config.scarcity_mode,
            "scarcity_multiplier": self.config.scarcity_multiplier,
        }

    def _publish(self, event: Dict[str, Any]) -> None:
        event["timestamp"] = _utcnow().isoformat()
        self.event_bus.append(event)


def get_payout_multiplier(world: World) -> float:
    return world.config.scarcity_multiplier
