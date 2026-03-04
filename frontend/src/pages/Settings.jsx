/**
 * Settings page for configuring LLM provider, API keys, and custom sensitive terms.
 */
import { useState, useEffect, useCallback } from 'react'
import { useToast } from '../components/ToastContext'
import {
  getSettings,
  updateSettings,
  getTranscriptWatcherStatus,
  startTranscriptWatcher,
  stopTranscriptWatcher,
} from '../services/api'

/** Settings page — loads current config on mount, saves changes via PUT /api/settings. */
export default function Settings() {
  const [llmProvider, setLlmProvider] = useState('claude')
  const [anthropicKey, setAnthropicKey] = useState('')
  const [geminiKey, setGeminiKey] = useState('')
  const [sensitiveTerms, setSensitiveTerms] = useState('')
  const [showAnthropicKey, setShowAnthropicKey] = useState(false)
  const [showGeminiKey, setShowGeminiKey] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Transcript watcher state
  const [watchFolder, setWatchFolder] = useState('')
  const [watchMode, setWatchMode] = useState('extract')
  const [watcherStatus, setWatcherStatus] = useState(null)
  const [isTogglingWatcher, setIsTogglingWatcher] = useState(false)

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
      setWatchFolder(s.transcript_watch_folder || '')
      setWatchMode(s.transcript_auto_mode || 'extract')
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
            ].map(opt => (
              <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="llm_provider"
                  value={opt.value}
                  checked={llmProvider === opt.value}
                  onChange={(e) => setLlmProvider(e.target.value)}
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
            <input
              id="watch-folder"
              type="text"
              value={watchFolder}
              onChange={(e) => setWatchFolder(e.target.value)}
              placeholder="/Users/you/Transcripts"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
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
                  <li key={i} className="flex items-center gap-2 text-xs">
                    <span className={`inline-block w-1.5 h-1.5 rounded-full ${
                      f.status === 'processed' ? 'bg-green-400' :
                      f.status === 'skipped' ? 'bg-yellow-400' : 'bg-red-400'
                    }`} />
                    <span className="text-gray-700 truncate">{f.file}</span>
                    <span className="text-gray-400">{f.status}</span>
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
