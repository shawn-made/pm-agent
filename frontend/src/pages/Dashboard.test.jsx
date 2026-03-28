import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from './Dashboard'
import { ToastProvider } from '../components/Toast'

vi.mock('../context/ChatContext', () => ({
  useChat: () => ({ isOpen: false, openChat: vi.fn(), closeChat: vi.fn(), toggleChat: vi.fn() }),
  ChatProvider: ({ children }) => children,
}))

// Mock the API module
vi.mock('../services/api', () => ({
  getLPDStaleness: vi.fn(),
  getLPDSections: vi.fn(),
  getBriefing: vi.fn(),
}))

import { getLPDStaleness, getLPDSections, getBriefing } from '../services/api'

function renderDashboard() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Dashboard />
      </ToastProvider>
    </MemoryRouter>
  )
}

const mockStaleness = [
  { section_name: 'Overview', days_since_update: 3 },
  { section_name: 'Risks', days_since_update: 18 },
  { section_name: 'Decisions', days_since_update: 5 },
  { section_name: 'Timeline & Milestones', days_since_update: 32 },
  { section_name: 'Open Questions', days_since_update: 10 },
  { section_name: 'Stakeholders', days_since_update: 2 },
  { section_name: 'Recent Context', days_since_update: 1 },
]

const mockSections = {
  sections: {
    'Overview': 'Project overview content',
    'Risks': 'Risk entries',
    'Decisions': 'Decision log',
    'Timeline & Milestones': 'M1: Feb, M2: March',
    'Open Questions': 'Q1: Budget?',
    'Stakeholders': 'PM: Jordan',
    'Recent Context': 'Sprint 4 completed',
  },
}

const mockBriefing = {
  attention_items: [
    { severity: 'high', description: 'Risks section is 18 days stale', source_section: 'Risks' },
    { severity: 'medium', description: 'Open question about budget unresolved', source_section: 'Open Questions' },
  ],
  upcoming_dates: [
    { description: 'M2: Phase 2 kickoff', date: '2026-04-01' },
  ],
  contradictions: [
    { description: 'Phase 2 date conflict', section_a: 'Overview', section_b: 'Timeline' },
  ],
  suggested_next_action: 'Update the Risks section — 18 days stale.',
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    getLPDStaleness.mockReturnValue(new Promise(() => {}))
    getLPDSections.mockReturnValue(new Promise(() => {}))
    getBriefing.mockReturnValue(new Promise(() => {}))
    renderDashboard()
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
  })

  it('shows empty state when no data', async () => {
    getLPDStaleness.mockResolvedValue([])
    getLPDSections.mockResolvedValue({ sections: {} })
    getBriefing.mockRejectedValue(new Error('no briefing'))
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('No project data yet.')).toBeInTheDocument()
    })
  })

  it('displays health banner with reasoning', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Needs Attention')).toBeInTheDocument()
      expect(screen.getByText(/sections stale/)).toBeInTheDocument()
    })
  })

  it('displays staleness bars sorted by age', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Section Freshness')).toBeInTheDocument()
      expect(screen.getByText('32d')).toBeInTheDocument()
      expect(screen.getByText('18d')).toBeInTheDocument()
    })
  })

  it('displays attention items from briefing', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Risks section is 18 days stale')).toBeInTheDocument()
    })
  })

  it('displays upcoming dates', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('M2: Phase 2 kickoff')).toBeInTheDocument()
    })
  })

  it('displays contradictions', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Phase 2 date conflict')).toBeInTheDocument()
    })
  })

  it('shows suggested next action', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Update the Risks section/)).toBeInTheDocument()
    })
  })

  it('shows quick action buttons', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue(mockBriefing)
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Add to Knowledge Base')).toBeInTheDocument()
      expect(screen.getByText('Run Audit')).toBeInTheDocument()
      expect(screen.getByText('Ask Assistant')).toBeInTheDocument()
    })
  })

  it('handles partial data gracefully', async () => {
    getLPDStaleness.mockResolvedValue(mockStaleness)
    getLPDSections.mockResolvedValue(mockSections)
    getBriefing.mockResolvedValue({})  // Empty briefing (no attention items)
    renderDashboard()

    await waitFor(() => {
      // Should still show staleness data even with empty briefing
      expect(screen.getByText('Section Freshness')).toBeInTheDocument()
      // Empty briefing triggers "No Assessment"
      expect(screen.getByText('No Assessment')).toBeInTheDocument()
    })
  })
})
