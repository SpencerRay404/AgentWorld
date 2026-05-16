from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict
import uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RoleType(str, Enum):
    WORKER = "WORKER"
    BALANCED = "BALANCED"
    EXPLORER = "EXPLORER"


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    RESTING = "RESTING"
    PLAYING = "PLAYING"
    EXHAUSTED = "EXHAUSTED"
    TERMINATED = "TERMINATED"


@dataclass
class Agent:
    name: str
    role_type: RoleType
    personality_weights: Dict[str, float]  # keys: risk_tolerance, rest_preference, efficiency
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=_utcnow)


@dataclass
class AgentState:
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    energy: float = 100.0
    balance: float = 0.0
    current_tick: int = 0
    last_action: str = "spawned"
    consecutive_work_ticks: int = 0
    recorded_at: datetime = field(default_factory=_utcnow)
