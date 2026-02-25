import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TextInput from './TextInput'

describe('TextInput', () => {
  let onSubmit
  let onModeChange

  beforeEach(() => {
    onSubmit = vi.fn()
    onModeChange = vi.fn()
  })

  it('renders textarea with extract mode placeholder by default', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    expect(
      screen.getByPlaceholderText('Paste meeting notes, transcripts, or project updates...')
    ).toBeInTheDocument()
  })

  it('shows character count starting at 0', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    expect(screen.getByText('0 characters')).toBeInTheDocument()
  })

  it('updates character count on typing', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'hello' } })
    expect(screen.getByText('5 characters')).toBeInTheDocument()
  })

  it('shows Clear button only when text is present', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    expect(screen.queryByText('Clear')).not.toBeInTheDocument()

    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'text' } })
    expect(screen.getByText('Clear')).toBeInTheDocument()
  })

  it('clears text when Clear is clicked', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'some text' } })
    fireEvent.click(screen.getByText('Clear'))
    expect(textarea.value).toBe('')
    expect(screen.getByText('0 characters')).toBeInTheDocument()
  })

  it('calls onSubmit with text on form submit', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: 'meeting notes' } })
    // Submit button says "Extract" in default mode (no toggle shown)
    const submitBtn = screen.getByRole('button', { name: 'Extract' })
    fireEvent.click(submitBtn)
    expect(onSubmit).toHaveBeenCalledWith('meeting notes')
  })

  it('does not submit empty or whitespace-only text', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: '   ' } })
    const submitBtn = screen.getByRole('button', { name: 'Extract' })
    fireEvent.click(submitBtn)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('shows Extracting... during loading in extract mode', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={true} mode="extract" onModeChange={onModeChange} />)
    expect(screen.getByText('Extracting...')).toBeInTheDocument()
  })

  it('shows Analyzing... during loading in analyze mode', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={true} mode="analyze" onModeChange={onModeChange} />)
    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
  })

  it('disables textarea and buttons during loading', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={true} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    expect(textarea).toBeDisabled()
  })

  // --- Mode toggle tests ---

  it('renders mode toggle when onModeChange provided', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} mode="extract" onModeChange={onModeChange} />)
    // Should have both toggle buttons (type="button") plus the submit button
    const extractButtons = screen.getAllByText('Extract')
    expect(extractButtons).toHaveLength(2) // toggle + submit
    const analyzeToggle = screen.getAllByText('Analyze')
    expect(analyzeToggle.length).toBeGreaterThanOrEqual(1)
  })

  it('does not render mode toggle when onModeChange is not provided', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    // Only the submit button should have "Extract" text
    const extractElements = screen.getAllByText('Extract')
    expect(extractElements).toHaveLength(1) // just the submit button
  })

  it('calls onModeChange when clicking Analyze toggle', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} mode="extract" onModeChange={onModeChange} />)
    // Find the toggle button (type="button"), not the submit
    const analyzeButtons = screen.getAllByText('Analyze')
    const toggleBtn = analyzeButtons.find((b) => b.getAttribute('type') === 'button')
    fireEvent.click(toggleBtn)
    expect(onModeChange).toHaveBeenCalledWith('analyze')
  })

  it('shows analyze placeholder when mode is analyze', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} mode="analyze" onModeChange={onModeChange} />)
    expect(
      screen.getByPlaceholderText('Paste a draft document for review...')
    ).toBeInTheDocument()
  })

  it('submit button shows Analyze in analyze mode', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} mode="analyze" onModeChange={onModeChange} />)
    // Both the toggle and submit say "Analyze" — verify a submit-type button exists
    const allButtons = screen.getAllByRole('button')
    const submitButtons = allButtons.filter(
      (b) => b.getAttribute('type') === 'submit' && b.textContent === 'Analyze'
    )
    expect(submitButtons).toHaveLength(1)
  })
})
