import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ArtifactUploader from './ArtifactUploader'

// Mock the API module
vi.mock('../services/api', () => ({
  getAvailableArtifacts: vi.fn(),
}))

import { getAvailableArtifacts } from '../services/api'

describe('ArtifactUploader', () => {
  let onAnalyze

  beforeEach(() => {
    onAnalyze = vi.fn()
    vi.clearAllMocks()
  })

  it('renders two empty artifact inputs by default', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    const textareas = screen.getAllByPlaceholderText(/Paste artifact content/i)
    expect(textareas).toHaveLength(2)
  })

  it('renders priority explanation text', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    expect(screen.getByText(/source-of-truth priority/i)).toBeInTheDocument()
  })

  it('adds an artifact when Add Artifact is clicked', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    fireEvent.click(screen.getByText('+ Add Artifact'))
    const textareas = screen.getAllByPlaceholderText(/Paste artifact content/i)
    expect(textareas).toHaveLength(3)
  })

  it('disables analyze button when fewer than 2 artifacts have content', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    const button = screen.getByRole('button', { name: /Analyze/i })
    expect(button).toBeDisabled()
  })

  it('enables analyze button when 2+ artifacts have content', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    const textareas = screen.getAllByPlaceholderText(/Paste artifact content/i)
    fireEvent.change(textareas[0], { target: { value: 'Content A' } })
    fireEvent.change(textareas[1], { target: { value: 'Content B' } })
    const button = screen.getByRole('button', { name: /Analyze 2 Artifacts/i })
    expect(button).not.toBeDisabled()
  })

  it('calls onAnalyze with prepared artifacts on submit', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    const textareas = screen.getAllByPlaceholderText(/Paste artifact content/i)
    const nameInputs = screen.getAllByPlaceholderText(/Artifact \d+ name/i)

    fireEvent.change(nameInputs[0], { target: { value: 'Charter' } })
    fireEvent.change(textareas[0], { target: { value: 'Charter content' } })
    fireEvent.change(nameInputs[1], { target: { value: 'Schedule' } })
    fireEvent.change(textareas[1], { target: { value: 'Schedule content' } })

    fireEvent.click(screen.getByRole('button', { name: /Analyze 2 Artifacts/i }))

    expect(onAnalyze).toHaveBeenCalledWith([
      { name: 'Charter', content: 'Charter content', priority: 1 },
      { name: 'Schedule', content: 'Schedule content', priority: 2 },
    ])
  })

  it('assigns default names when name is empty', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    const textareas = screen.getAllByPlaceholderText(/Paste artifact content/i)

    fireEvent.change(textareas[0], { target: { value: 'Content A' } })
    fireEvent.change(textareas[1], { target: { value: 'Content B' } })

    fireEvent.click(screen.getByRole('button', { name: /Analyze 2 Artifacts/i }))

    expect(onAnalyze).toHaveBeenCalledWith([
      { name: 'Artifact 1', content: 'Content A', priority: 1 },
      { name: 'Artifact 2', content: 'Content B', priority: 2 },
    ])
  })

  it('shows character count when content is present', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} />)
    const textareas = screen.getAllByPlaceholderText(/Paste artifact content/i)
    fireEvent.change(textareas[0], { target: { value: 'Hello World' } })
    expect(screen.getByText('11 characters')).toBeInTheDocument()
  })

  it('shows Analyzing when isLoading is true', () => {
    render(<ArtifactUploader onAnalyze={onAnalyze} isLoading={true} />)
    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
  })

  // Load from VPMA tests
  describe('Load from VPMA', () => {
    it('renders Load from VPMA button', () => {
      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      expect(screen.getByText('Load from VPMA')).toBeInTheDocument()
    })

    it('opens loader panel and fetches available artifacts', async () => {
      getAvailableArtifacts.mockResolvedValue({
        items: [
          { name: 'Raid Log', content: 'Risk content', source: 'artifact' },
          { name: 'LPD: Overview', content: 'Overview text', source: 'lpd' },
        ],
      })

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText('Raid Log')).toBeInTheDocument()
        expect(screen.getByText('LPD: Overview')).toBeInTheDocument()
      })

      expect(getAvailableArtifacts).toHaveBeenCalled()
    })

    it('shows source badges (Artifact vs LPD)', async () => {
      getAvailableArtifacts.mockResolvedValue({
        items: [
          { name: 'Raid Log', content: 'content', source: 'artifact' },
          { name: 'LPD: Risks', content: 'content', source: 'lpd' },
        ],
      })

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText('Artifact')).toBeInTheDocument()
        expect(screen.getByText('LPD')).toBeInTheDocument()
      })
    })

    it('shows empty message when no artifacts exist', async () => {
      getAvailableArtifacts.mockResolvedValue({ items: [] })

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText(/No artifacts or LPD sections found/)).toBeInTheDocument()
      })
    })

    it('shows error on API failure', async () => {
      getAvailableArtifacts.mockRejectedValue(new Error('Network error'))

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument()
      })
    })

    it('loads selected items into empty artifact slots', async () => {
      getAvailableArtifacts.mockResolvedValue({
        items: [
          { name: 'Raid Log', content: 'Risk content here', source: 'artifact' },
          { name: 'LPD: Overview', content: 'Overview text here', source: 'lpd' },
        ],
      })

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText('Raid Log')).toBeInTheDocument()
      })

      // Select both items
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[0])
      fireEvent.click(checkboxes[1])

      // Click load
      fireEvent.click(screen.getByText('Load 2 items'))

      // Verify artifacts were populated
      await waitFor(() => {
        const nameInputs = screen.getAllByPlaceholderText(/Artifact \d+ name/i)
        expect(nameInputs[0].value).toBe('Raid Log')
        expect(nameInputs[1].value).toBe('LPD: Overview')
      })
    })

    it('disables load button when nothing selected', async () => {
      getAvailableArtifacts.mockResolvedValue({
        items: [
          { name: 'Raid Log', content: 'content', source: 'artifact' },
        ],
      })

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText('Select items to load')).toBeInTheDocument()
      })

      const loadButton = screen.getByText('Select items to load')
      expect(loadButton).toBeDisabled()
    })

    it('closes loader panel on X button', async () => {
      getAvailableArtifacts.mockResolvedValue({
        items: [
          { name: 'Raid Log', content: 'content', source: 'artifact' },
        ],
      })

      render(<ArtifactUploader onAnalyze={onAnalyze} />)
      fireEvent.click(screen.getByText('Load from VPMA'))

      await waitFor(() => {
        expect(screen.getByText('Raid Log')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByLabelText('Close loader'))

      expect(screen.queryByText('Raid Log')).not.toBeInTheDocument()
    })
  })
})
