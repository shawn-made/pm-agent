import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import ReviewPanel from './ReviewPanel'
import { ToastProvider } from './Toast'

// Mock the API module
vi.mock('../services/api', () => ({
  skepticalReview: vi.fn(),
}))

import { skepticalReview } from '../services/api'

function renderPanel(props = {}) {
  return render(
    <ToastProvider>
      <ReviewPanel onClose={vi.fn()} {...props} />
    </ToastProvider>
  )
}

const mockResult = {
  findings: [
    {
      category: 'contradiction',
      severity: 'high',
      title: 'Phase 2 date conflict',
      description: 'Overview says Phase 2 starts March 15 but Timeline section says April 1.',
      evidence: "Overview: 'Phase 2 begins March 15' vs Timeline: 'Phase 2 target: April 1'",
      recommendation: 'Confirm Phase 2 start date with sponsor.',
    },
    {
      category: 'blind_spot',
      severity: 'medium',
      title: 'No data validation strategy',
      description: 'Project integrates 6 source systems but has no documented data quality plan.',
      evidence: "Overview: '6 source systems' — Risks: no data quality mention",
      recommendation: 'Add data validation checkpoints to Timeline.',
    },
    {
      category: 'timeline_risk',
      severity: 'low',
      title: 'Tight milestone spacing',
      description: 'M3 and M4 are only 1 week apart with a dependency chain.',
      evidence: "Timeline: 'M3: March 20' and 'M4: March 27, depends on M3'",
      recommendation: 'Add buffer between M3 and M4.',
    },
  ],
  sections_analyzed: 7,
  artifacts_analyzed: 2,
  pii_detected: 3,
  session_id: 'test-session',
}

describe('ReviewPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    skepticalReview.mockReturnValue(new Promise(() => {}))
    renderPanel()
    expect(screen.getByText('Cross-referencing your project documents...')).toBeInTheDocument()
  })

  it('shows error message on failure', async () => {
    skepticalReview.mockRejectedValue(new Error('LLM unavailable'))
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('LLM unavailable')).toBeInTheDocument()
    })
  })

  it('displays findings after loading', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Phase 2 date conflict')).toBeInTheDocument()
    })
    expect(screen.getByText('No data validation strategy')).toBeInTheDocument()
    expect(screen.getByText('Tight milestone spacing')).toBeInTheDocument()
  })

  it('groups findings by category', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/Contradiction/)).toBeInTheDocument()
      expect(screen.getByText(/Blind Spot/)).toBeInTheDocument()
      expect(screen.getByText(/Timeline Risk/)).toBeInTheDocument()
    })
  })

  it('shows summary bar with counts', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument() // Findings count
      expect(screen.getByText('7')).toBeInTheDocument() // Sections
      expect(screen.getByText('2')).toBeInTheDocument() // Artifacts
    })
  })

  it('shows severity badges', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('high')).toBeInTheDocument()
      expect(screen.getByText('medium')).toBeInTheDocument()
      expect(screen.getByText('low')).toBeInTheDocument()
    })
  })

  it('expands finding details on click', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getAllByText('Details')).toHaveLength(3)
    })

    fireEvent.click(screen.getAllByText('Details')[0])

    await waitFor(() => {
      expect(screen.getByText('Evidence')).toBeInTheDocument()
      expect(screen.getByText('Recommendation')).toBeInTheDocument()
    })
  })

  it('dismisses finding on click', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel()

    await waitFor(() => {
      expect(screen.getAllByText('Dismiss')).toHaveLength(3)
    })

    fireEvent.click(screen.getAllByText('Dismiss')[0])

    expect(screen.queryByText('Phase 2 date conflict')).not.toBeInTheDocument()
    expect(screen.getByText('No data validation strategy')).toBeInTheDocument()
  })

  it('calls onClose when close button clicked', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    const onClose = vi.fn()
    renderPanel({ onClose })

    await waitFor(() => {
      expect(screen.getByText('Pressure Test')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('Close'))
    expect(onClose).toHaveBeenCalled()
  })

  it('shows empty state when no findings', async () => {
    skepticalReview.mockResolvedValue({
      ...mockResult,
      findings: [],
    })
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText('No issues found.')).toBeInTheDocument()
    })
  })

  it('passes projectId to API call', async () => {
    skepticalReview.mockResolvedValue(mockResult)
    renderPanel({ projectId: 'my-project' })

    await waitFor(() => {
      expect(skepticalReview).toHaveBeenCalledWith('my-project')
    })
  })
})
