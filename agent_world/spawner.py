import random
import sqlite3
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
from typing import Dict, List, Optional

from agent_world.config import SimConfig
from agent_world.db.agent_repo import emit_lifecycle_event, save_agent, save_agent_state
from agent_world.models.agent import Agent, AgentState, AgentStatus, RoleType
from agent_world.models.events import LifecycleEvent, LifecycleEventType

_NAMES = [
    "Ada", "Blaze", "Coda", "Drift", "Echo", "Flux", "Grit", "Haze",
    "Iris", "Jolt", "Kira", "Loom", "Muse", "Nova", "Oryn", "Pike",
    "Quill", "Rift", "Sage", "Thorn", "Ulla", "Vex", "Wren", "Xen",
    "Yore", "Zap",
]


def _random_weights() -> Dict[str, float]:
    w = [random.random() for _ in range(3)]
    total = sum(w)
    keys = ["risk_tolerance", "rest_preference", "efficiency"]
    return {k: round(v / total, 4) for k, v in zip(keys, w)}


def spawn_agent(
    conn: sqlite3.Connection,
    name: str,
    role_type: RoleType,
    config: SimConfig,
    personality_weights: Optional[Dict[str, float]] = None,
) -> Agent:
    weights = personality_weights if personality_weights is not None else _random_weights()
    agent = Agent(name=name, role_type=role_type, personality_weights=weights)
    state = AgentState(
        agent_id=agent.agent_id,
        energy=config.starting_energy,
        balance=config.starting_balance,
    )
    save_agent(conn, agent)
    save_agent_state(conn, state)
    emit_lifecycle_event(
        conn,
        LifecycleEvent(
            agent_id=agent.agent_id,
            event_type=LifecycleEventType.SPAWNED,
            tick=0,
            timestamp=_utcnow(),
        ),
    )
    return agent


def spawn_population(
    conn: sqlite3.Connection,
    n: int,
    config: SimConfig,
) -> List[Agent]:
    roles = list(RoleType)
    names = random.sample(_NAMES, min(n, len(_NAMES)))
    # pad with numbered names if n > name pool
    while len(names) < n:
        names.append(f"Agent-{len(names)+1}")
    agents = []
    for i in range(n):
        role = roles[i % len(roles)]
        agents.append(spawn_agent(conn, names[i], role, config))
    return agents
