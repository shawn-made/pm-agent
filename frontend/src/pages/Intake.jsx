/**
 * Intake page — import existing PM files to populate the LPD.
 *
 * Flow:
 * 1. User pastes file content (one or more files)
 * 2. Click "Preview" to extract entities via LLM
 * 3. Review proposed LPD sections and conflicts
 * 4. Select which sections to approve
 * 5. Click "Apply" to commit to LPD
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../components/ToastContext'
import { intakePreview, intakeApply } from '../services/api'

export default function Intake() {
  const [files, setFiles] = useState([{ filename: '', content: '' }])
  const [draft, setDraft] = useState(null) // IntakeDraft from backend
  const [approved, setApproved] = useState(new Set())
  const [isExtracting, setIsExtracting] = useState(false)
  const [isApplying, setIsApplying] = useState(false)
  const [error, setError] = useState(null)
  const toast = useToast()
  const navigate = useNavigate()
  const projectId = 'default'

  function addFile() {
    setFiles([...files, { filename: '', content: '' }])
  }

  function removeFile(index) {
    if (files.length <= 1) return
    setFiles(files.filter((_, i) => i !== index))
  }

  function updateFile(index, field, value) {
    const updated = [...files]
    updated[index] = { ...updated[index], [field]: value }
    setFiles(updated)
  }

  async function handlePreview() {
    setIsExtracting(true)
    setError(null)
    setDraft(null)
    setApproved(new Set())

    // Validate
    const validFiles = files.filter(f => f.content.trim())
    if (validFiles.length === 0) {
      setError('At least one file must have content')
      setIsExtracting(false)
      return
    }

    // Auto-fill filenames
    const namedFiles = validFiles.map((f, i) => ({
      filename: f.filename.trim() || `file_${i + 1}.md`,
      content: f.content,
    }))

    try {
      const result = await intakePreview(projectId, namedFiles)
      setDraft(result)
      // Auto-select all proposed sections
      setApproved(new Set(Object.keys(result.proposed_sections)))
      toast.success(`Extracted from ${namedFiles.length} file${namedFiles.length > 1 ? 's' : ''}`)
    } catch (err) {
      setError(err.message)
      toast.error('Extraction failed')
    } finally {
      setIsExtracting(false)
    }
  }

  function toggleSection(sectionName) {
    const next = new Set(approved)
    if (next.has(sectionName)) {
      next.delete(sectionName)
    } else {
      next.add(sectionName)
    }
    setApproved(next)
  }

  async function handleApply() {
    if (approved.size === 0) {
      toast.info('Select at least one section to apply')
      return
    }

    setIsApplying(true)
    try {
      const result = await intakeApply(
        projectId,
        draft.proposed_sections,
        [...approved],
      )
      toast.success(`Applied ${result.sections_updated.length} section${result.sections_updated.length !== 1 ? 's' : ''} to knowledge base`)
      navigate('/project')
    } catch (err) {
      setError(err.message)
      toast.error('Apply failed')
    } finally {
      setIsApplying(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Import Files</h2>
        <p className="text-sm text-gray-500">
          Paste existing PM documents to populate your knowledge base. Each file is processed individually.
        </p>
      </div>

      {/* File inputs */}
      <div className="space-y-4">
        {files.map((file, index) => (
          <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between">
              <input
                type="text"
                value={file.filename}
                onChange={(e) => updateFile(index, 'filename', e.target.value)}
                placeholder={`File name (e.g., kickoff_notes.md)`}
                className="text-sm border border-gray-300 rounded px-3 py-1.5 w-64 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
              {files.length > 1 && (
                <button
                  onClick={() => removeFile(index)}
                  className="text-xs text-gray-400 hover:text-red-500 transition-colors"
                >
                  Remove
                </button>
              )}
            </div>
            <textarea
              value={file.content}
              onChange={(e) => updateFile(index, 'content', e.target.value)}
              placeholder="Paste file content here..."
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-y text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
          </div>
        ))}

        <div className="flex gap-2">
          <button
            onClick={addFile}
            className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            + Add File
          </button>
          <button
            onClick={handlePreview}
            disabled={isExtracting}
            className="px-4 py-1.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
          >
            {isExtracting ? 'Extracting...' : 'Preview'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Draft preview */}
      {draft && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">
              Preview — {Object.keys(draft.proposed_sections).length} sections extracted
            </h3>
            {draft.pii_detected > 0 && (
              <span className="flex items-center gap-1 text-xs text-green-600">
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                {draft.pii_detected} PII item{draft.pii_detected > 1 ? 's' : ''} anonymized
              </span>
            )}
          </div>

          {/* Conflicts */}
          {draft.conflicts?.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 space-y-2">
              <h4 className="text-xs font-semibold text-amber-700 uppercase tracking-wide">
                Conflicts Detected ({draft.conflicts.length})
              </h4>
              {draft.conflicts.map((c, i) => (
                <div key={i} className="text-xs text-amber-700">
                  <strong>{c.section}</strong> ({c.source_file}): Existing content will be preserved; new content will be appended.
                </div>
              ))}
            </div>
          )}

          {/* Proposed sections with checkboxes */}
          <div className="space-y-2">
            {Object.entries(draft.proposed_sections).map(([name, content]) => (
              <div key={name} className="bg-white border border-gray-200 rounded-lg">
                <label className="flex items-center gap-3 px-4 py-2.5 border-b border-gray-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={approved.has(name)}
                    onChange={() => toggleSection(name)}
                    className="rounded border-gray-300 text-gray-900 focus:ring-gray-900"
                  />
                  <span className="text-sm font-semibold text-gray-700">{name}</span>
                </label>
                <div className="px-4 py-3 text-sm text-gray-600 whitespace-pre-wrap">
                  {content}
                </div>
              </div>
            ))}
          </div>

          {/* Apply button */}
          <div className="flex justify-end gap-2">
            <button
              onClick={() => { setDraft(null); setApproved(new Set()) }}
              className="text-xs px-3 py-1.5 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={isApplying || approved.size === 0}
              className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
            >
              {isApplying ? 'Applying...' : `Apply ${approved.size} Section${approved.size !== 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
