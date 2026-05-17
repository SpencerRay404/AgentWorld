from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AgentSummary(BaseModel):
    agent_id: str
    name: str
    role_type: str
    status: str
    energy: float
    balance: float
    last_action: str
    consecutive_work_ticks: int


class AgentDetail(AgentSummary):
    personality_weights: Dict[str, float]
    created_at: str
    state_history: List[Dict[str, Any]] = []
    lifecycle_events: List[Dict[str, Any]] = []


class WorldState(BaseModel):
    tick: int
    cycle: int
    world_time: float
    active_workers_count: int
    max_concurrent_workers: int
    scarcity_mode: str
    scarcity_multiplier: float


class KPIReport(BaseModel):
    population_total_profit: float
    earnings_variance: Dict[str, float]
    per_agent: Dict[str, Any]


class AlertItem(BaseModel):
    alert_type: str
    severity: str
    agent_id: Optional[str]
    message: str
    tick: int
    timestamp: str


class ControlResponse(BaseModel):
    status: str
