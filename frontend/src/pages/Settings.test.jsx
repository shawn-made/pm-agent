import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Settings from './Settings'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  getSettings: vi.fn(),
  updateSettings: vi.fn(),
  getOllamaStatus: vi.fn(),
  getOllamaInfo: vi.fn(),
  startOllama: vi.fn(),
  getTranscriptWatcherStatus: vi.fn(),
  startTranscriptWatcher: vi.fn(),
  stopTranscriptWatcher: vi.fn(),
  applySuggestionByType: vi.fn(),
  getTranscriptWatcherResults: vi.fn(),
  uploadTranscriptFile: vi.fn(),
}))

import {
  getSettings,
  updateSettings,
  getOllamaInfo,
  startOllama,
  getTranscriptWatcherStatus,
  startTranscriptWatcher,
  stopTranscriptWatcher,
  applySuggestionByType,
  getTranscriptWatcherResults,
  uploadTranscriptFile,
} from '../services/api'

function renderSettings() {
  return render(
    <ToastProvider>
      <Settings />
    </ToastProvider>
  )
}

describe('Settings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getTranscriptWatcherStatus.mockResolvedValue({
      running: false,
      watch_folder: null,
      mode: 'extract',
      files_processed: 0,
      recent_files: [],
    })
  })

  it('shows loading state initially', () => {
    getSettings.mockReturnValue(new Promise(() => {})) // never resolves
    renderSettings()
    expect(screen.getByText('Loading settings...')).toBeInTheDocument()
  })

  it('loads and displays settings', async () => {
    getSettings.mockResolvedValue({
      settings: {
        llm_provider: 'gemini',
        anthropic_api_key: '****key',
        google_ai_api_key: '****gkey',
        sensitive_terms: 'ProjectX, ClientY',
      },
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })
    // Gemini radio should be checked
    const geminiRadio = screen.getByDisplayValue('gemini')
    expect(geminiRadio).toBeChecked()
  })

  it('shows error toast when loading fails', async () => {
    getSettings.mockRejectedValue(new Error('Network error'))
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Failed to load settings')).toBeInTheDocument()
    })
  })

  it('toggles LLM provider', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })

    const geminiRadio = screen.getByDisplayValue('gemini')
    fireEvent.click(geminiRadio)
    expect(geminiRadio).toBeChecked()
  })

  it('saves settings successfully', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    updateSettings.mockResolvedValue({ success: true })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      expect(updateSettings).toHaveBeenCalledWith(
        expect.objectContaining({ llm_provider: 'claude' })
      )
      expect(screen.getByText('Settings saved')).toBeInTheDocument()
    })
  })

  it('shows error toast when save fails', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    updateSettings.mockRejectedValue(new Error('save failed'))
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      expect(screen.getByText('Failed to save settings')).toBeInTheDocument()
    })
  })

  it('shows warning when Claude selected without API key', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('missing-key-warning')).toBeInTheDocument()
      expect(screen.getByText(/Anthropic API key required/)).toBeInTheDocument()
    })
  })

  it('shows warning when Gemini selected without API key', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'gemini' } })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('missing-key-warning')).toBeInTheDocument()
      expect(screen.getByText(/Google AI API key required/)).toBeInTheDocument()
    })
  })

  it('hides warning when API key is present', async () => {
    getSettings.mockResolvedValue({
      settings: { llm_provider: 'claude', anthropic_api_key: 'sk-ant-real-key' },
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })
    expect(screen.queryByTestId('missing-key-warning')).not.toBeInTheDocument()
  })

  it('does not send masked API keys', async () => {
    getSettings.mockResolvedValue({
      settings: {
        llm_provider: 'claude',
        anthropic_api_key: '****masked',
        google_ai_api_key: '****masked',
      },
    })
    updateSettings.mockResolvedValue({ success: true })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      const payload = updateSettings.mock.calls[0][0]
      expect(payload).not.toHaveProperty('anthropic_api_key')
      expect(payload).not.toHaveProperty('google_ai_api_key')
    })
  })
})

describe('Settings — Ollama', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getTranscriptWatcherStatus.mockResolvedValue({
      running: false,
      watch_folder: null,
      mode: 'extract',
      files_processed: 0,
      recent_files: [],
    })
  })

  it('shows Ollama radio option', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByDisplayValue('ollama')).toBeInTheDocument()
      expect(screen.getByText('Ollama (Local)')).toBeInTheDocument()
    })
  })

  it('shows Ollama config panel when Ollama is selected', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama', ollama_model: 'llama3.2' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: true, models: ['llama3.2'], error: null })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Ollama Configuration')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('llama3.2')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('http://localhost:11434')).toBeInTheDocument()
    })
  })

  it('hides Ollama config when other provider selected', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Ollama Configuration')).not.toBeInTheDocument()
    })
  })

  it('checks Ollama info when selecting Ollama', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'claude' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: true, models: ['llama3.2', 'mistral'], error: null })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByDisplayValue('ollama'))
    await waitFor(() => {
      expect(getOllamaInfo).toHaveBeenCalled()
    })
  })

  it('auto-checks status when Ollama is loaded as active provider', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: true, models: ['llama3.2', 'mistral'], error: null })
    renderSettings()
    await waitFor(() => {
      expect(getOllamaInfo).toHaveBeenCalled()
      expect(screen.getByTestId('ollama-status-dot')).toBeInTheDocument()
    })
  })

  it('shows Test Connection button', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: false, models: [], error: 'Cannot connect' })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Test Connection')).toBeInTheDocument()
    })
  })

  it('includes ollama settings in save payload', async () => {
    getSettings.mockResolvedValue({
      settings: { llm_provider: 'ollama', ollama_base_url: 'http://myhost:11434', ollama_model: 'phi3' },
    })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: true, models: ['phi3'], error: null })
    updateSettings.mockResolvedValue({ success: true })
    renderSettings()
    await waitFor(() => {
      expect(screen.queryByText('Loading settings...')).not.toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      const payload = updateSettings.mock.calls[0][0]
      expect(payload.ollama_base_url).toBe('http://myhost:11434')
      expect(payload.ollama_model).toBe('phi3')
    })
  })

  it('shows not-installed state when Ollama is not installed', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama' } })
    getOllamaInfo.mockResolvedValue({ installed: false, install_path: null, running: false, models: [], error: 'Cannot connect' })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('ollama-not-installed')).toBeInTheDocument()
      expect(screen.getByText('Ollama is not installed')).toBeInTheDocument()
      expect(screen.getByText('ollama.com')).toBeInTheDocument()
    })
  })

  it('shows start button when Ollama is installed but not running', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: false, models: [], error: 'Cannot connect' })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('ollama-not-running')).toBeInTheDocument()
      expect(screen.getByText('Start Ollama')).toBeInTheDocument()
    })
  })

  it('shows no-models state when Ollama is running with no models', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: true, models: [], error: null })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('ollama-no-models')).toBeInTheDocument()
      expect(screen.getByText(/no models are installed/)).toBeInTheDocument()
    })
  })

  it('starts Ollama when start button is clicked', async () => {
    getSettings.mockResolvedValue({ settings: { llm_provider: 'ollama' } })
    getOllamaInfo.mockResolvedValue({ installed: true, install_path: '/usr/local/bin/ollama', running: false, models: [], error: 'Cannot connect' })
    startOllama.mockResolvedValue({ started: true, error: null })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Start Ollama')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Start Ollama'))
    await waitFor(() => {
      expect(startOllama).toHaveBeenCalled()
    })
  })
})

describe('Settings — Transcript Watcher', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getTranscriptWatcherStatus.mockResolvedValue({
      running: false,
      watch_folder: null,
      mode: 'extract',
      files_processed: 0,
      recent_files: [],
    })
  })

  it('renders Transcript Watcher section', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Transcript Watcher')).toBeInTheDocument()
    })
  })

  it('shows stopped status when watcher is not running', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Stopped')).toBeInTheDocument()
    })
  })

  it('shows running status when watcher is active', async () => {
    getSettings.mockResolvedValue({ settings: { transcript_watch_folder: '/tmp/transcripts' } })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp/transcripts',
      mode: 'extract',
      files_processed: 3,
      recent_files: [],
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Running')).toBeInTheDocument()
      expect(screen.getByText('(3 files processed)')).toBeInTheDocument()
    })
  })

  it('shows Start button when stopped', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Start')).toBeInTheDocument()
    })
  })

  it('shows Stop button when running', async () => {
    getSettings.mockResolvedValue({ settings: { transcript_watch_folder: '/tmp' } })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp',
      mode: 'extract',
      files_processed: 0,
      recent_files: [],
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Stop')).toBeInTheDocument()
    })
  })

  it('starts watcher on Start click', async () => {
    getSettings.mockResolvedValue({ settings: { transcript_watch_folder: '/tmp/transcripts' } })
    updateSettings.mockResolvedValue({ success: true })
    startTranscriptWatcher.mockResolvedValue({ status: 'started' })
    // After start, return running status
    getTranscriptWatcherStatus
      .mockResolvedValueOnce({ running: false, watch_folder: null, mode: 'extract', files_processed: 0, recent_files: [] })
      .mockResolvedValueOnce({ running: true, watch_folder: '/tmp/transcripts', mode: 'extract', files_processed: 0, recent_files: [] })

    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Start')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Start'))
    await waitFor(() => {
      expect(startTranscriptWatcher).toHaveBeenCalled()
      expect(screen.getByText('Transcript watcher started')).toBeInTheDocument()
    })
  })

  it('stops watcher on Stop click', async () => {
    getSettings.mockResolvedValue({ settings: { transcript_watch_folder: '/tmp' } })
    stopTranscriptWatcher.mockResolvedValue({ status: 'stopped' })
    getTranscriptWatcherStatus
      .mockResolvedValueOnce({ running: true, watch_folder: '/tmp', mode: 'extract', files_processed: 0, recent_files: [] })
      .mockResolvedValueOnce({ running: false, watch_folder: null, mode: 'extract', files_processed: 0, recent_files: [] })

    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Stop')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Stop'))
    await waitFor(() => {
      expect(stopTranscriptWatcher).toHaveBeenCalled()
      expect(screen.getByText('Transcript watcher stopped')).toBeInTheDocument()
    })
  })

  it('shows recent files when available', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp',
      mode: 'extract',
      files_processed: 2,
      recent_files: [
        { file: 'meeting.vtt', status: 'processed', timestamp: '2026-03-01T10:00:00Z' },
        { file: 'notes.txt', status: 'skipped', timestamp: '2026-03-01T09:00:00Z' },
      ],
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Recent Files')).toBeInTheDocument()
      expect(screen.getByText('meeting.vtt')).toBeInTheDocument()
      expect(screen.getByText('notes.txt')).toBeInTheDocument()
    })
  })

  it('loads watch folder from settings', async () => {
    getSettings.mockResolvedValue({
      settings: { transcript_watch_folder: '/Users/test/Transcripts' },
    })
    renderSettings()
    await waitFor(() => {
      const input = screen.getByPlaceholderText('/Users/you/Transcripts')
      expect(input).toHaveValue('/Users/test/Transcripts')
    })
  })

  it('expands a recent file to show suggestions', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp',
      mode: 'extract',
      files_processed: 1,
      recent_files: [
        {
          file: 'standup.vtt',
          status: 'processed',
          mode: 'extract',
          suggestion_count: 2,
          sync_result: {
            suggestions: [
              { artifact_type: 'raid_log', proposed_text: 'Risk: timeline delay from vendor' },
              { artifact_type: 'status_report', proposed_text: 'Sprint 5 on track' },
            ],
            input_type: 'transcript',
            pii_detected: false,
            session_id: 'abc123',
            mode: 'extract',
          },
        },
      ],
    })
    getTranscriptWatcherResults.mockResolvedValue({
      results: [
        {
          file: 'standup.vtt',
          status: 'processed',
          mode: 'extract',
          suggestion_count: 2,
          sync_result: {
            suggestions: [
              { artifact_type: 'raid_log', proposed_text: 'Risk: timeline delay from vendor' },
              { artifact_type: 'status_report', proposed_text: 'Sprint 5 on track' },
            ],
          },
        },
      ],
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('standup.vtt')).toBeInTheDocument()
    })

    // Click to expand
    fireEvent.click(screen.getByText('standup.vtt'))
    await waitFor(() => {
      expect(screen.getByText('raid log')).toBeInTheDocument()
      expect(screen.getByText('status report')).toBeInTheDocument()
    })
  })

  it('shows error reason for failed files', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp',
      mode: 'extract',
      files_processed: 0,
      recent_files: [
        { file: 'bad.vtt', status: 'error', reason: 'Invalid format' },
      ],
    })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('bad.vtt')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('bad.vtt'))
    await waitFor(() => {
      expect(screen.getByText('Invalid format')).toBeInTheDocument()
    })
  })

  it('applies a suggestion from expanded results', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp',
      mode: 'extract',
      files_processed: 1,
      recent_files: [
        {
          file: 'retro.vtt',
          status: 'processed',
          mode: 'extract',
          suggestion_count: 1,
          sync_result: {
            suggestions: [
              { artifact_type: 'meeting_notes', proposed_text: 'Action: follow up with design team' },
            ],
          },
        },
      ],
    })
    getTranscriptWatcherResults.mockResolvedValue({ results: [] })
    applySuggestionByType.mockResolvedValue({ status: 'applied', artifact_type: 'meeting_notes', lpd_updated: false })

    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('retro.vtt')).toBeInTheDocument()
    })

    // Expand and click Apply
    fireEvent.click(screen.getByText('retro.vtt'))
    await waitFor(() => {
      expect(screen.getByText('Apply')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(applySuggestionByType).toHaveBeenCalledWith(
        expect.objectContaining({ artifact_type: 'meeting_notes' })
      )
      expect(screen.getByText('Applied to meeting notes')).toBeInTheDocument()
    })
  })

  it('collapses expanded file on second click', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    getTranscriptWatcherStatus.mockResolvedValue({
      running: true,
      watch_folder: '/tmp',
      mode: 'extract',
      files_processed: 1,
      recent_files: [
        {
          file: 'call.vtt',
          status: 'processed',
          mode: 'extract',
          suggestion_count: 1,
          sync_result: {
            suggestions: [
              { artifact_type: 'raid_log', proposed_text: 'Risk item found' },
            ],
          },
        },
      ],
    })
    getTranscriptWatcherResults.mockResolvedValue({ results: [] })

    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('call.vtt')).toBeInTheDocument()
    })

    // Expand
    fireEvent.click(screen.getByText('call.vtt'))
    await waitFor(() => {
      expect(screen.getByText('raid log')).toBeInTheDocument()
    })

    // Collapse
    fireEvent.click(screen.getByText('call.vtt'))
    await waitFor(() => {
      expect(screen.queryByText('raid log')).not.toBeInTheDocument()
    })
  })
})

describe('Settings — Drop Zone', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getTranscriptWatcherStatus.mockResolvedValue({
      running: false,
      watch_folder: null,
      mode: 'extract',
      files_processed: 0,
      recent_files: [],
    })
  })

  it('renders drop zone with instructions', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText(/Drop a transcript file here/)).toBeInTheDocument()
    })
  })

  it('processes a dropped VTT file', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    uploadTranscriptFile.mockResolvedValue({
      file: 'standup.vtt',
      status: 'processed',
      suggestion_count: 2,
      sync_result: {
        suggestions: [
          { artifact_type: 'raid_log', proposed_text: 'Risk found in standup' },
          { artifact_type: 'status_report', proposed_text: 'Sprint progress update' },
        ],
      },
    })

    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('drop-zone')).toBeInTheDocument()
    })

    const fileContent = 'WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nHello'
    const file = { name: 'standup.vtt', text: () => Promise.resolve(fileContent) }
    const dropZone = screen.getByTestId('drop-zone')

    fireEvent.drop(dropZone, {
      dataTransfer: { files: [file] },
    })

    await waitFor(() => {
      expect(uploadTranscriptFile).toHaveBeenCalledWith('standup.vtt', fileContent)
      expect(screen.getByTestId('upload-result')).toBeInTheDocument()
      expect(screen.getByText('raid log')).toBeInTheDocument()
    })
  })

  it('rejects unsupported file types', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('drop-zone')).toBeInTheDocument()
    })

    const file = new File(['fake pdf'], 'document.pdf', { type: 'application/pdf' })
    fireEvent.drop(screen.getByTestId('drop-zone'), {
      dataTransfer: { files: [file] },
    })

    await waitFor(() => {
      expect(screen.getByText('Unsupported file type. Accepted: .vtt, .srt, .txt')).toBeInTheDocument()
    })
    expect(uploadTranscriptFile).not.toHaveBeenCalled()
  })

  it('shows error when upload fails', async () => {
    getSettings.mockResolvedValue({ settings: {} })
    uploadTranscriptFile.mockRejectedValue(new Error('Network error'))

    renderSettings()
    await waitFor(() => {
      expect(screen.getByTestId('drop-zone')).toBeInTheDocument()
    })

    const file = { name: 'notes.txt', text: () => Promise.resolve('content') }
    fireEvent.drop(screen.getByTestId('drop-zone'), {
      dataTransfer: { files: [file] },
    })

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })
})
