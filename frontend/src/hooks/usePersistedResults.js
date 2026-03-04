/**
 * Custom hook for persisting artifact sync results across tab navigation.
 * Uses localStorage with "clear on new sync" semantics (D41).
 * Each mode (extract/analyze/log_session) gets independent storage.
 */
import { useState, useCallback } from 'react'

const STORAGE_PREFIX = 'vpma_results_'

function getStorageKey(mode) {
  return `${STORAGE_PREFIX}${mode}`
}

function loadFromStorage(mode) {
  try {
    const raw = localStorage.getItem(getStorageKey(mode))
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function saveToStorage(mode, data) {
  try {
    localStorage.setItem(getStorageKey(mode), JSON.stringify(data))
  } catch {
    // localStorage full or unavailable — silently ignore
  }
}

function clearStorage(mode) {
  try {
    localStorage.removeItem(getStorageKey(mode))
  } catch {
    // silently ignore
  }
}

/**
 * Hook that persists artifact sync results to localStorage.
 * Results survive tab navigation but are cleared on new submission.
 *
 * Uses the React docs-approved pattern for adjusting state when a prop changes:
 * https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes
 *
 * @param {string} mode - Current mode ('extract', 'analyze', 'log_session')
 * @returns {{ results, setResults, clearResults }}
 */
export default function usePersistedResults(mode) {
  const [prevMode, setPrevMode] = useState(mode)
  const [results, setResultsInternal] = useState(() => loadFromStorage(mode))

  // When mode changes, load that mode's stored results (render-time state adjustment)
  if (prevMode !== mode) {
    setPrevMode(mode)
    setResultsInternal(loadFromStorage(mode))
  }

  const setResults = useCallback((data) => {
    setResultsInternal(data)
    if (data) {
      saveToStorage(mode, data)
    } else {
      clearStorage(mode)
    }
  }, [mode])

  const clearResults = useCallback(() => {
    setResultsInternal(null)
    clearStorage(mode)
  }, [mode])

  return { results, setResults, clearResults }
}
