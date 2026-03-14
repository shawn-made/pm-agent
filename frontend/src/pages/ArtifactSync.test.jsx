import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import ArtifactSync from './ArtifactSync'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  applySuggestionByType: vi.fn(),
  appendToLPDSection: vi.fn(),
  submitJob: vi.fn(),
  getJobStatus: vi.fn(),
}))

import { applySuggestionByType, submitJob, getJobStatus } from '../services/api'

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

const mockSyncResult = {
  suggestions: [mockSuggestion],
  analysis: [],
  analysis_summary: null,
  lpd_updates: [],
  session_summary: null,
  input_type: 'meeting_notes',
  session_id: 'sess-1',
  pii_detected: 2,
  mode: 'extract',
  content_gate_active: true,
}

/** Helper: simulate submit → job complete flow */
async function submitAndCompleteJob(result = mockSyncResult) {
  submitJob.mockResolvedValue({ job_id: 'test-job', status: 'pending' })
  getJobStatus.mockResolvedValue({ status: 'completed', result })
}

// Mock localStorage
let store = {}
const mockLocalStorage = {
  getItem: vi.fn((key) => store[key] ?? null),
  setItem: vi.fn((key, value) => { store[key] = value }),
  removeItem: vi.fn((key) => { delete store[key] }),
}

beforeEach(() => {
  store = {}
  vi.stubGlobal('localStorage', mockLocalStorage)
  vi.clearAllMocks()
  vi.useFakeTimers()
  Object.assign(navigator, {
    clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('ArtifactSync', () => {
  it('renders heading and empty state', () => {
    renderPage()
    expect(screen.getByText('Process')).toBeInTheDocument()
    expect(
      screen.getByText('No suggestions yet. Paste some text above to get started.')
    ).toBeInTheDocument()
  })

  it('shows coaching hint about Knowledge Base in empty state', () => {
    renderPage()
    expect(
      screen.getByText(/populate your Knowledge Base first/)
    ).toBeInTheDocument()
  })

  it('renders text input area', () => {
    renderPage()
    expect(
      screen.getByPlaceholderText('Paste meeting notes, transcripts, or project updates...')
    ).toBeInTheDocument()
  })

  it('submits text via job and displays suggestions', async () => {
    await submitAndCompleteJob()
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'We discussed the budget overrun.' } })

    await act(async () => {
      fireEvent.click(getSubmitButton())
    })

    // Job submitted
    expect(submitJob).toHaveBeenCalledWith(
      'artifact_sync_extract', 'default',
      { text: 'We discussed the budget overrun.', project_id: 'default', mode: 'extract' }
    )

    // Poll completes — async version flushes microtasks from poll promise
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('RAID Log')).toBeInTheDocument()
    expect(screen.getByText('Budget discussion detected')).toBeInTheDocument()
  })

  it('shows meta bar with input type and PII count', async () => {
    await submitAndCompleteJob({
      ...mockSyncResult,
      pii_detected: 3,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    await act(async () => { fireEvent.click(getSubmitButton()) })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('meeting notes')).toBeInTheDocument()
    expect(screen.getByText('3 PII items anonymized')).toBeInTheDocument()
  })

  it('shows "No PII detected" when pii_detected is 0', async () => {
    await submitAndCompleteJob({
      ...mockSyncResult,
      pii_detected: 0,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    await act(async () => { fireEvent.click(getSubmitButton()) })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('No PII detected')).toBeInTheDocument()
  })

  it('shows error state on job failure', async () => {
    submitJob.mockResolvedValue({ job_id: 'fail-job', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'failed', error_message: 'LLM call failed' })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    await act(async () => { fireEvent.click(getSubmitButton()) })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('LLM call failed')).toBeInTheDocument()
  })

  it('shows info toast when no suggestions returned', async () => {
    await submitAndCompleteJob({
      ...mockSyncResult,
      suggestions: [],
      pii_detected: 0,
    })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'hello' } })
    await act(async () => { fireEvent.click(getSubmitButton()) })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('No artifact updates found in this text')).toBeInTheDocument()
  })

  it('calls applySuggestionByType when Apply is clicked', async () => {
    await submitAndCompleteJob()
    applySuggestionByType.mockResolvedValue({ success: true })
    renderPage()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    await act(async () => { fireEvent.click(getSubmitButton()) })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('Apply')).toBeInTheDocument()

    await act(async () => {
      fireEvent.click(screen.getByText('Apply'))
    })
    expect(applySuggestionByType).toHaveBeenCalledWith(mockSuggestion)
  })
})
