import React, { useState, useEffect, useCallback } from 'react';
import IncidentList from './components/IncidentList';
import IncidentModal from './components/IncidentModal';
import Desk from './components/Desk';
import {
  fetchIncidents,
  fetchIncidentStats,
  createIncident,
  updateIncident,
  deleteIncident,
  fetchHealth
} from './api';

const FILTERS = [
  ['all', 'All'],
  ['open', 'Open'],
  ['resolved', 'Resolved']
];

const EDITION_DATE = new Intl.DateTimeFormat('en-GB', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
}).format(new Date());

function Ticker({ incidents }) {
  const open = incidents.filter((i) => i.status !== 'RESOLVED');
  if (open.length === 0) return null;
  const items = open.map((i) => (
    <span key={i.id} className="ticker-item">
      {i.severity === 'P1_CRITICAL' && <b>Breaking</b>}
      {i.service_name}: {i.title}
    </span>
  ));
  return (
    <div className="ticker" role="marquee" aria-label="Open incidents">
      <div className="ticker-track">
        <div>{items}</div>
        <div aria-hidden="true">{items}</div>
      </div>
    </div>
  );
}

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState(null);
  const [healthy, setHealthy] = useState(true);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sheet, setSheet] = useState(null);

  const load = useCallback(async () => {
    try {
      const [list, statsData, ok] = await Promise.all([
        fetchIncidents({ status: filter === 'resolved' ? 'RESOLVED' : undefined }),
        fetchIncidentStats(),
        fetchHealth()
      ]);
      setIncidents(filter === 'open' ? list.filter((i) => i.status !== 'RESOLVED') : list);
      setStats(statsData);
      setHealthy(ok);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    load();
    const id = setInterval(load, 10000);
    return () => clearInterval(id);
  }, [load]);

  const save = async (form) => {
    if (sheet.incident) await updateIncident(sheet.incident.id, form);
    else await createIncident(form);
    await load();
  };

  const remove = async (id) => {
    await deleteIncident(id);
    await load();
  };

  return (
    <div className="paper">
      <header className="masthead">
        <div className="edition">
          <span>Vol. 1</span>
          <span>{EDITION_DATE}</span>
          <span className={healthy ? undefined : 'offline'}>{healthy ? 'Wire: online' : 'Wire: down'}</span>
        </div>
        <h1>Kairos</h1>
        <p className="motto">The Outage Record · All the incidents fit to resolve</p>
      </header>

      <Ticker incidents={incidents} />

      <main className="page">
        <div className="toolbar">
          <div className="tabs" role="group" aria-label="Filter incidents">
            {FILTERS.map(([value, label]) => (
              <button key={value} aria-pressed={filter === value} onClick={() => setFilter(value)}>
                {label}
              </button>
            ))}
          </div>
          <button className="btn" onClick={() => setSheet({ incident: null })}>File a report</button>
        </div>

        <div className="columns">
          <section aria-label="Incidents">
            {loading ? (
              <p className="quiet">Going to press…</p>
            ) : error ? (
              <p className="quiet">Couldn’t load incidents. {error}</p>
            ) : (
              <IncidentList incidents={incidents} onSelect={(incident) => setSheet({ incident })} />
            )}
          </section>
          <Desk stats={stats} />
        </div>
      </main>

      <footer className="colophon">Edition: Vol 1.0 · Printed by the Kairos SRE desk</footer>

      {sheet && (
        <IncidentModal
          key={sheet.incident?.id ?? 'new'}
          incident={sheet.incident}
          onClose={() => setSheet(null)}
          onSave={save}
          onDelete={remove}
        />
      )}
    </div>
  );
}
