import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import LogSessionCard from './LogSessionCard'
import { ToastProvider } from './Toast'

function renderCard(props = {}) {
  const defaults = {
    sessionSummary: 'Discussed Phase 2 planning.',
    lpdUpdates: [
      { section: 'Decisions', content: '- Decided to use PostgreSQL.' },
    ],
    suggestions: [
      {
        artifact_type: 'RAID Log',
        change_type: 'add',
        section: 'Risks',
        proposed_text: '- Vendor delay risk.',
        confidence: 0.9,
        reasoning: 'Vendor dependency flagged.',
      },
    ],
    contentGateActive: true,
    onApply: vi.fn().mockResolvedValue(undefined),
    onApplyAnyway: vi.fn().mockResolvedValue(undefined),
  }
  return render(
    <ToastProvider>
      <LogSessionCard {...defaults} {...props} />
    </ToastProvider>
  )
}

describe('LogSessionCard', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  it('displays session summary', () => {
    renderCard()
    expect(screen.getByText('Discussed Phase 2 planning.')).toBeInTheDocument()
  })

  it('displays LPD updates with section names', () => {
    renderCard()
    expect(screen.getByText('Decisions')).toBeInTheDocument()
    expect(screen.getByText('- Decided to use PostgreSQL.')).toBeInTheDocument()
  })

  it('displays LPD updates applied heading with count', () => {
    renderCard()
    expect(screen.getByText(/LPD Updates Applied/)).toBeInTheDocument()
  })

  it('displays artifact suggestions', () => {
    renderCard()
    expect(screen.getByText('RAID Log')).toBeInTheDocument()
    expect(screen.getByText('- Vendor delay risk.')).toBeInTheDocument()
  })

  it('calls onApply when Apply button clicked', async () => {
    const onApply = vi.fn().mockResolvedValue(undefined)
    renderCard({ onApply })
    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(onApply).toHaveBeenCalled()
    })
  })

  it('disables Apply button after successful apply', async () => {
    const onApply = vi.fn().mockResolvedValue(undefined)
    renderCard({ onApply })
    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(screen.getByText('Applied')).toBeInTheDocument()
    })
  })

  it('shows KB toast when apply returns lpd_updated true', async () => {
    const onApply = vi.fn().mockResolvedValue({ status: 'applied', lpd_updated: true })
    renderCard({ onApply })
    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(screen.getByText('Applied to artifact + knowledge base')).toBeInTheDocument()
    })
  })

  it('shows duplicate toast when apply returns duplicate status', async () => {
    const onApply = vi.fn().mockResolvedValue({ status: 'duplicate', lpd_updated: false })
    renderCard({ onApply })
    fireEvent.click(screen.getByText('Apply'))
    await waitFor(() => {
      expect(screen.getByText('Already applied (duplicate)')).toBeInTheDocument()
    })
  })

  it('renders Copy All button', () => {
    renderCard()
    expect(screen.getByText('Copy All')).toBeInTheDocument()
  })

  it('copies all content when Copy All clicked', async () => {
    renderCard()
    fireEvent.click(screen.getByText('Copy All'))
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalled()
    })
  })

  it('handles empty LPD updates gracefully', () => {
    renderCard({ lpdUpdates: [], suggestions: [] })
    expect(screen.getByText('Discussed Phase 2 planning.')).toBeInTheDocument()
    expect(screen.queryByText(/LPD Updates Applied/)).not.toBeInTheDocument()
  })

  it('handles missing session summary', () => {
    renderCard({ sessionSummary: null })
    expect(screen.queryByText('Session Summary')).not.toBeInTheDocument()
    expect(screen.getByText('Decisions')).toBeInTheDocument()
  })
})

describe('LogSessionCard — Content Gate Classifications', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  it('shows classified new updates as applied', () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Risks',
          content: '- New risk.',
          classification: { classification: 'new', reason: 'New info' },
        },
      ],
    })
    expect(screen.getByText(/LPD Updates Applied/)).toBeInTheDocument()
    expect(screen.getByText('- New risk.')).toBeInTheDocument()
  })

  it('shows classified update updates as applied with extends label', () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Risks',
          content: '- Extended risk detail.',
          classification: { classification: 'update', reason: 'Adds detail' },
        },
      ],
    })
    expect(screen.getByText(/LPD Updates Applied/)).toBeInTheDocument()
    expect(screen.getByText('(extends existing)')).toBeInTheDocument()
  })

  it('shows duplicates as skipped note', () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Decisions',
          content: '- Already recorded decision.',
          classification: { classification: 'duplicate', reason: 'Same fact' },
        },
      ],
    })
    expect(screen.queryByText(/LPD Updates Applied/)).not.toBeInTheDocument()
    expect(screen.getByText(/1 duplicate skipped/)).toBeInTheDocument()
  })

  it('shows multiple duplicates with plural', () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Decisions',
          content: '- Dup 1.',
          classification: { classification: 'duplicate', reason: 'Same' },
        },
        {
          section: 'Risks',
          content: '- Dup 2.',
          classification: { classification: 'duplicate', reason: 'Same' },
        },
      ],
    })
    expect(screen.getByText(/2 duplicates skipped/)).toBeInTheDocument()
  })

  it('expands duplicates when clicked', async () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Decisions',
          content: '- Already recorded.',
          classification: { classification: 'duplicate', reason: 'Same fact' },
        },
      ],
    })
    fireEvent.click(screen.getByText(/1 duplicate skipped/))
    await waitFor(() => {
      expect(screen.getByText('- Already recorded.')).toBeInTheDocument()
      expect(screen.getByText('Same fact')).toBeInTheDocument()
    })
  })

  it('shows contradictions with Apply Anyway button', () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Decisions',
          content: '- Changed to MySQL.',
          classification: { classification: 'contradiction', reason: 'Contradicts PostgreSQL decision' },
        },
      ],
    })
    expect(screen.getByText(/Needs Review/)).toBeInTheDocument()
    expect(screen.getByText('- Changed to MySQL.')).toBeInTheDocument()
    expect(screen.getByText('Contradicts PostgreSQL decision')).toBeInTheDocument()
    expect(screen.getByText('Apply Anyway')).toBeInTheDocument()
  })

  it('calls onApplyAnyway when Apply Anyway clicked', async () => {
    const onApplyAnyway = vi.fn().mockResolvedValue(undefined)
    renderCard({
      lpdUpdates: [
        {
          section: 'Decisions',
          content: '- Changed to MySQL.',
          classification: { classification: 'contradiction', reason: 'Contradicts' },
        },
      ],
      onApplyAnyway,
    })
    fireEvent.click(screen.getByText('Apply Anyway'))
    await waitFor(() => {
      expect(onApplyAnyway).toHaveBeenCalledWith(
        expect.objectContaining({ section: 'Decisions', content: '- Changed to MySQL.' })
      )
    })
  })

  it('disables Apply Anyway after successful apply', async () => {
    const onApplyAnyway = vi.fn().mockResolvedValue(undefined)
    renderCard({
      lpdUpdates: [
        {
          section: 'Decisions',
          content: '- Changed.',
          classification: { classification: 'contradiction', reason: 'Conflict' },
        },
      ],
      onApplyAnyway,
    })
    fireEvent.click(screen.getByText('Apply Anyway'))
    await waitFor(() => {
      expect(screen.getByText('Applied')).toBeInTheDocument()
    })
  })

  it('partitions mixed updates correctly', () => {
    renderCard({
      lpdUpdates: [
        {
          section: 'Risks',
          content: '- New risk.',
          classification: { classification: 'new', reason: 'New' },
        },
        {
          section: 'Decisions',
          content: '- Duplicate.',
          classification: { classification: 'duplicate', reason: 'Same' },
        },
        {
          section: 'Stakeholders',
          content: '- Contradiction.',
          classification: { classification: 'contradiction', reason: 'Conflict' },
        },
      ],
    })
    expect(screen.getByText(/LPD Updates Applied \(1\)/)).toBeInTheDocument()
    expect(screen.getByText(/1 duplicate skipped/)).toBeInTheDocument()
    expect(screen.getByText(/Needs Review \(1\)/)).toBeInTheDocument()
  })

  it('treats updates with no classification as applied (backward compat)', () => {
    renderCard({
      lpdUpdates: [
        { section: 'Risks', content: '- No classification.' },
      ],
    })
    expect(screen.getByText(/LPD Updates Applied/)).toBeInTheDocument()
    expect(screen.getByText('- No classification.')).toBeInTheDocument()
  })
})
