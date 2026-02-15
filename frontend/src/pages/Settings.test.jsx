import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Settings from './Settings'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  getSettings: vi.fn(),
  updateSettings: vi.fn(),
}))

import { getSettings, updateSettings } from '../services/api'

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
