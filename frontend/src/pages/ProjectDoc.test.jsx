import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ProjectDoc from './ProjectDoc'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  getLPDSections: vi.fn(),
  getLPDStaleness: vi.fn(),
  getLPDMarkdown: vi.fn(),
  updateLPDSection: vi.fn(),
  verifyLPDSection: vi.fn(),
  initializeLPD: vi.fn(),
}))

import {
  getLPDSections,
  getLPDStaleness,
  getLPDMarkdown,
  updateLPDSection,
  verifyLPDSection,
  initializeLPD,
} from '../services/api'

function renderPage() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <ProjectDoc />
      </ToastProvider>
    </MemoryRouter>
  )
}

const mockSections = {
  'Overview': 'Project Falcon — mobile app redesign.',
  'Stakeholders': '- Alice — PM\n- Bob — Dev Lead',
  'Timeline & Milestones': '',
  'Risks': '- Budget risk.',
  'Decisions': '- Chose React.',
  'Open Questions': '',
  'Recent Context': '- **2026-02-25**: Extracted from meeting notes.',
}

const mockStaleness = [
  { section_name: 'Overview', days_since_update: 0, days_since_verified: null, has_content: true },
  { section_name: 'Stakeholders', days_since_update: 3, days_since_verified: 2, has_content: true },
  { section_name: 'Timeline & Milestones', days_since_update: 7, days_since_verified: null, has_content: false },
  { section_name: 'Risks', days_since_update: 1, days_since_verified: null, has_content: true },
  { section_name: 'Decisions', days_since_update: 14, days_since_verified: null, has_content: true },
  { section_name: 'Open Questions', days_since_update: 0, days_since_verified: null, has_content: false },
  { section_name: 'Recent Context', days_since_update: 0, days_since_verified: null, has_content: true },
]

describe('ProjectDoc', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  it('shows initialize button when no LPD exists', async () => {
    getLPDSections.mockResolvedValue({ sections: {} })
    getLPDStaleness.mockResolvedValue({ staleness: [] })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Initialize Knowledge Base')).toBeInTheDocument()
    })
  })

  it('calls initializeLPD when initialize clicked', async () => {
    getLPDSections.mockResolvedValueOnce({ sections: {} })
    getLPDStaleness.mockResolvedValueOnce({ staleness: [] })
    initializeLPD.mockResolvedValue({ status: 'initialized' })
    getLPDSections.mockResolvedValueOnce({ sections: mockSections })
    getLPDStaleness.mockResolvedValueOnce({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Initialize Knowledge Base')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Initialize Knowledge Base'))

    await waitFor(() => {
      expect(initializeLPD).toHaveBeenCalledWith('default')
    })
  })

  it('displays all LPD sections when data exists', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getAllByText('Overview').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Stakeholders').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Risks').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Decisions').length).toBeGreaterThan(0)
      expect(screen.getByText('Recent Context')).toBeInTheDocument()
    })
  })

  it('shows section content', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Project Falcon — mobile app redesign.')).toBeInTheDocument()
      expect(screen.getByText('- Budget risk.')).toBeInTheDocument()
    })
  })

  it('shows staleness indicators', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      // Multiple sections can show "Updated today"
      expect(screen.getAllByText('Updated today').length).toBeGreaterThan(0)
      expect(screen.getByText('3d ago')).toBeInTheDocument()
    })
  })

  it('shows edit button for non-Recent Context sections', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      const editButtons = screen.getAllByText('Edit')
      expect(editButtons.length).toBeGreaterThan(0)
    })
  })

  it('shows auto-managed label for Recent Context', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('auto-managed')).toBeInTheDocument()
    })
  })

  it('opens inline editor when Edit clicked', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getAllByText('Edit').length).toBeGreaterThan(0)
    })

    // Click first Edit button
    fireEvent.click(screen.getAllByText('Edit')[0])

    await waitFor(() => {
      expect(screen.getByText('Save')).toBeInTheDocument()
      expect(screen.getByText('Cancel')).toBeInTheDocument()
    })
  })

  it('saves section content via API', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })
    updateLPDSection.mockResolvedValue({ status: 'updated' })

    renderPage()

    await waitFor(() => {
      expect(screen.getAllByText('Edit').length).toBeGreaterThan(0)
    })

    fireEvent.click(screen.getAllByText('Edit')[0])

    await waitFor(() => {
      expect(screen.getByText('Save')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      expect(updateLPDSection).toHaveBeenCalled()
    })
  })

  it('copies all as markdown', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })
    getLPDMarkdown.mockResolvedValue({ markdown: '# Living Project Document\n...' })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Copy All')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Copy All'))

    await waitFor(() => {
      expect(getLPDMarkdown).toHaveBeenCalledWith('default')
      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    })
  })

  it('calls verifyLPDSection when Verify clicked', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })
    verifyLPDSection.mockResolvedValue({ status: 'verified' })

    renderPage()

    await waitFor(() => {
      expect(screen.getAllByText('Verify').length).toBeGreaterThan(0)
    })

    fireEvent.click(screen.getAllByText('Verify')[0])

    await waitFor(() => {
      expect(verifyLPDSection).toHaveBeenCalled()
    })
  })

  it('has Import Files link', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Import Files')).toBeInTheDocument()
    })
  })

  describe('Staleness Nudge Banner', () => {
    const staleData = [
      { section_name: 'Overview', days_since_update: 0, days_since_verified: null, has_content: true },
      { section_name: 'Stakeholders', days_since_update: 21, days_since_verified: null, has_content: true },
      { section_name: 'Timeline & Milestones', days_since_update: 14, days_since_verified: null, has_content: false },
      { section_name: 'Risks', days_since_update: 1, days_since_verified: null, has_content: true },
      { section_name: 'Decisions', days_since_update: 30, days_since_verified: null, has_content: true },
      { section_name: 'Open Questions', days_since_update: 0, days_since_verified: null, has_content: false },
      { section_name: 'Recent Context', days_since_update: 0, days_since_verified: null, has_content: true },
    ]

    it('shows banner when sections are stale (14+ days)', async () => {
      getLPDSections.mockResolvedValue({ sections: mockSections })
      getLPDStaleness.mockResolvedValue({ staleness: staleData })

      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('staleness-banner')).toBeInTheDocument()
        expect(screen.getByText(/3 sections haven\u2019t been updated in 2\+ weeks/)).toBeInTheDocument()
      })
    })

    it('lists stale section names as clickable links', async () => {
      getLPDSections.mockResolvedValue({ sections: mockSections })
      getLPDStaleness.mockResolvedValue({ staleness: staleData })

      renderPage()

      await waitFor(() => {
        const banner = screen.getByTestId('staleness-banner')
        expect(banner).toHaveTextContent('Stakeholders')
        expect(banner).toHaveTextContent('Timeline & Milestones')
        expect(banner).toHaveTextContent('Decisions')
        expect(banner).toHaveTextContent('(21d)')
        expect(banner).toHaveTextContent('(14d)')
        expect(banner).toHaveTextContent('(30d)')
      })
    })

    it('dismisses banner when close button clicked', async () => {
      getLPDSections.mockResolvedValue({ sections: mockSections })
      getLPDStaleness.mockResolvedValue({ staleness: staleData })

      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('staleness-banner')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByLabelText('Dismiss staleness warning'))

      expect(screen.queryByTestId('staleness-banner')).not.toBeInTheDocument()
    })

    it('does not show banner when all sections are fresh', async () => {
      const freshData = mockStaleness.map(s => ({ ...s, days_since_update: 5 }))
      getLPDSections.mockResolvedValue({ sections: mockSections })
      getLPDStaleness.mockResolvedValue({ staleness: freshData })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Overview')).toBeInTheDocument()
      })

      expect(screen.queryByTestId('staleness-banner')).not.toBeInTheDocument()
    })

    it('does not show banner when LPD is empty', async () => {
      getLPDSections.mockResolvedValue({ sections: {} })
      getLPDStaleness.mockResolvedValue({ staleness: [] })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Initialize Knowledge Base')).toBeInTheDocument()
      })

      expect(screen.queryByTestId('staleness-banner')).not.toBeInTheDocument()
    })

    it('shows singular text for single stale section', async () => {
      const oneStale = mockStaleness.map(s => ({
        ...s,
        days_since_update: s.section_name === 'Decisions' ? 20 : 3,
      }))
      getLPDSections.mockResolvedValue({ sections: mockSections })
      getLPDStaleness.mockResolvedValue({ staleness: oneStale })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText(/1 section hasn\u2019t been updated in 2\+ weeks/)).toBeInTheDocument()
      })
    })

    it('scrolls to section when name clicked in banner', async () => {
      getLPDSections.mockResolvedValue({ sections: mockSections })
      getLPDStaleness.mockResolvedValue({ staleness: staleData })

      renderPage()

      await waitFor(() => {
        expect(screen.getByTestId('staleness-banner')).toBeInTheDocument()
      })

      // Mock scrollIntoView on the target element
      const sectionEl = document.getElementById('lpd-section-Stakeholders')
      sectionEl.scrollIntoView = vi.fn()

      // Click section name in banner
      const banner = screen.getByTestId('staleness-banner')
      const stakeholderButton = Array.from(banner.querySelectorAll('button')).find(
        b => b.textContent === 'Stakeholders'
      )
      fireEvent.click(stakeholderButton)

      expect(sectionEl.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth', block: 'start' })
    })
  })
})
