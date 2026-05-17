const STATUS_COLOR = {
  WORKING: 'var(--teal)',
  RESTING: 'var(--violet)',
  PLAYING: 'var(--amber)',
  IDLE: 'var(--muted)',
  EXHAUSTED: 'var(--red)',
  TERMINATED: '#374151',
};

const ROLE_BADGE = { WORKER: 'WRK', BALANCED: 'BAL', EXPLORER: 'EXP' };

export default function AgentCard({ agent, onClick }) {
  const color = STATUS_COLOR[agent.status] || 'var(--muted)';
  const isWorking = agent.status === 'WORKING';

  return (
    <div
      onClick={() => onClick(agent.agent_id)}
      style={{
        border: `1px solid ${color}33`,
        borderRadius: 6,
        padding: '12px 14px',
        background: 'var(--surface)',
        cursor: 'pointer',
        transition: 'border-color 0.15s',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {isWorking && (
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: 2,
          background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
          animation: 'pulse 1.5s ease-in-out infinite',
        }} />
      )}
      <style>{`@keyframes pulse { 0%,100%{opacity:0.3} 50%{opacity:1} }`}</style>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ color: 'var(--bright)', fontSize: 13, fontWeight: 500 }}>{agent.name}</span>
        <span style={{ fontSize: 9, color: color, border: `1px solid ${color}55`, padding: '1px 6px', borderRadius: 3 }}>
          {ROLE_BADGE[agent.role_type] || agent.role_type}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <div style={{ width: 6, height: 6, borderRadius: '50%', background: color, flexShrink: 0 }} />
        <span style={{ color, fontSize: 11 }}>{agent.status}</span>
      </div>

      <div style={{ marginBottom: 4 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--textDim)', marginBottom: 3 }}>
          <span>ENERGY</span><span>{agent.energy.toFixed(1)}</span>
        </div>
        <div style={{ height: 3, background: 'var(--border)', borderRadius: 2 }}>
          <div style={{ height: '100%', width: `${agent.energy}%`, background: color, borderRadius: 2, transition: 'width 0.3s' }} />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginTop: 6 }}>
        <span style={{ color: 'var(--textDim)' }}>BALANCE</span>
        <span style={{ color: 'var(--bright)' }}>${agent.balance.toFixed(2)}</span>
      </div>
    </div>
  );
}
