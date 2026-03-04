/**
 * Settings page for configuring LLM provider, API keys, and custom sensitive terms.
 */
import { useState, useEffect, useCallback } from 'react'
import { useToast } from '../components/ToastContext'
import FolderBrowser from '../components/FolderBrowser'
import {
  getSettings,
  updateSettings,
  getOllamaStatus,
  getTranscriptWatcherStatus,
  startTranscriptWatcher,
  stopTranscriptWatcher,
  applySuggestionByType,
  getTranscriptWatcherResults,
  uploadTranscriptFile,
} from '../services/api'

/** Settings page — loads current config on mount, saves changes via PUT /api/settings. */
export default function Settings() {
  const [llmProvider, setLlmProvider] = useState('claude')
  const [anthropicKey, setAnthropicKey] = useState('')
  const [geminiKey, setGeminiKey] = useState('')
  const [sensitiveTerms, setSensitiveTerms] = useState('')
  const [ollamaBaseUrl, setOllamaBaseUrl] = useState('')
  const [ollamaModel, setOllamaModel] = useState('')
  const [ollamaStatus, setOllamaStatus] = useState(null)
  const [showAnthropicKey, setShowAnthropicKey] = useState(false)
  const [showGeminiKey, setShowGeminiKey] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Transcript watcher state
  const [watchFolder, setWatchFolder] = useState('')
  const [watchMode, setWatchMode] = useState('extract')
  const [watcherStatus, setWatcherStatus] = useState(null)
  const [isTogglingWatcher, setIsTogglingWatcher] = useState(false)
  const [expandedFile, setExpandedFile] = useState(null)
  const [watcherResults, setWatcherResults] = useState(null)
  const [applyingIdx, setApplyingIdx] = useState(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [showFolderBrowser, setShowFolderBrowser] = useState(false)

  const toast = useToast()

  const loadWatcherStatus = useCallback(async () => {
    try {
      const status = await getTranscriptWatcherStatus()
      setWatcherStatus(status)
    } catch {
      // Watcher status is non-critical
    }
  }, [])

  useEffect(() => {
    loadSettings()
    loadWatcherStatus()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadSettings() {
    try {
      const data = await getSettings()
      const s = data.settings || {}
      setLlmProvider(s.llm_provider || 'claude')
      setAnthropicKey(s.anthropic_api_key || '')
      setGeminiKey(s.google_ai_api_key || '')
      setSensitiveTerms(s.sensitive_terms || '')
      setOllamaBaseUrl(s.ollama_base_url || '')
      setOllamaModel(s.ollama_model || '')
      setWatchFolder(s.transcript_watch_folder || '')
      setWatchMode(s.transcript_auto_mode || 'extract')
      // Auto-check Ollama status when it's the active provider
      if ((s.llm_provider || 'claude') === 'ollama') {
        getOllamaStatus()
          .then(setOllamaStatus)
          .catch(() => setOllamaStatus({ available: false, models: [], error: 'Failed to check status' }))
      }
    } catch {
      toast.error('Failed to load settings')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSave(e) {
    e.preventDefault()
    setIsSaving(true)

    try {
      const payload = {
        llm_provider: llmProvider,
        sensitive_terms: sensitiveTerms,
        ollama_base_url: ollamaBaseUrl || undefined,
        ollama_model: ollamaModel || undefined,
        transcript_watch_folder: watchFolder || undefined,
        transcript_auto_mode: watchMode,
      }

      // Only send API keys if they've been changed (not masked values)
      if (anthropicKey && !anthropicKey.startsWith('****')) {
        payload.anthropic_api_key = anthropicKey
      }
      if (geminiKey && !geminiKey.startsWith('****')) {
        payload.google_ai_api_key = geminiKey
      }

      await updateSettings(payload)
      toast.success('Settings saved')
    } catch {
      toast.error('Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="text-center py-16">
        <p className="text-sm text-gray-400">Loading settings...</p>
      </div>
    )
  }

  return (
    <div className="max-w-lg">
      <h2 className="text-lg font-semibold text-gray-900 mb-1">Settings</h2>
      <p className="text-sm text-gray-500 mb-6">
        Configure API keys, LLM provider, and privacy settings.
      </p>

      <form onSubmit={handleSave} className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
        {/* LLM Provider */}
        <fieldset>
          <legend className="text-sm font-medium text-gray-700 mb-2">LLM Provider</legend>
          <div className="flex gap-4">
            {[
              { value: 'claude', label: 'Claude' },
              { value: 'gemini', label: 'Gemini' },
              { value: 'ollama', label: 'Ollama (Local)' },
            ].map(opt => (
              <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="llm_provider"
                  value={opt.value}
                  checked={llmProvider === opt.value}
                  onChange={(e) => {
                    setLlmProvider(e.target.value)
                    if (e.target.value === 'ollama') {
                      // Check Ollama status when selected
                      getOllamaStatus()
                        .then(setOllamaStatus)
                        .catch(() => setOllamaStatus({ available: false, models: [], error: 'Failed to check status' }))
                    }
                  }}
                  className="text-gray-900 focus:ring-gray-900"
                />
                <span className="text-sm text-gray-700">{opt.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* API Keys */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-700">API Keys</h3>

          {/* Anthropic */}
          <div>
            <label htmlFor="anthropic-key" className="block text-xs text-gray-500 mb-1">
              Anthropic API Key
            </label>
            <div className="relative">
              <input
                id="anthropic-key"
                type={showAnthropicKey ? 'text' : 'password'}
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
                placeholder="sk-ant-..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent pr-16"
              />
              <button
                type="button"
                onClick={() => setShowAnthropicKey(!showAnthropicKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-400 hover:text-gray-600"
              >
                {showAnthropicKey ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          {/* Gemini */}
          <div>
            <label htmlFor="gemini-key" className="block text-xs text-gray-500 mb-1">
              Google AI API Key
            </label>
            <div className="relative">
              <input
                id="gemini-key"
                type={showGeminiKey ? 'text' : 'password'}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AIza..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent pr-16"
              />
              <button
                type="button"
                onClick={() => setShowGeminiKey(!showGeminiKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-400 hover:text-gray-600"
              >
                {showGeminiKey ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
        </div>

        {/* Ollama Configuration (visible when Ollama selected) */}
        {llmProvider === 'ollama' && (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-700">Ollama Configuration</h3>
              {ollamaStatus && (
                <span className={`flex items-center gap-1.5 text-xs ${
                  ollamaStatus.available ? 'text-green-600' : 'text-red-500'
                }`}>
                  <span className={`inline-block w-2 h-2 rounded-full ${
                    ollamaStatus.available ? 'bg-green-500' : 'bg-red-400'
                  }`} data-testid="ollama-status-dot" />
                  {ollamaStatus.available
                    ? `Connected (${ollamaStatus.models?.length || 0} model${ollamaStatus.models?.length !== 1 ? 's' : ''})`
                    : ollamaStatus.error || 'Not connected'}
                </span>
              )}
            </div>

            <div>
              <label htmlFor="ollama-model" className="block text-xs text-gray-500 mb-1">
                Model Name
              </label>
              <input
                id="ollama-model"
                type="text"
                value={ollamaModel}
                onChange={(e) => setOllamaModel(e.target.value)}
                placeholder="llama3.2"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
              {ollamaStatus?.available && ollamaStatus?.models?.length > 0 && (
                <p className="text-xs text-gray-400 mt-1">
                  Available: {ollamaStatus.models.join(', ')}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="ollama-url" className="block text-xs text-gray-500 mb-1">
                Base URL
              </label>
              <input
                id="ollama-url"
                type="text"
                value={ollamaBaseUrl}
                onChange={(e) => setOllamaBaseUrl(e.target.value)}
                placeholder="http://localhost:11434"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>

            <button
              type="button"
              onClick={async () => {
                try {
                  const status = await getOllamaStatus()
                  setOllamaStatus(status)
                  if (status.available) {
                    toast.success(`Ollama connected: ${status.models.length} model(s) available`)
                  } else {
                    toast.error(status.error || 'Cannot connect to Ollama')
                  }
                } catch {
                  toast.error('Failed to check Ollama status')
                }
              }}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              Test Connection
            </button>
          </div>
        )}

        {/* Sensitive Terms */}
        <div>
          <label htmlFor="sensitive-terms" className="block text-sm font-medium text-gray-700 mb-1">
            Custom Sensitive Terms
          </label>
          <p className="text-xs text-gray-400 mb-2">
            Enter project names, client names, or other terms to anonymize (comma or newline separated).
          </p>
          <textarea
            id="sensitive-terms"
            value={sensitiveTerms}
            onChange={(e) => setSensitiveTerms(e.target.value)}
            placeholder="Project Falcon, ClientCo, PartnerOrg"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />
        </div>

        {/* Save */}
        <button
          type="submit"
          disabled={isSaving}
          className="px-6 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </button>
      </form>

      {/* Transcript Watcher */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Transcript Watcher</h2>
        <p className="text-sm text-gray-500 mb-4">
          Automatically process transcript files (.vtt, .srt, .txt) dropped into a watched folder.
        </p>

        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          {/* Watch folder */}
          <div>
            <label htmlFor="watch-folder" className="block text-sm font-medium text-gray-700 mb-1">
              Watch Folder
            </label>
            <p className="text-xs text-gray-400 mb-2">
              Absolute path to the folder to monitor for transcript files.
            </p>
            <div className="flex gap-2">
              <input
                id="watch-folder"
                type="text"
                value={watchFolder}
                onChange={(e) => setWatchFolder(e.target.value)}
                placeholder="/Users/you/Transcripts"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowFolderBrowser(true)}
                className="px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors whitespace-nowrap"
              >
                Browse
              </button>
            </div>

            {showFolderBrowser && (
              <FolderBrowser
                onSelect={(path) => setWatchFolder(path)}
                onClose={() => setShowFolderBrowser(false)}
              />
            )}
          </div>

          {/* Processing mode */}
          <fieldset>
            <legend className="text-sm font-medium text-gray-700 mb-2">Processing Mode</legend>
            <div className="flex gap-4">
              {[
                { value: 'extract', label: 'Extract & Route' },
                { value: 'log_session', label: 'Log Session' },
              ].map(opt => (
                <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="watch_mode"
                    value={opt.value}
                    checked={watchMode === opt.value}
                    onChange={(e) => setWatchMode(e.target.value)}
                    className="text-gray-900 focus:ring-gray-900"
                  />
                  <span className="text-sm text-gray-700">{opt.label}</span>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Status + Toggle */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <span
                className={`inline-block w-2.5 h-2.5 rounded-full ${
                  watcherStatus?.running ? 'bg-green-500' : 'bg-gray-300'
                }`}
                data-testid="watcher-status-dot"
              />
              <span className="text-sm text-gray-600">
                {watcherStatus?.running ? 'Running' : 'Stopped'}
              </span>
              {watcherStatus?.running && watcherStatus?.files_processed > 0 && (
                <span className="text-xs text-gray-400 ml-2">
                  ({watcherStatus.files_processed} file{watcherStatus.files_processed !== 1 ? 's' : ''} processed)
                </span>
              )}
            </div>
            <button
              type="button"
              disabled={isTogglingWatcher || (!watchFolder && !watcherStatus?.running)}
              onClick={async () => {
                setIsTogglingWatcher(true)
                try {
                  if (watcherStatus?.running) {
                    await stopTranscriptWatcher()
                    toast.success('Transcript watcher stopped')
                  } else {
                    // Save settings first to ensure watch folder is persisted
                    if (watchFolder) {
                      await updateSettings({
                        transcript_watch_folder: watchFolder,
                        transcript_auto_mode: watchMode,
                      })
                    }
                    await startTranscriptWatcher()
                    toast.success('Transcript watcher started')
                  }
                  await loadWatcherStatus()
                } catch (err) {
                  toast.error(err.message || 'Failed to toggle watcher')
                } finally {
                  setIsTogglingWatcher(false)
                }
              }}
              className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                watcherStatus?.running
                  ? 'bg-red-50 text-red-700 hover:bg-red-100 border border-red-200'
                  : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
              }`}
            >
              {isTogglingWatcher ? '...' : watcherStatus?.running ? 'Stop' : 'Start'}
            </button>
          </div>

          {/* Recent Files */}
          {watcherStatus?.recent_files?.length > 0 && (
            <div className="pt-2 border-t border-gray-100">
              <h4 className="text-xs font-medium text-gray-500 mb-2">Recent Files</h4>
              <ul className="space-y-1">
                {watcherStatus.recent_files.slice(0, 5).map((f, i) => (
                  <li key={i} className="text-xs">
                    <button
                      type="button"
                      className="flex items-center gap-2 w-full text-left hover:bg-gray-50 rounded px-1 py-0.5"
                      onClick={async () => {
                        if (expandedFile === i) {
                          setExpandedFile(null)
                        } else {
                          setExpandedFile(i)
                          // Fetch full results if not already loaded
                          if (!watcherResults) {
                            try {
                              const data = await getTranscriptWatcherResults()
                              setWatcherResults(data.results)
                            } catch {
                              // Fall back to status data
                            }
                          }
                        }
                      }}
                    >
                      <span className={`inline-block w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                        f.status === 'processed' ? 'bg-green-400' :
                        f.status === 'skipped' ? 'bg-yellow-400' : 'bg-red-400'
                      }`} />
                      <span className="text-gray-700 truncate flex-1">{f.file}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                        f.status === 'processed' ? 'bg-green-50 text-green-700' :
                        f.status === 'skipped' ? 'bg-yellow-50 text-yellow-700' : 'bg-red-50 text-red-700'
                      }`}>{f.status}</span>
                      <span className="text-gray-400">{expandedFile === i ? '\u25B2' : '\u25BC'}</span>
                    </button>

                    {/* Expanded results panel */}
                    {expandedFile === i && (
                      <div className="mt-1 ml-4 p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2">
                        {f.status === 'error' && (
                          <p className="text-xs text-red-600">{f.reason || 'Processing failed'}</p>
                        )}
                        {f.status === 'skipped' && (
                          <p className="text-xs text-yellow-600">{f.reason || 'Skipped'}</p>
                        )}
                        {f.status === 'processed' && (() => {
                          const result = watcherResults?.[i] || f
                          const suggestions = result.sync_result?.suggestions || []
                          return (
                            <>
                              <div className="flex items-center gap-3 text-[11px] text-gray-500">
                                <span>Mode: {result.mode}</span>
                                <span>{result.suggestion_count ?? suggestions.length} suggestion{(result.suggestion_count ?? suggestions.length) !== 1 ? 's' : ''}</span>
                                {result.lpd_update_count != null && (
                                  <span>{result.lpd_update_count} KB update{result.lpd_update_count !== 1 ? 's' : ''}</span>
                                )}
                              </div>
                              {suggestions.length > 0 && (
                                <ul className="space-y-1.5">
                                  {suggestions.map((s, si) => (
                                    <li key={si} className="bg-white rounded border border-gray-200 p-2">
                                      <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                          <span className="text-[10px] font-medium text-gray-400 uppercase">
                                            {s.artifact_type?.replace(/_/g, ' ')}
                                          </span>
                                          <p className="text-xs text-gray-700 mt-0.5 line-clamp-2">
                                            {s.proposed_text?.slice(0, 150)}{s.proposed_text?.length > 150 ? '...' : ''}
                                          </p>
                                        </div>
                                        <button
                                          type="button"
                                          disabled={applyingIdx === `${i}-${si}`}
                                          onClick={async () => {
                                            setApplyingIdx(`${i}-${si}`)
                                            try {
                                              const applyResult = await applySuggestionByType(s)
                                              if (applyResult.lpd_updated) {
                                                toast.success(`Applied to ${s.artifact_type?.replace(/_/g, ' ')}${applyResult.lpd_change ? ` + KB "${applyResult.lpd_change.section}"` : ''}`)
                                              } else {
                                                toast.success(`Applied to ${s.artifact_type?.replace(/_/g, ' ')}`)
                                              }
                                            } catch {
                                              toast.error('Failed to apply suggestion')
                                            } finally {
                                              setApplyingIdx(null)
                                            }
                                          }}
                                          className="flex-shrink-0 px-2 py-1 text-[10px] font-medium bg-gray-900 text-white rounded hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed"
                                        >
                                          {applyingIdx === `${i}-${si}` ? '...' : 'Apply'}
                                        </button>
                                      </div>
                                    </li>
                                  ))}
                                </ul>
                              )}
                              {suggestions.length === 0 && (
                                <p className="text-xs text-gray-400 italic">No suggestions generated</p>
                              )}
                              {result.sync_result?.session_summary && (
                                <div className="mt-2 pt-2 border-t border-gray-200">
                                  <span className="text-[10px] font-medium text-gray-400 uppercase">Session Summary</span>
                                  <p className="text-xs text-gray-600 mt-0.5">{result.sync_result.session_summary}</p>
                                </div>
                              )}
                            </>
                          )
                        })()}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Drag-and-Drop Upload */}
          <div
            className={`mt-4 border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              isDragOver
                ? 'border-gray-900 bg-gray-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            data-testid="drop-zone"
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={async (e) => {
              e.preventDefault()
              setIsDragOver(false)
              const file = e.dataTransfer.files?.[0]
              if (!file) return

              const ext = file.name.split('.').pop()?.toLowerCase()
              if (!['vtt', 'srt', 'txt'].includes(ext)) {
                toast.error('Unsupported file type. Accepted: .vtt, .srt, .txt')
                return
              }

              setIsUploading(true)
              setUploadResult(null)
              try {
                const content = await file.text()
                const result = await uploadTranscriptFile(file.name, content)
                setUploadResult(result)
                if (result.status === 'processed') {
                  toast.success(`Processed ${file.name}: ${result.suggestion_count ?? 0} suggestion(s)`)
                } else {
                  toast.error(result.reason || `File ${result.status}`)
                }
                // Refresh watcher status to show in recent files
                await loadWatcherStatus()
              } catch (err) {
                toast.error(err.message || 'Failed to process file')
              } finally {
                setIsUploading(false)
              }
            }}
          >
            {isUploading ? (
              <p className="text-sm text-gray-500">Processing...</p>
            ) : (
              <>
                <p className="text-sm text-gray-500">
                  Drop a transcript file here (.vtt, .srt, .txt)
                </p>
                <p className="text-xs text-gray-400 mt-1">or use the watched folder above</p>
              </>
            )}
          </div>

          {/* Upload Result */}
          {uploadResult?.status === 'processed' && uploadResult.sync_result?.suggestions?.length > 0 && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2" data-testid="upload-result">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-medium text-gray-600">
                  {uploadResult.file} — {uploadResult.sync_result.suggestions.length} suggestion{uploadResult.sync_result.suggestions.length !== 1 ? 's' : ''}
                </h4>
                <button
                  type="button"
                  onClick={() => setUploadResult(null)}
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  Dismiss
                </button>
              </div>
              <ul className="space-y-1.5">
                {uploadResult.sync_result.suggestions.map((s, si) => (
                  <li key={si} className="bg-white rounded border border-gray-200 p-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <span className="text-[10px] font-medium text-gray-400 uppercase">
                          {s.artifact_type?.replace(/_/g, ' ')}
                        </span>
                        <p className="text-xs text-gray-700 mt-0.5 line-clamp-2">
                          {s.proposed_text?.slice(0, 150)}{s.proposed_text?.length > 150 ? '...' : ''}
                        </p>
                      </div>
                      <button
                        type="button"
                        disabled={applyingIdx === `upload-${si}`}
                        onClick={async () => {
                          setApplyingIdx(`upload-${si}`)
                          try {
                            const applyResult = await applySuggestionByType(s)
                            if (applyResult.lpd_updated) {
                              toast.success(`Applied to ${s.artifact_type?.replace(/_/g, ' ')}${applyResult.lpd_change ? ` + KB "${applyResult.lpd_change.section}"` : ''}`)
                            } else {
                              toast.success(`Applied to ${s.artifact_type?.replace(/_/g, ' ')}`)
                            }
                          } catch {
                            toast.error('Failed to apply suggestion')
                          } finally {
                            setApplyingIdx(null)
                          }
                        }}
                        className="flex-shrink-0 px-2 py-1 text-[10px] font-medium bg-gray-900 text-white rounded hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed"
                      >
                        {applyingIdx === `upload-${si}` ? '...' : 'Apply'}
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
