/**
 * LogSessionCard — displays results from log_session mode.
 * Shows: session summary, LPD updates (grouped by classification), artifact suggestions.
 *
 * Content gate classifications:
 * - new/update → auto-applied (green checkmark)
 * - duplicate → skipped (gray collapsed note)
 * - contradiction → needs review (amber warning with "Apply Anyway" button)
 * - no classification → treated as applied (backward compat / gate inactive)
 */
import { useState } from 'react'
import { useToast } from './ToastContext'

const SECTION_COLORS = {
  'Risks': 'text-red-700 bg-red-50 border-red-200',
  'Decisions': 'text-purple-700 bg-purple-50 border-purple-200',
  'Stakeholders': 'text-blue-700 bg-blue-50 border-blue-200',
  'Open Questions': 'text-amber-700 bg-amber-50 border-amber-200',
  'Overview': 'text-green-700 bg-green-50 border-green-200',
  'Timeline & Milestones': 'text-indigo-700 bg-indigo-50 border-indigo-200',
}

function classifyUpdate(update) {
  return update.classification?.classification || null
}

export default function LogSessionCard({ sessionSummary, lpdUpdates, suggestions, onApply, onApplyAnyway }) {
  const toast = useToast()
  const [appliedSuggestions, setAppliedSuggestions] = useState(new Set())
  const [appliedContradictions, setAppliedContradictions] = useState(new Set())
  const [showDuplicates, setShowDuplicates] = useState(false)

  // Partition LPD updates by classification
  const applied = []
  const duplicates = []
  const contradictions = []

  lpdUpdates?.forEach((update, i) => {
    const cls = classifyUpdate(update)
    if (cls === 'duplicate') {
      duplicates.push({ update, index: i })
    } else if (cls === 'contradiction') {
      contradictions.push({ update, index: i })
    } else {
      // new, update, or no classification (backward compat)
      applied.push({ update, index: i })
    }
  })

  async function handleApplySuggestion(suggestion, index) {
    try {
      const result = await onApply(suggestion)
      setAppliedSuggestions(prev => new Set([...prev, index]))
      if (result?.status === 'duplicate') {
        toast.info('Already applied (duplicate)')
      } else if (result?.lpd_updated && result?.lpd_change) {
        toast.success(`Applied to artifact + KB "${result.lpd_change.section}"`)
      } else if (result?.lpd_updated) {
        toast.success('Applied to artifact + knowledge base')
      } else {
        toast.success('Applied to artifact')
      }
    } catch {
      toast.error('Failed to apply suggestion')
    }
  }

  async function handleApplyContradiction(update, index) {
    try {
      await onApplyAnyway(update)
      setAppliedContradictions(prev => new Set([...prev, index]))
      toast.success(`Applied to ${update.section}`)
    } catch {
      toast.error('Failed to apply update')
    }
  }

  function handleCopyAll() {
    const lines = []
    if (sessionSummary) {
      lines.push(`## Session Summary\n${sessionSummary}\n`)
    }
    if (applied.length > 0) {
      lines.push('## LPD Updates Applied')
      applied.forEach(({ update }) => {
        lines.push(`\n### ${update.section}\n${update.content}`)
      })
      lines.push('')
    }
    if (contradictions.length > 0) {
      lines.push('## Contradictions (Needs Review)')
      contradictions.forEach(({ update }) => {
        lines.push(`\n### ${update.section}\n${update.content}`)
        if (update.classification?.reason) {
          lines.push(`> ${update.classification.reason}`)
        }
      })
      lines.push('')
    }
    if (suggestions?.length > 0) {
      lines.push('## Artifact Suggestions')
      suggestions.forEach(s => {
        lines.push(`\n**${s.artifact_type} — ${s.section}**\n${s.proposed_text}`)
      })
    }
    navigator.clipboard.writeText(lines.join('\n'))
    toast.success('Copied session log')
  }

  const hasContent = sessionSummary || (lpdUpdates?.length > 0) || (suggestions?.length > 0)

  return (
    <div className="space-y-4">
      {/* Session Summary */}
      {sessionSummary && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Session Summary</h4>
          <p className="text-sm text-gray-700">{sessionSummary}</p>
        </div>
      )}

      {/* LPD Updates Applied (new + update + unclassified) */}
      {applied.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide flex items-center gap-2">
            <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            LPD Updates Applied ({applied.length})
          </h4>
          {applied.map(({ update, index }) => {
            const colors = SECTION_COLORS[update.section] || 'text-gray-700 bg-gray-50 border-gray-200'
            return (
              <div key={index} className={`border rounded-lg p-3 ${colors}`}>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold uppercase">{update.section}</span>
                  {update.classification?.classification === 'update' && (
                    <span className="text-xs opacity-60">(extends existing)</span>
                  )}
                </div>
                <pre className="mt-1 text-sm whitespace-pre-wrap font-sans">{update.content}</pre>
              </div>
            )
          })}
        </div>
      )}

      {/* Duplicates Skipped */}
      {duplicates.length > 0 && (
        <div className="text-xs text-gray-400">
          <button
            onClick={() => setShowDuplicates(!showDuplicates)}
            className="hover:text-gray-600 transition-colors"
          >
            {duplicates.length} duplicate{duplicates.length !== 1 ? 's' : ''} skipped
            <span className="ml-1">{showDuplicates ? '\u25B4' : '\u25BE'}</span>
          </button>
          {showDuplicates && (
            <div className="mt-2 space-y-1">
              {duplicates.map(({ update, index }) => (
                <div key={index} className="bg-gray-50 border border-gray-100 rounded p-2 text-gray-500">
                  <span className="font-semibold uppercase text-xs">{update.section}</span>
                  <pre className="mt-1 text-xs whitespace-pre-wrap font-sans opacity-70">{update.content}</pre>
                  {update.classification?.reason && (
                    <p className="text-xs text-gray-400 mt-1 italic">{update.classification.reason}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Contradictions — Needs Review */}
      {contradictions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-amber-600 uppercase tracking-wide flex items-center gap-2">
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            Needs Review ({contradictions.length})
          </h4>
          {contradictions.map(({ update, index }) => (
            <div key={index} className={`border border-amber-200 bg-amber-50 rounded-lg p-3 ${appliedContradictions.has(index) ? 'opacity-50' : ''}`}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-amber-700 uppercase">{update.section}</span>
                <button
                  onClick={() => handleApplyContradiction(update, index)}
                  disabled={appliedContradictions.has(index)}
                  className="text-xs px-2 py-1 bg-amber-600 text-white rounded hover:bg-amber-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {appliedContradictions.has(index) ? 'Applied' : 'Apply Anyway'}
                </button>
              </div>
              <pre className="text-sm text-amber-800 whitespace-pre-wrap font-sans">{update.content}</pre>
              {update.classification?.reason && (
                <p className="text-xs text-amber-600 mt-1 italic">{update.classification.reason}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Artifact Suggestions for Review */}
      {suggestions?.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Artifact Suggestions ({suggestions.length})
          </h4>
          {suggestions.map((s, i) => (
            <div key={i} className={`bg-white border border-gray-200 rounded-lg p-3 ${appliedSuggestions.has(i) ? 'opacity-50' : ''}`}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-gray-600">{s.artifact_type}</span>
                  <span className="text-xs text-gray-400">·</span>
                  <span className="text-xs text-gray-500">{s.section}</span>
                </div>
                <button
                  onClick={() => handleApplySuggestion(s, i)}
                  disabled={appliedSuggestions.has(i)}
                  className="text-xs px-2 py-1 bg-gray-900 text-white rounded hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {appliedSuggestions.has(i) ? 'Applied' : 'Apply'}
                </button>
              </div>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">{s.proposed_text}</pre>
              {s.reasoning && (
                <p className="text-xs text-gray-400 mt-1 italic">{s.reasoning}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Copy All */}
      {hasContent && (
        <div className="flex justify-end">
          <button
            onClick={handleCopyAll}
            className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Copy All
          </button>
        </div>
      )}
    </div>
  )
}
