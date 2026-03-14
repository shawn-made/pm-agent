/**
 * Audit page — Document Consistency analysis + Reconciliation.
 * Upload 2+ artifacts, run 4-pass LLM analysis, review and apply updates.
 * Also includes cross-section LPD reconciliation (moved from Knowledge Base).
 *
 * Uses job-based polling (Task 57) — submit fires a background job,
 * results persist across tab switches and page reloads.
 */
import { useState, useEffect } from 'react'
import ArtifactUploader from '../components/ArtifactUploader'
import DeepStrategyResults from '../components/DeepStrategyResults'
import PassProgressBar from '../components/PassProgressBar'
import ReconciliationPanel from '../components/ReconciliationPanel'
import { useToast } from '../components/ToastContext'
import { deepStrategyApply } from '../services/api'
import useJobPolling from '../hooks/useJobPolling'

export default function DeepStrategy() {
  const [isApplying, setIsApplying] = useState(false)
  const [uploaderKey, setUploaderKey] = useState(0)
  const [showReconPanel, setShowReconPanel] = useState(false)
  const toast = useToast()
  const job = useJobPolling('deep_strategy')

  const isAnalyzing = job.status === 'pending' || job.status === 'running'

  // Toast on completion
  useEffect(() => {
    if (job.status === 'completed' && job.result) {
      const s = job.result.summary
      if (s.inconsistencies_found === 0) {
        toast.success('Analysis complete — no inconsistencies found')
      } else {
        toast.success(
          `Found ${s.inconsistencies_found} inconsistenc${s.inconsistencies_found > 1 ? 'ies' : 'y'}, ` +
          `${s.updates_proposed} update${s.updates_proposed !== 1 ? 's' : ''} proposed`
        )
      }
    }
    if (job.status === 'failed' && job.error) {
      toast.error('Document consistency analysis failed')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [job.status])

  async function handleAnalyze(artifacts) {
    await job.submit({ artifacts, project_id: 'default' })
  }

  async function handleApply(selectedUpdates) {
    setIsApplying(true)
    try {
      const result = await deepStrategyApply(selectedUpdates)

      const appliedCount = result.applied?.filter(a => a.status === 'applied').length || 0
      const clipboardCount = result.copied_to_clipboard?.length || 0

      let message = ''
      if (appliedCount > 0) message += `Applied ${appliedCount} update${appliedCount !== 1 ? 's' : ''}`
      if (clipboardCount > 0) {
        if (message) message += '. '
        message += `${clipboardCount} artifact${clipboardCount !== 1 ? 's' : ''} available for clipboard`
      }

      toast.success(message || 'Updates processed')
    } catch (err) {
      toast.error('Failed to apply updates: ' + err.message)
    } finally {
      setIsApplying(false)
    }
  }

  function handleNewAnalysis() {
    job.clear()
    setUploaderKey(k => k + 1)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Audit</h2>
        <p className="text-sm text-gray-500">
          Check your documents for inconsistencies and cross-section conflicts.
        </p>
      </div>

      {/* --- Document Consistency section --- */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-1">Document Consistency</h3>
        <p className="text-xs text-gray-400 mb-3">
          Upload 2+ project artifacts to check for cross-document inconsistencies.
        </p>
      </div>

      {/* Upload section — kept mounted but hidden to preserve content on error */}
      <div className={job.result || isAnalyzing ? 'hidden' : ''}>
        <ArtifactUploader key={uploaderKey} onAnalyze={handleAnalyze} isLoading={isAnalyzing} />
      </div>

      {/* Progress bar during analysis */}
      {isAnalyzing && (
        <div className="border rounded-lg p-6 bg-gray-50 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">Analyzing artifacts...</h3>
            <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
          </div>
          <PassProgressBar activePass={job.status === 'running' ? 1 : 0} />
          <p className="text-xs text-gray-400">
            This may take 2-5 minutes depending on artifact size. You can switch tabs — results will be here when you return.
          </p>
        </div>
      )}

      {/* Error display */}
      {job.status === 'failed' && job.error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{job.error}</p>
          <button
            onClick={handleNewAnalysis}
            className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Results */}
      {job.result && (
        <>
          <DeepStrategyResults
            results={job.result}
            onApply={handleApply}
            isApplying={isApplying}
          />

          {/* New analysis button */}
          <button
            onClick={handleNewAnalysis}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            Start new analysis
          </button>
        </>
      )}

      {/* --- Reconciliation section --- */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-1">Reconciliation</h3>
        <p className="text-xs text-gray-400 mb-3">
          Detect contradictions and conflicts across Knowledge Base sections.
        </p>
        <button
          onClick={() => setShowReconPanel(true)}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Run Reconciliation
        </button>
      </div>

      {showReconPanel && (
        <ReconciliationPanel
          onClose={() => setShowReconPanel(false)}
        />
      )}
    </div>
  )
}
