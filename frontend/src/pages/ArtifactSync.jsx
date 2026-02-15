/**
 * Main Artifact Sync page — accepts user text, runs the LLM pipeline, and displays suggestion cards.
 */
import { useState } from 'react'
import TextInput from '../components/TextInput'
import SuggestionCard from '../components/SuggestionCard'
import { useToast } from '../components/ToastContext'
import { artifactSync, applySuggestionByType } from '../services/api'

/** Artifact Sync page — orchestrates text input, LLM analysis, and suggestion display. */
export default function ArtifactSync() {
  const [suggestions, setSuggestions] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [meta, setMeta] = useState(null) // input_type, pii_detected, session_id
  const toast = useToast()

  async function handleApply(suggestion) {
    await applySuggestionByType(suggestion)
  }

  async function handleSubmit(text) {
    setIsLoading(true)
    setError(null)
    setSuggestions([])
    setMeta(null)

    try {
      const result = await artifactSync(text)
      setSuggestions(result.suggestions)
      setMeta({
        inputType: result.input_type,
        piiDetected: result.pii_detected,
        sessionId: result.session_id,
      })

      if (result.suggestions.length === 0) {
        toast.info('No artifact updates found in this text')
      } else {
        toast.success(`Found ${result.suggestions.length} suggestion${result.suggestions.length > 1 ? 's' : ''}`)
      }
    } catch (err) {
      setError(err.message)
      toast.error('Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Artifact Sync</h2>
        <p className="text-sm text-gray-500">
          Paste meeting notes, transcripts, or project updates. VPMA will suggest updates to your PM artifacts.
        </p>
      </div>

      <TextInput onSubmit={handleSubmit} isLoading={isLoading} />

      {/* Error display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Meta info bar */}
      {meta && (
        <div className="flex items-center gap-4 text-xs text-gray-400 border-t border-gray-100 pt-3">
          <span className="bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
            {meta.inputType.replaceAll('_', ' ')}
          </span>
          {meta.piiDetected > 0 && (
            <span className="flex items-center gap-1 text-green-600">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              {meta.piiDetected} PII item{meta.piiDetected > 1 ? 's' : ''} anonymized
            </span>
          )}
          {meta.piiDetected === 0 && (
            <span className="text-gray-400">No PII detected</span>
          )}
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700">
            Suggestions ({suggestions.length})
          </h3>
          {suggestions.map((s, i) => (
            <SuggestionCard key={i} suggestion={s} onApply={handleApply} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && suggestions.length === 0 && !meta && (
        <div className="text-center py-12">
          <div className="text-gray-300 text-4xl mb-3">&#9998;</div>
          <p className="text-sm text-gray-400">No suggestions yet. Paste some text above to get started.</p>
        </div>
      )}
    </div>
  )
}
