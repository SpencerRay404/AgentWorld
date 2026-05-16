import pytest
from unittest.mock import MagicMock

from agent_world.config import SimConfig
from agent_world.db.schema import init_db
from agent_world.ledger import Ledger
from agent_world.models.agent import Agent, AgentState, AgentStatus, RoleType
from agent_world.orchestrator.engine import SimEngine
from agent_world.orchestrator.event_bus import EventBus
from agent_world.orchestrator.scheduler import Scheduler
from agent_world.world import World


@pytest.fixture
def config():
    return SimConfig(
        population_size=4,
        ticks_per_cycle=5,
        max_concurrent_workers=2,
        auto_rest_threshold=15.0,
        exhaustion_threshold=20.0,
        play_minimum_balance=5.0,
        event_log_path="logs/test_events.jsonl",
    )


@pytest.fixture
def db():
    conn = init_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def engine(db, config):
    e = SimEngine(db, config)
    e.initialize()
    return e


def _make_agent(name="Bot", role=RoleType.BALANCED, weights=None):
    if weights is None:
        weights = {"risk_tolerance": 0.33, "rest_preference": 0.34, "efficiency": 0.33}
    return Agent(name=name, role_type=role, personality_weights=weights)


def _make_state(agent_id, energy=100.0, balance=0.0, status=AgentStatus.IDLE):
    return AgentState(agent_id=agent_id, energy=energy, balance=balance, status=status)


def test_low_energy_forces_rest(config):
    scheduler = Scheduler(config)
    world = World(config)
    agent = _make_agent()
    state = _make_state(agent.agent_id, energy=5.0)
    assignments = scheduler.assign_actions([agent], {agent.agent_id: state}, world)
    assert assignments[0][1] in (AgentStatus.RESTING, AgentStatus.EXHAUSTED)


def test_capacity_cap_enforced(config):
    scheduler = Scheduler(config)
    world = World(config)
    agents = [_make_agent(f"Bot{i}", weights={"risk_tolerance": 0.0, "rest_preference": 0.0, "efficiency": 1.0}) for i in range(4)]
    states = {a.agent_id: _make_state(a.agent_id, balance=100.0) for a in agents}
    assignments = scheduler.assign_actions(agents, states, world)
    working = [s for _, s in assignments if s == AgentStatus.WORKING]
    assert len(working) <= config.max_concurrent_workers


def test_20_tick_engine_run(engine):
    engine.run(20)
    # All agents should have state history > 1
    from agent_world.db.agent_repo import load_state_history
    for agent in engine.agents:
        history = load_state_history(engine.conn, agent.agent_id)
        assert len(history) > 1


def test_pay_period_triggers_earnings(engine):
    engine.run(engine.config.ticks_per_cycle)  # exactly 1 pay period
    totals = engine.ledger.get_population_totals(cycle=1)
    # At least some agents should have earned something
    assert sum(totals.values()) > 0


def test_event_bus_delivers(config):
    received = []
    bus = EventBus(log_path="logs/test_bus.jsonl")
    bus.register(lambda e: received.append(e))
    bus.publish({"event_type": "TEST", "agent_id": None, "tick": 1, "payload": {}})
    bus.dispatch_all()
    test_events = [e for e in received if e["event_type"] == "TEST"]
    assert len(test_events) == 1


def test_anomaly_detection(config):
    """Agent exhausted for 4+ consecutive ticks should be flagged."""
    scheduler = Scheduler(config)
    world = World(config)
    agent = _make_agent(weights={"risk_tolerance": 0.0, "rest_preference": 0.0, "efficiency": 1.0})
    # Drain energy fully
    state = _make_state(agent.agent_id, energy=0.0, balance=0.0)
    for _ in range(4):
        scheduler.assign_actions([agent], {agent.agent_id: state}, world)
        world.advance_tick()
    assert agent.agent_id in scheduler.anomalies
