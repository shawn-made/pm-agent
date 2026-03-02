/**
 * Auto-resizing text area with submit, clear, mode toggle, and character count for user input.
 */
import { useState, useRef, useEffect } from 'react'

const PLACEHOLDERS = {
  extract: 'Paste meeting notes, transcripts, or project updates...',
  analyze: 'Paste a draft document for review...',
  log_session: 'Paste session conclusions, decisions, or discussion outcomes...',
}

/**
 * @param {Object} props
 * @param {function} props.onSubmit - Called with the text string when the user submits
 * @param {boolean} props.isLoading - Disables input and shows spinner when true
 * @param {string} props.mode - 'extract' or 'analyze'
 * @param {function} props.onModeChange - Called with new mode string
 */
export default function TextInput({ onSubmit, isLoading, mode = 'extract', onModeChange }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 400) + 'px'
    }
  }, [text])

  function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim() || isLoading) return
    onSubmit(text)
  }

  function handleClear() {
    setText('')
    textareaRef.current?.focus()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={PLACEHOLDERS[mode] || PLACEHOLDERS.extract}
          disabled={isLoading}
          rows={6}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-sm leading-relaxed disabled:bg-gray-50 disabled:text-gray-400"
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">
            {text.length.toLocaleString()} characters
          </span>

          {/* Mode toggle */}
          {onModeChange && (
            <div className="flex items-center gap-0.5 bg-gray-100 rounded-lg p-0.5">
              <button
                type="button"
                onClick={() => onModeChange('extract')}
                className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                  mode === 'extract'
                    ? 'bg-gray-900 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Extract
              </button>
              <button
                type="button"
                onClick={() => onModeChange('analyze')}
                className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                  mode === 'analyze'
                    ? 'bg-gray-900 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Analyze
              </button>
              <button
                type="button"
                onClick={() => onModeChange('log_session')}
                className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                  mode === 'log_session'
                    ? 'bg-gray-900 text-white shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Log
              </button>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {text.length > 0 && (
            <button
              type="button"
              onClick={handleClear}
              disabled={isLoading}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 disabled:text-gray-300"
            >
              Clear
            </button>
          )}
          <button
            type="submit"
            disabled={!text.trim() || isLoading}
            className="px-6 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {mode === 'analyze' ? 'Analyzing...' : mode === 'log_session' ? 'Logging...' : 'Extracting...'}
              </span>
            ) : mode === 'analyze' ? 'Analyze' : mode === 'log_session' ? 'Log Session' : 'Extract'}
          </button>
        </div>
      </div>
    </form>
  )
}
