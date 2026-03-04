/**
 * ReconciliationPanel — modal panel showing cross-section LPD impacts.
 *
 * Triggered from the Project Doc page. Calls the reconciliation API,
 * displays cross-section impacts grouped by type with color coding,
 * and provides navigation links to affected sections.
 */
import { useState, useEffect } from 'react'
import { reconcileLPD } from '../services/api'

const IMPACT_COLORS = {
  resolves: { bg: 'bg-green-50', border: 'border-green-200', badge: 'bg-green-100 text-green-700 border-green-200', label: 'Resolves' },
  contradicts: { bg: 'bg-red-50', border: 'border-red-200', badge: 'bg-red-100 text-red-700 border-red-200', label: 'Contradicts' },
  supersedes: { bg: 'bg-blue-50', border: 'border-blue-200', badge: 'bg-blue-100 text-blue-700 border-blue-200', label: 'Supersedes' },
  requires_update: { bg: 'bg-amber-50', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-700 border-amber-200', label: 'Requires Update' },
}

export default function ReconciliationPanel({ projectId = 'default', onClose, onNavigateToSection }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const res = await reconcileLPD(projectId)
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

  // Group impacts by type
  const grouped = {}
  if (result?.impacts) {
    for (const impact of result.impacts) {
      const type = impact.impact_type || 'requires_update'
      if (!grouped[type]) grouped[type] = []
      grouped[type].push(impact)
    }
  }

  const typeOrder = ['contradicts', 'requires_update', 'supersedes', 'resolves']

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">LPD Reconciliation</h3>
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
              <p className="text-sm text-gray-500">Analyzing cross-section relationships...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Summary */}
              <div className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3">
                <div>
                  <span className="text-xs text-gray-500">Sections Analyzed</span>
                  <p className="text-sm font-semibold text-gray-700">{result.sections_analyzed}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-gray-500">Impacts Found</span>
                  <p className="text-sm font-semibold text-gray-700">{result.impacts.length}</p>
                </div>
              </div>

              {/* Impacts by type */}
              {result.impacts.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-6">No cross-section impacts detected. Sections are consistent.</p>
              ) : (
                typeOrder.map(type => {
                  const impacts = grouped[type]
                  if (!impacts?.length) return null
                  const colors = IMPACT_COLORS[type] || IMPACT_COLORS.requires_update

                  return (
                    <div key={type} className="space-y-2">
                      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        {colors.label} ({impacts.length})
                      </h4>
                      {impacts.map((impact, i) => (
                        <div
                          key={i}
                          className={`border rounded-lg p-4 ${colors.bg} ${colors.border}`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-0.5 text-xs font-medium rounded border ${colors.badge}`}>
                              {impact.source_section}
                            </span>
                            <svg className="w-3 h-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                            <span className={`px-2 py-0.5 text-xs font-medium rounded border ${colors.badge}`}>
                              {impact.target_section}
                            </span>
                          </div>

                          <p className="text-sm text-gray-700">{impact.description}</p>

                          {(impact.source_excerpt || impact.target_excerpt) && (
                            <div className="mt-2 space-y-1">
                              {impact.source_excerpt && (
                                <p className="text-xs text-gray-500">
                                  <span className="font-medium">Source:</span> &ldquo;{impact.source_excerpt}&rdquo;
                                </p>
                              )}
                              {impact.target_excerpt && (
                                <p className="text-xs text-gray-500">
                                  <span className="font-medium">Target:</span> &ldquo;{impact.target_excerpt}&rdquo;
                                </p>
                              )}
                            </div>
                          )}

                          {impact.suggested_action && (
                            <p className="mt-2 text-xs text-gray-600 italic">
                              Suggested: {impact.suggested_action}
                            </p>
                          )}

                          {onNavigateToSection && (
                            <button
                              onClick={() => {
                                onNavigateToSection(impact.target_section)
                                onClose()
                              }}
                              className="mt-2 text-xs text-gray-500 hover:text-gray-700 underline"
                            >
                              Go to {impact.target_section}
                            </button>
                          )}
                        </div>
                      ))}
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
