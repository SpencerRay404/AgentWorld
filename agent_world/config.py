import json
import os
from dataclasses import dataclass, field


@dataclass
class SimConfig:
    population_size: int = 8
    db_path: str = "agent_world.db"
    starting_energy: float = 100.0
    starting_balance: float = 0.0


def load_config(path: str = "config.json") -> SimConfig:
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        return SimConfig(**{k: v for k, v in data.items() if k in SimConfig.__dataclass_fields__})
    return SimConfig()
