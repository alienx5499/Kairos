const API_BASE = '/api/v1/incidents';

// 422 detail arrives as a list
const errorText = (detail) =>
  Array.isArray(detail) ? detail.map((d) => d.msg).join(', ') : detail;

export async function fetchIncidents(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.severity) params.append('severity', filters.severity);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);

  const query = params.toString() ? `?${params.toString()}` : '';
  const response = await fetch(`${API_BASE}${query}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch incidents: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchIncidentStats() {
  const response = await fetch(`${API_BASE}/stats/summary`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }
  return response.json();
}

export async function createIncident(data) {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorText(errorData.detail) || `Failed to create incident: ${response.statusText}`);
  }
  return response.json();
}

export async function updateIncident(id, data) {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorText(errorData.detail) || `Failed to update incident: ${response.statusText}`);
  }
  return response.json();
}

export async function deleteIncident(id) {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'DELETE'
  });
  if (!response.ok && response.status !== 204) {
    throw new Error(`Failed to delete incident: ${response.statusText}`);
  }
  return true;
}

export async function fetchHealth() {
  try {
    const res = await fetch('/health');
    return res.ok;
  } catch {
    return false;
  }
}
