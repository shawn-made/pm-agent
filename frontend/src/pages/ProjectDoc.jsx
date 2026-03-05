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
  const toast = useToast()
  const projectId = 'default'

  const loadData = useCallback(async () => {
    try {
      const [sectionRes, stalenessRes] = await Promise.all([
        getLPDSections(projectId),
        getLPDStaleness(projectId),
      ])
      setSections(sectionRes.sections)
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
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Knowledge Base</h2>
          <p className="text-sm text-gray-500">Your project knowledge base — accumulated context across sessions.</p>
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
              to="/intake"
              className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Import from Files
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // LPD exists — show sections
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Knowledge Base</h2>
          <p className="text-sm text-gray-500">Your project knowledge base — accumulated context across sessions.</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/intake"
            className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Import Files
          </Link>
          <button
            onClick={handleCopyAll}
            className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Copy All
          </button>
          <button
            onClick={handleDownloadMarkdown}
            className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Download .md
          </button>
          <button
            onClick={handleExportArtifacts}
            className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Export Artifacts
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {SECTION_ORDER.map((name) => {
          if (!(name in sections)) return null
          const content = sections[name]
          const stale = staleness[name]
          const isEditing = editingSection === name
          const isRecent = name === 'Recent Context'

          return (
            <div key={name} className="bg-white border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-100">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-semibold text-gray-700">{name}</h3>
                  {stale && <StalenessIndicator days={stale.days_since_update} />}
                  {stale?.days_since_verified !== null && stale?.days_since_verified !== undefined && (
                    <span className="text-xs text-gray-400">
                      verified {stale.days_since_verified}d ago
                    </span>
                  )}
                </div>
                <div className="flex gap-1">
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

              <div className="px-4 py-3">
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
            </div>
          )
        })}
      </div>
    </div>
  )
}
