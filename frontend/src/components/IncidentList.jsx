import React from 'react';
import { SEVERITIES, STATUSES, relativeTime } from '../incident';

const SEVERITY_RANK = Object.keys(SEVERITIES);

// open first, then by severity
const byUrgency = (a, b) =>
  (a.status === 'RESOLVED') - (b.status === 'RESOLVED') ||
  SEVERITY_RANK.indexOf(a.severity) - SEVERITY_RANK.indexOf(b.severity);

export default function IncidentList({ incidents, onSelect }) {
  if (incidents.length === 0) {
    return <p className="quiet">No incidents on record. A quiet day at the desk.</p>;
  }

  return (
    <ol className="stories">
      {[...incidents].sort(byUrgency).map((inc) => {
        const sev = SEVERITIES[inc.severity] || SEVERITIES.P4_LOW;
        const resolved = inc.status === 'RESOLVED';
        return (
          <li key={inc.id}>
            <button
              className={`story${resolved ? ' resolved' : ''}`}
              onClick={() => onSelect(inc)}
            >
              <span className="kicker">
                <span className={`sev${inc.severity === 'P1_CRITICAL' ? ' breaking' : ''}`}>
                  {sev.short} {sev.label}
                </span>
                <span>{inc.service_name}</span>
                <span>{relativeTime(inc.created_at)}</span>
              </span>
              <span className="headline">{inc.title}</span>
              <span className="dek">{inc.summary}</span>
              <span className="byline">
                {STATUSES[inc.status] || inc.status} · {inc.responder}
              </span>
            </button>
          </li>
        );
      })}
    </ol>
  );
}
