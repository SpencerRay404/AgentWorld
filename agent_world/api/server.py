from __future__ import annotations

import asyncio
import json
import threading
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from agent_world.api.schemas import (
    AgentDetail, AgentSummary, AlertItem, ControlResponse, KPIReport, WorldState,
)
from agent_world.config import load_config
from agent_world.db.schema import init_db
from agent_world.orchestrator.engine import SimEngine

app = FastAPI(title="Agent World API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine — initialized on startup
_engine: Optional[SimEngine] = None
_sim_thread: Optional[threading.Thread] = None
_ws_clients: List[WebSocket] = []
_recent_alerts: List[Dict[str, Any]] = []


def _get_engine() -> SimEngine:
    if _engine is None:
        raise RuntimeError("Engine not initialized — POST /control/start first")
    return _engine


def _ws_broadcast(event: Dict[str, Any]) -> None:
    """Called from the sim thread; schedules broadcast on the event loop."""
    pass  # filled in by lifespan


@app.on_event("startup")
async def _startup():
    global _engine
    config = load_config()
    conn = init_db(config.db_path)
    _engine = SimEngine(conn, config)
    _engine.initialize()

    # Hook EventBus to broadcast to all WS clients
    loop = asyncio.get_event_loop()

    def _broadcast(event):
        _recent_alerts.append(event) if event.get("event_type") == "ALERT" else None
        if len(_recent_alerts) > 50:
            _recent_alerts.pop(0)
        msg = json.dumps(event)
        for ws in list(_ws_clients):
            asyncio.run_coroutine_threadsafe(ws.send_text(msg), loop)

    _engine.event_bus.register(_broadcast)


# ── World ──────────────────────────────────────────────────────────────────────

@app.get("/world", response_model=WorldState)
def get_world():
    e = _get_engine()
    return e.world.get_world_state()


# ── Agents ─────────────────────────────────────────────────────────────────────

@app.get("/agents", response_model=List[AgentSummary])
def get_agents():
    e = _get_engine()
    result = []
    for agent in e.agents:
        s = e.states[agent.agent_id]
        result.append(AgentSummary(
            agent_id=agent.agent_id, name=agent.name, role_type=agent.role_type.value,
            status=s.status.value, energy=s.energy, balance=s.balance,
            last_action=s.last_action, consecutive_work_ticks=s.consecutive_work_ticks,
        ))
    return sorted(result, key=lambda x: x.balance, reverse=True)


@app.get("/agents/{agent_id}", response_model=AgentDetail)
def get_agent(agent_id: str):
    e = _get_engine()
    from agent_world.db.agent_repo import load_agent, load_state_history
    agent = load_agent(e.conn, agent_id)
    if not agent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent not found")
    s = e.states[agent_id]
    history_rows = load_state_history(e.conn, agent_id)[-50:]
    lifecycle = e.conn.execute(
        "SELECT event_type, tick, timestamp, notes FROM lifecycle_events WHERE agent_id=? ORDER BY tick",
        (agent_id,),
    ).fetchall()
    return AgentDetail(
        agent_id=agent.agent_id, name=agent.name, role_type=agent.role_type.value,
        status=s.status.value, energy=s.energy, balance=s.balance,
        last_action=s.last_action, consecutive_work_ticks=s.consecutive_work_ticks,
        personality_weights=agent.personality_weights,
        created_at=agent.created_at.isoformat(),
        state_history=[
            {"tick": h.current_tick, "status": h.status.value,
             "energy": h.energy, "balance": h.balance}
            for h in history_rows
        ],
        lifecycle_events=[
            {"event_type": r[0], "tick": r[1], "timestamp": r[2], "notes": r[3]}
            for r in lifecycle
        ],
    )


@app.get("/agents/{agent_id}/transactions")
def get_agent_transactions(agent_id: str):
    e = _get_engine()
    rows = e.conn.execute(
        "SELECT tx_id, amount, tx_type, tick, cycle, timestamp, notes FROM transactions WHERE agent_id=? ORDER BY tx_id",
        (agent_id,),
    ).fetchall()
    return [{"tx_id": r[0], "amount": r[1], "tx_type": r[2], "tick": r[3],
             "cycle": r[4], "timestamp": r[5], "notes": r[6]} for r in rows]


# ── KPIs ───────────────────────────────────────────────────────────────────────

@app.get("/kpis")
def get_kpis():
    e = _get_engine()
    return e.tracking.compute_full_report()


@app.get("/kpis/timeseries")
def get_kpi_timeseries(kpi: str = "balance", cycles: int = 5):
    e = _get_engine()
    min_cycle = max(0, e.world.cycle - cycles)
    rows = e.conn.execute(
        "SELECT tick, cycle, agent_id, kpi_value FROM kpi_snapshots WHERE kpi_name=? AND cycle>=? ORDER BY tick",
        (kpi, min_cycle),
    ).fetchall()
    return [{"tick": r[0], "cycle": r[1], "agent_id": r[2], "value": r[3]} for r in rows]


@app.get("/alerts")
def get_alerts():
    return _recent_alerts[-20:]


@app.get("/population")
def get_population():
    e = _get_engine()
    var = e.kpis.earnings_variance()
    totals = e.kpis.earnings_per_cycle()
    sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    agent_names = {a.agent_id: a.name for a in e.agents}
    return {
        "total_profit": e.kpis.population_total_profit(),
        "cycle": e.world.cycle,
        "earnings_variance": var,
        "top_earner": {"agent_id": sorted_totals[0][0], "name": agent_names.get(sorted_totals[0][0], ""),
                       "earnings": sorted_totals[0][1]} if sorted_totals else None,
        "bottom_earner": {"agent_id": sorted_totals[-1][0], "name": agent_names.get(sorted_totals[-1][0], ""),
                          "earnings": sorted_totals[-1][1]} if sorted_totals else None,
    }


# ── Control ────────────────────────────────────────────────────────────────────

@app.post("/control/start", response_model=ControlResponse)
def control_start():
    global _sim_thread
    e = _get_engine()
    if _sim_thread and _sim_thread.is_alive():
        return ControlResponse(status="already_running")
    e._running = False
    e._paused = False

    def _run():
        e._running = True
        while e._running:
            e.run_tick()
            import time
            if e.config.simulation_speed_delay > 0:
                time.sleep(e.config.simulation_speed_delay)
            else:
                time.sleep(0.05)  # yield to avoid pegging CPU

    _sim_thread = threading.Thread(target=_run, daemon=True)
    _sim_thread.start()
    return ControlResponse(status="started")


@app.post("/control/pause", response_model=ControlResponse)
def control_pause():
    _get_engine().pause()
    return ControlResponse(status="paused")


@app.post("/control/resume", response_model=ControlResponse)
def control_resume():
    _get_engine().resume()
    return ControlResponse(status="resumed")


@app.post("/control/reset", response_model=ControlResponse)
def control_reset():
    global _engine, _sim_thread
    if _sim_thread and _sim_thread.is_alive():
        _engine.stop()
        _sim_thread.join(timeout=2)
    config = load_config()
    conn = init_db(":memory:")
    _engine = SimEngine(conn, config)
    _engine.initialize()
    return ControlResponse(status="reset")


# ── Exports ────────────────────────────────────────────────────────────────────

@app.get("/export/csv")
def export_csv(type: str = "agent_summary"):
    e = _get_engine()
    from agent_world.analytics.exporter import Exporter
    exporter = Exporter(e)
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    if type == "agent_summary":
        exporter.export_agent_summary_csv(path)
    elif type == "tick_history":
        exporter.export_tick_history_csv(path)
    return FileResponse(path, media_type="text/csv", filename=f"{type}.csv")


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await websocket.accept()
    _ws_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        _ws_clients.remove(websocket)
