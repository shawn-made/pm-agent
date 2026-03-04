/**
 * RiskPredictionPanel — modal panel showing AI-predicted risks.
 *
 * Triggered from the Project Doc page. Calls the risk prediction API,
 * displays results with severity badges and confidence bars, and allows
 * adding predictions to the RAID Log via the existing apply flow.
 */
import { useState, useEffect } from 'react'
import { useToast } from './ToastContext'
import { predictRisks, applySuggestionByType } from '../services/api'

const SEVERITY_COLORS = {
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-green-100 text-green-700 border-green-200',
}

const HEALTH_LABELS = {
  healthy: { text: 'Healthy', color: 'text-green-600' },
  needs_attention: { text: 'Needs Attention', color: 'text-amber-600' },
  at_risk: { text: 'At Risk', color: 'text-red-600' },
  unknown: { text: 'Unknown', color: 'text-gray-400' },
}

export default function RiskPredictionPanel({ projectId = 'default', onClose }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [addedRisks, setAddedRisks] = useState(new Set())
  const [dismissedRisks, setDismissedRisks] = useState(new Set())
  const toast = useToast()

  useEffect(() => {
    let cancelled = false
    async function run() {
      try {
        const res = await predictRisks(projectId)
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

  async function handleAddToRAID(prediction, index) {
    try {
      await applySuggestionByType({
        artifact_type: 'RAID Log',
        section: 'Risks',
        change_type: 'add',
        proposed_text: prediction.suggested_raid_entry,
        confidence: prediction.confidence,
        reasoning: prediction.description,
      }, projectId)
      setAddedRisks(prev => new Set([...prev, index]))
      toast.success('Added to RAID Log')
    } catch {
      toast.error('Failed to add to RAID Log')
    }
  }

  function handleDismiss(index) {
    setDismissedRisks(prev => new Set([...prev, index]))
  }

  const healthInfo = HEALTH_LABELS[result?.project_health] || HEALTH_LABELS.unknown

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">AI Risk Prediction</h3>
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
              <p className="text-sm text-gray-500">Analyzing project health...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Health Summary */}
              <div className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3">
                <div>
                  <span className="text-xs text-gray-500">Project Health</span>
                  <p className={`text-sm font-semibold ${healthInfo.color}`}>{healthInfo.text}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-gray-500">Risks Found</span>
                  <p className="text-sm font-semibold text-gray-700">{result.predictions.length}</p>
                </div>
              </div>

              {/* Predictions */}
              {result.predictions.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-6">No additional risks predicted.</p>
              ) : (
                result.predictions.map((pred, i) => {
                  const isAdded = addedRisks.has(i)
                  const isDismissed = dismissedRisks.has(i)
                  if (isDismissed) return null

                  const severityClass = SEVERITY_COLORS[pred.severity] || SEVERITY_COLORS.low

                  return (
                    <div
                      key={i}
                      className={`border rounded-lg p-4 ${isAdded ? 'opacity-60' : ''}`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 text-xs font-medium rounded border ${severityClass}`}>
                            {pred.severity}
                          </span>
                          <span className="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-600">
                            {pred.category}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gray-600 rounded-full"
                              style={{ width: `${Math.round(pred.confidence * 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-400">{Math.round(pred.confidence * 100)}%</span>
                        </div>
                      </div>

                      <p className="mt-2 text-sm text-gray-700">{pred.description}</p>
                      <p className="mt-1 text-xs text-gray-500">Evidence: {pred.evidence}</p>

                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => handleAddToRAID(pred, i)}
                          disabled={isAdded}
                          className="px-3 py-1.5 text-xs font-medium rounded bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
                        >
                          {isAdded ? 'Added' : 'Add to RAID Log'}
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
                })
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
