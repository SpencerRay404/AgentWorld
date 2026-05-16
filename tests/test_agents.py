import sqlite3
import pytest
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)

from agent_world.config import SimConfig
from agent_world.db.agent_repo import (
    emit_lifecycle_event,
    load_agent,
    load_latest_state,
    load_state_history,
    save_agent_state,
)
from agent_world.db.schema import init_db
from agent_world.models.agent import AgentStatus, RoleType
from agent_world.models.events import LifecycleEvent, LifecycleEventType
from agent_world.spawner import spawn_agent, spawn_population


@pytest.fixture
def db():
    conn = init_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def config():
    return SimConfig()


def test_spawn_single_agent(db, config):
    agent = spawn_agent(db, "TestBot", RoleType.WORKER, config)
    assert agent.name == "TestBot"
    assert agent.role_type == RoleType.WORKER
    assert len(agent.agent_id) == 36  # UUID format

    weights = agent.personality_weights
    assert set(weights.keys()) == {"risk_tolerance", "rest_preference", "efficiency"}
    assert abs(sum(weights.values()) - 1.0) < 0.001

    loaded = load_agent(db, agent.agent_id)
    assert loaded is not None
    assert loaded.agent_id == agent.agent_id
    assert loaded.name == agent.name


def test_spawn_population_persisted(db, config):
    agents = spawn_population(db, 5, config)
    assert len(agents) == 5
    for agent in agents:
        loaded = load_agent(db, agent.agent_id)
        assert loaded is not None


def test_state_history_grows(db, config):
    agent = spawn_agent(db, "GrowBot", RoleType.BALANCED, config)

    state = load_latest_state(db, agent.agent_id)
    assert state is not None

    from agent_world.models.agent import AgentState
    state2 = AgentState(
        agent_id=agent.agent_id,
        status=AgentStatus.WORKING,
        energy=90.0,
        balance=5.0,
        current_tick=1,
        last_action="started working",
        recorded_at=_utcnow(),
    )
    save_agent_state(db, state2)

    history = load_state_history(db, agent.agent_id)
    assert len(history) == 2
    assert history[0].status == AgentStatus.IDLE
    assert history[1].status == AgentStatus.WORKING


def test_lifecycle_events_logged(db, config):
    agent = spawn_agent(db, "EventBot", RoleType.EXPLORER, config)

    extra = LifecycleEvent(
        agent_id=agent.agent_id,
        event_type=LifecycleEventType.ACTIVATED,
        tick=1,
        timestamp=_utcnow(),
        notes="manually activated",
    )
    emit_lifecycle_event(db, extra)

    rows = db.execute(
        "SELECT * FROM lifecycle_events WHERE agent_id = ?", (agent.agent_id,)
    ).fetchall()
    assert len(rows) == 2
    types = [r["event_type"] for r in rows]
    assert "SPAWNED" in types
    assert "ACTIVATED" in types
