import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Intake from './Intake'
import { ToastProvider } from '../components/Toast'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('../services/api', () => ({
  intakePreview: vi.fn(),
  intakeApply: vi.fn(),
}))

import { intakePreview, intakeApply } from '../services/api'

function renderPage() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Intake />
      </ToastProvider>
    </MemoryRouter>
  )
}

const mockDraft = {
  extractions: [{ source_file: 'notes.md', overview: 'Project info.', risks: '- Risk A.' }],
  proposed_sections: {
    'Overview': 'Project info.',
    'Risks': '- Risk A.',
  },
  conflicts: [],
  pii_detected: 0,
}

describe('Intake', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders heading and file input area', () => {
    renderPage()
    expect(screen.getByText('Import Files')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Paste file content here...')).toBeInTheDocument()
  })

  it('renders filename input', () => {
    renderPage()
    expect(screen.getByPlaceholderText(/File name/)).toBeInTheDocument()
  })

  it('adds a file when Add File clicked', () => {
    renderPage()
    fireEvent.click(screen.getByText('+ Add File'))
    const textareas = screen.getAllByPlaceholderText('Paste file content here...')
    expect(textareas).toHaveLength(2)
  })

  it('shows preview button', () => {
    renderPage()
    expect(screen.getByText('Preview')).toBeInTheDocument()
  })

  it('shows error when previewing with empty content', async () => {
    renderPage()
    fireEvent.click(screen.getByText('Preview'))
    await waitFor(() => {
      expect(screen.getByText('At least one file must have content')).toBeInTheDocument()
    })
  })

  it('calls intakePreview on preview', async () => {
    intakePreview.mockResolvedValue(mockDraft)
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Some project notes.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(intakePreview).toHaveBeenCalledWith('default', [
        { filename: 'file_1.md', content: 'Some project notes.' },
      ])
    })
  })

  it('displays proposed sections after preview', async () => {
    intakePreview.mockResolvedValue(mockDraft)
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Notes content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(screen.getByText('Overview')).toBeInTheDocument()
      expect(screen.getByText('Risks')).toBeInTheDocument()
      expect(screen.getByText('Project info.')).toBeInTheDocument()
    })
  })

  it('auto-selects all sections in preview', async () => {
    intakePreview.mockResolvedValue(mockDraft)
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes).toHaveLength(2)
      checkboxes.forEach(cb => expect(cb).toBeChecked())
    })
  })

  it('toggles section selection', async () => {
    intakePreview.mockResolvedValue(mockDraft)
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(screen.getAllByRole('checkbox')).toHaveLength(2)
    })

    // Uncheck Overview
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    expect(checkboxes[0]).not.toBeChecked()
  })

  it('calls intakeApply on apply', async () => {
    intakePreview.mockResolvedValue(mockDraft)
    intakeApply.mockResolvedValue({ sections_updated: ['Overview', 'Risks'], sections_skipped: [] })
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(screen.getByText(/Apply 2 Section/)).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText(/Apply 2 Section/))

    await waitFor(() => {
      expect(intakeApply).toHaveBeenCalledWith(
        'default',
        mockDraft.proposed_sections,
        expect.arrayContaining(['Overview', 'Risks']),
      )
    })
  })

  it('navigates to project page after successful apply', async () => {
    intakePreview.mockResolvedValue(mockDraft)
    intakeApply.mockResolvedValue({ sections_updated: ['Overview'], sections_skipped: ['Risks'] })
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(screen.getByText(/Apply 2 Section/)).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText(/Apply 2 Section/))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/project')
    })
  })

  it('shows conflicts when detected', async () => {
    const draftWithConflict = {
      ...mockDraft,
      conflicts: [
        { section: 'Risks', existing: '- Old risk.', proposed: '- New risk.', source_file: 'notes.md' },
      ],
    }
    intakePreview.mockResolvedValue(draftWithConflict)
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(screen.getByText(/Conflicts Detected/)).toBeInTheDocument()
    })
  })

  it('shows PII count when detected', async () => {
    intakePreview.mockResolvedValue({ ...mockDraft, pii_detected: 3 })
    renderPage()

    const textarea = screen.getByPlaceholderText('Paste file content here...')
    fireEvent.change(textarea, { target: { value: 'Content.' } })
    fireEvent.click(screen.getByText('Preview'))

    await waitFor(() => {
      expect(screen.getByText(/3 PII item/)).toBeInTheDocument()
    })
  })
})
