import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import RiskPredictionPanel from './RiskPredictionPanel'
import { ToastProvider } from './Toast'

// Mock the API module
vi.mock('../services/api', () => ({
  predictRisks: vi.fn(),
  applySuggestionByType: vi.fn(),
}))

import { predictRisks, applySuggestionByType } from '../services/api'

function renderPanel(props = {}) {
  return render(
    <ToastProvider>
      <RiskPredictionPanel onClose={vi.fn()} {...props} />
    </ToastProvider>
  )
}

const mockResult = {
  predictions: [
    {
      description: 'Timeline risk: Phase 2 milestone has no buffer',
      severity: 'high',
      evidence: 'Timeline section shows 3 sequential dependencies',
      confidence: 0.85,
      suggested_raid_entry: 'R-NEW | Timeline risk | High | Add buffer',
      category: 'timeline',
    },
    {
      description: 'Resource gap: No QA engineer assigned',
      severity: 'medium',
      evidence: 'Stakeholders section missing QA role',
      confidence: 0.7,
      suggested_raid_entry: 'R-NEW | Resource gap | Medium | Assign QA',
      category: 'resource',
    },
  ],
  project_health: 'needs_attention',
  pii_detected: 0,
  session_id: 'test-session',
}

describe('RiskPredictionPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    predictRisks.mockReturnValue(new Promise(() => {})) // Never resolves
    renderPanel()
    expect(screen.getByText('Analyzing project health...')).toBeInTheDocument()
  })

  it('shows error message on failure', async () => {
    predictRisks.mockRejectedValue(new Error('LLM unavailable'))
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('LLM unavailable')).toBeInTheDocument()
    })
  })

  it('displays predictions after loading', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Timeline risk: Phase 2 milestone has no buffer')).toBeInTheDocument()
    })
    expect(screen.getByText('Resource gap: No QA engineer assigned')).toBeInTheDocument()
  })

  it('shows project health summary', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Needs Attention')).toBeInTheDocument()
    })
    expect(screen.getByText('2')).toBeInTheDocument() // Risks Found count
  })

  it('shows severity badges', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('high')).toBeInTheDocument()
      expect(screen.getByText('medium')).toBeInTheDocument()
    })
  })

  it('shows confidence bars', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument()
      expect(screen.getByText('70%')).toBeInTheDocument()
    })
  })

  it('shows evidence text', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/Timeline section shows 3 sequential dependencies/)).toBeInTheDocument()
    })
  })

  it('adds prediction to RAID Log on click', async () => {
    predictRisks.mockResolvedValue(mockResult)
    applySuggestionByType.mockResolvedValue({ status: 'applied' })
    renderPanel()

    await waitFor(() => {
      expect(screen.getAllByText('Add to RAID Log')).toHaveLength(2)
    })

    fireEvent.click(screen.getAllByText('Add to RAID Log')[0])

    await waitFor(() => {
      expect(applySuggestionByType).toHaveBeenCalledWith(
        expect.objectContaining({
          artifact_type: 'RAID Log',
          section: 'Risks',
          proposed_text: 'R-NEW | Timeline risk | High | Add buffer',
        }),
        'default',
      )
    })
  })

  it('disables Add button after adding', async () => {
    predictRisks.mockResolvedValue(mockResult)
    applySuggestionByType.mockResolvedValue({ status: 'applied' })
    renderPanel()

    await waitFor(() => {
      expect(screen.getAllByText('Add to RAID Log')).toHaveLength(2)
    })

    fireEvent.click(screen.getAllByText('Add to RAID Log')[0])

    await waitFor(() => {
      expect(screen.getByText('Added')).toBeInTheDocument()
    })
  })

  it('dismisses prediction on click', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel()

    await waitFor(() => {
      expect(screen.getAllByText('Dismiss')).toHaveLength(2)
    })

    fireEvent.click(screen.getAllByText('Dismiss')[0])

    // First prediction should be gone
    expect(screen.queryByText('Timeline risk: Phase 2 milestone has no buffer')).not.toBeInTheDocument()
    // Second should remain
    expect(screen.getByText('Resource gap: No QA engineer assigned')).toBeInTheDocument()
  })

  it('calls onClose when close button clicked', async () => {
    predictRisks.mockResolvedValue(mockResult)
    const onClose = vi.fn()
    renderPanel({ onClose })

    await waitFor(() => {
      expect(screen.getByText('AI Risk Prediction')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('Close'))
    expect(onClose).toHaveBeenCalled()
  })

  it('shows empty state when no predictions', async () => {
    predictRisks.mockResolvedValue({
      ...mockResult,
      predictions: [],
      project_health: 'healthy',
    })
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText('No additional risks predicted.')).toBeInTheDocument()
    })
  })

  it('passes projectId to API call', async () => {
    predictRisks.mockResolvedValue(mockResult)
    renderPanel({ projectId: 'my-project' })

    await waitFor(() => {
      expect(predictRisks).toHaveBeenCalledWith('my-project')
    })
  })
})
