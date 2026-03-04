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

/**
 * Check Ollama connectivity and list available models.
 * @returns {Promise<{available: boolean, models: string[], error: string|null}>}
 */
export async function getOllamaStatus() {
  const res = await fetch(`${API_BASE}/settings/ollama-status`);
  if (!res.ok) throw new Error(`Failed to check Ollama status: ${res.status}`);
  return res.json();
}

/**
 * Export all artifacts for a project as combined Markdown.
 * @param {string} projectId - Project scope
 * @returns {Promise<{markdown: string, artifact_count: number}>}
 */
export async function exportArtifacts(projectId = 'default') {
  const res = await fetch(`${API_BASE}/artifacts/${encodeURIComponent(projectId)}/export`);
  if (!res.ok) throw new Error(`Failed to export artifacts: ${res.status}`);
  return res.json();
}

// ============================================================
// LPD (Living Project Document)
// ============================================================

/**
 * Initialize an LPD for a project (idempotent — safe to call if already initialized).
 * @param {string} projectId - Project scope
 * @returns {Promise<{status: string, section_count: number, sections: string[]}>}
 */
export async function initializeLPD(projectId = 'default') {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/initialize`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to initialize LPD: ${res.status}`);
  return res.json();
}

/**
 * Get all LPD sections for a project.
 * @param {string} projectId - Project scope
 * @returns {Promise<{sections: Object}>} Map of section_name → content
 */
export async function getLPDSections(projectId = 'default') {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/sections`);
  if (!res.ok) throw new Error(`Failed to load LPD sections: ${res.status}`);
  return res.json();
}

/**
 * Update a single LPD section's content.
 * @param {string} projectId - Project scope
 * @param {string} sectionName - Section to update (e.g., 'Risks')
 * @param {string} content - New content for the section
 * @returns {Promise<{status: string, section: string}>}
 */
export async function updateLPDSection(projectId, sectionName, content) {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/sections/${encodeURIComponent(sectionName)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`Failed to update section: ${res.status}`);
  return res.json();
}

/**
 * Get staleness metrics for all LPD sections.
 * @param {string} projectId - Project scope
 * @returns {Promise<{staleness: Array}>}
 */
export async function getLPDStaleness(projectId = 'default') {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/staleness`);
  if (!res.ok) throw new Error(`Failed to load staleness data: ${res.status}`);
  return res.json();
}

/**
 * Get the full LPD as rendered Markdown.
 * @param {string} projectId - Project scope
 * @returns {Promise<{markdown: string}>}
 */
export async function getLPDMarkdown(projectId = 'default') {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/markdown`);
  if (!res.ok) throw new Error(`Failed to load LPD markdown: ${res.status}`);
  return res.json();
}

/**
 * Mark an LPD section as verified (human reviewed and confirmed accurate).
 * @param {string} projectId - Project scope
 * @param {string} sectionName - Section to verify
 * @returns {Promise<{status: string, section: string}>}
 */
export async function verifyLPDSection(projectId, sectionName) {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/sections/${encodeURIComponent(sectionName)}/verify`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to verify section: ${res.status}`);
  return res.json();
}

/**
 * Append content to an LPD section (reads current content, appends, writes back).
 * Used by the "Apply Anyway" flow for contradiction overrides.
 * @param {string} projectId - Project scope
 * @param {string} sectionName - Section to append to (e.g., 'Risks')
 * @param {string} content - Content to append
 * @returns {Promise<{status: string, section: string}>}
 */
export async function appendToLPDSection(projectId, sectionName, content) {
  const { sections } = await getLPDSections(projectId)
  const current = sections[sectionName] || ''
  const updated = current ? current + '\n' + content : content
  return updateLPDSection(projectId, sectionName, updated)
}

/**
 * Submit files for intake preview (extract entities for LPD population).
 * @param {string} projectId - Project scope
 * @param {Array<{filename: string, content: string}>} files - Files to process
 * @returns {Promise<Object>} IntakeDraft with extractions, proposed_sections, conflicts
 */
export async function intakePreview(projectId, files) {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/intake/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

/**
 * Apply approved intake sections to the LPD.
 * @param {string} projectId - Project scope
 * @param {Object} proposedSections - Section name → content map
 * @param {string[]} approvedSections - Sections the user approved
 * @returns {Promise<{sections_updated: string[], sections_skipped: string[]}>}
 */
// ============================================================
// TRANSCRIPT WATCHER
// ============================================================

/**
 * Get the current transcript watcher status.
 * @returns {Promise<{running: boolean, watch_folder: string|null, mode: string, files_processed: number, recent_files: Array}>}
 */
export async function getTranscriptWatcherStatus() {
  const res = await fetch(`${API_BASE}/transcript-watcher/status`);
  if (!res.ok) throw new Error(`Failed to get watcher status: ${res.status}`);
  return res.json();
}

/**
 * Start the transcript watcher.
 * @param {string} [projectId='default'] - Project scope
 * @returns {Promise<Object>} Watcher status after starting
 */
export async function startTranscriptWatcher(projectId = 'default') {
  const res = await fetch(`${API_BASE}/transcript-watcher/start?project_id=${encodeURIComponent(projectId)}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Failed to start watcher: ${res.status}`);
  }
  return res.json();
}

/**
 * Stop the transcript watcher.
 * @returns {Promise<{status: string}>}
 */
export async function stopTranscriptWatcher() {
  const res = await fetch(`${API_BASE}/transcript-watcher/stop`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Failed to stop watcher: ${res.status}`);
  }
  return res.json();
}

/**
 * Process a single transcript file manually.
 * @param {string} filePath - Absolute path to the transcript file
 * @returns {Promise<Object>} Processing result
 */
/**
 * Get recent transcript processing results with full sync data.
 * @returns {Promise<{results: Array}>}
 */
export async function getTranscriptWatcherResults() {
  const res = await fetch(`${API_BASE}/transcript-watcher/results`);
  if (!res.ok) throw new Error(`Failed to get watcher results: ${res.status}`);
  return res.json();
}

/**
 * Upload a transcript file for processing (drag-and-drop / file picker).
 * @param {string} filename - Original filename
 * @param {string} content - File content as text
 * @returns {Promise<Object>} Processing result
 */
export async function uploadTranscriptFile(filename, content) {
  const res = await fetch(`${API_BASE}/transcript-watcher/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, content }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Failed to upload file: ${res.status}`);
  }
  return res.json();
}

export async function processTranscriptFile(filePath) {
  const res = await fetch(`${API_BASE}/transcript-watcher/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: filePath }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Failed to process file: ${res.status}`);
  }
  return res.json();
}

// ============================================================
// DEEP STRATEGY
// ============================================================

/**
 * Run 4-pass Deep Strategy analysis on uploaded artifacts.
 * @param {Array<{name: string, content: string, priority: number}>} artifacts - Artifacts to analyze
 * @param {string} [projectId='default'] - Project scope
 * @returns {Promise<Object>} DeepStrategyResponse with all pass results and summary
 */
export async function deepStrategyAnalyze(artifacts, projectId = 'default') {
  const res = await fetch(`${API_BASE}/deep-strategy/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ artifacts, project_id: projectId }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

/**
 * Apply selected Deep Strategy updates to artifacts.
 * @param {Array} updates - ProposedUpdate objects to apply
 * @param {string} [projectId='default'] - Project scope
 * @returns {Promise<{applied: Array, copied_to_clipboard: string[]}>}
 */
export async function deepStrategyApply(updates, projectId = 'default') {
  const res = await fetch(`${API_BASE}/deep-strategy/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ updates, project_id: projectId }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ============================================================
// RISK PREDICTION & RECONCILIATION
// ============================================================

/**
 * Run AI risk prediction based on project LPD state.
 * @param {string} [projectId='default'] - Project scope
 * @returns {Promise<{predictions: Array, project_health: string, pii_detected: number, session_id: string}>}
 */
export async function predictRisks(projectId = 'default') {
  const res = await fetch(`${API_BASE}/risk-prediction/${encodeURIComponent(projectId)}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

/**
 * Run cross-section LPD reconciliation.
 * @param {string} [projectId='default'] - Project scope
 * @returns {Promise<{impacts: Array, sections_analyzed: number, pii_detected: number, session_id: string}>}
 */
export async function reconcileLPD(projectId = 'default') {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/reconcile`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// ============================================================
// FOLDER BROWSER
// ============================================================

/**
 * Browse directories for folder selection.
 * @param {string} [path] - Directory path to browse (defaults to home)
 * @returns {Promise<{current_path: string, parent_path: string|null, directories: Array}>}
 */
export async function browseFolders(path) {
  const params = path ? `?path=${encodeURIComponent(path)}` : '';
  const res = await fetch(`${API_BASE}/settings/browse-folders${params}`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function intakeApply(projectId, proposedSections, approvedSections) {
  const res = await fetch(`${API_BASE}/lpd/${encodeURIComponent(projectId)}/intake/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      proposed_sections: proposedSections,
      approved_sections: approvedSections,
    }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: `Request failed: ${res.status}` }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}
