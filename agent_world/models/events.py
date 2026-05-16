from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LifecycleEventType(str, Enum):
    SPAWNED = "SPAWNED"
    ACTIVATED = "ACTIVATED"
    EXHAUSTED = "EXHAUSTED"
    IDLE = "IDLE"
    TERMINATED = "TERMINATED"


@dataclass
class LifecycleEvent:
    agent_id: str
    event_type: LifecycleEventType
    tick: int
    timestamp: datetime
    notes: str = ""
