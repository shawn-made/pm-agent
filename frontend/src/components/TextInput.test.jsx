import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TextInput from './TextInput'

describe('TextInput', () => {
  let onSubmit

  beforeEach(() => {
    onSubmit = vi.fn()
  })

  it('renders textarea with placeholder', () => {
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
    fireEvent.click(screen.getByText('Analyze'))
    expect(onSubmit).toHaveBeenCalledWith('meeting notes')
  })

  it('does not submit empty or whitespace-only text', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={false} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    fireEvent.change(textarea, { target: { value: '   ' } })
    fireEvent.click(screen.getByText('Analyze'))
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('shows Analyzing... during loading', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={true} />)
    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
  })

  it('disables textarea and buttons during loading', () => {
    render(<TextInput onSubmit={onSubmit} isLoading={true} />)
    const textarea = screen.getByPlaceholderText(
      'Paste meeting notes, transcripts, or project updates...'
    )
    expect(textarea).toBeDisabled()
  })
})
