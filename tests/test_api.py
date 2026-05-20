"""API endpoint tests using FastAPI TestClient (synchronous).

These tests use the startup-initialized engine (in-memory from default SimConfig),
so they don't assume specific population sizes or config values — just structural correctness.
"""
import time
import pytest
from fastapi.testclient import TestClient

from agent_world.api.server import app


@pytest.fixture(scope="module")
def client():
    """Single TestClient for the whole module — startup runs once."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ── World ──────────────────────────────────────────────────────────────────────

def test_get_world_shape(client):
    r = client.get("/world")
    assert r.status_code == 200
    body = r.json()
    expected_keys = {"tick", "cycle", "world_time", "ticks_per_cycle",
                     "active_workers_count", "max_concurrent_workers",
                     "scarcity_mode", "scarcity_multiplier"}
    assert expected_keys.issubset(body.keys())
    assert body["tick"] == 0
    assert body["cycle"] == 0
    assert isinstance(body["ticks_per_cycle"], int)
    assert body["ticks_per_cycle"] > 0


# ── Agents ─────────────────────────────────────────────────────────────────────

def test_get_agents_returns_population(client):
    r = client.get("/agents")
    assert r.status_code == 200
    agents = r.json()
    assert len(agents) > 0
    required_keys = {"agent_id", "name", "role_type", "status", "energy", "balance"}
    for a in agents:
        assert required_keys.issubset(a.keys())
        assert a["energy"] >= 0.0
        assert a["balance"] >= 0.0


def test_get_agent_detail(client):
    # Get a real agent_id from the agents list
    agents = client.get("/agents").json()
    agent_id = agents[0]["agent_id"]

    r = client.get(f"/agents/{agent_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["agent_id"] == agent_id
    assert "personality_weights" in body
    assert isinstance(body["personality_weights"], dict)
    assert "state_history" in body
    assert "lifecycle_events" in body


def test_get_agent_not_found(client):
    r = client.get("/agents/nonexistent-id-that-cannot-exist")
    assert r.status_code == 404


def test_get_agent_transactions(client):
    agents = client.get("/agents").json()
    agent_id = agents[0]["agent_id"]
    r = client.get(f"/agents/{agent_id}/transactions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── KPIs ───────────────────────────────────────────────────────────────────────

def test_get_kpis_returns_per_agent_report(client):
    r = client.get("/kpis")
    assert r.status_code == 200
    body = r.json()
    # Should have one entry per agent (same count as /agents)
    agent_count = len(client.get("/agents").json())
    assert len(body) == agent_count
    first = next(iter(body.values()))
    assert "work_rest_play" in first
    assert "fatigue_index" in first
    assert "efficiency_score" in first
    assert "earnings" in first
    assert isinstance(first["work_rest_play"], dict)


def test_get_kpi_timeseries_shape(client):
    # Run a pay cycle to generate snapshots
    client.post("/control/start")
    time.sleep(0.3)
    client.post("/control/pause")

    r = client.get("/kpis/timeseries?kpi=balance&cycles=2")
    assert r.status_code == 200
    rows = r.json()
    assert isinstance(rows, list)
    for row in rows:
        assert {"tick", "cycle", "agent_id", "value"}.issubset(row.keys())


# ── Population ─────────────────────────────────────────────────────────────────

def test_get_population_shape(client):
    r = client.get("/population")
    assert r.status_code == 200
    body = r.json()
    assert "total_profit" in body
    assert "earnings_variance" in body
    assert "cycle" in body
    assert isinstance(body["total_profit"], (int, float))


# ── Alerts ─────────────────────────────────────────────────────────────────────

def test_get_alerts_returns_list(client):
    r = client.get("/alerts")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Control ────────────────────────────────────────────────────────────────────

def test_control_start_returns_valid_status(client):
    r = client.post("/control/start")
    assert r.status_code == 200
    assert r.json()["status"] in {"started", "already_running"}


def test_control_pause_and_resume(client):
    client.post("/control/start")
    r = client.post("/control/pause")
    assert r.status_code == 200
    assert r.json()["status"] == "paused"
    r = client.post("/control/resume")
    assert r.status_code == 200
    assert r.json()["status"] == "resumed"


def test_control_reset_clears_state(client):
    r = client.post("/control/reset")
    assert r.status_code == 200
    assert r.json()["status"] == "reset"
    # After reset, tick should be back to 0
    world = client.get("/world").json()
    assert world["tick"] == 0
    assert world["cycle"] == 0


# ── Export ─────────────────────────────────────────────────────────────────────

def test_export_agent_summary_csv(client):
    r = client.get("/export/csv?type=agent_summary")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    lines = r.text.splitlines()
    assert len(lines) >= 2  # header + at least 1 agent row
    assert "agent_id" in lines[0]


def test_export_tick_history_csv(client):
    r = client.get("/export/csv?type=tick_history")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
