/**
 * Main Artifact Sync page — accepts user text, runs the LLM pipeline,
 * and displays either suggestion cards (Extract mode) or analysis feedback (Analyze mode).
 */
import { useState } from 'react'
import TextInput from '../components/TextInput'
import SuggestionCard from '../components/SuggestionCard'
import DocumentDraftCard from '../components/DocumentDraftCard'
import AnalysisCard from '../components/AnalysisCard'
import LogSessionCard from '../components/LogSessionCard'
import { useToast } from '../components/ToastContext'
import { artifactSync, applySuggestionByType, appendToLPDSection } from '../services/api'

const SUBTITLES = {
  extract: 'Paste meeting notes, transcripts, or project updates. VPMA will suggest updates to your PM artifacts.',
  analyze: 'Paste a draft or document. VPMA will give you feedback, observations, and recommendations.',
  log_session: 'Paste session conclusions or decisions. VPMA will update your project hub and suggest artifact entries.',
}

/** Artifact Sync page — orchestrates text input, LLM analysis, and suggestion/analysis display. */
export default function ArtifactSync() {
  const [mode, setMode] = useState('extract')
  const [suggestions, setSuggestions] = useState([])
  const [analysis, setAnalysis] = useState(null) // { summary, items }
  const [logSession, setLogSession] = useState(null) // { summary, lpdUpdates, suggestions }
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [meta, setMeta] = useState(null) // input_type, pii_detected, session_id, mode
  const toast = useToast()

  async function handleApply(suggestion) {
    await applySuggestionByType(suggestion)
  }

  async function handleApplyAnyway(update) {
    await appendToLPDSection('default', update.section, update.content)
  }

  async function handleApplyAll(suggestionsToApply) {
    for (const suggestion of suggestionsToApply) {
      await applySuggestionByType(suggestion)
    }
  }

  function handleModeChange(newMode) {
    setMode(newMode)
    setSuggestions([])
    setAnalysis(null)
    setLogSession(null)
    setError(null)
    setMeta(null)
  }

  async function handleSubmit(text) {
    setIsLoading(true)
    setError(null)
    setSuggestions([])
    setAnalysis(null)
    setLogSession(null)
    setMeta(null)

    try {
      const result = await artifactSync(text, 'default', mode)

      if (result.mode === 'log_session') {
        setLogSession({
          summary: result.session_summary,
          lpdUpdates: result.lpd_updates || [],
          suggestions: result.suggestions || [],
          contentGateActive: result.content_gate_active !== false,
        })
        const updateCount = (result.lpd_updates || []).length
        const suggestionCount = (result.suggestions || []).length
        if (updateCount === 0 && suggestionCount === 0) {
          toast.info('No updates extracted from this session')
        } else {
          toast.success(`Logged: ${updateCount} LPD update${updateCount !== 1 ? 's' : ''}, ${suggestionCount} suggestion${suggestionCount !== 1 ? 's' : ''}`)
        }
      } else if (result.mode === 'analyze') {
        setAnalysis({
          summary: result.analysis_summary,
          items: result.analysis || [],
        })
        if (!result.analysis || result.analysis.length === 0) {
          toast.info('No analysis generated for this text')
        } else {
          toast.success(`Generated ${result.analysis.length} observation${result.analysis.length > 1 ? 's' : ''}`)
        }
      } else {
        setSuggestions(result.suggestions)
        if (result.suggestions.length === 0) {
          toast.info('No artifact updates found in this text')
        } else {
          toast.success(`Found ${result.suggestions.length} suggestion${result.suggestions.length > 1 ? 's' : ''}`)
        }
      }

      setMeta({
        inputType: result.input_type,
        piiDetected: result.pii_detected,
        sessionId: result.session_id,
        mode: result.mode,
      })
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
          {SUBTITLES[mode] || SUBTITLES.extract}
        </p>
      </div>

      <TextInput onSubmit={handleSubmit} isLoading={isLoading} mode={mode} onModeChange={handleModeChange} />

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
          {meta.mode && (
            <span className="bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
              {meta.mode === 'analyze' ? 'analyze' : meta.mode === 'log_session' ? 'log session' : 'extract'}
            </span>
          )}
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

      {/* Extract mode: Suggestions grouped by artifact type */}
      {mode === 'extract' && suggestions.length > 0 && (() => {
        const groups = {}
        const order = ['RAID Log', 'Status Report', 'Meeting Notes']
        suggestions.forEach((s) => {
          const type = s.artifact_type
          if (!groups[type]) groups[type] = []
          groups[type].push(s)
        })
        const sortedTypes = Object.keys(groups).sort(
          (a, b) => (order.indexOf(a) === -1 ? 999 : order.indexOf(a))
                   - (order.indexOf(b) === -1 ? 999 : order.indexOf(b))
        )
        return (
          <div className="space-y-6">
            <h3 className="text-sm font-medium text-gray-700">
              Suggestions ({suggestions.length})
            </h3>
            {sortedTypes.map((type) => (
              <div key={type} className="space-y-3">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-100 pb-1">
                  {type} ({groups[type].length})
                </h4>
                {type === 'RAID Log' ? (
                  groups[type].map((s, i) => (
                    <SuggestionCard key={`${type}-${i}`} suggestion={s} onApply={handleApply} />
                  ))
                ) : (
                  <DocumentDraftCard
                    artifactType={type}
                    suggestions={groups[type]}
                    onApplyAll={handleApplyAll}
                  />
                )}
              </div>
            ))}
          </div>
        )
      })()}

      {/* Analyze mode: Analysis feedback */}
      {mode === 'analyze' && analysis && analysis.items.length > 0 && (
        <AnalysisCard summary={analysis.summary} items={analysis.items} />
      )}

      {/* Log Session mode: Summary + LPD updates + artifact suggestions */}
      {mode === 'log_session' && logSession && (
        <LogSessionCard
          sessionSummary={logSession.summary}
          lpdUpdates={logSession.lpdUpdates}
          suggestions={logSession.suggestions}
          contentGateActive={logSession.contentGateActive}
          onApply={handleApply}
          onApplyAnyway={handleApplyAnyway}
        />
      )}

      {/* Empty state */}
      {!isLoading && !error && suggestions.length === 0 && !analysis && !logSession && !meta && (
        <div className="text-center py-12">
          <div className="text-gray-300 text-4xl mb-3">&#9998;</div>
          <p className="text-sm text-gray-400">No suggestions yet. Paste some text above to get started.</p>
        </div>
      )}
    </div>
  )
}
