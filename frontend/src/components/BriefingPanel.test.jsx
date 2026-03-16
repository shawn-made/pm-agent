import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import BriefingPanel from './BriefingPanel'

vi.mock('../services/api', () => ({
  getBriefing: vi.fn(),
  refreshBriefing: vi.fn(),
}))

import { getBriefing, refreshBriefing } from '../services/api'

const mockBriefing = {
  attention_items: [
    {
      title: 'Stale Timeline',
      detail: 'Timeline section is 12 days old',
      source_section: 'Timeline & Milestones',
      severity: 'high',
      category: 'staleness',
    },
    {
      title: 'Unresolved question',
      detail: 'Open question about scope',
      source_section: 'Open Questions',
      severity: 'medium',
      category: 'gap',
    },
  ],
  upcoming_dates: [
    {
      description: 'API milestone deadline',
      date_text: 'March 20',
      source_section: 'Timeline & Milestones',
      urgency: 'imminent',
    },
  ],
  contradictions: [
    {
      description: 'Phase 2 date mismatch',
      section_a: 'Timeline & Milestones',
      section_b: 'Decisions',
      suggested_resolution: 'Align the dates',
    },
  ],
  suggested_next_action: 'Update the Timeline section first.',
  generated_at: '2026-03-16T10:00:00Z',
  session_id: 'test-session',
  from_cache: false,
}

describe('BriefingPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state initially', () => {
    getBriefing.mockReturnValue(new Promise(() => {})) // never resolves
    render(<BriefingPanel />)
    // Loading skeleton should be present (animated pulse)
    const container = document.querySelector('.animate-pulse')
    expect(container).toBeTruthy()
  })

  it('renders briefing content on success', async () => {
    getBriefing.mockResolvedValue(mockBriefing)
    render(<BriefingPanel />)

    await waitFor(() => {
      expect(screen.getByText('Project Briefing')).toBeTruthy()
    })

    // Attention items
    expect(screen.getByText('Stale Timeline')).toBeTruthy()
    expect(screen.getByText('Unresolved question')).toBeTruthy()

    // Upcoming dates
    expect(screen.getByText('March 20')).toBeTruthy()
    expect(screen.getByText('API milestone deadline')).toBeTruthy()

    // Contradictions
    expect(screen.getByText('Phase 2 date mismatch')).toBeTruthy()

    // Suggested next action
    expect(screen.getByText(/Update the Timeline section first/)).toBeTruthy()
  })

  it('shows error state on API failure', async () => {
    getBriefing.mockRejectedValue(new Error('502: LLM call failed'))
    render(<BriefingPanel />)

    await waitFor(() => {
      expect(screen.getByText('Retry')).toBeTruthy()
    })
    expect(screen.getByText(/check your LLM configuration/)).toBeTruthy()
  })

  it('calls refreshBriefing when refresh button is clicked', async () => {
    getBriefing.mockResolvedValue(mockBriefing)
    refreshBriefing.mockResolvedValue({ ...mockBriefing, from_cache: false })

    render(<BriefingPanel />)

    await waitFor(() => {
      expect(screen.getByText('Refresh')).toBeTruthy()
    })

    fireEvent.click(screen.getByText('Refresh'))
    await waitFor(() => {
      expect(refreshBriefing).toHaveBeenCalledWith('default')
    })
  })

  it('collapses and expands when header is clicked', async () => {
    getBriefing.mockResolvedValue(mockBriefing)
    render(<BriefingPanel />)

    await waitFor(() => {
      expect(screen.getByText('Stale Timeline')).toBeTruthy()
    })

    // Click to collapse
    fireEvent.click(screen.getByText('Project Briefing'))

    // Content should be hidden
    expect(screen.queryByText('Stale Timeline')).toBeNull()

    // Click to expand
    fireEvent.click(screen.getByText('Project Briefing'))
    expect(screen.getByText('Stale Timeline')).toBeTruthy()
  })

  it('shows cached indicator when from_cache is true', async () => {
    getBriefing.mockResolvedValue({ ...mockBriefing, from_cache: true })
    render(<BriefingPanel />)

    await waitFor(() => {
      expect(screen.getByText('(cached)')).toBeTruthy()
    })
  })

  it('renders empty state when project is healthy', async () => {
    getBriefing.mockResolvedValue({
      attention_items: [],
      upcoming_dates: [],
      contradictions: [],
      suggested_next_action: 'Everything looks good.',
      generated_at: '2026-03-16T10:00:00Z',
      session_id: 'test-session',
      from_cache: false,
    })
    render(<BriefingPanel />)

    await waitFor(() => {
      expect(screen.getByText(/Everything looks good/)).toBeTruthy()
    })
    expect(screen.getByText(/Your project looks healthy/)).toBeTruthy()
  })
})
