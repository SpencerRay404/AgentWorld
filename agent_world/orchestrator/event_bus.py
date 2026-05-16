from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventBus:
    def __init__(self, log_path: str = "logs/events.jsonl"):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._handlers: List[Callable] = []
        self._log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.register(self._log_handler)

    def publish(self, event: Dict[str, Any]) -> None:
        if "timestamp" not in event:
            event["timestamp"] = _utcnow()
        self._queue.put_nowait(event)

    def register(self, handler: Callable) -> None:
        self._handlers.append(handler)

    def dispatch_all(self) -> None:
        while not self._queue.empty():
            event = self._queue.get_nowait()
            for handler in self._handlers:
                handler(event)

    def _log_handler(self, event: Dict[str, Any]) -> None:
        with open(self._log_path, "a") as f:
            f.write(json.dumps(event) + "\n")
