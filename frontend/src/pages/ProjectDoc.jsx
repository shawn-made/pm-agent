/**
 * Knowledge Base page — Living Project Document (LPD) viewer and editor.
 *
 * Displays all LPD sections with:
 * - Staleness indicators (days since last update)
 * - Inline editing (click to edit section content)
 * - Verify button (mark section as human-reviewed)
 * - Copy All (export full LPD as Markdown)
 * - Initialize LPD (for first-time setup)
 */
import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useToast } from '../components/ToastContext'
import BriefingPanel from '../components/BriefingPanel'
import RiskPredictionPanel from '../components/RiskPredictionPanel'
import {
  getLPDSections,
  getLPDStaleness,
  getLPDMarkdown,
  updateLPDSection,
  verifyLPDSection,
  initializeLPD,
  exportArtifacts,
} from '../services/api'

const SECTION_ORDER = [
  'Overview',
  'Stakeholders',
  'Timeline & Milestones',
  'Risks',
  'Decisions',
  'Open Questions',
  'Recent Context',
]

function StalenessIndicator({ days }) {
  if (days === null || days === undefined) return null
  if (days <= 1) return <span className="text-green-600 text-xs">Updated today</span>
  if (days <= 7) return <span className="text-green-500 text-xs">{days}d ago</span>
  if (days <= 14) return <span className="text-amber-500 text-xs">{days}d ago</span>
  return <span className="text-red-500 text-xs">{days}d ago</span>
}

export default function ProjectDoc() {
  const [sections, setSections] = useState(null) // null = loading, {} = no LPD
  const [staleness, setStaleness] = useState({})
  const [editingSection, setEditingSection] = useState(null)
  const [editContent, setEditContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [initializing, setInitializing] = useState(false)
  const [showRiskPanel, setShowRiskPanel] = useState(false)
  const [nudgeDismissed, setNudgeDismissed] = useState(false)
  const [collapsedSections, setCollapsedSections] = useState(new Set())
  const toast = useToast()
  const projectId = 'default'

  const loadData = useCallback(async () => {
    try {
      const [sectionRes, stalenessRes] = await Promise.all([
        getLPDSections(projectId),
        getLPDStaleness(projectId),
      ])
      setSections(sectionRes.sections)
      // Collapse all sections by default on initial load
      setCollapsedSections((prev) => {
        if (prev.size === 0) {
          return new Set(SECTION_ORDER.filter((name) => name in sectionRes.sections))
        }
        return prev
      })
      const stalenessMap = {}
      for (const s of stalenessRes.staleness) {
        stalenessMap[s.section_name] = s
      }
      setStaleness(stalenessMap)
    } catch {
      toast.error('Failed to load knowledge base')
      setSections({})
    }
  }, [projectId, toast])

  useEffect(() => {
    loadData()
  }, [loadData])

  async function handleInitialize() {
    setInitializing(true)
    try {
      await initializeLPD(projectId)
      toast.success('Knowledge base initialized')
      await loadData()
    } catch {
      toast.error('Failed to initialize knowledge base')
    } finally {
      setInitializing(false)
    }
  }

  function startEditing(sectionName) {
    if (sectionName === 'Recent Context') return // Auto-managed
    setEditingSection(sectionName)
    setEditContent(sections[sectionName] || '')
  }

  async function handleSave() {
    setSaving(true)
    try {
      await updateLPDSection(projectId, editingSection, editContent)
      toast.success(`Updated "${editingSection}"`)
      setEditingSection(null)
      await loadData()
    } catch {
      toast.error('Failed to save section')
    } finally {
      setSaving(false)
    }
  }

  function handleCancel() {
    setEditingSection(null)
    setEditContent('')
  }

  async function handleVerify(sectionName) {
    try {
      await verifyLPDSection(projectId, sectionName)
      toast.success(`Verified "${sectionName}"`)
      await loadData()
    } catch {
      toast.error('Failed to verify section')
    }
  }

  async function handleCopyAll() {
    try {
      const res = await getLPDMarkdown(projectId)
      await navigator.clipboard.writeText(res.markdown)
      toast.success('Copied knowledge base')
    } catch {
      toast.error('Failed to copy')
    }
  }

  async function handleDownloadMarkdown() {
    try {
      const res = await getLPDMarkdown(projectId)
      const blob = new Blob([res.markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${projectId}_knowledge-base.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('Downloaded knowledge base')
    } catch {
      toast.error('Failed to download')
    }
  }

  async function handleExportArtifacts() {
    try {
      const res = await exportArtifacts(projectId)
      if (!res.markdown || res.artifact_count === 0) {
        toast.info('No artifacts to export')
        return
      }
      const blob = new Blob([res.markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${projectId}_artifacts.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success(`Exported ${res.artifact_count} artifact${res.artifact_count !== 1 ? 's' : ''}`)
    } catch {
      toast.error('Failed to export artifacts')
    }
  }

  // Loading state
  if (sections === null) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-gray-400">Loading knowledge base...</p>
      </div>
    )
  }

  // No LPD yet
  const hasLPD = Object.keys(sections).length > 0
  if (!hasLPD) {
    return (
      <div className="space-y-6">
        <div className="border-l-4 border-emerald-400 pl-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Knowledge Base</h2>
          <p className="text-sm text-gray-500">Your living project document — view, edit, and get insights.</p>
        </div>
        <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
          <div className="text-gray-300 text-4xl mb-3">&#128196;</div>
          <p className="text-sm text-gray-500 mb-4">No knowledge base yet. Initialize one to get started.</p>
          <div className="flex justify-center gap-3">
            <button
              onClick={handleInitialize}
              disabled={initializing}
              className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
            >
              {initializing ? 'Initializing...' : 'Initialize Knowledge Base'}
            </button>
            <Link
              to="/import"
              className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Import from Files
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // Compute stale sections (14+ days since update)
  const staleSections = Object.entries(staleness)
    .filter(([, s]) => s.days_since_update >= 14)
    .map(([name, s]) => ({ name, days: s.days_since_update }))

  function scrollToSection(sectionName) {
    // Expand section if collapsed before scrolling
    setCollapsedSections((prev) => {
      const next = new Set(prev)
      next.delete(sectionName)
      return next
    })
    setTimeout(() => {
      const el = document.getElementById(`lpd-section-${sectionName}`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        el.classList.add('ring-2', 'ring-amber-400')
        setTimeout(() => el.classList.remove('ring-2', 'ring-amber-400'), 2000)
      }
    }, 50)
  }

  function toggleSection(sectionName) {
    setCollapsedSections((prev) => {
      const next = new Set(prev)
      if (next.has(sectionName)) {
        next.delete(sectionName)
      } else {
        next.add(sectionName)
      }
      return next
    })
  }

  const sectionNames = SECTION_ORDER.filter((name) => name in sections)
  const allCollapsed = sectionNames.length > 0 && collapsedSections.size === sectionNames.length

  function toggleAll() {
    if (allCollapsed) {
      setCollapsedSections(new Set())
    } else {
      setCollapsedSections(new Set(sectionNames))
    }
  }

  // LPD exists — show sections
  return (
    <div className="space-y-6">
      {/* Morning Briefing */}
      <BriefingPanel projectId={projectId} />

      <div className="flex items-center justify-between">
        <div className="border-l-4 border-emerald-400 pl-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Knowledge Base</h2>
          <p className="text-sm text-gray-500">Your living project document — view, edit, and get insights.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRiskPanel(true)}
            className="flex items-center gap-1 text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>
            Predict Risks
          </button>
          <Link
            to="/import"
            className="flex items-center gap-1 text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
            Import Files
          </Link>

          <span className="w-px h-5 bg-gray-200" />

          <button
            onClick={handleCopyAll}
            className="flex items-center gap-1 text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9.75a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
            </svg>
            Copy All
          </button>
          <button
            onClick={handleDownloadMarkdown}
            className="flex items-center gap-1 text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            Download .md
          </button>
          <button
            onClick={handleExportArtifacts}
            className="flex items-center gap-1 text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />
            </svg>
            Export Artifacts
          </button>
        </div>
      </div>

      {staleSections.length > 0 && !nudgeDismissed && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 flex items-start justify-between" data-testid="staleness-banner">
          <div className="text-sm text-amber-800">
            <span className="font-medium">{staleSections.length} {staleSections.length === 1 ? 'section hasn\u2019t' : 'sections haven\u2019t'} been updated in 2+ weeks:</span>{' '}
            {staleSections.map((s, i) => (
              <span key={s.name}>
                {i > 0 && ', '}
                <button
                  onClick={() => scrollToSection(s.name)}
                  className="underline hover:text-amber-900 transition-colors"
                >
                  {s.name}
                </button>
                <span className="text-amber-600"> ({s.days}d)</span>
              </span>
            ))}
          </div>
          <button
            onClick={() => setNudgeDismissed(true)}
            className="ml-3 text-amber-400 hover:text-amber-600 transition-colors flex-shrink-0"
            aria-label="Dismiss staleness warning"
          >
            &#10005;
          </button>
        </div>
      )}

      {showRiskPanel && (
        <RiskPredictionPanel
          projectId={projectId}
          onClose={() => setShowRiskPanel(false)}
        />
      )}

      <div className="flex justify-end mb-1">
        <button
          onClick={toggleAll}
          className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors"
        >
          {allCollapsed ? (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
          ) : (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14" />
            </svg>
          )}
          {allCollapsed ? 'Expand All' : 'Collapse All'}
        </button>
      </div>

      <div className="space-y-3">
        {SECTION_ORDER.map((name) => {
          if (!(name in sections)) return null
          const content = sections[name]
          const stale = staleness[name]
          const isEditing = editingSection === name
          const isRecent = name === 'Recent Context'

          const isCollapsed = collapsedSections.has(name) && !isEditing

          return (
            <div key={name} id={`lpd-section-${name}`} className="bg-white border border-gray-200 rounded-lg">
              <div
                className="flex items-center justify-between px-4 py-2.5 cursor-pointer select-none hover:bg-gray-50 transition-colors"
                onClick={() => !isEditing && toggleSection(name)}
              >
                <div className="flex items-center gap-2">
                  <svg
                    className={`w-3.5 h-3.5 text-gray-400 transition-transform ${isCollapsed ? '' : 'rotate-90'}`}
                    fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                  </svg>
                  <h3 className="text-sm font-semibold text-gray-700">{name}</h3>
                  {stale && <StalenessIndicator days={stale.days_since_update} />}
                  {stale?.days_since_verified !== null && stale?.days_since_verified !== undefined && (
                    <span className="text-xs text-gray-400">
                      verified {stale.days_since_verified}d ago
                    </span>
                  )}
                </div>
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  {!isRecent && !isEditing && (
                    <>
                      <button
                        onClick={() => startEditing(name)}
                        className="text-xs px-2 py-1 text-gray-500 hover:text-gray-700 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleVerify(name)}
                        className="text-xs px-2 py-1 text-gray-500 hover:text-green-600 transition-colors"
                      >
                        Verify
                      </button>
                    </>
                  )}
                  {isRecent && (
                    <span className="text-xs text-gray-400 italic">auto-managed</span>
                  )}
                </div>
              </div>

              {!isCollapsed && (
              <div className="px-4 py-3 border-t border-gray-100">
                {isEditing ? (
                  <div className="space-y-2">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={Math.max(4, (editContent.match(/\n/g) || []).length + 2)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-y text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    />
                    <div className="flex gap-2 justify-end">
                      <button
                        onClick={handleCancel}
                        className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSave}
                        disabled={saving}
                        className="text-xs px-3 py-1.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
                      >
                        {saving ? 'Saving...' : 'Save'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-gray-600 whitespace-pre-wrap">
                    {content || <span className="text-gray-400 italic">No {name.toLowerCase()} recorded yet.</span>}
                  </div>
                )}
              </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
