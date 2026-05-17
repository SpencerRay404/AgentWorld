import AgentCard from './AgentCard';

export default function PopulationGrid({ agents, onSelectAgent }) {
  return (
    <div style={{
      width: '40%', minWidth: 280, borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
    }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', fontSize: 10, color: 'var(--textDim)', letterSpacing: '0.12em' }}>
        POPULATION GRID · {agents.length} AGENTS
      </div>
      <div style={{ overflowY: 'auto', padding: 12, display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: 10, flex: 1 }}>
        {agents.map(agent => (
          <AgentCard key={agent.agent_id} agent={agent} onClick={onSelectAgent} />
        ))}
        {agents.length === 0 && (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', color: 'var(--dim)', padding: 40, fontSize: 12 }}>
            No agents — press START
          </div>
        )}
      </div>
    </div>
  );
}
