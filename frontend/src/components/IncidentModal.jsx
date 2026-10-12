import React, { useEffect, useRef, useState } from 'react';
import { SEVERITIES, STATUSES, relativeTime } from '../incident';

const EMPTY = { title: '', service_name: '', severity: 'P2_HIGH', summary: '', responder: '' };

function Field({ label, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}

export default function IncidentModal({ incident, onClose, onSave, onDelete }) {
  const editing = Boolean(incident);
  const [form, setForm] = useState(() =>
    editing
      ? { status: incident.status, severity: incident.severity, responder: incident.responder, root_cause: incident.root_cause || '' }
      : EMPTY
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    dialog.querySelector('input, select, textarea')?.focus();
    return () => dialog.close();
  }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const run = async (action) => {
    setBusy(true);
    setError(null);
    try {
      await action();
      onClose();
    } catch (err) {
      setError(err.message || 'Something went wrong.');
      setBusy(false);
    }
  };

  const submit = (e) => {
    e.preventDefault();
    run(() => onSave(form));
  };

  const remove = () => {
    if (window.confirm('Delete this incident? This can’t be undone.')) run(() => onDelete(incident.id));
  };

  return (
    <dialog
      ref={ref}
      className="sheet"
      aria-labelledby="sheet-title"
      onCancel={(e) => { e.preventDefault(); onClose(); }}
      onClick={(e) => e.target === ref.current && onClose()}
    >
      <form onSubmit={submit}>
        <header className="sheet-bar">
          <button type="button" className="text-btn" onClick={onClose}>Cancel</button>
          <h2 id="sheet-title">{editing ? 'Incident report' : 'File a report'}</h2>
          <button type="submit" className="text-btn strong" disabled={busy}>
            {editing ? 'Save' : 'File'}
          </button>
        </header>

        <div className="sheet-body">
          {editing && (
            <div className="detail">
              <h3>{incident.title}</h3>
              <p className="meta">{incident.service_name} · opened {relativeTime(incident.created_at)}</p>
              <p>{incident.summary}</p>
            </div>
          )}

          {!editing && (
            <>
              <Field label="Title">
                <input required minLength={3} maxLength={255} value={form.title} onChange={set('title')} />
              </Field>
              <Field label="Service">
                <input required minLength={2} maxLength={100} value={form.service_name} onChange={set('service_name')} placeholder="api-gateway" />
              </Field>
            </>
          )}

          <div className="pair">
            <Field label="Severity">
              <select value={form.severity} onChange={set('severity')}>
                {Object.entries(SEVERITIES).map(([value, s]) => (
                  <option key={value} value={value}>{s.short} · {s.label}</option>
                ))}
              </select>
            </Field>
            {editing && (
              <Field label="Status">
                <select value={form.status} onChange={set('status')}>
                  {Object.entries(STATUSES).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </Field>
            )}
          </div>

          <Field label="Responder">
            <input required minLength={2} maxLength={100} value={form.responder} onChange={set('responder')} />
          </Field>

          {editing ? (
            <Field label="Root cause">
              <textarea rows={3} value={form.root_cause} onChange={set('root_cause')} />
            </Field>
          ) : (
            <Field label="Summary">
              <textarea required minLength={5} rows={3} value={form.summary} onChange={set('summary')} />
            </Field>
          )}

          {error && <p className="error" role="alert">{error}</p>}

          {editing && (
            <button type="button" className="text-btn danger" onClick={remove} disabled={busy}>
              Delete Incident
            </button>
          )}
        </div>
      </form>
    </dialog>
  );
}
