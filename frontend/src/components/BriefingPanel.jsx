/**
 * BriefingPanel — AI-generated morning project briefing (Task 59).
 * Renders attention items, upcoming dates, contradictions, and a suggested next action.
 * Uses cached briefing if fresh; supports manual refresh.
 */
import { useState, useEffect, useCallback } from 'react'
import { getBriefing, refreshBriefing } from '../services/api'

const SEVERITY_COLORS = {
  high: 'border-red-400 bg-red-50',
  medium: 'border-amber-400 bg-amber-50',
  low: 'border-blue-400 bg-blue-50',
}

const SEVERITY_BADGES = {
  high: 'bg-red-100 text-red-800',
  medium: 'bg-amber-100 text-amber-800',
  low: 'bg-blue-100 text-blue-800',
}

const URGENCY_BADGES = {
  imminent: 'bg-red-100 text-red-800',
  upcoming: 'bg-amber-100 text-amber-800',
  future: 'bg-gray-100 text-gray-600',
}

const CATEGORY_LABELS = {
  staleness: 'Stale Data',
  risk: 'Risk',
  contradiction: 'Conflict',
  deadline: 'Deadline',
  gap: 'Gap',
}

function BriefingPanel({ projectId = 'default' }) {
  const [briefing, setBriefing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)
  const [collapsed, setCollapsed] = useState(false)

  const loadBriefing = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getBriefing(projectId)
      setBriefing(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    loadBriefing()
  }, [loadBriefing])

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      setError(null)
      const data = await refreshBriefing(projectId)
      setBriefing(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-5 bg-gray-200 rounded w-48"></div>
          <div className="h-3 bg-gray-100 rounded w-full"></div>
          <div className="h-3 bg-gray-100 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Project Briefing</h3>
          <button
            onClick={loadBriefing}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Retry
          </button>
        </div>
        <p className="mt-2 text-sm text-gray-500">
          {error.includes('502') || error.includes('LLM')
            ? 'Could not generate briefing — check your LLM configuration in Settings.'
            : `Unable to load briefing: ${error}`}
        </p>
      </div>
    )
  }

  if (!briefing) return null

  const hasContent = briefing.attention_items?.length > 0 ||
    briefing.upcoming_dates?.length > 0 ||
    briefing.contradictions?.length > 0

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* Header */}
      <div className="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-2 text-left"
        >
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform ${collapsed ? '' : 'rotate-90'}`}
            fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-900">Project Briefing</h3>
          {briefing.from_cache && (
            <span className="text-xs text-gray-400">(cached)</span>
          )}
        </button>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="text-xs text-blue-600 hover:text-blue-800 disabled:text-gray-400 flex items-center gap-1"
          title="Regenerate briefing"
        >
          <svg
            className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`}
            fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
          </svg>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {!collapsed && (
        <div className="p-5 space-y-4">
          {/* Suggested next action */}
          {briefing.suggested_next_action && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3">
              <p className="text-sm text-emerald-800">
                <span className="font-medium">Next action: </span>
                {briefing.suggested_next_action}
              </p>
            </div>
          )}

          {/* Attention items */}
          {briefing.attention_items?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Needs Attention ({briefing.attention_items.length})
              </h4>
              <div className="space-y-2">
                {briefing.attention_items.map((item, idx) => (
                  <div
                    key={idx}
                    className={`border-l-[3px] rounded-r-lg px-3 py-2 ${SEVERITY_COLORS[item.severity] || SEVERITY_COLORS.medium}`}
                  >
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-sm font-medium text-gray-900">{item.title}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${SEVERITY_BADGES[item.severity] || ''}`}>
                        {item.severity}
                      </span>
                      {CATEGORY_LABELS[item.category] && (
                        <span className="text-xs text-gray-400">
                          {CATEGORY_LABELS[item.category]}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-600">{item.detail}</p>
                    <p className="text-xs text-gray-400 mt-0.5">Source: {item.source_section}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upcoming dates */}
          {briefing.upcoming_dates?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Upcoming Dates ({briefing.upcoming_dates.length})
              </h4>
              <div className="space-y-1.5">
                {briefing.upcoming_dates.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${URGENCY_BADGES[item.urgency] || URGENCY_BADGES.upcoming}`}>
                      {item.date_text}
                    </span>
                    <span className="text-gray-700">{item.description}</span>
                    <span className="text-xs text-gray-400 ml-auto">{item.source_section}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contradictions */}
          {briefing.contradictions?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Contradictions ({briefing.contradictions.length})
              </h4>
              <div className="space-y-2">
                {briefing.contradictions.map((item, idx) => (
                  <div key={idx} className="bg-orange-50 border border-orange-200 rounded-lg px-3 py-2">
                    <p className="text-sm text-gray-900">{item.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {item.section_a} vs. {item.section_b}
                    </p>
                    {item.suggested_resolution && (
                      <p className="text-xs text-orange-700 mt-1">
                        Resolution: {item.suggested_resolution}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {!hasContent && briefing.suggested_next_action && !briefing.suggested_next_action.includes('No project data') && (
            <p className="text-sm text-gray-500">
              Your project looks healthy — no issues detected.
            </p>
          )}

          {/* Timestamp */}
          {briefing.generated_at && (
            <p className="text-xs text-gray-400 pt-2 border-t border-gray-100">
              Generated {new Date(briefing.generated_at).toLocaleString()}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default BriefingPanel
