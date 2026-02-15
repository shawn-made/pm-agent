import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ArtifactSync from './ArtifactSync'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  artifactSync: vi.fn(),
  applySuggestionByType: vi.fn(),
}))

import { artifactSync, applySuggestionByType } from '../services/api'

function renderPage() {
  return render(
    <ToastProvider>
      <ArtifactSync />
    </ToastProvider>
  )
}

const mockSuggestion = {
  artifact_type: 'RAID Log',
  change_type: 'add',
  section: 'Risks',
  proposed_text: 'Risk: budget overrun',
  confidence: 0.9,
  reasoning: 'Budget discussion detected',
}

describe('ArtifactSync', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Default clipboard mock
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  it('renders heading and empty state', () => {
    renderPage()
    expect(screen.getByText('Artifact Sync')).toBeInTheDocument()
    expect(
      screen.getByText('No suggestions yet. Paste some text above to get started.')
    ).toBeInTheDocument()
  })

  it('renders text input area', () => {
    renderPage()
    expect(
      screen.getByPlaceholderText('Paste meeting notes, transcripts, or project updates...')
    ).toBeInTheDocument()
  })

  it('submits text and displays suggestions', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      input_type: 'meeting_notes',
      session_id: 'sess-1',
      pii_detected: 2,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'We discussed the budget overrun.' } })
    fireEvent.click(screen.getByText('Analyze'))

    await waitFor(() => {
      expect(artifactSync).toHaveBeenCalledWith('We discussed the budget overrun.')
      expect(screen.getByText('RAID Log')).toBeInTheDocument()
      expect(screen.getByText('Budget discussion detected')).toBeInTheDocument()
    })
  })

  it('shows meta bar with input type and PII count', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      input_type: 'meeting_notes',
      session_id: 'sess-1',
      pii_detected: 3,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(screen.getByText('Analyze'))

    await waitFor(() => {
      expect(screen.getByText('meeting notes')).toBeInTheDocument()
      expect(screen.getByText('3 PII items anonymized')).toBeInTheDocument()
    })
  })

  it('shows "No PII detected" when pii_detected is 0', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      input_type: 'text',
      session_id: 'sess-1',
      pii_detected: 0,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(screen.getByText('Analyze'))

    await waitFor(() => {
      expect(screen.getByText('No PII detected')).toBeInTheDocument()
    })
  })

  it('shows error state on failure', async () => {
    artifactSync.mockRejectedValue(new Error('LLM call failed'))
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(screen.getByText('Analyze'))

    await waitFor(() => {
      expect(screen.getByText('LLM call failed')).toBeInTheDocument()
    })
  })

  it('shows info toast when no suggestions returned', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [],
      input_type: 'general_text',
      session_id: 'sess-1',
      pii_detected: 0,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'hello' } })
    fireEvent.click(screen.getByText('Analyze'))

    await waitFor(() => {
      expect(screen.getByText('No artifact updates found in this text')).toBeInTheDocument()
    })
  })

  it('calls applySuggestionByType when Apply is clicked', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      input_type: 'text',
      session_id: 'sess-1',
      pii_detected: 0,
    })
    applySuggestionByType.mockResolvedValue({ success: true })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(screen.getByText('Analyze'))

    await waitFor(() => {
      expect(screen.getByText('Apply')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(applySuggestionByType).toHaveBeenCalledWith(mockSuggestion)
    })
  })
})
