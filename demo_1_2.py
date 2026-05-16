"""Subphase 1.2 demo — World + Ledger."""
from agent_world.config import SimConfig
from agent_world.db.schema import init_db, save_world_snapshot
from agent_world.ledger import Ledger, TxType
from agent_world.spawner import spawn_population
from agent_world.world import World

N_TICKS = 15


def main():
    config = SimConfig(ticks_per_cycle=5)
    conn = init_db(":memory:")
    agents = spawn_population(conn, 5, config)
    world = World(config)
    ledger = Ledger(conn)

    import random
    for _ in range(N_TICKS):
        world.advance_tick()
        save_world_snapshot(conn, world.tick, world.cycle, len(world.active_workers))
        if world.is_pay_period():
            for agent in agents:
                pay = round(random.uniform(2.0, 10.0), 2)
                ledger.record(agent.agent_id, pay, TxType.EARNING, world.tick, world.cycle,
                              notes="cycle pay")

    print(f"\nWorld state after {N_TICKS} ticks:")
    state = world.get_world_state()
    for k, v in state.items():
        print(f"  {k:<28} {v}")

    print(f"\nPopulation earnings totals:")
    totals = ledger.get_population_totals()
    for agent in agents:
        earned = totals.get(agent.agent_id, 0.0)
        print(f"  {agent.name:<12} ${earned:>7.2f}")
    print(f"  {'TOTAL':<12} ${sum(totals.values()):>7.2f}")
    print()


if __name__ == "__main__":
    main()
