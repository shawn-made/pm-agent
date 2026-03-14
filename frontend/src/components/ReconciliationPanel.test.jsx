import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import ReconciliationPanel from './ReconciliationPanel'

// Mock the API module
vi.mock('../services/api', () => ({
  reconcileLPD: vi.fn(),
}))

import { reconcileLPD } from '../services/api'

function renderPanel(props = {}) {
  return render(
    <ReconciliationPanel onClose={vi.fn()} {...props} />
  )
}

const mockResult = {
  impacts: [
    {
      source_section: 'Decisions',
      target_section: 'Open Questions',
      impact_type: 'resolves',
      description: 'Decision D5 resolves Q3 about database choice',
      source_excerpt: 'Decided to use PostgreSQL',
      target_excerpt: 'Which database should we use?',
      suggested_action: 'Remove Q3 from Open Questions',
    },
    {
      source_section: 'Timeline & Milestones',
      target_section: 'Decisions',
      impact_type: 'contradicts',
      description: 'Timeline shows Phase 2 starting March but Decision D2 says April',
      source_excerpt: 'Phase 2: March 15',
      target_excerpt: 'D2: Phase 2 starts April 1',
      suggested_action: 'Align Timeline with Decision D2',
    },
    {
      source_section: 'Stakeholders',
      target_section: 'Risks',
      impact_type: 'requires_update',
      description: 'New stakeholder added but no corresponding risk assessment',
      source_excerpt: 'Added: VP of Engineering',
      target_excerpt: '',
      suggested_action: 'Add stakeholder risk entry',
    },
  ],
  sections_analyzed: 7,
  pii_detected: 0,
  session_id: 'recon-session-1',
}

describe('ReconciliationPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    reconcileLPD.mockReturnValue(new Promise(() => {}))
    renderPanel()
    expect(screen.getByText('Analyzing cross-section relationships...')).toBeInTheDocument()
  })

  it('shows error message on failure', async () => {
    reconcileLPD.mockRejectedValue(new Error('LLM error'))
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('LLM error')).toBeInTheDocument()
    })
  })

  it('displays impacts after loading', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/Decision D5 resolves Q3/)).toBeInTheDocument()
    })
    expect(screen.getByText(/Timeline shows Phase 2/)).toBeInTheDocument()
    expect(screen.getByText(/New stakeholder added/)).toBeInTheDocument()
  })

  it('shows summary with section count and impact count', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('7')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  it('groups impacts by type with correct headings', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Contradicts (1)')).toBeInTheDocument()
      expect(screen.getByText('Requires Update (1)')).toBeInTheDocument()
      expect(screen.getByText('Resolves (1)')).toBeInTheDocument()
    })
  })

  it('shows source and target section badges', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      // "Decisions" appears as both source and target badge across different impacts
      expect(screen.getAllByText('Decisions').length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText('Open Questions')).toBeInTheDocument()
    })
  })

  it('shows excerpts when available', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/Decided to use PostgreSQL/)).toBeInTheDocument()
      expect(screen.getByText(/Which database should we use/)).toBeInTheDocument()
    })
  })

  it('shows suggested actions', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/Remove Q3 from Open Questions/)).toBeInTheDocument()
    })
  })

  it('calls onClose when close button clicked', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    const onClose = vi.fn()
    renderPanel({ onClose })

    await waitFor(() => {
      expect(screen.getByText('LPD Reconciliation')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('Close'))
    expect(onClose).toHaveBeenCalled()
  })

  it('shows navigate button and calls handler', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    const onClose = vi.fn()
    const onNavigateToSection = vi.fn()
    renderPanel({ onClose, onNavigateToSection })

    await waitFor(() => {
      expect(screen.getAllByText(/Go to/).length).toBeGreaterThan(0)
    })

    fireEvent.click(screen.getAllByText(/Go to/)[0])
    expect(onNavigateToSection).toHaveBeenCalled()
    expect(onClose).toHaveBeenCalled()
  })

  it('shows empty state when no impacts', async () => {
    reconcileLPD.mockResolvedValue({
      ...mockResult,
      impacts: [],
    })
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText('No cross-section impacts detected.')).toBeInTheDocument()
    })
  })

  it('shows coaching hint when no impacts', async () => {
    reconcileLPD.mockResolvedValue({
      ...mockResult,
      impacts: [],
    })
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText(/normal for small or newly-created project documents/)).toBeInTheDocument()
    })
  })

  it('passes projectId to API call', async () => {
    reconcileLPD.mockResolvedValue(mockResult)
    renderPanel({ projectId: 'my-project' })

    await waitFor(() => {
      expect(reconcileLPD).toHaveBeenCalledWith('my-project')
    })
  })
})
