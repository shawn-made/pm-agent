import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ArtifactUploader from './ArtifactUploader'

describe('ArtifactUploader', () => {
  let onAnalyze

  beforeEach(() => {
    onAnalyze = vi.fn()
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
})
