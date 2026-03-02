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
      expect(screen.getByText('Initialize Project Hub')).toBeInTheDocument()
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
      expect(screen.getByText('Initialize Project Hub')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Initialize Project Hub'))

    await waitFor(() => {
      expect(initializeLPD).toHaveBeenCalledWith('default')
    })
  })

  it('displays all LPD sections when data exists', async () => {
    getLPDSections.mockResolvedValue({ sections: mockSections })
    getLPDStaleness.mockResolvedValue({ staleness: mockStaleness })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Overview')).toBeInTheDocument()
      expect(screen.getByText('Stakeholders')).toBeInTheDocument()
      expect(screen.getByText('Risks')).toBeInTheDocument()
      expect(screen.getByText('Decisions')).toBeInTheDocument()
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
})
