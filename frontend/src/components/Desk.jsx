import React from 'react';

export default function Desk({ stats }) {
  const rows = stats
    ? [
        ['Critical, active', stats.p1_active, true],
        ['Investigating', stats.investigating],
        ['Mitigated', stats.mitigated],
        ['Resolved', stats.resolved],
        ['On record', stats.total]
      ]
    : [];

  return (
    <aside className="desk" aria-labelledby="desk-title">
      <h2 id="desk-title" className="label">The Desk</h2>
      <dl>
        {rows.map(([label, value, alert]) => (
          <div key={label} className="figure">
            <dt>{label}</dt>
            <dd className={alert && value > 0 ? 'alert' : undefined}>{value}</dd>
          </div>
        ))}
      </dl>
      <p className="caption">Fig. 1.1 · Figures refresh every ten seconds.</p>
    </aside>
  );
}
