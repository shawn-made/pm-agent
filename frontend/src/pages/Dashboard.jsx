/**
 * Dashboard — visual project status overview.
 *
 * Aggregates existing data (LPD staleness, briefing, sections) into
 * a scannable at-a-glance view. No LLM calls — reads cached/stored data only.
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getLPDStaleness, getLPDSections, getBriefing } from '../services/api'

const SEVERITY_COLORS = {
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-green-100 text-green-700 border-green-200',
}

function StatCard({ label, value, subtitle, color = 'text-gray-900' }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}

function StalenessBar({ section, days }) {
  let barColor = 'bg-green-400'
  let textColor = 'text-green-700'
  if (days >= 30) { barColor = 'bg-red-400'; textColor = 'text-red-700' }
  else if (days >= 14) { barColor = 'bg-amber-400'; textColor = 'text-amber-700' }
  else if (days >= 7) { barColor = 'bg-yellow-400'; textColor = 'text-yellow-700' }

  const width = Math.min(100, (days / 30) * 100)

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-600 w-36 truncate" title={section}>{section}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${barColor} rounded-full transition-all`} style={{ width: `${width}%` }} />
      </div>
      <span className={`text-xs font-medium w-12 text-right ${textColor}`}>{days}d</span>
    </div>
  )
}

export default function Dashboard() {
  const [staleness, setStaleness] = useState(null)
  const [sections, setSections] = useState(null)
  const [briefing, setBriefing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const [staleData, sectData, briefData] = await Promise.allSettled([
          getLPDStaleness(),
          getLPDSections(),
          getBriefing(),
        ])
        if (cancelled) return

        if (staleData.status === 'fulfilled') setStaleness(staleData.value?.staleness || staleData.value || [])
        if (sectData.status === 'fulfilled') setSections(sectData.value?.sections || {})
        if (briefData.status === 'fulfilled') setBriefing(briefData.value)
      } catch (err) {
        if (!cancelled) setError(err.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return (
      <div className="text-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-3" />
        <p className="text-sm text-gray-500">Loading dashboard...</p>
      </div>
    )
  }

  // Compute stats
  const sectionList = staleness || []
  const staleCount = sectionList.filter(s => s.days_since_update >= 14).length
  const totalSections = sectionList.length

  const populatedSections = sections
    ? Object.values(sections).filter(c => c && c.trim().length > 0).length
    : 0

  const attentionItems = briefing?.attention_items || []
  const highAttention = attentionItems.filter(a => a.severity === 'high').length
  const upcomingDates = briefing?.upcoming_dates || []
  const contradictions = briefing?.contradictions || []

  // Overall health with reasoning — requires briefing data for meaningful assessment
  const hasBriefing = briefing && (attentionItems.length > 0 || upcomingDates.length > 0 || contradictions.length > 0 || briefing.suggested_next_action)
  let healthLabel = 'Healthy'
  let healthColor = 'text-green-600'
  const healthReasons = []

  if (!hasBriefing) {
    healthLabel = 'No Assessment'
    healthColor = 'text-gray-400'
  } else {
    if (staleCount >= 4) healthReasons.push(`${staleCount} sections stale 14+ days`)
    else if (staleCount >= 2) healthReasons.push(`${staleCount} sections stale 14+ days`)
    if (highAttention >= 3) healthReasons.push(`${highAttention} high-severity items`)
    else if (highAttention >= 1) healthReasons.push(`${highAttention} high-severity item${highAttention > 1 ? 's' : ''}`)
    if (contradictions.length > 0) healthReasons.push(`${contradictions.length} contradiction${contradictions.length > 1 ? 's' : ''}`)
    if (staleCount >= 4 || highAttention >= 3) { healthLabel = 'At Risk'; healthColor = 'text-red-600' }
    else if (staleCount >= 2 || highAttention >= 1) { healthLabel = 'Needs Attention'; healthColor = 'text-amber-600' }
  }
  const healthReason = !hasBriefing
    ? 'Generate a briefing from the Knowledge Base to enable health assessment'
    : healthReasons.length > 0 ? healthReasons.join(', ') : 'No issues detected'

  // Last updated — most recent section update
  const mostRecent = sectionList.length > 0
    ? Math.min(...sectionList.map(s => s.days_since_update))
    : null

  const hasData = totalSections > 0 && populatedSections > 0

  if (!hasData) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">At-a-glance project status</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-sm text-gray-500">No project data yet.</p>
          <p className="text-xs text-gray-400 mt-2">
            Start by importing files on the <button onClick={() => navigate('/import')} className="text-blue-600 hover:underline">Import</button> page
            or adding content to your <button onClick={() => navigate('/kb')} className="text-blue-600 hover:underline">Knowledge Base</button>.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Dashboard</h2>
        <p className="text-sm text-gray-500 mt-1">At-a-glance project status</p>
      </div>

      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-2">
          <p className="text-xs text-amber-700">{error}</p>
        </div>
      )}

      {/* Health banner */}
      <div className={`bg-white border rounded-lg p-4 ${healthColor === 'text-red-600' ? 'border-red-200' : healthColor === 'text-amber-600' ? 'border-amber-200' : 'border-green-200'}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-lg font-bold ${healthColor}`}>{healthLabel}</p>
            <p className="text-sm text-gray-500 mt-0.5">{healthReason}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400">Data freshness</p>
            <p className="text-sm font-medium text-gray-600">
              {mostRecent !== null ? (mostRecent === 0 ? 'Updated today' : `${mostRecent}d since latest update`) : 'No data'}
            </p>
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="Attention Items"
          value={attentionItems.length}
          color={highAttention >= 1 ? 'text-red-600' : 'text-gray-900'}
          subtitle={highAttention > 0 ? `${highAttention} high severity` : 'from briefing'}
        />
        <StatCard
          label="Upcoming Dates"
          value={upcomingDates.length}
          subtitle={upcomingDates.length > 0 ? upcomingDates[0]?.date || '' : 'none extracted'}
        />
        <StatCard
          label="Contradictions"
          value={contradictions.length}
          color={contradictions.length > 0 ? 'text-red-600' : 'text-gray-900'}
          subtitle={contradictions.length > 0 ? 'cross-section conflicts' : 'none detected'}
        />
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column — Staleness */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Section Freshness</h3>
          <div className="space-y-3">
            {sectionList.length > 0 ? (
              sectionList
                .sort((a, b) => b.days_since_update - a.days_since_update)
                .map(s => (
                  <StalenessBar
                    key={s.section_name}
                    section={s.section_name}
                    days={s.days_since_update}
                  />
                ))
            ) : (
              <p className="text-xs text-gray-400">No staleness data available.</p>
            )}
          </div>
          <div className="mt-4 flex items-center gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-400" /> &lt;7d</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-400" /> 7-13d</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-400" /> 14-29d</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400" /> 30d+</span>
          </div>
        </div>

        {/* Right column — Attention Items */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Attention Items</h3>
          {attentionItems.length > 0 ? (
            <div className="space-y-3">
              {attentionItems.slice(0, 8).map((item, i) => {
                const severityClass = SEVERITY_COLORS[item.severity] || SEVERITY_COLORS.low
                return (
                  <div key={i} className="flex items-start gap-2">
                    <span className={`px-1.5 py-0.5 text-xs font-medium rounded border flex-shrink-0 ${severityClass}`}>
                      {item.severity}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm text-gray-700">{item.description}</p>
                      <p className="text-xs text-gray-400 mt-0.5">Source: {item.source_section}</p>
                    </div>
                  </div>
                )
              })}
              {attentionItems.length > 8 && (
                <p className="text-xs text-gray-400">+{attentionItems.length - 8} more items</p>
              )}
            </div>
          ) : (
            <p className="text-xs text-gray-400">No attention items. Generate a briefing from the Knowledge Base page to populate this.</p>
          )}
        </div>
      </div>

      {/* Bottom row — Upcoming dates and Contradictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming dates */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Upcoming Dates</h3>
          {upcomingDates.length > 0 ? (
            <div className="space-y-2">
              {upcomingDates.slice(0, 6).map((d, i) => (
                <div key={i} className="flex items-center justify-between">
                  <p className="text-sm text-gray-700">{d.description}</p>
                  <span className="text-xs text-gray-500 flex-shrink-0 ml-3">{d.date}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400">No upcoming dates extracted. Add timeline information to your Knowledge Base.</p>
          )}
        </div>

        {/* Contradictions */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Contradictions</h3>
          {contradictions.length > 0 ? (
            <div className="space-y-2">
              {contradictions.slice(0, 5).map((c, i) => (
                <div key={i} className="border-l-2 border-red-300 pl-3 py-1">
                  <p className="text-sm text-gray-700">{c.description}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {c.section_a} vs {c.section_b}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400">No contradictions detected. Run a briefing or Pressure Test from the Audit page.</p>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate('/process')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Process New Input
          </button>
          <button
            onClick={() => navigate('/audit')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Run Audit
          </button>
          <button
            onClick={() => navigate('/chat')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Ask Assistant
          </button>
          {briefing?.suggested_next_action && (
            <div className="w-full mt-2 bg-blue-50 border border-blue-100 rounded-lg px-4 py-3">
              <p className="text-xs font-medium text-blue-600 mb-1">Suggested Next Action</p>
              <p className="text-sm text-gray-700">{briefing.suggested_next_action}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
