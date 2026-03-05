/**
 * Displays a single LLM-generated suggestion card with expand/collapse, copy, and apply actions.
 */
import { useState } from 'react'
import { useToast } from './ToastContext'

const TYPE_COLORS = {
  'RAID Log': 'bg-amber-50 text-amber-700 border-amber-200',
  'Status Report': 'bg-blue-50 text-blue-700 border-blue-200',
  'Meeting Notes': 'bg-green-50 text-green-700 border-green-200',
}

const CHANGE_LABELS = {
  'add': 'Add',
  'update': 'Update',
}

/**
 * @param {Object} props
 * @param {Object} props.suggestion - Suggestion object from the artifact sync pipeline
 * @param {string} props.suggestion.artifact_type - 'RAID Log', 'Status Report', or 'Meeting Notes'
 * @param {string} props.suggestion.change_type - 'add' or 'update'
 * @param {string} props.suggestion.section - Target section within the artifact
 * @param {string} props.suggestion.proposed_text - The suggested content to add/update
 * @param {number} props.suggestion.confidence - Confidence score (0.0-1.0)
 * @param {string} props.suggestion.reasoning - Why this suggestion was generated
 * @param {function} props.onApply - Callback when user clicks Apply (receives suggestion)
 */
export default function SuggestionCard({ suggestion, onApply }) {
  const [expanded, setExpanded] = useState(false)
  const [applied, setApplied] = useState(false)
  const [copied, setCopied] = useState(false)
  const toast = useToast()

  const colorClass = TYPE_COLORS[suggestion.artifact_type] || 'bg-gray-50 text-gray-700 border-gray-200'

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(suggestion.proposed_text)
      setCopied(true)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy to clipboard')
    }
  }

  async function handleApply() {
    try {
      const result = onApply ? await onApply(suggestion) : null
      setApplied(true)
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

  return (
    <div className={`border rounded-lg p-4 ${applied ? 'opacity-60' : ''}`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`px-2 py-0.5 text-xs font-medium rounded border ${colorClass}`}>
            {suggestion.artifact_type}
          </span>
          <span className="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-600">
            {CHANGE_LABELS[suggestion.change_type] || suggestion.change_type}
          </span>
          <span className="text-xs text-gray-400">
            {suggestion.section}
          </span>
        </div>
        <span className="text-xs text-gray-400 whitespace-nowrap">
          {Math.round(suggestion.confidence * 100)}% confidence
        </span>
      </div>

      {/* Reasoning */}
      <p className="mt-2 text-sm text-gray-600">{suggestion.reasoning}</p>

      {/* Proposed text (expandable) */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-2 text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
      >
        <svg className={`w-3 h-3 transition-transform ${expanded ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        {expanded ? 'Hide preview' : 'Show preview'}
      </button>

      {expanded && (
        <pre className="mt-2 p-3 bg-gray-50 rounded text-xs text-gray-700 whitespace-pre-wrap font-mono overflow-x-auto">
          {suggestion.proposed_text}
        </pre>
      )}

      {/* Actions */}
      <div className="mt-3 flex gap-2">
        <button
          onClick={handleCopy}
          disabled={copied}
          className="px-3 py-1.5 text-xs font-medium rounded bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
        >
          {copied ? 'Copied' : 'Copy'}
        </button>
        <button
          onClick={handleApply}
          disabled={applied}
          className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:text-gray-300 disabled:border-gray-200 transition-colors"
        >
          {applied ? 'Applied' : 'Apply'}
        </button>
      </div>
    </div>
  )
}
