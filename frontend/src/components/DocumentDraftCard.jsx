/**
 * Renders a group of suggestions for one artifact type as an assembled document draft.
 * Used for Status Report and Meeting Notes — artifacts that are created as a whole document,
 * not as individual items (unlike RAID Log).
 */
import { useState } from 'react'
import { useToast } from './ToastContext'

const TYPE_COLORS = {
  'Status Report': 'bg-blue-50 text-blue-700 border-blue-200',
  'Meeting Notes': 'bg-green-50 text-green-700 border-green-200',
}

const SECTION_ORDER = {
  'Status Report': ['Accomplishments', 'In Progress', 'Upcoming', 'Blockers / Risks'],
  'Meeting Notes': ['Discussion', 'Decisions', 'Action Items'],
}

/** Group suggestions by section and order them according to the artifact template. */
function assembleSections(artifactType, suggestions) {
  const order = SECTION_ORDER[artifactType] || []
  const bySection = {}
  suggestions.forEach((s) => {
    if (!bySection[s.section]) bySection[s.section] = []
    bySection[s.section].push(s)
  })
  // Return sections in template order, skip empty ones
  return order
    .filter((section) => bySection[section]?.length > 0)
    .map((section) => ({ section, suggestions: bySection[section] }))
}

/** Build a markdown string ready for clipboard — sections with proposed_text. */
function assembleMarkdown(sections) {
  return sections
    .map(({ section, suggestions }) => {
      const items = suggestions.map((s) => s.proposed_text).join('\n')
      return `## ${section}\n\n${items}`
    })
    .join('\n\n')
}

/**
 * @param {Object} props
 * @param {string} props.artifactType - 'Status Report' or 'Meeting Notes'
 * @param {Array} props.suggestions - All suggestions for this artifact type
 * @param {function} props.onApplyAll - Callback receiving the full suggestions array
 */
export default function DocumentDraftCard({ artifactType, suggestions, onApplyAll }) {
  const [applied, setApplied] = useState(false)
  const [applying, setApplying] = useState(false)
  const [copied, setCopied] = useState(false)
  const toast = useToast()

  const sections = assembleSections(artifactType, suggestions)
  const markdown = assembleMarkdown(sections)
  const avgConfidence = Math.round(
    (suggestions.reduce((sum, s) => sum + s.confidence, 0) / suggestions.length) * 100
  )
  const colorClass = TYPE_COLORS[artifactType] || 'bg-gray-50 text-gray-700 border-gray-200'

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      toast.success('Document copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy to clipboard')
    }
  }

  async function handleApplyAll() {
    try {
      setApplying(true)
      if (onApplyAll) await onApplyAll(suggestions)
      setApplied(true)
      toast.success(`Applied ${suggestions.length} items to ${artifactType}`)
    } catch {
      toast.error('Failed to apply suggestions')
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className={`border rounded-lg p-4 ${applied ? 'opacity-60' : ''}`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`px-2 py-0.5 text-xs font-medium rounded border ${colorClass}`}>
            {artifactType}
          </span>
          <span className="text-xs text-gray-400">
            {suggestions.length} item{suggestions.length !== 1 ? 's' : ''}
          </span>
        </div>
        <span className="text-xs text-gray-400 whitespace-nowrap">
          avg {avgConfidence}% confidence
        </span>
      </div>

      {/* Assembled document preview */}
      <div className="mt-3 p-3 bg-gray-50 rounded overflow-x-auto">
        {sections.map(({ section, suggestions: sectionSuggestions }) => (
          <div key={section} className="mb-3 last:mb-0">
            <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              {section}
            </h5>
            {sectionSuggestions.map((s, i) => (
              <pre
                key={i}
                className="text-xs text-gray-700 whitespace-pre-wrap font-mono pl-2 border-l-2 border-gray-200 mb-1 last:mb-0"
              >
                {s.proposed_text}
              </pre>
            ))}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="mt-3 flex gap-2">
        <button
          onClick={handleCopy}
          disabled={copied}
          className="px-3 py-1.5 text-xs font-medium rounded bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
        >
          {copied ? 'Copied' : 'Copy All'}
        </button>
        <button
          onClick={handleApplyAll}
          disabled={applied || applying}
          className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:text-gray-300 disabled:border-gray-200 transition-colors"
        >
          {applied ? 'Applied' : applying ? 'Applying...' : 'Apply All'}
        </button>
      </div>
    </div>
  )
}
