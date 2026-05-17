from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


_MAX_BYTES = 10 * 1024 * 1024  # 10 MB


def _write(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and os.path.getsize(path) >= _MAX_BYTES:
        os.rename(path, path + ".1")
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")


class SimLogger:
    def __init__(
        self,
        event_log: str = "logs/events.jsonl",
        health_log: str = "logs/health.jsonl",
        audit_log: str = "logs/audit.jsonl",
    ):
        self.event_log = event_log
        self.health_log = health_log
        self.audit_log = audit_log

    def log_event(self, event: Dict[str, Any]) -> None:
        _write(self.event_log, event)

    def log_health(self, event: Dict[str, Any]) -> None:
        _write(self.health_log, event)

    def log_audit(self, agent_id: str, old_state: Any, new_state: Any, tick: int) -> None:
        _write(
            self.audit_log,
            {
                "agent_id": agent_id,
                "old_status": old_state.status.value,
                "new_status": new_state.status.value,
                "energy_delta": round(new_state.energy - old_state.energy, 4),
                "balance_delta": round(new_state.balance - old_state.balance, 4),
                "tick": tick,
                "timestamp": _utcnow(),
            },
        )
