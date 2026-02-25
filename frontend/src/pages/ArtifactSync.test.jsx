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

/** Find the submit button (type="submit") — avoids conflict with mode toggle buttons. */
function getSubmitButton() {
  const allButtons = screen.getAllByRole('button')
  return allButtons.find((b) => b.getAttribute('type') === 'submit')
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
      analysis: [],
      analysis_summary: null,
      input_type: 'meeting_notes',
      session_id: 'sess-1',
      pii_detected: 2,
      mode: 'extract',
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'We discussed the budget overrun.' } })
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(artifactSync).toHaveBeenCalledWith('We discussed the budget overrun.', 'default', 'extract')
      expect(screen.getByText('RAID Log')).toBeInTheDocument()
      expect(screen.getByText('Budget discussion detected')).toBeInTheDocument()
    })
  })

  it('shows meta bar with input type and PII count', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      analysis: [],
      analysis_summary: null,
      input_type: 'meeting_notes',
      session_id: 'sess-1',
      pii_detected: 3,
      mode: 'extract',
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(screen.getByText('meeting notes')).toBeInTheDocument()
      expect(screen.getByText('3 PII items anonymized')).toBeInTheDocument()
    })
  })

  it('shows "No PII detected" when pii_detected is 0', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      analysis: [],
      analysis_summary: null,
      input_type: 'text',
      session_id: 'sess-1',
      pii_detected: 0,
      mode: 'extract',
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(getSubmitButton())

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
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(screen.getByText('LLM call failed')).toBeInTheDocument()
    })
  })

  it('shows info toast when no suggestions returned', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [],
      analysis: [],
      analysis_summary: null,
      input_type: 'general_text',
      session_id: 'sess-1',
      pii_detected: 0,
      mode: 'extract',
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'hello' } })
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(screen.getByText('No artifact updates found in this text')).toBeInTheDocument()
    })
  })

  it('calls applySuggestionByType when Apply is clicked', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      analysis: [],
      analysis_summary: null,
      input_type: 'text',
      session_id: 'sess-1',
      pii_detected: 0,
      mode: 'extract',
    })
    applySuggestionByType.mockResolvedValue({ success: true })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(screen.getByText('Apply')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(applySuggestionByType).toHaveBeenCalledWith(mockSuggestion)
    })
  })

  // --- Analyze mode tests ---

  it('displays analysis results in analyze mode', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [],
      analysis: [
        {
          category: 'strength',
          title: 'Clear structure',
          detail: 'The document is well organized.',
          priority: 'low',
          artifact_type: 'Status Report',
        },
        {
          category: 'gap',
          title: 'Missing blockers',
          detail: 'No blockers section found.',
          priority: 'high',
          artifact_type: 'Status Report',
        },
      ],
      analysis_summary: 'Good document but missing blockers.',
      input_type: 'status_update',
      session_id: 'sess-2',
      pii_detected: 0,
      mode: 'analyze',
    })
    renderPage()

    // Switch to analyze mode via the toggle button
    const allButtons = screen.getAllByRole('button')
    const analyzeToggle = allButtons.find(
      (b) => b.getAttribute('type') === 'button' && b.textContent === 'Analyze'
    )
    fireEvent.click(analyzeToggle)

    const textarea = screen.getByPlaceholderText('Paste a draft document for review...')
    fireEvent.change(textarea, { target: { value: 'draft status report' } })
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(artifactSync).toHaveBeenCalledWith('draft status report', 'default', 'analyze')
      expect(screen.getByText('Good document but missing blockers.')).toBeInTheDocument()
      expect(screen.getByText('Clear structure')).toBeInTheDocument()
      expect(screen.getByText('Missing blockers')).toBeInTheDocument()
    })
  })

  it('clears results when mode toggles', async () => {
    artifactSync.mockResolvedValue({
      suggestions: [mockSuggestion],
      analysis: [],
      analysis_summary: null,
      input_type: 'meeting_notes',
      session_id: 'sess-1',
      pii_detected: 0,
      mode: 'extract',
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'some text' } })
    fireEvent.click(getSubmitButton())

    await waitFor(() => {
      expect(screen.getByText('RAID Log')).toBeInTheDocument()
    })

    // Toggle to analyze mode — results should clear
    const allButtons = screen.getAllByRole('button')
    const analyzeToggle = allButtons.find(
      (b) => b.getAttribute('type') === 'button' && b.textContent === 'Analyze'
    )
    fireEvent.click(analyzeToggle)

    expect(screen.queryByText('RAID Log')).not.toBeInTheDocument()
    expect(
      screen.getByText('No suggestions yet. Paste some text above to get started.')
    ).toBeInTheDocument()
  })
})
