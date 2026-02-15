const API_BASE = '/api';

export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function artifactSync(text, projectId = 'default') {
  const res = await fetch(`${API_BASE}/artifact-sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, project_id: projectId }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function getSettings() {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error(`Failed to load settings: ${res.status}`);
  return res.json();
}

export async function updateSettings(settings) {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error(`Failed to save settings: ${res.status}`);
  return res.json();
}

export async function applySuggestion(artifactId, suggestion) {
  const res = await fetch(`${API_BASE}/artifacts/${artifactId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(suggestion),
  });
  if (!res.ok) throw new Error(`Failed to apply suggestion: ${res.status}`);
  return res.json();
}

export async function applySuggestionByType(suggestion, projectId = 'default') {
  const res = await fetch(`${API_BASE}/artifacts/apply?project_id=${encodeURIComponent(projectId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(suggestion),
  });
  if (!res.ok) throw new Error(`Failed to apply suggestion: ${res.status}`);
  return res.json();
}
