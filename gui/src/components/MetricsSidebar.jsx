const SEV_COLOR = { INFO: 'var(--teal)', WARNING: 'var(--amber)', CRITICAL: 'var(--red)' };

export default function MetricsSidebar({ population, alerts, events }) {
  const recentAlerts = (alerts || []).slice(-5).reverse();
  const recentEvents = (events || []).slice(-10).reverse();

  return (
    <div style={{
      width: 260, minWidth: 220, borderLeft: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', overflowY: 'auto',
    }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', fontSize: 10, color: 'var(--textDim)', letterSpacing: '0.12em' }}>
        METRICS
      </div>

      {population && (
        <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)' }}>
          <Metric label="TOTAL PROFIT" value={`$${(population.total_profit || 0).toFixed(2)}`} color="var(--teal)" />
          <Metric label="GINI" value={(population.earnings_variance?.gini || 0).toFixed(3)} />
          <Metric label="MEAN EARN" value={`$${(population.earnings_variance?.mean || 0).toFixed(2)}`} />
          {population.top_earner && (
            <Metric label="TOP EARNER" value={`${population.top_earner.name} $${population.top_earner.earnings.toFixed(0)}`} color="var(--teal)" />
          )}
          {population.bottom_earner && (
            <Metric label="LOW EARNER" value={`${population.bottom_earner.name} $${population.bottom_earner.earnings.toFixed(0)}`} color="var(--amber)" />
          )}
        </div>
      )}

      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 8 }}>
          ALERTS ({recentAlerts.length})
        </div>
        {recentAlerts.length === 0 && <div style={{ fontSize: 11, color: 'var(--dim)' }}>No alerts</div>}
        {recentAlerts.map((a, i) => (
          <div key={i} style={{ marginBottom: 6, padding: '6px 8px', border: `1px solid ${SEV_COLOR[a.severity] || 'var(--border)'}33`, borderRadius: 4, background: 'var(--bg)' }}>
            <div style={{ fontSize: 10, color: SEV_COLOR[a.severity], marginBottom: 2 }}>{a.alert_type}</div>
            <div style={{ fontSize: 11, color: 'var(--textDim)', lineHeight: 1.4 }}>{a.message?.slice(0, 60)}</div>
          </div>
        ))}
      </div>

      <div style={{ padding: '12px 16px', flex: 1, overflow: 'hidden' }}>
        <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 8 }}>LIVE EVENTS</div>
        <div style={{ overflowY: 'auto', maxHeight: 300 }}>
          {recentEvents.map((e, i) => (
            <div key={i} style={{ marginBottom: 4, fontSize: 10, color: 'var(--dim)', borderLeft: '2px solid var(--border)', paddingLeft: 8 }}>
              <span style={{ color: 'var(--teal)' }}>{e.event_type}</span>
              {e.agent_id && <span style={{ color: 'var(--textDim)' }}> · {e.agent_id.slice(0, 8)}</span>}
              <span style={{ color: 'var(--dim)' }}> T{e.tick}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, color }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 11 }}>
      <span style={{ color: 'var(--textDim)' }}>{label}</span>
      <span style={{ color: color || 'var(--bright)' }}>{value}</span>
    </div>
  );
}
