/**
 * Settings page for configuring LLM provider, API keys, and custom sensitive terms.
 */
import { useState, useEffect } from 'react'
import { useToast } from '../components/Toast'
import { getSettings, updateSettings } from '../services/api'

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
  const toast = useToast()

  useEffect(() => {
    loadSettings()
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
      const payload = { llm_provider: llmProvider, sensitive_terms: sensitiveTerms }

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
    </div>
  )
}
