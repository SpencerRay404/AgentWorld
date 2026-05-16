import json
import os
from dataclasses import dataclass


@dataclass
class SimConfig:
    # Population
    population_size: int = 8
    db_path: str = "agent_world.db"
    starting_energy: float = 100.0
    starting_balance: float = 0.0
    # World / tick
    ticks_per_cycle: int = 10
    max_concurrent_workers: int = 4
    # Energy / action costs
    energy_regen_per_rest_tick: float = 15.0
    energy_cost_per_work_tick: float = 10.0
    play_cost_per_tick: float = 5.0
    play_energy_regen: float = 5.0
    # Economy
    base_pay_per_tick: float = 5.0
    play_minimum_balance: float = 5.0
    exhaustion_threshold: float = 20.0
    auto_rest_threshold: float = 15.0
    # Scarcity
    scarcity_mode: str = "normal"
    scarcity_multiplier: float = 1.0
    # Simulation control
    simulation_speed_delay: float = 0.0
    event_log_path: str = "logs/events.jsonl"
    # Maintenance
    checkpoint_interval: int = 20
    # Analytics / alerts
    fatigue_alert_threshold: float = 0.75
    earnings_variance_alert: float = 2.0
    zero_earner_cycles: int = 2
    population_profit_drop: float = 0.3


def load_config(path: str = "config.json") -> SimConfig:
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        valid = {k: v for k, v in data.items() if k in SimConfig.__dataclass_fields__}
        return SimConfig(**valid)
    return SimConfig()
