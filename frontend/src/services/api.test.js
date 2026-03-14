import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  healthCheck,
  artifactSync,
  getSettings,
  updateSettings,
  applySuggestion,
  applySuggestionByType,
  deepStrategyAnalyze,
  deepStrategyApply,
  getAvailableArtifacts,
  predictRisks,
  reconcileLPD,
  browseFolders,
  getOllamaInfo,
  startOllama,
  exportArtifacts,
} from './api'

// There are 6 exported functions (healthCheck was counted twice in the spec —
// applySuggestion + applySuggestionByType = 7 total including healthCheck).

beforeEach(() => {
  vi.restoreAllMocks()
})

function mockFetch(body, ok = true, status = 200) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(body),
  })
}

describe('healthCheck', () => {
  it('returns JSON on success', async () => {
    mockFetch({ status: 'ok' })
    const result = await healthCheck()
    expect(result).toEqual({ status: 'ok' })
    expect(fetch).toHaveBeenCalledWith('/api/health')
  })

  it('throws on non-ok response', async () => {
    mockFetch({}, false, 503)
    await expect(healthCheck()).rejects.toThrow('Health check failed: 503')
  })
})

describe('artifactSync', () => {
  it('posts text and returns suggestions (defaults to extract mode)', async () => {
    const response = { suggestions: [], input_type: 'text', session_id: 's1', pii_detected: 0 }
    mockFetch(response)
    const result = await artifactSync('hello world')
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/artifact-sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'hello world', project_id: 'default', mode: 'extract' }),
    })
  })

  it('sends custom project_id', async () => {
    mockFetch({ suggestions: [] })
    await artifactSync('text', 'proj-1')
    expect(fetch).toHaveBeenCalledWith('/api/artifact-sync', expect.objectContaining({
      body: JSON.stringify({ text: 'text', project_id: 'proj-1', mode: 'extract' }),
    }))
  })

  it('sends analyze mode when specified', async () => {
    mockFetch({ analysis: [], analysis_summary: null })
    await artifactSync('draft text', 'default', 'analyze')
    expect(fetch).toHaveBeenCalledWith('/api/artifact-sync', expect.objectContaining({
      body: JSON.stringify({ text: 'draft text', project_id: 'default', mode: 'analyze' }),
    }))
  })

  it('throws with error detail from response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 422,
      json: () => Promise.resolve({ detail: 'Bad input' }),
    })
    await expect(artifactSync('x')).rejects.toThrow('Bad input')
  })

  it('throws with status code when no detail', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.reject(new Error('parse error')),
    })
    await expect(artifactSync('x')).rejects.toThrow('Request failed: 500')
  })
})

describe('getSettings', () => {
  it('returns settings on success', async () => {
    const data = { settings: { llm_provider: 'claude' } }
    mockFetch(data)
    const result = await getSettings()
    expect(result).toEqual(data)
    expect(fetch).toHaveBeenCalledWith('/api/settings')
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 500)
    await expect(getSettings()).rejects.toThrow('Failed to load settings: 500')
  })
})

describe('updateSettings', () => {
  it('PUTs settings and returns result', async () => {
    const payload = { llm_provider: 'gemini' }
    mockFetch({ success: true })
    const result = await updateSettings(payload)
    expect(result).toEqual({ success: true })
    expect(fetch).toHaveBeenCalledWith('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 400)
    await expect(updateSettings({})).rejects.toThrow('Failed to save settings: 400')
  })
})

describe('applySuggestion', () => {
  it('posts suggestion to artifact endpoint', async () => {
    const suggestion = { artifact_type: 'RAID Log', proposed_text: 'text' }
    mockFetch({ success: true })
    const result = await applySuggestion('art-1', suggestion)
    expect(result).toEqual({ success: true })
    expect(fetch).toHaveBeenCalledWith('/api/artifacts/art-1/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(suggestion),
    })
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 404)
    await expect(applySuggestion('x', {})).rejects.toThrow('Failed to apply suggestion: 404')
  })
})

describe('applySuggestionByType', () => {
  it('posts to /artifacts/apply with project_id', async () => {
    const suggestion = { artifact_type: 'Status Report' }
    mockFetch({ success: true })
    const result = await applySuggestionByType(suggestion, 'proj-2')
    expect(result).toEqual({ success: true })
    expect(fetch).toHaveBeenCalledWith('/api/artifacts/apply?project_id=proj-2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(suggestion),
    })
  })

  it('defaults to project_id=default', async () => {
    mockFetch({ success: true })
    await applySuggestionByType({ artifact_type: 'Meeting Notes' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/artifacts/apply?project_id=default',
      expect.any(Object),
    )
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 500)
    await expect(applySuggestionByType({})).rejects.toThrow('Failed to apply suggestion: 500')
  })
})

// ============================================================
// Phase 2B API functions
// ============================================================

describe('deepStrategyAnalyze (XHR)', () => {
  let xhrInstances

  class MockXHR {
    constructor() {
      this.open = vi.fn()
      this.setRequestHeader = vi.fn()
      this.send = vi.fn()
      this.timeout = 0
      this.onload = null
      this.onerror = null
      this.ontimeout = null
      this.status = 0
      this.responseText = ''
      xhrInstances.push(this)
    }
  }

  function setupXHR(responseBody, status = 200) {
    xhrInstances = []
    const OrigSend = MockXHR.prototype.send
    vi.stubGlobal('XMLHttpRequest', class extends MockXHR {
      constructor() {
        super()
        this.send = vi.fn(() => {
          this.status = status
          this.responseText = JSON.stringify(responseBody)
          this.onload?.()
        })
      }
    })
  }

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('posts artifacts and returns analysis result', async () => {
    const artifacts = [{ name: 'A', content: 'text', priority: 1 }]
    const response = { summary: {}, inconsistencies: [], proposed_updates: [] }
    setupXHR(response)
    const result = await deepStrategyAnalyze(artifacts)
    expect(result).toEqual(response)
    expect(xhrInstances[0].open).toHaveBeenCalledWith('POST', '/api/deep-strategy/analyze')
    expect(xhrInstances[0].send).toHaveBeenCalledWith(
      JSON.stringify({ artifacts, project_id: 'default' })
    )
    expect(xhrInstances[0].timeout).toBe(300000)
  })

  it('sends custom project_id', async () => {
    setupXHR({})
    await deepStrategyAnalyze([], 'proj-x')
    expect(xhrInstances[0].send).toHaveBeenCalledWith(
      JSON.stringify({ artifacts: [], project_id: 'proj-x' })
    )
  })

  it('throws with error detail from response', async () => {
    setupXHR({ detail: 'Need at least 2 artifacts' }, 422)
    await expect(deepStrategyAnalyze([])).rejects.toThrow('Need at least 2 artifacts')
  })

  it('throws on network error', async () => {
    xhrInstances = []
    vi.stubGlobal('XMLHttpRequest', class extends MockXHR {
      constructor() {
        super()
        this.send = vi.fn(() => { this.onerror?.() })
      }
    })
    await expect(deepStrategyAnalyze([])).rejects.toThrow('Network error')
  })

  it('throws on timeout', async () => {
    xhrInstances = []
    vi.stubGlobal('XMLHttpRequest', class extends MockXHR {
      constructor() {
        super()
        this.send = vi.fn(() => { this.ontimeout?.() })
      }
    })
    await expect(deepStrategyAnalyze([])).rejects.toThrow('Request timed out')
  })
})

describe('deepStrategyApply', () => {
  it('posts updates and returns apply result', async () => {
    const updates = [{ target: 'A', change_type: 'modify' }]
    const response = { applied: [{ status: 'applied' }], copied_to_clipboard: [] }
    mockFetch(response)
    const result = await deepStrategyApply(updates)
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/deep-strategy/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates, project_id: 'default' }),
    })
  })

  it('throws on failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false, status: 500,
      json: () => Promise.reject(new Error('parse error')),
    })
    await expect(deepStrategyApply([])).rejects.toThrow('Request failed: 500')
  })
})

describe('getAvailableArtifacts', () => {
  it('fetches available artifacts for default project', async () => {
    const response = { items: [{ name: 'RAID Log', content: 'stuff', source: 'artifact' }] }
    mockFetch(response)
    const result = await getAvailableArtifacts()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/deep-strategy/available-artifacts/default')
  })

  it('encodes custom project_id', async () => {
    mockFetch({ items: [] })
    await getAvailableArtifacts('my project')
    expect(fetch).toHaveBeenCalledWith('/api/deep-strategy/available-artifacts/my%20project')
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 500)
    await expect(getAvailableArtifacts()).rejects.toThrow('Failed to load available artifacts: 500')
  })
})

describe('predictRisks', () => {
  it('posts risk prediction request', async () => {
    const response = { predictions: [], project_health: 'healthy', pii_detected: 0 }
    mockFetch(response)
    const result = await predictRisks()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/risk-prediction/default', { method: 'POST' })
  })

  it('encodes custom project_id', async () => {
    mockFetch({})
    await predictRisks('proj-2')
    expect(fetch).toHaveBeenCalledWith('/api/risk-prediction/proj-2', { method: 'POST' })
  })

  it('throws with error detail from response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false, status: 422,
      json: () => Promise.resolve({ detail: 'LPD not initialized' }),
    })
    await expect(predictRisks()).rejects.toThrow('LPD not initialized')
  })
})

describe('reconcileLPD', () => {
  it('posts reconciliation request', async () => {
    const response = { impacts: [], sections_analyzed: 5, pii_detected: 0 }
    mockFetch(response)
    const result = await reconcileLPD()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/lpd/default/reconcile', { method: 'POST' })
  })

  it('encodes custom project_id', async () => {
    mockFetch({})
    await reconcileLPD('proj-3')
    expect(fetch).toHaveBeenCalledWith('/api/lpd/proj-3/reconcile', { method: 'POST' })
  })

  it('throws on failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false, status: 500,
      json: () => Promise.reject(new Error('parse error')),
    })
    await expect(reconcileLPD()).rejects.toThrow('Request failed: 500')
  })
})

describe('browseFolders', () => {
  it('fetches default path when no path provided', async () => {
    const response = { current_path: '/home', parent_path: null, directories: [] }
    mockFetch(response)
    const result = await browseFolders()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/settings/browse-folders')
  })

  it('encodes path parameter', async () => {
    mockFetch({ current_path: '/tmp/my folder', parent_path: '/tmp', directories: [] })
    await browseFolders('/tmp/my folder')
    expect(fetch).toHaveBeenCalledWith('/api/settings/browse-folders?path=%2Ftmp%2Fmy%20folder')
  })

  it('throws with error detail from response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false, status: 403,
      json: () => Promise.resolve({ detail: 'Permission denied' }),
    })
    await expect(browseFolders('/root')).rejects.toThrow('Permission denied')
  })
})

describe('getOllamaInfo', () => {
  it('fetches Ollama info', async () => {
    const response = { installed: true, install_path: '/usr/bin/ollama', running: true, models: ['llama3.2'], error: null }
    mockFetch(response)
    const result = await getOllamaInfo()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/settings/ollama-info')
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 500)
    await expect(getOllamaInfo()).rejects.toThrow('Failed to get Ollama info: 500')
  })
})

describe('startOllama', () => {
  it('posts start request', async () => {
    const response = { started: true, error: null }
    mockFetch(response)
    const result = await startOllama()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/settings/ollama-start', { method: 'POST' })
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 500)
    await expect(startOllama()).rejects.toThrow('Failed to start Ollama: 500')
  })
})

describe('exportArtifacts', () => {
  it('fetches export for default project', async () => {
    const response = { markdown: '# RAID Log\n...', artifact_count: 3 }
    mockFetch(response)
    const result = await exportArtifacts()
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/artifacts/default/export')
  })

  it('encodes custom project_id', async () => {
    mockFetch({ markdown: '', artifact_count: 0 })
    await exportArtifacts('proj-x')
    expect(fetch).toHaveBeenCalledWith('/api/artifacts/proj-x/export')
  })

  it('throws on failure', async () => {
    mockFetch({}, false, 500)
    await expect(exportArtifacts()).rejects.toThrow('Failed to export artifacts: 500')
  })
})
