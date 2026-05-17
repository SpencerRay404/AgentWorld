import { useState, useCallback } from 'react';

const BASE = 'http://localhost:8000';

export function useSimData() {
  const [world, setWorld] = useState(null);
  const [agents, setAgents] = useState([]);
  const [population, setPopulation] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [kpis, setKpis] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [w, a, p, al] = await Promise.all([
        fetch(`${BASE}/world`).then(r => r.json()),
        fetch(`${BASE}/agents`).then(r => r.json()),
        fetch(`${BASE}/population`).then(r => r.json()),
        fetch(`${BASE}/alerts`).then(r => r.json()),
      ]);
      setWorld(w);
      setAgents(a);
      setPopulation(p);
      setAlerts(al);
    } catch {}
  }, []);

  const fetchAgent = useCallback(async (id) => {
    const r = await fetch(`${BASE}/agents/${id}`);
    return r.json();
  }, []);

  const fetchTransactions = useCallback(async (id) => {
    const r = await fetch(`${BASE}/agents/${id}/transactions`);
    return r.json();
  }, []);

  const fetchKpis = useCallback(async () => {
    try {
      const k = await fetch(`${BASE}/kpis`).then(r => r.json());
      setKpis(k);
    } catch {}
  }, []);

  const fetchTimeseries = useCallback(async (kpi = 'balance', cycles = 5) => {
    const r = await fetch(`${BASE}/kpis/timeseries?kpi=${kpi}&cycles=${cycles}`);
    return r.json();
  }, []);

  const control = useCallback(async (action) => {
    await fetch(`${BASE}/control/${action}`, { method: 'POST' });
    fetchAll();
  }, [fetchAll]);

  return { world, agents, population, alerts, kpis, fetchAll, fetchAgent, fetchTransactions, fetchKpis, fetchTimeseries, control };
}
