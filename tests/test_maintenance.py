import os
import tempfile
import pytest

from agent_world.config import SimConfig
from agent_world.db.schema import init_db
from agent_world.maintenance.checkpoint import CheckpointManager
from agent_world.maintenance.health import HealthMonitor
from agent_world.maintenance.recovery import RecoveryManager
from agent_world.models.agent import AgentStatus
from agent_world.orchestrator.engine import SimEngine


@pytest.fixture
def config():
    return SimConfig(
        population_size=4,
        ticks_per_cycle=5,
        max_concurrent_workers=2,
        event_log_path="logs/test_maintenance_events.jsonl",
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


def test_health_flags_stuck_agent(engine):
    # check_interval=5, stuck_threshold=4 → fires after 2 checks (streak reaches 5)
    monitor = HealthMonitor(check_interval=5, stuck_threshold=4)
    aid = engine.agents[0].agent_id
    all_events = []
    for tick in [5, 10]:
        engine.world.tick = tick
        for a in engine.agents:
            engine.states[a.agent_id].status = AgentStatus.RESTING
            engine.states[a.agent_id].current_tick = tick
        all_events.extend(monitor.check(engine))
    stuck = [e for e in all_events if e["check_type"] == "STUCK" and e["agent_id"] == aid]
    assert len(stuck) > 0


def test_recovery_unsticks_agent(engine):
    recovery = RecoveryManager()
    aid = engine.agents[0].agent_id
    engine.states[aid].status = AgentStatus.RESTING
    engine.world.tick = 10
    health_event = {
        "check_type": "STUCK", "agent_id": aid,
        "severity": "WARNING", "detail": "test", "tick": 10,
    }
    recovery.handle(health_event, engine)
    assert engine.states[aid].status == AgentStatus.IDLE


def test_overdrained_recovery(engine):
    recovery = RecoveryManager()
    aid = engine.agents[0].agent_id
    engine.states[aid].energy = 0.0
    engine.states[aid].status = AgentStatus.EXHAUSTED
    engine.world.tick = 5
    health_event = {
        "check_type": "OVERDRAINED", "agent_id": aid,
        "severity": "CRITICAL", "detail": "energy=0", "tick": 5,
    }
    recovery.handle(health_event, engine)
    assert engine.states[aid].status == AgentStatus.RESTING
    assert engine.states[aid].energy > 0


def test_agent_terminated_after_max_recoveries(engine):
    recovery = RecoveryManager(max_recoveries=2)
    aid = engine.agents[0].agent_id
    engine.world.tick = 1
    event = {"check_type": "STUCK", "agent_id": aid, "severity": "WARNING", "detail": "x", "tick": 1}
    initial_count = len(engine.agents)
    for i in range(4):
        recovery.handle(event, engine)
    assert engine.states[aid].status == AgentStatus.TERMINATED
    assert len(engine.agents) < initial_count


def test_checkpoint_save_and_restore(engine):
    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = CheckpointManager(interval=5, directory=tmpdir)
        engine.run(5)
        path = mgr.save_checkpoint(engine)
        assert os.path.exists(path)

        data = mgr.load_checkpoint(path)
        assert data["tick"] == 5
        assert len(data["agents"]) == len(engine.agents)

        # Mutate then restore
        original_tick = data["tick"]
        engine.world.tick = 999
        mgr.restore_from_checkpoint(path, engine)
        assert engine.world.tick == original_tick


def test_checkpoint_list_sorted(engine):
    with tempfile.TemporaryDirectory() as tmpdir:
        mgr = CheckpointManager(directory=tmpdir)
        for t in [20, 40, 10]:
            engine.world.tick = t
            mgr.save_checkpoint(engine)
        listed = mgr.list_checkpoints()
        ticks = [int(p.split("_tick_")[1].replace(".json", "")) for p in listed]
        assert ticks == sorted(ticks)
