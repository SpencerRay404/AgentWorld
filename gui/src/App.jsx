import { useState, useEffect, useCallback } from 'react';
import './styles/theme.css';
import PopulationGrid from './components/PopulationGrid';
import WorldState from './components/WorldState';
import MetricsSidebar from './components/MetricsSidebar';
import Charts from './components/Charts';
import AgentDetailDrawer from './components/AgentDetailDrawer';
import ControlPanel from './components/ControlPanel';
import { useSimData } from './hooks/useSimData';
import { useWebSocket } from './hooks/useWebSocket';

export default function App() {
  const { world, agents, population, alerts, fetchAll } = useSimData();
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [liveEvents, setLiveEvents] = useState([]);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 1500);
    return () => clearInterval(id);
  }, [fetchAll]);

  const onWsMessage = useCallback((event) => {
    setLiveEvents(prev => [...prev.slice(-49), event]);
    if (event.event_type === 'ALERT') {
      setToast(event.payload);
      setTimeout(() => setToast(null), 4000);
    }
    if (['TICK_COMPLETE', 'PAY_PERIOD'].includes(event.event_type)) {
      fetchAll();
    }
  }, [fetchAll]);

  useWebSocket('ws://localhost:8000/ws/live', onWsMessage);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      {/* Top bar */}
      <div style={{ borderBottom: '1px solid var(--border)', padding: '10px 20px', display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
        <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 800, color: 'var(--bright)', letterSpacing: '-0.02em' }}>AGENT WORLD</span>
        <span style={{ fontSize: 9, color: 'var(--textDim)', letterSpacing: '0.15em' }}>OBSERVER v1.0</span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 16, fontSize: 10, color: 'var(--dim)' }}>
          <span>{agents.length} agents</span>
          <span style={{ color: world ? 'var(--teal)' : 'var(--red)' }}>● {world ? 'connected' : 'offline'}</span>
        </div>
      </div>

      {/* World state (center top) */}
      <WorldState world={world} agents={agents} />

      {/* Main body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <PopulationGrid agents={agents} onSelectAgent={setSelectedAgent} />

        {/* Center — charts */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Charts agents={agents} />
        </div>

        <MetricsSidebar population={population} alerts={alerts} events={liveEvents} />
      </div>

      {/* Control panel */}
      <ControlPanel world={world} onRefresh={fetchAll} />

      {/* Agent drawer */}
      {selectedAgent && (
        <AgentDetailDrawer agentId={selectedAgent} onClose={() => setSelectedAgent(null)} />
      )}

      {/* Alert toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 60, left: '50%', transform: 'translateX(-50%)',
          background: 'var(--surface)', border: '1px solid var(--red)',
          borderRadius: 6, padding: '10px 18px', fontSize: 12, color: 'var(--red)',
          zIndex: 200, maxWidth: 360, textAlign: 'center',
        }}>
          ⚠ {toast.alert_type}: {toast.message}
        </div>
      )}
    </div>
  );
}
