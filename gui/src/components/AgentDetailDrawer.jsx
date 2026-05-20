import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useSimData } from '../hooks/useSimData';

const STATUS_COLOR = { WORKING:'var(--teal)', RESTING:'var(--violet)', PLAYING:'var(--amber)',
  IDLE:'var(--muted)', EXHAUSTED:'var(--red)', TERMINATED:'#374151' };

export default function AgentDetailDrawer({ agentId, onClose }) {
  const { fetchAgent, fetchTransactions } = useSimData();
  const [detail, setDetail] = useState(null);
  const [txns, setTxns] = useState([]);

  useEffect(() => {
    if (!agentId) return;
    const load = () => {
      fetchAgent(agentId).then(setDetail);
      fetchTransactions(agentId).then(setTxns);
    };
    load();
    const id = setInterval(load, 2000);
    return () => clearInterval(id);
  }, [agentId]);

  if (!agentId) return null;

  const weightData = detail ? Object.entries(detail.personality_weights).map(([k,v]) => ({ name: k.replace('_', ' '), value: v })) : [];
  const energyHistory = (detail?.state_history || []).map(h => ({ tick: h.tick, energy: h.energy }));

  return (
    <div style={{
      position: 'fixed', top: 0, right: 0, bottom: 0, width: 380,
      background: 'var(--surface)', borderLeft: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', zIndex: 100, overflowY: 'auto',
    }}>
      <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 16, color: 'var(--bright)', fontWeight: 700 }}>{detail?.name || '…'}</div>
          <div style={{ fontSize: 10, color: 'var(--textDim)', marginTop: 2 }}>{detail?.role_type} · {detail?.agent_id?.slice(0,16)}…</div>
        </div>
        <button onClick={onClose} style={{ fontSize: 18, color: 'var(--muted)', padding: '4px 8px' }}>×</button>
      </div>

      {detail && (
        <>
          {/* Status summary */}
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 20 }}>
            <Stat label="STATUS" value={detail.status} color={STATUS_COLOR[detail.status]} />
            <Stat label="ENERGY" value={`${detail.energy.toFixed(1)}`} />
            <Stat label="BALANCE" value={`$${detail.balance.toFixed(2)}`} color="var(--teal)" />
          </div>

          {/* Personality weights bar chart */}
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)' }}>
            <Label>PERSONALITY WEIGHTS</Label>
            <ResponsiveContainer width="100%" height={70}>
              <BarChart data={weightData} layout="vertical">
                <XAxis type="number" domain={[0,1]} tick={{ fontSize: 9, fill: 'var(--textDim)' }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 9, fill: 'var(--textDim)' }} width={80} />
                <Bar dataKey="value" fill="var(--violet)" radius={2} />
                <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 10 }} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Energy sparkline */}
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)' }}>
            <Label>ENERGY (last 50 ticks)</Label>
            <ResponsiveContainer width="100%" height={60}>
              <LineChart data={energyHistory}>
                <Line type="monotone" dataKey="energy" stroke="var(--teal)" dot={false} strokeWidth={1.5} />
                <XAxis dataKey="tick" hide />
                <YAxis domain={[0,100]} hide />
                <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', fontSize: 10 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Lifecycle events */}
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)' }}>
            <Label>LIFECYCLE EVENTS</Label>
            {detail.lifecycle_events.slice(-6).map((e, i) => (
              <div key={i} style={{ fontSize: 11, color: 'var(--textDim)', marginBottom: 4 }}>
                <span style={{ color: 'var(--teal)' }}>T{e.tick}</span> {e.event_type} {e.notes && `— ${e.notes}`}
              </div>
            ))}
          </div>

          {/* Transactions */}
          <div style={{ padding: '14px 18px' }}>
            <Label>TRANSACTIONS ({txns.length})</Label>
            <div style={{ maxHeight: 200, overflowY: 'auto' }}>
              {txns.slice(-20).reverse().map(t => (
                <div key={t.tx_id} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 11 }}>
                  <span style={{ color: 'var(--textDim)' }}>T{t.tick} {t.tx_type}</span>
                  <span style={{ color: t.amount >= 0 ? 'var(--teal)' : 'var(--red)' }}>${t.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, value, color }) {
  return (
    <div>
      <div style={{ fontSize: 9, color: 'var(--textDim)', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 13, color: color || 'var(--bright)' }}>{value}</div>
    </div>
  );
}

function Label({ children }) {
  return <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 8 }}>{children}</div>;
}
