/**
 * API client for communicating with the VPMA FastAPI backend.
 * All requests go through the Vite dev proxy (/api → localhost:8000).
 */

const API_BASE = '/api';

/**
 * Check if the backend is running and healthy.
 * @returns {Promise<{status: string}>} Backend health status
 */
export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

/**
 * Send text through the artifact sync pipeline (anonymize → LLM → suggestions).
 * @param {string} text - Raw user input (meeting notes, transcript, etc.)
 * @param {string} [projectId='default'] - Project scope for the sync
 * @returns {Promise<{suggestions: Array, input_type: string, session_id: string, pii_detected: number}>}
 */
export async function artifactSync(text, projectId = 'default', mode = 'extract') {
  const res = await fetch(`${API_BASE}/artifact-sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, project_id: projectId, mode }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

/**
 * Retrieve current application settings (LLM provider, masked API keys, sensitive terms).
 * @returns {Promise<{settings: Object}>} Current settings object
 */
export async function getSettings() {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error(`Failed to load settings: ${res.status}`);
  return res.json();
}

/**
 * Save updated application settings.
 * @param {Object} settings - Settings to update
 * @param {string} [settings.llm_provider] - 'claude' or 'gemini'
 * @param {string} [settings.anthropic_api_key] - Anthropic API key (omit to keep existing)
 * @param {string} [settings.google_ai_api_key] - Google AI API key (omit to keep existing)
 * @param {string} [settings.sensitive_terms] - Comma/newline-separated terms to anonymize
 * @returns {Promise<Object>} Updated settings confirmation
 */
export async function updateSettings(settings) {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error(`Failed to save settings: ${res.status}`);
  return res.json();
}

/**
 * Apply a suggestion to an existing artifact by artifact ID.
 * @param {string} artifactId - UUID of the target artifact
 * @param {Object} suggestion - Suggestion payload with proposed_text
 * @returns {Promise<Object>} Apply result confirmation
 */
export async function applySuggestion(artifactId, suggestion) {
  const res = await fetch(`${API_BASE}/artifacts/${artifactId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(suggestion),
  });
  if (!res.ok) throw new Error(`Failed to apply suggestion: ${res.status}`);
  return res.json();
}

/**
 * Apply a suggestion by artifact type (auto-creates artifact if needed).
 * @param {Object} suggestion - Suggestion with artifact_type and proposed_text
 * @param {string} [projectId='default'] - Project scope
 * @returns {Promise<Object>} Apply result confirmation
 */
export async function applySuggestionByType(suggestion, projectId = 'default') {
  const res = await fetch(`${API_BASE}/artifacts/apply?project_id=${encodeURIComponent(projectId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(suggestion),
  });
  if (!res.ok) throw new Error(`Failed to apply suggestion: ${res.status}`);
  return res.json();
}
