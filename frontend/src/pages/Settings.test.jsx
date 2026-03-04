import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Settings from './Settings'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  getSettings: vi.fn(),
  updateSettings: vi.fn(),
  getTranscriptWatcherStatus: vi.fn(),
  startTranscriptWatcher: vi.fn(),
  stopTranscriptWatcher: vi.fn(),
}))

import {
  getSettings,
  updateSettings,
  getTranscriptWatcherStatus,
  startTranscriptWatcher,
  stopTranscriptWatcher,
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
})
