const SEV_COLOR = { INFO: 'var(--teal)', WARNING: 'var(--amber)', CRITICAL: 'var(--red)' };

const BAR_COLORS = { work: 'var(--teal)', rest: 'var(--violet)', play: 'var(--amber)' };

function fatigueColor(fi) {
  if (fi >= 0.75) return 'var(--red)';
  if (fi >= 0.4) return 'var(--amber)';
  return 'var(--teal)';
}

export default function MetricsSidebar({ population, alerts, events, kpis }) {
  const recentAlerts = (alerts || []).slice(-5).reverse();
  const recentEvents = (events || []).slice(-10).reverse();

  // Sort agents by fatigue descending for the KPI table
  const kpiRows = kpis
    ? Object.values(kpis).sort((a, b) => b.fatigue_index - a.fatigue_index)
    : [];

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

      {/* Per-agent KPI table */}
      {kpiRows.length > 0 && (
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.12em', marginBottom: 8 }}>
            AGENT KPIs
          </div>
          {kpiRows.map(row => (
            <div key={row.name} style={{ marginBottom: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ fontSize: 10, color: 'var(--bright)' }}>{row.name}</span>
                <span style={{ fontSize: 10, color: fatigueColor(row.fatigue_index) }}>
                  FI {row.fatigue_index.toFixed(3)}
                </span>
              </div>
              {/* Work/rest/play mini bar */}
              <div style={{ display: 'flex', height: 4, borderRadius: 2, overflow: 'hidden', gap: 1 }}>
                {['work', 'rest', 'play'].map(k => (
                  <div key={k} style={{
                    width: `${(row.work_rest_play?.[k] || 0) * 100}%`,
                    background: BAR_COLORS[k],
                    minWidth: row.work_rest_play?.[k] > 0 ? 1 : 0,
                  }} />
                ))}
              </div>
              <div style={{ display: 'flex', gap: 8, fontSize: 9, color: 'var(--dim)', marginTop: 2 }}>
                <span style={{ color: BAR_COLORS.work }}>W {((row.work_rest_play?.work || 0) * 100).toFixed(0)}%</span>
                <span style={{ color: BAR_COLORS.rest }}>R {((row.work_rest_play?.rest || 0) * 100).toFixed(0)}%</span>
                <span style={{ color: BAR_COLORS.play }}>P {((row.work_rest_play?.play || 0) * 100).toFixed(0)}%</span>
                <span style={{ marginLeft: 'auto', color: 'var(--teal)' }}>${row.earnings.toFixed(0)}</span>
              </div>
            </div>
          ))}
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
