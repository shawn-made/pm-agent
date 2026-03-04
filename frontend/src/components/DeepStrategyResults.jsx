/**
 * Deep Strategy analysis results display.
 * Shows summary, inconsistencies, proposed updates with diff view, and validation checks.
 */
import { useState } from 'react'
import { useToast } from './ToastContext'

const SEVERITY_COLORS = {
  high: 'bg-red-50 text-red-700 border-red-200',
  medium: 'bg-amber-50 text-amber-700 border-amber-200',
  low: 'bg-blue-50 text-blue-700 border-blue-200',
}

const TABS = ['Summary', 'Inconsistencies', 'Proposed Updates', 'Validation']

/**
 * @param {Object} props
 * @param {Object} props.results - DeepStrategyResponse from the API
 * @param {function} props.onApply - Callback with selected updates array
 * @param {boolean} props.isApplying - Whether apply is in progress
 */
export default function DeepStrategyResults({ results, onApply, isApplying = false }) {
  const [activeTab, setActiveTab] = useState('Summary')
  const [selectedUpdates, setSelectedUpdates] = useState({})
  const [expandedItems, setExpandedItems] = useState({})
  const toast = useToast()

  if (!results) return null

  const { summary, inconsistencies, proposed_updates, validation_checks, dependency_graph, pii_detected } = results

  function toggleUpdate(index) {
    setSelectedUpdates(prev => ({ ...prev, [index]: !prev[index] }))
  }

  function selectAll() {
    const all = {}
    proposed_updates.forEach((_, i) => { all[i] = true })
    setSelectedUpdates(all)
  }

  function deselectAll() {
    setSelectedUpdates({})
  }

  function toggleExpand(key) {
    setExpandedItems(prev => ({ ...prev, [key]: !prev[key] }))
  }

  function handleApply() {
    const selected = proposed_updates.filter((_, i) => selectedUpdates[i])
    if (selected.length === 0) {
      toast.info('No updates selected')
      return
    }
    onApply(selected)
  }

  const selectedCount = Object.values(selectedUpdates).filter(Boolean).length

  return (
    <div className="space-y-4">
      {/* Tab navigation */}
      <div className="flex gap-1 border-b border-gray-200">
        {TABS.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-gray-900 text-gray-900'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab}
            {tab === 'Inconsistencies' && inconsistencies.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-red-100 text-red-600">
                {inconsistencies.length}
              </span>
            )}
            {tab === 'Proposed Updates' && proposed_updates.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                {proposed_updates.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Summary tab */}
      {activeTab === 'Summary' && (
        <div className="space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="border rounded-lg p-3 text-center">
              <p className="text-2xl font-semibold text-gray-900">{summary.artifacts_analyzed}</p>
              <p className="text-xs text-gray-500">Artifacts</p>
            </div>
            <div className="border rounded-lg p-3 text-center">
              <p className={`text-2xl font-semibold ${summary.inconsistencies_found > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {summary.inconsistencies_found}
              </p>
              <p className="text-xs text-gray-500">Inconsistencies</p>
            </div>
            <div className="border rounded-lg p-3 text-center">
              <p className="text-2xl font-semibold text-gray-900">{summary.updates_proposed}</p>
              <p className="text-xs text-gray-500">Updates Proposed</p>
            </div>
            <div className="border rounded-lg p-3 text-center">
              <p className={`text-2xl font-semibold ${summary.consistency_score >= 0.8 ? 'text-green-600' : summary.consistency_score >= 0.5 ? 'text-amber-600' : 'text-red-600'}`}>
                {Math.round(summary.consistency_score * 100)}%
              </p>
              <p className="text-xs text-gray-500">Consistency</p>
            </div>
          </div>

          {/* Dependency graph summary */}
          {dependency_graph?.summary && (
            <div className="border rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Dependency Overview</h4>
              <p className="text-sm text-gray-600">{dependency_graph.summary}</p>
              {dependency_graph.edges?.length > 0 && (
                <div className="mt-3 space-y-1">
                  {dependency_graph.edges.map((edge, i) => (
                    <p key={i} className="text-xs text-gray-500">
                      <span className="font-medium text-gray-700">{edge.source}</span>
                      {' → '}
                      <span className="font-medium text-gray-700">{edge.target}</span>
                      <span className="text-gray-400 ml-1">({edge.relationship})</span>
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PII info */}
          {pii_detected > 0 && (
            <p className="text-xs text-green-600 flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              {pii_detected} PII item{pii_detected > 1 ? 's' : ''} anonymized during analysis
            </p>
          )}
        </div>
      )}

      {/* Inconsistencies tab */}
      {activeTab === 'Inconsistencies' && (
        <div className="space-y-3">
          {inconsistencies.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">No inconsistencies detected.</p>
          ) : (
            inconsistencies.map((inc, i) => (
              <div key={i} className={`border rounded-lg p-4 ${SEVERITY_COLORS[inc.severity] || ''}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className={`px-2 py-0.5 text-xs font-medium rounded border ${SEVERITY_COLORS[inc.severity] || 'bg-gray-50 text-gray-600 border-gray-200'}`}>
                      {inc.severity}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      {inc.source_artifact} → {inc.target_artifact}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">{inc.id}</span>
                </div>
                <p className="mt-2 text-sm text-gray-800">{inc.description}</p>

                <button
                  onClick={() => toggleExpand(`inc-${i}`)}
                  className="mt-2 text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                >
                  <svg className={`w-3 h-3 transition-transform ${expandedItems[`inc-${i}`] ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  {expandedItems[`inc-${i}`] ? 'Hide excerpts' : 'Show excerpts'}
                </button>

                {expandedItems[`inc-${i}`] && (
                  <div className="mt-2 grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Source ({inc.source_artifact})</p>
                      <pre className="p-2 bg-white/50 rounded text-xs font-mono whitespace-pre-wrap">{inc.source_excerpt}</pre>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Target ({inc.target_artifact})</p>
                      <pre className="p-2 bg-white/50 rounded text-xs font-mono whitespace-pre-wrap">{inc.target_excerpt}</pre>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Proposed Updates tab */}
      {activeTab === 'Proposed Updates' && (
        <div className="space-y-3">
          {proposed_updates.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">No updates proposed.</p>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-500">
                  {selectedCount} of {proposed_updates.length} selected
                </p>
                <div className="flex gap-2">
                  <button onClick={selectAll} className="text-xs text-gray-500 hover:text-gray-700">
                    Select All
                  </button>
                  <button onClick={deselectAll} className="text-xs text-gray-500 hover:text-gray-700">
                    Deselect All
                  </button>
                </div>
              </div>

              {proposed_updates.map((update, i) => (
                <div key={i} className={`border rounded-lg p-4 ${selectedUpdates[i] ? 'border-gray-900 bg-gray-50' : 'bg-white'}`}>
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={!!selectedUpdates[i]}
                      onChange={() => toggleUpdate(i)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-600">
                          {update.artifact_name}
                        </span>
                        {update.section && (
                          <span className="text-xs text-gray-400">
                            {update.section}
                          </span>
                        )}
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                          update.change_type === 'add' ? 'bg-green-100 text-green-700' :
                          update.change_type === 'remove' ? 'bg-red-100 text-red-700' :
                          'bg-amber-100 text-amber-700'
                        }`}>
                          {update.change_type}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-gray-600">{update.rationale}</p>

                      {/* Diff view */}
                      <div className="mt-2 space-y-1">
                        {update.current_text && (
                          <div className="flex gap-2">
                            <span className="text-xs text-red-500 font-mono">-</span>
                            <pre className="p-2 bg-red-50 rounded text-xs font-mono whitespace-pre-wrap flex-1 text-red-700">
                              {update.current_text}
                            </pre>
                          </div>
                        )}
                        {update.proposed_text && (
                          <div className="flex gap-2">
                            <span className="text-xs text-green-500 font-mono">+</span>
                            <pre className="p-2 bg-green-50 rounded text-xs font-mono whitespace-pre-wrap flex-1 text-green-700">
                              {update.proposed_text}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Apply button */}
              <button
                onClick={handleApply}
                disabled={selectedCount === 0 || isApplying}
                className="w-full py-3 text-sm font-medium rounded-lg bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
              >
                {isApplying ? 'Applying...' : `Apply ${selectedCount} Selected Update${selectedCount !== 1 ? 's' : ''}`}
              </button>
            </>
          )}
        </div>
      )}

      {/* Validation tab */}
      {activeTab === 'Validation' && (
        <div className="space-y-3">
          {validation_checks.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">No validation checks performed.</p>
          ) : (
            <>
              <div className="flex items-center gap-2 text-sm">
                <span className={`font-medium ${summary.validation_passed ? 'text-green-600' : 'text-red-600'}`}>
                  {summary.validation_passed ? 'All checks passed' : 'Some checks failed'}
                </span>
                <span className="text-gray-400">
                  ({validation_checks.filter(v => v.passed).length}/{validation_checks.length} passed)
                </span>
              </div>

              {validation_checks.map((check, i) => (
                <div
                  key={i}
                  className={`border rounded-lg p-3 flex items-start gap-3 ${
                    check.passed ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}
                >
                  <span className={`mt-0.5 ${check.passed ? 'text-green-600' : 'text-red-600'}`}>
                    {check.passed ? (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {check.artifact_name}: {check.check_description}
                    </p>
                    {check.detail && (
                      <p className="text-xs text-gray-600 mt-0.5">{check.detail}</p>
                    )}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}
