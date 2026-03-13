/**
 * Deep Strategy page — multi-artifact consistency analysis.
 * Upload 2+ artifacts, run 4-pass LLM analysis, review and apply updates.
 */
import { useState } from 'react'
import ArtifactUploader from '../components/ArtifactUploader'
import DeepStrategyResults from '../components/DeepStrategyResults'
import PassProgressBar from '../components/PassProgressBar'
import { useToast } from '../components/ToastContext'
import { deepStrategyAnalyze, deepStrategyApply } from '../services/api'

/** Simulates progress through 4 passes during the synchronous API call. */
function useSimulatedProgress() {
  const [activePass, setActivePass] = useState(-1)

  function start() {
    setActivePass(0)
    // Simulate pass transitions at estimated intervals
    const timers = [
      setTimeout(() => setActivePass(1), 15000),
      setTimeout(() => setActivePass(2), 35000),
      setTimeout(() => setActivePass(3), 55000),
    ]
    return () => timers.forEach(clearTimeout)
  }

  function complete() {
    setActivePass(4)
  }

  function reset() {
    setActivePass(-1)
  }

  return { activePass, start, complete, reset }
}

export default function DeepStrategy() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isApplying, setIsApplying] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [uploaderKey, setUploaderKey] = useState(0)
  const toast = useToast()
  const progress = useSimulatedProgress()

  async function handleAnalyze(artifacts) {
    setIsAnalyzing(true)
    setError(null)
    setResults(null)

    const cleanup = progress.start()

    try {
      const result = await deepStrategyAnalyze(artifacts)
      progress.complete()
      setResults(result)

      if (result.summary.inconsistencies_found === 0) {
        toast.success('Analysis complete — no inconsistencies found')
      } else {
        toast.success(
          `Found ${result.summary.inconsistencies_found} inconsistenc${result.summary.inconsistencies_found > 1 ? 'ies' : 'y'}, ` +
          `${result.summary.updates_proposed} update${result.summary.updates_proposed !== 1 ? 's' : ''} proposed`
        )
      }
    } catch (err) {
      progress.reset()
      setError(err.message)
      toast.error('Deep Strategy analysis failed')
    } finally {
      cleanup()
      setIsAnalyzing(false)
    }
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Deep Strategy</h2>
        <p className="text-sm text-gray-500">
          Upload 2+ project artifacts for multi-document consistency analysis.
          VPMA will detect inconsistencies and propose specific updates.
        </p>
      </div>

      {/* Upload section — kept mounted but hidden to preserve content on error */}
      <div className={results || isAnalyzing ? 'hidden' : ''}>
        <ArtifactUploader key={uploaderKey} onAnalyze={handleAnalyze} isLoading={isAnalyzing} />
      </div>

      {/* Progress bar during analysis */}
      {isAnalyzing && (
        <div className="border rounded-lg p-6 bg-gray-50 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">Analyzing artifacts...</h3>
            <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
          </div>
          <PassProgressBar activePass={progress.activePass} />
          <p className="text-xs text-gray-400">
            This may take 2-5 minutes depending on artifact size.
          </p>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
          <button
            onClick={() => { setError(null); progress.reset() }}
            className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Results */}
      {results && (
        <>
          <DeepStrategyResults
            results={results}
            onApply={handleApply}
            isApplying={isApplying}
          />

          {/* New analysis button */}
          <button
            onClick={() => { setResults(null); progress.reset(); setUploaderKey(k => k + 1) }}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            Start new analysis
          </button>
        </>
      )}
    </div>
  )
}
