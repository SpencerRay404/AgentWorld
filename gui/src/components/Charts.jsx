import { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend,
  AreaChart, Area, BarChart, Bar, ResponsiveContainer, Cell,
} from 'recharts';
import { useSimData } from '../hooks/useSimData';

const COLORS = ['#00E5CC','#A78BFA','#FB923C','#F472B6','#7DD3FC','#86EFAC','#FDE68A','#F87171'];
const RATIO_COLORS = { work: '#00E5CC', rest: '#A78BFA', play: '#FB923C' };

export default function Charts({ agents, kpis }) {
  const { fetchTimeseries } = useSimData();
  const [tsData, setTsData] = useState([]);
  const [view, setView] = useState('balance');

  // Refresh balance timeseries whenever agents change (fetchAll fires every 1.5s)
  useEffect(() => {
    if (!agents.length) return;
    fetchTimeseries('balance', 10).then(rows => {
      const byTick = {};
      rows.forEach(r => {
        if (!byTick[r.tick]) byTick[r.tick] = { tick: r.tick };
        const name = agents.find(a => a.agent_id === r.agent_id)?.name || r.agent_id.slice(0, 6);
        byTick[r.tick][name] = r.value;
      });
      setTsData(Object.values(byTick).sort((a, b) => a.tick - b.tick));
    });
  }, [agents]);

  const agentNames = agents.map(a => a.name);

  // Build work/rest/play ratio bar data from kpis
  const ratioData = kpis
    ? Object.values(kpis).map(row => ({
        name: row.name,
        work: +(( row.work_rest_play?.work || 0) * 100).toFixed(1),
        rest: +(( row.work_rest_play?.rest || 0) * 100).toFixed(1),
        play: +(( row.work_rest_play?.play || 0) * 100).toFixed(1),
      }))
    : [];

  const VIEWS = ['balance', 'aggregate', 'ratio'];

  return (
    <div style={{ borderTop: '1px solid var(--border)', padding: '12px 20px', height: 200 }}>
      <div style={{ display: 'flex', gap: 12, marginBottom: 10, alignItems: 'center' }}>
        <span style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em' }}>
          {view === 'ratio' ? 'WORK / REST / PLAY RATIO' : 'BALANCE OVER TIME'}
        </span>
        {VIEWS.map(v => (
          <button key={v} onClick={() => setView(v)}
            style={{
              fontSize: 10,
              color: view === v ? 'var(--teal)' : 'var(--dim)',
              borderBottom: view === v ? '1px solid var(--teal)' : '1px solid transparent',
              padding: '1px 4px',
            }}>
            {v}
          </button>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={140}>
        {view === 'balance' ? (
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
        ) : view === 'aggregate' ? (
          <AreaChart data={tsData}>
            <XAxis dataKey="tick" tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
            <YAxis tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
            <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 10 }} />
            {agentNames.map((name, i) => (
              <Area key={name} type="monotone" dataKey={name} stackId="1"
                stroke={COLORS[i % COLORS.length]} fill={COLORS[i % COLORS.length] + '40'} />
            ))}
          </AreaChart>
        ) : (
          <BarChart data={ratioData} layout="vertical">
            <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 9, fill: 'var(--textDim)' }} unit="%" />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 9, fill: 'var(--textDim)' }} width={52} />
            <Tooltip
              contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 10 }}
              formatter={(v, n) => [`${v}%`, n]}
            />
            <Bar dataKey="work" stackId="a" fill={RATIO_COLORS.work} name="work" />
            <Bar dataKey="rest" stackId="a" fill={RATIO_COLORS.rest} name="rest" />
            <Bar dataKey="play" stackId="a" fill={RATIO_COLORS.play} name="play" radius={[0, 2, 2, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
