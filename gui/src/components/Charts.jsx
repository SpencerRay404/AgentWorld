import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, AreaChart, Area, ResponsiveContainer } from 'recharts';
import { useSimData } from '../hooks/useSimData';

const COLORS = ['#00E5CC','#A78BFA','#FB923C','#F472B6','#7DD3FC','#86EFAC','#FDE68A','#F87171'];

export default function Charts({ agents }) {
  const { fetchTimeseries } = useSimData();
  const [tsData, setTsData] = useState([]);
  const [view, setView] = useState('agent');

  useEffect(() => {
    if (!agents.length) return;
    fetchTimeseries('balance', 10).then(rows => {
      const byTick = {};
      rows.forEach(r => {
        if (!byTick[r.tick]) byTick[r.tick] = { tick: r.tick };
        const name = agents.find(a => a.agent_id === r.agent_id)?.name || r.agent_id.slice(0,6);
        byTick[r.tick][name] = r.value;
      });
      setTsData(Object.values(byTick).sort((a,b) => a.tick - b.tick));
    });
  }, [agents]);

  const agentNames = agents.map(a => a.name);

  return (
    <div style={{ borderTop: '1px solid var(--border)', padding: '12px 20px', height: 200 }}>
      <div style={{ display: 'flex', gap: 12, marginBottom: 10, alignItems: 'center' }}>
        <span style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em' }}>BALANCE OVER TIME</span>
        {['agent', 'aggregate'].map(v => (
          <button key={v} onClick={() => setView(v)}
            style={{ fontSize: 10, color: view === v ? 'var(--teal)' : 'var(--dim)',
              borderBottom: view === v ? '1px solid var(--teal)' : '1px solid transparent', padding: '1px 4px' }}>
            {v}
          </button>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={140}>
        {view === 'agent' ? (
          <LineChart data={tsData}>
            <XAxis dataKey="tick" tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
            <YAxis tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
            <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 10 }} />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {agentNames.map((name, i) => (
              <Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]}
                dot={false} strokeWidth={1.5} />
            ))}
          </LineChart>
        ) : (
          <AreaChart data={tsData}>
            <XAxis dataKey="tick" tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
            <YAxis tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
            <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 10 }} />
            {agentNames.map((name, i) => (
              <Area key={name} type="monotone" dataKey={name} stackId="1"
                stroke={COLORS[i % COLORS.length]} fill={COLORS[i % COLORS.length] + '40'} />
            ))}
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
