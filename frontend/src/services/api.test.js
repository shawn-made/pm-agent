import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  healthCheck,
  artifactSync,
  getSettings,
  updateSettings,
  applySuggestion,
  applySuggestionByType,
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
  it('posts text and returns suggestions', async () => {
    const response = { suggestions: [], input_type: 'text', session_id: 's1', pii_detected: 0 }
    mockFetch(response)
    const result = await artifactSync('hello world')
    expect(result).toEqual(response)
    expect(fetch).toHaveBeenCalledWith('/api/artifact-sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'hello world', project_id: 'default' }),
    })
  })

  it('sends custom project_id', async () => {
    mockFetch({ suggestions: [] })
    await artifactSync('text', 'proj-1')
    expect(fetch).toHaveBeenCalledWith('/api/artifact-sync', expect.objectContaining({
      body: JSON.stringify({ text: 'text', project_id: 'proj-1' }),
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
