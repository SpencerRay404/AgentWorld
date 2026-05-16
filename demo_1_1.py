"""Subphase 1.1 demo — spawn population and print summary."""
from agent_world.config import load_config
from agent_world.db.schema import init_db
from agent_world.db.agent_repo import load_latest_state
from agent_world.spawner import spawn_population


def main():
    config = load_config()
    conn = init_db(":memory:")
    agents = spawn_population(conn, config.population_size, config)

    print(f"\n{'─'*74}")
    print(f"  {'NAME':<12} {'ROLE':<10} {'STATUS':<12} {'ENERGY':>6} {'BALANCE':>8}  WEIGHTS")
    print(f"{'─'*74}")
    for agent in agents:
        state = load_latest_state(conn, agent.agent_id)
        w = agent.personality_weights
        print(
            f"  {agent.name:<12} {agent.role_type.value:<10} {state.status.value:<12}"
            f" {state.energy:>6.1f} {state.balance:>8.2f}"
            f"  risk={w['risk_tolerance']:.2f} rest={w['rest_preference']:.2f} eff={w['efficiency']:.2f}"
        )
    print(f"{'─'*74}")
    print(f"  {len(agents)} agents spawned · all persisted to SQLite · lifecycle events logged\n")


if __name__ == "__main__":
    main()
