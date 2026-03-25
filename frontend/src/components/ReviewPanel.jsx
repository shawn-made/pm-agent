/**
 * ReviewPanel — modal panel showing Skeptical Reviewer findings.
 *
 * Triggered from the Audit page. Calls the skeptical review API,
 * displays evidence-backed findings grouped by category with severity badges.
 */
import { useState, useEffect } from 'react'
import { useToast } from './ToastContext'
import { skepticalReview } from '../services/api'

const SEVERITY_COLORS = {
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-green-100 text-green-700 border-green-200',
}

const CATEGORY_LABELS = {
  contradiction: { label: 'Contradiction', icon: '⚡', color: 'text-red-600' },
  blind_spot: { label: 'Blind Spot', icon: '👁', color: 'text-amber-600' },
  timeline_risk: { label: 'Timeline Risk', icon: '⏱', color: 'text-orange-600' },
  underestimated_risk: { label: 'Underestimated Risk', icon: '📉', color: 'text-purple-600' },
}

export default function ReviewPanel({ projectId = 'default', onClose }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [dismissedFindings, setDismissedFindings] = useState(new Set())
  const [expandedFindings, setExpandedFindings] = useState(new Set())
  const toast = useToast()

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const res = await skepticalReview(projectId)
        if (!cancelled) setResult(res)
      } catch (err) {
        if (!cancelled) setError(err.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    run()
    return () => { cancelled = true }
  }, [projectId])

  function handleDismiss(index) {
    setDismissedFindings(prev => new Set([...prev, index]))
  }

  function toggleExpand(index) {
    setExpandedFindings(prev => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })
  }

  function handleCopyFinding(finding) {
    const text = `**${finding.title}** (${finding.severity})\n\n${finding.description}\n\nEvidence: ${finding.evidence}\n\nRecommendation: ${finding.recommendation}`
    navigator.clipboard.writeText(text)
      .then(() => toast.success('Finding copied to clipboard'))
      .catch(() => toast.error('Failed to copy'))
  }

  // Group findings by category
  const grouped = {}
  if (result?.findings) {
    result.findings.forEach((f, i) => {
      if (!dismissedFindings.has(i)) {
        if (!grouped[f.category]) grouped[f.category] = []
        grouped[f.category].push({ ...f, _index: i })
      }
    })
  }

  const categoryOrder = ['contradiction', 'blind_spot', 'timeline_risk', 'underestimated_risk']
  const activeCount = result ? result.findings.length - dismissedFindings.size : 0

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Pressure Test</h3>
            <p className="text-xs text-gray-400">Evidence-based critical review of your project</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-3" />
              <p className="text-sm text-gray-500">Cross-referencing your project documents...</p>
              <p className="text-xs text-gray-400 mt-1">Checking for contradictions, blind spots, and risks</p>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Summary bar */}
              <div className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3">
                <div>
                  <span className="text-xs text-gray-500">Findings</span>
                  <p className="text-sm font-semibold text-gray-700">{activeCount}</p>
                </div>
                <div className="text-center">
                  <span className="text-xs text-gray-500">Sections Analyzed</span>
                  <p className="text-sm font-semibold text-gray-700">{result.sections_analyzed}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-gray-500">Artifacts</span>
                  <p className="text-sm font-semibold text-gray-700">{result.artifacts_analyzed}</p>
                </div>
              </div>

              {/* Findings grouped by category */}
              {result.findings.length === 0 ? (
                <div className="text-center py-6 space-y-2">
                  <p className="text-sm text-gray-500">No issues found.</p>
                  <p className="text-xs text-gray-400">Your project documents appear consistent. Add more content to your Knowledge Base and artifacts for deeper analysis.</p>
                </div>
              ) : (
                categoryOrder.map(category => {
                  const items = grouped[category]
                  if (!items || items.length === 0) return null
                  const catInfo = CATEGORY_LABELS[category] || { label: category, icon: '?', color: 'text-gray-600' }

                  return (
                    <div key={category}>
                      <h4 className={`text-xs font-semibold uppercase tracking-wide ${catInfo.color} mb-2`}>
                        {catInfo.icon} {catInfo.label} ({items.length})
                      </h4>
                      <div className="space-y-3">
                        {items.map(finding => {
                          const i = finding._index
                          const isExpanded = expandedFindings.has(i)
                          const severityClass = SEVERITY_COLORS[finding.severity] || SEVERITY_COLORS.low

                          return (
                            <div
                              key={i}
                              className="border rounded-lg p-4 hover:border-gray-300 transition-colors"
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className={`px-2 py-0.5 text-xs font-medium rounded border ${severityClass}`}>
                                      {finding.severity}
                                    </span>
                                  </div>
                                  <p className="text-sm font-medium text-gray-900">{finding.title}</p>
                                </div>
                                <button
                                  onClick={() => toggleExpand(i)}
                                  className="text-gray-400 hover:text-gray-600 text-xs flex-shrink-0"
                                >
                                  {isExpanded ? 'Collapse' : 'Details'}
                                </button>
                              </div>

                              <p className="mt-1 text-sm text-gray-600">{finding.description}</p>

                              {isExpanded && (
                                <div className="mt-3 space-y-2">
                                  <div className="bg-gray-50 rounded p-3">
                                    <p className="text-xs font-medium text-gray-500 mb-1">Evidence</p>
                                    <p className="text-sm text-gray-700">{finding.evidence}</p>
                                  </div>
                                  <div className="bg-blue-50 rounded p-3">
                                    <p className="text-xs font-medium text-blue-600 mb-1">Recommendation</p>
                                    <p className="text-sm text-gray-700">{finding.recommendation}</p>
                                  </div>
                                </div>
                              )}

                              <div className="mt-3 flex gap-2">
                                <button
                                  onClick={() => handleCopyFinding(finding)}
                                  className="px-3 py-1.5 text-xs font-medium rounded bg-gray-900 text-white hover:bg-gray-800 transition-colors"
                                >
                                  Copy Finding
                                </button>
                                <button
                                  onClick={() => handleDismiss(i)}
                                  className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors"
                                >
                                  Dismiss
                                </button>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
