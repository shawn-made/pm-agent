import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import usePersistedResults from './usePersistedResults'

// Use a simple in-memory store to mock localStorage
let store = {}

const mockLocalStorage = {
  getItem: vi.fn((key) => store[key] ?? null),
  setItem: vi.fn((key, value) => { store[key] = value }),
  removeItem: vi.fn((key) => { delete store[key] }),
}

describe('usePersistedResults', () => {
  beforeEach(() => {
    store = {}
    vi.stubGlobal('localStorage', mockLocalStorage)
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns null when no stored results', () => {
    const { result } = renderHook(() => usePersistedResults('extract'))
    expect(result.current.results).toBeNull()
  })

  it('persists results to localStorage', () => {
    const { result } = renderHook(() => usePersistedResults('extract'))
    const data = { suggestions: [{ text: 'test' }], meta: { mode: 'extract' } }

    act(() => {
      result.current.setResults(data)
    })

    expect(result.current.results).toEqual(data)
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'vpma_results_extract',
      JSON.stringify(data)
    )
  })

  it('restores results from localStorage on mount', () => {
    const data = { suggestions: [{ text: 'saved' }], meta: { mode: 'extract' } }
    store['vpma_results_extract'] = JSON.stringify(data)

    const { result } = renderHook(() => usePersistedResults('extract'))
    expect(result.current.results).toEqual(data)
  })

  it('clears results from state and localStorage', () => {
    const data = { suggestions: [{ text: 'test' }] }
    store['vpma_results_extract'] = JSON.stringify(data)

    const { result } = renderHook(() => usePersistedResults('extract'))

    act(() => {
      result.current.clearResults()
    })

    expect(result.current.results).toBeNull()
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('vpma_results_extract')
  })

  it('stores each mode independently', () => {
    const extractData = { suggestions: [{ text: 'extract' }] }
    const analyzeData = { analysis: { items: [{ text: 'analyze' }] } }

    store['vpma_results_extract'] = JSON.stringify(extractData)
    store['vpma_results_analyze'] = JSON.stringify(analyzeData)

    const { result: extractResult } = renderHook(() => usePersistedResults('extract'))
    const { result: analyzeResult } = renderHook(() => usePersistedResults('analyze'))

    expect(extractResult.current.results).toEqual(extractData)
    expect(analyzeResult.current.results).toEqual(analyzeData)
  })

  it('loads different results when mode changes', () => {
    const extractData = { suggestions: [{ text: 'extract' }] }
    const analyzeData = { analysis: { items: [{ text: 'analyze' }] } }

    store['vpma_results_extract'] = JSON.stringify(extractData)
    store['vpma_results_analyze'] = JSON.stringify(analyzeData)

    const { result, rerender } = renderHook(
      ({ mode }) => usePersistedResults(mode),
      { initialProps: { mode: 'extract' } }
    )

    expect(result.current.results).toEqual(extractData)

    rerender({ mode: 'analyze' })
    expect(result.current.results).toEqual(analyzeData)
  })

  it('setting null clears from localStorage', () => {
    const data = { suggestions: [{ text: 'test' }] }

    const { result } = renderHook(() => usePersistedResults('extract'))

    act(() => {
      result.current.setResults(data)
    })
    expect(store['vpma_results_extract']).toBeDefined()

    act(() => {
      result.current.setResults(null)
    })
    expect(result.current.results).toBeNull()
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('vpma_results_extract')
  })

  it('handles corrupted localStorage gracefully', () => {
    store['vpma_results_extract'] = 'not valid json'

    const { result } = renderHook(() => usePersistedResults('extract'))
    expect(result.current.results).toBeNull()
  })
})
