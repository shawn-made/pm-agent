/**
 * Renders analysis feedback from Analyze & Advise mode.
 * Displays an overall summary and categorized observation items.
 */
import { useState } from 'react'
import { useToast } from './ToastContext'

const CATEGORY_CONFIG = {
  strength: {
    label: 'Strength',
    icon: (
      <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ),
    color: 'border-green-200 bg-green-50',
  },
  observation: {
    label: 'Observation',
    icon: (
      <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'border-blue-200 bg-blue-50',
  },
  gap: {
    label: 'Gap',
    icon: (
      <svg className="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    color: 'border-amber-200 bg-amber-50',
  },
  recommendation: {
    label: 'Recommendation',
    icon: (
      <svg className="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    color: 'border-purple-200 bg-purple-50',
  },
}

const PRIORITY_COLORS = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-gray-100 text-gray-500',
}

const ARTIFACT_COLORS = {
  'RAID Log': 'text-amber-600',
  'Status Report': 'text-blue-600',
  'Meeting Notes': 'text-green-600',
}

/** Build a markdown string from analysis for clipboard. */
function assembleMarkdown(summary, items) {
  let md = '## Analysis Summary\n\n' + summary + '\n'

  const categoryOrder = ['strength', 'observation', 'gap', 'recommendation']
  const categoryLabels = { strength: 'Strengths', observation: 'Observations', gap: 'Gaps', recommendation: 'Recommendations' }

  for (const cat of categoryOrder) {
    const catItems = items.filter((item) => item.category === cat)
    if (catItems.length === 0) continue
    md += `\n## ${categoryLabels[cat]}\n\n`
    for (const item of catItems) {
      md += `### [${item.priority.charAt(0).toUpperCase() + item.priority.slice(1)}] ${item.title}\n\n${item.detail}\n\n`
    }
  }

  return md.trim()
}

/**
 * @param {Object} props
 * @param {string} props.summary - Overall assessment text
 * @param {Array} props.items - AnalysisItem objects from the API
 */
export default function AnalysisCard({ summary, items }) {
  const [copied, setCopied] = useState(false)
  const toast = useToast()

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(assembleMarkdown(summary, items))
      setCopied(true)
      toast.success('Analysis copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy to clipboard')
    }
  }

  // Group items by category in display order
  const categoryOrder = ['strength', 'observation', 'gap', 'recommendation']
  const grouped = categoryOrder
    .map((cat) => ({ category: cat, items: items.filter((item) => item.category === cat) }))
    .filter((g) => g.items.length > 0)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">
          Analysis ({items.length} item{items.length !== 1 ? 's' : ''})
        </h3>
        <button
          onClick={handleCopy}
          disabled={copied}
          className="px-3 py-1.5 text-xs font-medium rounded bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
        >
          {copied ? 'Copied' : 'Copy All'}
        </button>
      </div>

      {/* Summary callout */}
      {summary && (
        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-sm text-gray-700 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Analysis items grouped by category */}
      {grouped.map(({ category, items: catItems }) => {
        const config = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.observation
        return (
          <div key={category} className="space-y-2">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              {config.label}s ({catItems.length})
            </h4>
            {catItems.map((item, i) => (
              <div
                key={i}
                className={`border rounded-lg p-3 ${config.color}`}
              >
                <div className="flex items-start gap-2">
                  <span className="mt-0.5 flex-shrink-0">{config.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-medium text-gray-900">{item.title}</span>
                      <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${PRIORITY_COLORS[item.priority] || PRIORITY_COLORS.medium}`}>
                        {item.priority}
                      </span>
                      {item.artifact_type && (
                        <span className={`text-[10px] ${ARTIFACT_COLORS[item.artifact_type] || 'text-gray-500'}`}>
                          {item.artifact_type}
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-gray-600 leading-relaxed">{item.detail}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      })}
    </div>
  )
}
