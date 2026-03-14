/**
 * Process page — accepts user text, runs the LLM pipeline,
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
import usePersistedResults from '../hooks/usePersistedResults'

const SUBTITLES = {
  extract: 'Paste meeting notes, transcripts, or project updates. VPMA will suggest updates to your PM artifacts.',
  analyze: 'Paste a draft or document. VPMA will give you feedback, observations, and recommendations.',
  log_session: 'Paste session conclusions or decisions. VPMA will update your knowledge base and suggest artifact entries.',
}

/** Process page — orchestrates text input, LLM analysis, and suggestion/analysis display. */
export default function ArtifactSync() {
  const [mode, setMode] = useState('extract')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const toast = useToast()
  const { results, setResults, clearResults } = usePersistedResults(mode)

  // Derive display state from persisted results
  const suggestions = results?.suggestions || []
  const analysis = results?.analysis || null
  const logSession = results?.logSession || null
  const meta = results?.meta || null

  function handleDismiss(suggestion) {
    if (!results?.suggestions) return
    const remaining = results.suggestions.filter(s => s !== suggestion)
    if (remaining.length === 0) {
      clearResults()
    } else {
      setResults({ ...results, suggestions: remaining })
    }
  }

  async function handleApply(suggestion) {
    const result = await applySuggestionByType(suggestion)
    return result
  }

  async function handleApplyAnyway(update) {
    await appendToLPDSection('default', update.section, update.content)
  }

  async function handleApplyAll(suggestionsToApply) {
    const results = []
    for (const suggestion of suggestionsToApply) {
      const result = await applySuggestionByType(suggestion)
      results.push(result)
    }
    return results
  }

  function handleModeChange(newMode) {
    setMode(newMode)
    setError(null)
    // Don't clear results — usePersistedResults loads each mode's stored results
  }

  function formatResultsAsMarkdown() {
    if (mode === 'extract' && suggestions.length > 0) {
      const groups = {}
      suggestions.forEach((s) => {
        if (!groups[s.artifact_type]) groups[s.artifact_type] = []
        groups[s.artifact_type].push(s)
      })
      let md = '# Process — Extract Results\n\n'
      for (const [type, items] of Object.entries(groups)) {
        md += `## ${type}\n\n`
        for (const s of items) {
          md += `### ${s.section}\n\n${s.proposed_text}\n\n`
          if (s.reasoning) md += `> ${s.reasoning}\n\n`
        }
      }
      return md
    }
    if (mode === 'analyze' && analysis?.items?.length > 0) {
      let md = '# Process — Analysis Results\n\n'
      if (analysis.summary) md += `${analysis.summary}\n\n`
      for (const item of analysis.items) {
        md += `## ${item.category || 'Observation'}\n\n${item.observation}\n\n`
        if (item.recommendation) md += `**Recommendation:** ${item.recommendation}\n\n`
      }
      return md
    }
    if (mode === 'log_session' && logSession) {
      let md = '# Process — Log Session Results\n\n'
      if (logSession.summary) md += `## Summary\n\n${logSession.summary}\n\n`
      if (logSession.lpdUpdates?.length > 0) {
        md += '## Knowledge Base Updates\n\n'
        for (const u of logSession.lpdUpdates) {
          md += `### ${u.section}\n\n${u.content}\n\n`
        }
      }
      if (logSession.suggestions?.length > 0) {
        md += '## Artifact Suggestions\n\n'
        for (const s of logSession.suggestions) {
          md += `### ${s.artifact_type} — ${s.section}\n\n${s.proposed_text}\n\n`
        }
      }
      return md
    }
    return null
  }

  async function handleExportResults() {
    const md = formatResultsAsMarkdown()
    if (!md) return

    // Download as file
    const blob = new Blob([md], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `artifact-sync-${mode}-results.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('Results exported')
  }

  async function handleCopyResults() {
    const md = formatResultsAsMarkdown()
    if (!md) return

    try {
      await navigator.clipboard.writeText(md)
      toast.success('Results copied to clipboard')
    } catch {
      toast.error('Failed to copy')
    }
  }

  async function handleSubmit(text) {
    setIsLoading(true)
    setError(null)
    clearResults() // Clear previous results for this mode on new submission

    try {
      const result = await artifactSync(text, 'default', mode)
      const newMeta = {
        inputType: result.input_type,
        piiDetected: result.pii_detected,
        sessionId: result.session_id,
        mode: result.mode,
      }

      if (result.mode === 'log_session') {
        const logSessionData = {
          summary: result.session_summary,
          lpdUpdates: result.lpd_updates || [],
          suggestions: result.suggestions || [],
          contentGateActive: result.content_gate_active !== false,
        }
        setResults({ logSession: logSessionData, meta: newMeta })
        const updateCount = (result.lpd_updates || []).length
        const suggestionCount = (result.suggestions || []).length
        if (updateCount === 0 && suggestionCount === 0) {
          toast.info('No updates extracted from this session')
        } else {
          toast.success(`Logged: ${updateCount} LPD update${updateCount !== 1 ? 's' : ''}, ${suggestionCount} suggestion${suggestionCount !== 1 ? 's' : ''}`)
        }
      } else if (result.mode === 'analyze') {
        const analysisData = {
          summary: result.analysis_summary,
          items: result.analysis || [],
        }
        setResults({ analysis: analysisData, meta: newMeta })
        if (!result.analysis || result.analysis.length === 0) {
          toast.info('No analysis generated for this text')
        } else {
          toast.success(`Generated ${result.analysis.length} observation${result.analysis.length > 1 ? 's' : ''}`)
        }
      } else {
        setResults({ suggestions: result.suggestions, meta: newMeta })
        if (result.suggestions.length === 0) {
          toast.info('No artifact updates found in this text')
        } else {
          toast.success(`Found ${result.suggestions.length} suggestion${result.suggestions.length > 1 ? 's' : ''}`)
        }
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
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Process</h2>
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
        <div className="flex items-center gap-4 text-xs text-gray-400 border-t border-gray-100 pt-3 flex-wrap">
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
          {formatResultsAsMarkdown() && (
            <span className="ml-auto flex gap-2">
              <button onClick={handleCopyResults} className="text-gray-400 hover:text-gray-600 transition-colors">
                Copy Results
              </button>
              <button onClick={handleExportResults} className="text-gray-400 hover:text-gray-600 transition-colors">
                Export .md
              </button>
              <button onClick={() => { clearResults(); toast.success('Results cleared') }} className="text-red-400 hover:text-red-600 transition-colors">
                Clear
              </button>
            </span>
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
                    <SuggestionCard key={`${type}-${i}`} suggestion={s} onApply={handleApply} onDismiss={handleDismiss} />
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
        <div className="text-center py-12 space-y-2">
          <div className="text-gray-300 text-4xl mb-3">&#9998;</div>
          <p className="text-sm text-gray-400">No suggestions yet. Paste some text above to get started.</p>
          <p className="text-xs text-gray-400">Tip: populate your Knowledge Base first — the AI gives better suggestions with project context.</p>
        </div>
      )}
    </div>
  )
}
