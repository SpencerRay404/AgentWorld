import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const STATUS_COLORS = {
  WORKING: '#00E5CC', RESTING: '#A78BFA', PLAYING: '#FB923C',
  IDLE: '#475569', EXHAUSTED: '#F87171',
};

export default function WorldState({ world, agents }) {
  if (!world) return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--dim)', fontSize: 12 }}>
      Waiting for engine...
    </div>
  );

  const statusCounts = agents.reduce((acc, a) => {
    acc[a.status] = (acc[a.status] || 0) + 1;
    return acc;
  }, {});
  const pieData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }));
  const progress = world.ticks_per_cycle
    ? (world.tick % (world.ticks_per_cycle || 10)) / (world.ticks_per_cycle || 10)
    : (world.tick % 10) / 10;

  return (
    <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>

        {/* Clock */}
        <div>
          <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 4 }}>WORLD CLOCK</div>
          <div style={{ fontSize: 28, color: 'var(--teal)', fontFamily: "'Syne', sans-serif", fontWeight: 800, letterSpacing: '-0.02em' }}>
            T{world.tick}
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>Cycle {world.cycle}</div>
        </div>

        {/* Cycle progress */}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 6 }}>CYCLE PROGRESS</div>
          <div style={{ height: 6, background: 'var(--border)', borderRadius: 3 }}>
            <div style={{ height: '100%', width: `${Math.min(progress * 100, 100)}%`, background: 'var(--teal)', borderRadius: 3, transition: 'width 0.3s' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--dim)', marginTop: 3 }}>
            <span>EARNING</span>
            <span style={{ color: 'var(--amber)' }}>{world.scarcity_mode?.toUpperCase()}</span>
            <span>PAY →</span>
          </div>
        </div>

        {/* Status donut */}
        <div style={{ width: 90, height: 80 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={20} outerRadius={38} dataKey="value" paddingAngle={2}>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#374151'} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Workers */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 4 }}>ACTIVE WORKERS</div>
          <div style={{ fontSize: 22, color: 'var(--bright)' }}>{world.active_workers_count}</div>
          <div style={{ fontSize: 10, color: 'var(--dim)' }}>/ {world.max_concurrent_workers} cap</div>
        </div>
      </div>
    </div>
  );
}
