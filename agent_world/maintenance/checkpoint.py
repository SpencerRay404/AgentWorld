from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from agent_world.orchestrator.engine import SimEngine


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class CheckpointManager:
    def __init__(self, interval: int = 20, directory: str = "checkpoints"):
        self.interval = interval
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def maybe_save(self, engine: "SimEngine") -> bool:
        if engine.world.tick % self.interval == 0 and engine.world.tick > 0:
            self.save_checkpoint(engine)
            return True
        return False

    def save_checkpoint(self, engine: "SimEngine") -> str:
        tick = engine.world.tick
        path = os.path.join(self.directory, f"checkpoint_tick_{tick}.json")
        data = {
            "tick": tick,
            "cycle": engine.world.cycle,
            "saved_at": _utcnow(),
            "config": engine.config.__dict__,
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "name": a.name,
                    "role_type": a.role_type.value,
                    "personality_weights": a.personality_weights,
                    "state": {
                        "status": engine.states[a.agent_id].status.value,
                        "energy": engine.states[a.agent_id].energy,
                        "balance": engine.states[a.agent_id].balance,
                        "consecutive_work_ticks": engine.states[a.agent_id].consecutive_work_ticks,
                    },
                }
                for a in engine.agents
            ],
            "ledger_totals": engine.ledger.get_population_totals(),
            "world_state": engine.world.get_world_state(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def load_checkpoint(self, path: str) -> Dict[str, Any]:
        with open(path) as f:
            data = json.load(f)
        required = {"tick", "cycle", "agents", "ledger_totals", "world_state"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Checkpoint missing keys: {missing}")
        return data

    def list_checkpoints(self) -> List[str]:
        files = [
            os.path.join(self.directory, f)
            for f in os.listdir(self.directory)
            if f.startswith("checkpoint_tick_") and f.endswith(".json")
        ]
        return sorted(files, key=lambda p: int(p.split("_tick_")[1].replace(".json", "")))

    def restore_from_checkpoint(self, path: str, engine: "SimEngine") -> None:
        data = self.load_checkpoint(path)
        engine.world.tick = data["tick"]
        engine.world.cycle = data["cycle"]
        for agent_entry in data["agents"]:
            aid = agent_entry["agent_id"]
            if aid in engine.states:
                s = engine.states[aid]
                from agent_world.models.agent import AgentStatus
                s.status = AgentStatus(agent_entry["state"]["status"])
                s.energy = agent_entry["state"]["energy"]
                s.balance = agent_entry["state"]["balance"]
                s.consecutive_work_ticks = agent_entry["state"]["consecutive_work_ticks"]
