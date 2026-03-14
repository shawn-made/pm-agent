/**
 * 4-step progress indicator for Document Consistency analysis passes.
 * Shows which pass is active with a pulsing indicator.
 */

const PASS_LABELS = [
  'Dependency Graph',
  'Inconsistencies',
  'Proposed Updates',
  'Cross-Validation',
]

/**
 * @param {Object} props
 * @param {number} props.activePass - Currently active pass (0-3), or -1 if not started, or 4 if complete
 */
export default function PassProgressBar({ activePass = -1 }) {
  return (
    <div className="flex items-center gap-2">
      {PASS_LABELS.map((label, i) => {
        const isComplete = i < activePass
        const isActive = i === activePass
        const isPending = i > activePass

        return (
          <div key={label} className="flex items-center gap-2">
            {i > 0 && (
              <div className={`w-6 h-px ${isComplete ? 'bg-gray-900' : 'bg-gray-200'}`} />
            )}
            <div className="flex items-center gap-1.5">
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium ${
                  isComplete
                    ? 'bg-gray-900 text-white'
                    : isActive
                      ? 'bg-gray-900 text-white animate-pulse'
                      : 'bg-gray-200 text-gray-400'
                }`}
              >
                {isComplete ? (
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  i + 1
                )}
              </div>
              <span
                className={`text-xs ${
                  isActive ? 'text-gray-900 font-medium' : isPending ? 'text-gray-400' : 'text-gray-600'
                }`}
              >
                {label}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
