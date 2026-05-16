import os
import tempfile
import pytest

from agent_world.config import SimConfig
from agent_world.db.schema import init_db
from agent_world.ledger import Ledger, TxType
from agent_world.world import World, get_payout_multiplier


@pytest.fixture
def config():
    return SimConfig(ticks_per_cycle=5)


@pytest.fixture
def db():
    conn = init_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def world(config):
    return World(config)


def test_world_initializes(world, config):
    assert world.tick == 0
    assert world.cycle == 0
    assert world.ticks_per_cycle == config.ticks_per_cycle
    assert world.max_concurrent_workers == config.max_concurrent_workers
    assert len(world.active_workers) == 0


def test_advance_tick_increments(world):
    world.advance_tick()
    assert world.tick == 1
    world.advance_tick()
    assert world.tick == 2


def test_pay_period_detected(world):
    for _ in range(4):
        world.advance_tick()
        assert not world.is_pay_period() or world.tick == 5  # not yet
    world.advance_tick()  # tick 5 = first pay period
    assert world.tick == 5
    assert world.cycle == 1


def test_pay_period_events_published(world):
    for _ in range(5):
        world.advance_tick()
    event_types = [e["event_type"] for e in world.event_bus]
    assert "PAY_PERIOD" in event_types
    assert event_types.count("TICK") == 5


def test_ledger_records_and_balance(db):
    ledger = Ledger(db)
    ledger.record("agent-1", 10.0, TxType.EARNING, tick=1, cycle=0)
    ledger.record("agent-1", -2.0, TxType.PENALTY, tick=2, cycle=0)
    assert ledger.get_balance("agent-1") == pytest.approx(8.0)


def test_ledger_cycle_earnings(db):
    ledger = Ledger(db)
    ledger.record("agent-1", 5.0, TxType.EARNING, tick=1, cycle=0)
    ledger.record("agent-1", 5.0, TxType.EARNING, tick=2, cycle=1)
    assert ledger.get_cycle_earnings("agent-1", 0) == pytest.approx(5.0)
    assert ledger.get_cycle_earnings("agent-1", 1) == pytest.approx(5.0)


def test_population_totals(db):
    ledger = Ledger(db)
    ledger.record("a1", 10.0, TxType.EARNING, tick=1, cycle=0)
    ledger.record("a2", 20.0, TxType.EARNING, tick=1, cycle=0)
    ledger.record("a1", 5.0, TxType.EARNING, tick=2, cycle=0)
    totals = ledger.get_population_totals()
    assert totals["a1"] == pytest.approx(15.0)
    assert totals["a2"] == pytest.approx(20.0)


def test_population_totals_cycle_filter(db):
    ledger = Ledger(db)
    ledger.record("a1", 10.0, TxType.EARNING, tick=1, cycle=0)
    ledger.record("a1", 20.0, TxType.EARNING, tick=5, cycle=1)
    totals_c0 = ledger.get_population_totals(cycle=0)
    assert totals_c0["a1"] == pytest.approx(10.0)
    assert "a1" not in ledger.get_population_totals(cycle=2)


def test_csv_export(db):
    ledger = Ledger(db)
    ledger.record("a1", 7.5, TxType.EARNING, tick=1, cycle=0, notes="test")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        ledger.export_csv(path)
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 2  # header + 1 row
        assert "tx_id" in lines[0]
        assert "7.5" in lines[1]
    finally:
        os.unlink(path)


def test_payout_multiplier(config):
    world = World(config)
    assert get_payout_multiplier(world) == pytest.approx(config.scarcity_multiplier)
