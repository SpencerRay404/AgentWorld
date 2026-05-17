const BASE = 'http://localhost:8000';

export default function ControlPanel({ world, onRefresh }) {
  const btn = async (action) => {
    await fetch(`${BASE}/control/${action}`, { method: 'POST' });
    onRefresh();
  };

  return (
    <div style={{
      borderTop: '1px solid var(--border)',
      padding: '10px 20px',
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      background: 'var(--surface)',
    }}>
      <span style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.1em', marginRight: 8 }}>CONTROLS</span>

      {[
        { label: 'START', action: 'start', color: 'var(--teal)' },
        { label: 'PAUSE', action: 'pause', color: 'var(--amber)' },
        { label: 'RESUME', action: 'resume', color: 'var(--violet)' },
        { label: 'RESET', action: 'reset', color: 'var(--red)' },
      ].map(({ label, action, color }) => (
        <button key={action} onClick={() => btn(action)} style={{
          padding: '6px 14px',
          border: `1px solid ${color}55`,
          borderRadius: 4,
          fontSize: 11,
          color,
          letterSpacing: '0.08em',
          background: `${color}11`,
          transition: 'background 0.1s',
        }}>
          {label}
        </button>
      ))}

      <div style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--dim)' }}>
        {world ? `T${world.tick} · C${world.cycle} · ${world.scarcity_mode}` : 'offline'}
      </div>
    </div>
  );
}
