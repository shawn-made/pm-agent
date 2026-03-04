/**
 * Multi-artifact uploader for Deep Strategy analysis.
 * Supports pasting text or uploading .md/.txt files, with priority ordering.
 */
import { useState, useRef } from 'react'

const MIN_ARTIFACTS = 2
const MAX_ARTIFACTS = 10

function createEmptyArtifact() {
  return { name: '', content: '', priority: 0 }
}

/**
 * @param {Object} props
 * @param {function} props.onAnalyze - Callback with artifacts array when user clicks Analyze
 * @param {boolean} props.isLoading - Whether analysis is in progress
 */
export default function ArtifactUploader({ onAnalyze, isLoading = false }) {
  const [artifacts, setArtifacts] = useState([createEmptyArtifact(), createEmptyArtifact()])
  const fileInputRef = useRef(null)
  const [addingIndex, setAddingIndex] = useState(null)

  function updateArtifact(index, field, value) {
    setArtifacts(prev => prev.map((a, i) => i === index ? { ...a, [field]: value } : a))
  }

  function addArtifact() {
    if (artifacts.length >= MAX_ARTIFACTS) return
    setArtifacts(prev => [...prev, createEmptyArtifact()])
  }

  function removeArtifact(index) {
    if (artifacts.length <= MIN_ARTIFACTS) return
    setArtifacts(prev => prev.filter((_, i) => i !== index))
  }

  function moveUp(index) {
    if (index === 0) return
    setArtifacts(prev => {
      const next = [...prev]
      ;[next[index - 1], next[index]] = [next[index], next[index - 1]]
      return next
    })
  }

  function moveDown(index) {
    if (index === artifacts.length - 1) return
    setArtifacts(prev => {
      const next = [...prev]
      ;[next[index], next[index + 1]] = [next[index + 1], next[index]]
      return next
    })
  }

  function handleFileUpload(index) {
    setAddingIndex(index)
    fileInputRef.current?.click()
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file || addingIndex === null) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result || ''
      const name = file.name.replace(/\.(md|txt)$/, '')
      updateArtifact(addingIndex, 'content', content)
      if (!artifacts[addingIndex].name) {
        updateArtifact(addingIndex, 'name', name)
      }
      setAddingIndex(null)
    }
    reader.readAsText(file)
    e.target.value = '' // Reset for re-upload
  }

  function handleSubmit() {
    const prepared = artifacts.map((a, i) => ({
      name: a.name || `Artifact ${i + 1}`,
      content: a.content,
      priority: i + 1, // Priority = position order (1 = highest)
    }))
    onAnalyze(prepared)
  }

  const canSubmit = artifacts.filter(a => a.content.trim()).length >= MIN_ARTIFACTS && !isLoading

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">
          Order = source-of-truth priority. Top artifact wins when two disagree.
        </p>
        <button
          onClick={addArtifact}
          disabled={artifacts.length >= MAX_ARTIFACTS}
          className="px-3 py-1.5 text-xs font-medium rounded border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:text-gray-300 disabled:border-gray-200 transition-colors"
        >
          + Add Artifact
        </button>
      </div>

      {artifacts.map((artifact, index) => (
        <div
          key={index}
          className="border rounded-lg p-4 bg-white space-y-3"
        >
          <div className="flex items-center gap-2">
            {/* Priority badge */}
            <span className="w-6 h-6 rounded-full bg-gray-900 text-white flex items-center justify-center text-xs font-medium">
              {index + 1}
            </span>

            {/* Name input */}
            <input
              type="text"
              value={artifact.name}
              onChange={e => updateArtifact(index, 'name', e.target.value)}
              placeholder={`Artifact ${index + 1} name (e.g., Charter, Schedule)`}
              className="flex-1 px-3 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-gray-400"
            />

            {/* Reorder buttons */}
            <div className="flex gap-0.5">
              <button
                onClick={() => moveUp(index)}
                disabled={index === 0}
                className="p-1 text-gray-400 hover:text-gray-700 disabled:text-gray-200"
                title="Move up (higher priority)"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <button
                onClick={() => moveDown(index)}
                disabled={index === artifacts.length - 1}
                className="p-1 text-gray-400 hover:text-gray-700 disabled:text-gray-200"
                title="Move down (lower priority)"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>

            {/* Upload file button */}
            <button
              onClick={() => handleFileUpload(index)}
              className="p-1 text-gray-400 hover:text-gray-700"
              title="Upload .md or .txt file"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </button>

            {/* Remove button */}
            {artifacts.length > MIN_ARTIFACTS && (
              <button
                onClick={() => removeArtifact(index)}
                className="p-1 text-gray-400 hover:text-red-500"
                title="Remove artifact"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Content textarea */}
          <textarea
            value={artifact.content}
            onChange={e => updateArtifact(index, 'content', e.target.value)}
            placeholder="Paste artifact content here, or upload a file..."
            rows={6}
            className="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-gray-400 font-mono resize-y"
          />

          {artifact.content && (
            <p className="text-xs text-gray-400">
              {artifact.content.length.toLocaleString()} characters
            </p>
          )}
        </div>
      ))}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".md,.txt"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Analyze button */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="w-full py-3 text-sm font-medium rounded-lg bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
      >
        {isLoading ? 'Analyzing...' : `Analyze ${artifacts.filter(a => a.content.trim()).length} Artifacts`}
      </button>
    </div>
  )
}
