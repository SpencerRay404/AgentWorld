import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from agent_world.models.agent import Agent, AgentState, AgentStatus, RoleType
from agent_world.models.events import LifecycleEvent, LifecycleEventType


def save_agent(conn: sqlite3.Connection, agent: Agent) -> None:
    conn.execute(
        """INSERT INTO agents (agent_id, name, role_type, risk_tolerance, rest_preference, efficiency, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            agent.agent_id,
            agent.name,
            agent.role_type.value,
            agent.personality_weights["risk_tolerance"],
            agent.personality_weights["rest_preference"],
            agent.personality_weights["efficiency"],
            agent.created_at.isoformat(),
        ),
    )
    conn.commit()


def save_agent_state(conn: sqlite3.Connection, state: AgentState) -> None:
    conn.execute(
        """INSERT INTO agent_states
           (agent_id, status, energy, balance, current_tick, last_action, consecutive_work_ticks, recorded_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            state.agent_id,
            state.status.value,
            state.energy,
            state.balance,
            state.current_tick,
            state.last_action,
            state.consecutive_work_ticks,
            state.recorded_at.isoformat(),
        ),
    )
    conn.commit()


def load_agent(conn: sqlite3.Connection, agent_id: str) -> Optional[Agent]:
    row = conn.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
    if row is None:
        return None
    return Agent(
        agent_id=row["agent_id"],
        name=row["name"],
        role_type=RoleType(row["role_type"]),
        personality_weights={
            "risk_tolerance": row["risk_tolerance"],
            "rest_preference": row["rest_preference"],
            "efficiency": row["efficiency"],
        },
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def load_latest_state(conn: sqlite3.Connection, agent_id: str) -> Optional[AgentState]:
    row = conn.execute(
        "SELECT * FROM agent_states WHERE agent_id = ? ORDER BY id DESC LIMIT 1",
        (agent_id,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_state(row)


def load_state_history(conn: sqlite3.Connection, agent_id: str) -> List[AgentState]:
    rows = conn.execute(
        "SELECT * FROM agent_states WHERE agent_id = ? ORDER BY id ASC",
        (agent_id,),
    ).fetchall()
    return [_row_to_state(r) for r in rows]


def _row_to_state(row) -> AgentState:
    return AgentState(
        agent_id=row["agent_id"],
        status=AgentStatus(row["status"]),
        energy=row["energy"],
        balance=row["balance"],
        current_tick=row["current_tick"],
        last_action=row["last_action"],
        consecutive_work_ticks=row["consecutive_work_ticks"],
        recorded_at=datetime.fromisoformat(row["recorded_at"]),
    )


def emit_lifecycle_event(conn: sqlite3.Connection, event: LifecycleEvent) -> None:
    conn.execute(
        """INSERT INTO lifecycle_events (agent_id, event_type, tick, timestamp, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (
            event.agent_id,
            event.event_type.value,
            event.tick,
            event.timestamp.isoformat(),
            event.notes,
        ),
    )
    conn.commit()
