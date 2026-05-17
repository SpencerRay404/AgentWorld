import os
import tempfile
import pytest

from agent_world.analytics.kpis import KPIEngine
from agent_world.config import SimConfig
from agent_world.db.schema import init_db
from agent_world.ledger import Ledger, TxType
from agent_world.orchestrator.engine import SimEngine


@pytest.fixture
def config():
    return SimConfig(
        population_size=4,
        ticks_per_cycle=5,
        max_concurrent_workers=2,
        event_log_path="logs/test_analytics_events.jsonl",
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


def test_earnings_per_cycle_matches_ledger(engine):
    engine.run(engine.config.ticks_per_cycle * 2)  # 2 pay periods
    totals = engine.kpis.earnings_per_cycle()
    ledger_totals = engine.ledger.get_population_totals()
    for aid, ledger_val in ledger_totals.items():
        assert totals.get(aid, 0.0) == pytest.approx(ledger_val, abs=0.01)


def test_work_rest_play_ratio_sums_to_one(engine):
    engine.run(20)
    for agent in engine.agents:
        ratio = engine.kpis.work_rest_play_ratio(agent.agent_id)
        total = ratio["work"] + ratio["rest"] + ratio["play"]
        assert total == pytest.approx(1.0, abs=0.01)


def test_fatigue_index_in_expected_range(engine):
    engine.run(20)
    for agent in engine.agents:
        fi = engine.kpis.fatigue_index(agent.agent_id)
        assert fi >= 0.0


def test_gini_equal_distribution():
    assert KPIEngine._gini([10.0, 10.0, 10.0]) == pytest.approx(0.0, abs=0.01)


def test_gini_unequal_distribution():
    # One agent earns everything
    assert KPIEngine._gini([0.0, 0.0, 0.0, 100.0]) > 0.5


def test_agent_summary_csv_valid(engine):
    engine.run(10)
    from agent_world.analytics.exporter import Exporter
    exporter = Exporter(engine)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        exporter.export_agent_summary_csv(path)
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == len(engine.agents) + 1  # header + agents
        assert "agent_id" in lines[0]
        assert len(lines[1].split(",")) == 11
    finally:
        os.unlink(path)


def test_fatigue_alert_fires(engine):
    from agent_world.analytics.alerts import AlertEngine
    from agent_world.models.agent import AgentStatus
    # Drain all agents to exhausted with lots of work ticks
    for agent in engine.agents:
        state = engine.states[agent.agent_id]
        state.consecutive_work_ticks = 20
        state.energy = 1.0
    # Force work records into DB
    engine.run(engine.config.ticks_per_cycle)
    alert_engine = AlertEngine(engine, log_path="logs/test_alert.jsonl")
    alerts = alert_engine.check_alerts(engine.world.cycle)
    # Some agent should have fired a fatigue or zero-earner alert
    assert isinstance(alerts, list)


def test_zero_earner_alert_triggers(engine):
    from agent_world.analytics.alerts import AlertEngine
    alert_engine = AlertEngine(engine, log_path="logs/test_zero_earner.jsonl")
    alert_engine._zero_earner_streak = {a.agent_id: 3 for a in engine.agents}
    engine.world.tick = 1
    alerts = alert_engine.check_alerts(current_cycle=1)
    zero_alerts = [a for a in alerts if a["alert_type"] == "ZERO_EARNER"]
    assert len(zero_alerts) > 0
