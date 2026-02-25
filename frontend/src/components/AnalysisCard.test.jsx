import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AnalysisCard from './AnalysisCard'
import { ToastProvider } from './Toast'

const sampleItems = [
  {
    category: 'strength',
    title: 'Clear accomplishments',
    detail: 'The API integration is well documented.',
    priority: 'low',
    artifact_type: 'Status Report',
  },
  {
    category: 'gap',
    title: 'Missing blocker details',
    detail: 'Security review blocker lacks deadline and escalation path.',
    priority: 'high',
    artifact_type: 'Status Report',
  },
  {
    category: 'recommendation',
    title: 'Add CI/CD mitigation plan',
    detail: 'Include who is investigating and target resolution date.',
    priority: 'medium',
    artifact_type: 'RAID Log',
  },
]

function renderCard(props = {}) {
  return render(
    <ToastProvider>
      <AnalysisCard
        summary="The document covers accomplishments but lacks blocker details."
        items={sampleItems}
        {...props}
      />
    </ToastProvider>
  )
}

describe('AnalysisCard', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders summary text', () => {
    renderCard()
    expect(
      screen.getByText('The document covers accomplishments but lacks blocker details.')
    ).toBeInTheDocument()
  })

  it('renders item count', () => {
    renderCard()
    expect(screen.getByText('Analysis (3 items)')).toBeInTheDocument()
  })

  it('renders all analysis items', () => {
    renderCard()
    expect(screen.getByText('Clear accomplishments')).toBeInTheDocument()
    expect(screen.getByText('Missing blocker details')).toBeInTheDocument()
    expect(screen.getByText('Add CI/CD mitigation plan')).toBeInTheDocument()
  })

  it('renders item details', () => {
    renderCard()
    expect(screen.getByText('The API integration is well documented.')).toBeInTheDocument()
    expect(
      screen.getByText('Security review blocker lacks deadline and escalation path.')
    ).toBeInTheDocument()
  })

  it('renders priority badges', () => {
    renderCard()
    expect(screen.getByText('low')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
    expect(screen.getByText('medium')).toBeInTheDocument()
  })

  it('renders artifact type labels', () => {
    renderCard()
    expect(screen.getAllByText('Status Report')).toHaveLength(2)
    expect(screen.getByText('RAID Log')).toBeInTheDocument()
  })

  it('renders category group headers', () => {
    renderCard()
    expect(screen.getByText('Strengths (1)')).toBeInTheDocument()
    expect(screen.getByText('Gaps (1)')).toBeInTheDocument()
    expect(screen.getByText('Recommendations (1)')).toBeInTheDocument()
  })

  it('copies analysis as markdown to clipboard', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.assign(navigator, { clipboard: { writeText } })

    renderCard()
    fireEvent.click(screen.getByText('Copy All'))

    await waitFor(() => {
      expect(writeText).toHaveBeenCalled()
      const copied = writeText.mock.calls[0][0]
      expect(copied).toContain('## Analysis Summary')
      expect(copied).toContain('The document covers accomplishments but lacks blocker details.')
      expect(copied).toContain('## Strengths')
      expect(copied).toContain('Clear accomplishments')
      expect(screen.getByText('Copied')).toBeInTheDocument()
    })
  })

  it('shows error toast when copy fails', async () => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) },
    })
    renderCard()
    fireEvent.click(screen.getByText('Copy All'))
    await waitFor(() => {
      expect(screen.getByText('Failed to copy to clipboard')).toBeInTheDocument()
    })
  })

  it('handles empty items gracefully', () => {
    renderCard({ items: [], summary: 'No issues found.' })
    expect(screen.getByText('No issues found.')).toBeInTheDocument()
    expect(screen.getByText('Analysis (0 items)')).toBeInTheDocument()
  })

  it('handles null summary', () => {
    renderCard({ summary: null })
    // Should not crash, items still render
    expect(screen.getByText('Clear accomplishments')).toBeInTheDocument()
  })
})
