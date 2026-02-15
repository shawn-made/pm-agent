import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SuggestionCard from './SuggestionCard'
import { ToastProvider } from './Toast'

const baseSuggestion = {
  artifact_type: 'RAID Log',
  change_type: 'add',
  section: 'Risks',
  proposed_text: 'New risk: server capacity may be insufficient',
  confidence: 0.85,
  reasoning: 'Meeting mentioned capacity concerns',
}

function renderCard(props = {}) {
  return render(
    <ToastProvider>
      <SuggestionCard suggestion={baseSuggestion} onApply={vi.fn()} {...props} />
    </ToastProvider>
  )
}

describe('SuggestionCard', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders artifact type, change type, section, and confidence', () => {
    renderCard()
    expect(screen.getByText('RAID Log')).toBeInTheDocument()
    expect(screen.getByText('Add')).toBeInTheDocument()
    expect(screen.getByText('Risks')).toBeInTheDocument()
    expect(screen.getByText('85% confidence')).toBeInTheDocument()
  })

  it('renders reasoning text', () => {
    renderCard()
    expect(screen.getByText('Meeting mentioned capacity concerns')).toBeInTheDocument()
  })

  it('starts collapsed — proposed text hidden', () => {
    renderCard()
    expect(screen.queryByText(baseSuggestion.proposed_text)).not.toBeInTheDocument()
    expect(screen.getByText('Show preview')).toBeInTheDocument()
  })

  it('expands to show proposed text on click', () => {
    renderCard()
    fireEvent.click(screen.getByText('Show preview'))
    expect(screen.getByText(baseSuggestion.proposed_text)).toBeInTheDocument()
    expect(screen.getByText('Hide preview')).toBeInTheDocument()
  })

  it('collapses again on second click', () => {
    renderCard()
    fireEvent.click(screen.getByText('Show preview'))
    fireEvent.click(screen.getByText('Hide preview'))
    expect(screen.queryByText(baseSuggestion.proposed_text)).not.toBeInTheDocument()
  })

  it('copies text to clipboard', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.assign(navigator, { clipboard: { writeText } })

    renderCard()
    fireEvent.click(screen.getByText('Copy'))

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(baseSuggestion.proposed_text)
      expect(screen.getByText('Copied')).toBeInTheDocument()
    })
  })

  it('calls onApply and shows Applied state', async () => {
    const onApply = vi.fn().mockResolvedValue(undefined)
    renderCard({ onApply })

    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(onApply).toHaveBeenCalledWith(baseSuggestion)
      expect(screen.getByText('Applied')).toBeInTheDocument()
    })
  })

  it('shows error toast when copy fails', async () => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) },
    })
    renderCard()
    fireEvent.click(screen.getByText('Copy'))
    await waitFor(() => {
      expect(screen.getByText('Failed to copy to clipboard')).toBeInTheDocument()
    })
  })

  it('shows error toast when apply fails', async () => {
    const onApply = vi.fn().mockRejectedValue(new Error('fail'))
    renderCard({ onApply })
    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(screen.getByText('Failed to apply suggestion')).toBeInTheDocument()
    })
  })

  it('applies correct color class for each artifact type', () => {
    const { rerender } = render(
      <ToastProvider>
        <SuggestionCard
          suggestion={{ ...baseSuggestion, artifact_type: 'Status Report' }}
          onApply={vi.fn()}
        />
      </ToastProvider>
    )
    expect(screen.getByText('Status Report').className).toContain('bg-blue-50')

    rerender(
      <ToastProvider>
        <SuggestionCard
          suggestion={{ ...baseSuggestion, artifact_type: 'Meeting Notes' }}
          onApply={vi.fn()}
        />
      </ToastProvider>
    )
    expect(screen.getByText('Meeting Notes').className).toContain('bg-green-50')
  })
})
