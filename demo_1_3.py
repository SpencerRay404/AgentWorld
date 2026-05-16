"""Subphase 1.3 demo — 30-tick orchestration run with tick-by-tick summary."""
from agent_world.config import SimConfig
from agent_world.db.schema import init_db
from agent_world.db.agent_repo import load_latest_state
from agent_world.orchestrator.engine import SimEngine

N_TICKS = 30
STATUS_SHORT = {"WORKING": "WORK", "RESTING": "REST", "PLAYING": "PLAY",
                "IDLE": "IDLE", "EXHAUSTED": "EXHS", "TERMINATED": "TERM"}


def main():
    config = SimConfig(population_size=8, ticks_per_cycle=10, event_log_path="logs/demo_1_3_events.jsonl")
    conn = init_db(":memory:")
    engine = SimEngine(conn, config)
    engine.initialize()

    names = {a.agent_id: a.name for a in engine.agents}
    agent_ids = [a.agent_id for a in engine.agents]

    # Header
    hdr = f"{'TICK':>4}  " + "  ".join(f"{names[aid]:<5}" for aid in agent_ids)
    print(f"\n{hdr}")
    print("─" * len(hdr))

    for _ in range(N_TICKS):
        engine.run_tick()
        tick = engine.world.tick
        row = f"{tick:>4}  "
        for aid in agent_ids:
            st = engine.states[aid].status.value
            row += f"{STATUS_SHORT[st]:<5}  "
        if engine.world.is_pay_period():
            row += f"← PAY (cycle {engine.world.cycle})"
        print(row)

    print("─" * len(hdr))
    print("\nFinal ledger totals:")
    totals = engine.ledger.get_population_totals()
    for agent in engine.agents:
        bal = totals.get(agent.agent_id, 0.0)
        state = engine.states[agent.agent_id]
        print(f"  {agent.name:<10} earned=${bal:>7.2f}  energy={state.energy:>5.1f}  balance={state.balance:>7.2f}")
    print()


if __name__ == "__main__":
    main()
