import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import DeepStrategyResults from './DeepStrategyResults'
import { ToastProvider } from './Toast'

const baseResults = {
  summary: {
    artifacts_analyzed: 3,
    inconsistencies_found: 2,
    updates_proposed: 1,
    validation_passed: true,
    consistency_score: 0.85,
  },
  dependency_graph: {
    artifacts: ['Charter', 'Schedule'],
    edges: [{ source: 'Charter', target: 'Schedule', relationship: 'drives' }],
    summary: 'Charter drives Schedule',
  },
  inconsistencies: [
    {
      id: 'INC-1',
      source_artifact: 'Charter',
      target_artifact: 'Schedule',
      description: 'Timeline mismatch',
      severity: 'high',
      source_excerpt: 'Q3 delivery',
      target_excerpt: 'Q4 start',
    },
    {
      id: 'INC-2',
      source_artifact: 'Charter',
      target_artifact: 'RAID Log',
      description: 'Missing risk entry',
      severity: 'medium',
      source_excerpt: 'New dependency',
      target_excerpt: '',
    },
  ],
  proposed_updates: [
    {
      inconsistency_id: 'INC-1',
      artifact_name: 'Schedule',
      section: 'Timeline',
      current_text: 'Q4 start',
      proposed_text: 'Q3 start',
      change_type: 'modify',
      rationale: 'Align with Charter',
    },
  ],
  validation_checks: [
    {
      artifact_name: 'Schedule',
      check_description: 'Timeline alignment',
      passed: true,
      detail: 'All dates consistent',
    },
  ],
  pii_detected: 3,
}

function renderResults(props = {}) {
  return render(
    <ToastProvider>
      <DeepStrategyResults results={baseResults} onApply={vi.fn()} {...props} />
    </ToastProvider>
  )
}

describe('DeepStrategyResults', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders nothing when results is null', () => {
    render(
      <ToastProvider>
        <DeepStrategyResults results={null} onApply={vi.fn()} />
      </ToastProvider>
    )
    // Should not render any tabs or summary
    expect(screen.queryByText('Summary')).not.toBeInTheDocument()
  })

  // Summary tab
  it('shows summary statistics on default tab', () => {
    renderResults()
    // Use label text alongside numbers to confirm the right cards render
    expect(screen.getByText('Artifacts')).toBeInTheDocument()
    expect(screen.getByText('Inconsistencies', { selector: 'p' })).toBeInTheDocument()
    expect(screen.getByText('Updates Proposed')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('shows dependency graph summary', () => {
    renderResults()
    expect(screen.getByText('Charter drives Schedule')).toBeInTheDocument()
  })

  it('shows PII anonymized count', () => {
    renderResults()
    expect(screen.getByText(/3 PII items anonymized/i)).toBeInTheDocument()
  })

  // Tab navigation — use getByRole('button') to find the tab button specifically
  function clickTab(tabName) {
    const tabs = screen.getAllByRole('button')
    const tab = tabs.find(b => b.textContent.includes(tabName))
    fireEvent.click(tab)
  }

  it('switches to Inconsistencies tab', () => {
    renderResults()
    clickTab('Inconsistencies')
    expect(screen.getByText('Timeline mismatch')).toBeInTheDocument()
    expect(screen.getByText('Missing risk entry')).toBeInTheDocument()
  })

  it('shows severity badges on inconsistencies', () => {
    renderResults()
    clickTab('Inconsistencies')
    expect(screen.getByText('high')).toBeInTheDocument()
    expect(screen.getByText('medium')).toBeInTheDocument()
  })

  it('shows source/target artifacts on inconsistencies', () => {
    renderResults()
    clickTab('Inconsistencies')
    expect(screen.getByText(/Charter → Schedule/)).toBeInTheDocument()
  })

  // Proposed Updates tab
  it('switches to Proposed Updates tab', () => {
    renderResults()
    clickTab('Proposed Updates')
    expect(screen.getByText('Align with Charter')).toBeInTheDocument()
  })

  it('shows diff view with current and proposed text', () => {
    renderResults()
    clickTab('Proposed Updates')
    expect(screen.getByText('Q4 start')).toBeInTheDocument()
    expect(screen.getByText('Q3 start')).toBeInTheDocument()
  })

  it('can select and deselect updates', () => {
    renderResults()
    clickTab('Proposed Updates')
    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).not.toBeChecked()

    fireEvent.click(checkbox)
    expect(checkbox).toBeChecked()

    fireEvent.click(screen.getByText('Deselect All'))
    expect(checkbox).not.toBeChecked()
  })

  it('calls onApply with selected updates', () => {
    const onApply = vi.fn()
    render(
      <ToastProvider>
        <DeepStrategyResults results={baseResults} onApply={onApply} />
      </ToastProvider>
    )
    clickTab('Proposed Updates')
    fireEvent.click(screen.getByRole('checkbox'))
    fireEvent.click(screen.getByText(/Apply 1 Selected Update/i))
    expect(onApply).toHaveBeenCalledWith([baseResults.proposed_updates[0]])
  })

  // Empty state coaching tests
  it('shows coaching hint when no inconsistencies', () => {
    render(
      <ToastProvider>
        <DeepStrategyResults
          results={{ ...baseResults, inconsistencies: [] }}
          onApply={vi.fn()}
        />
      </ToastProvider>
    )
    clickTab('Inconsistencies')
    expect(screen.getByText(/Your documents appear consistent/)).toBeInTheDocument()
  })

  it('shows coaching hint when no proposed updates', () => {
    render(
      <ToastProvider>
        <DeepStrategyResults
          results={{ ...baseResults, proposed_updates: [] }}
          onApply={vi.fn()}
        />
      </ToastProvider>
    )
    clickTab('Proposed Updates')
    expect(screen.getByText(/Updates are proposed when inconsistencies are found/)).toBeInTheDocument()
  })

  it('shows coaching hint when no validation checks', () => {
    render(
      <ToastProvider>
        <DeepStrategyResults
          results={{ ...baseResults, validation_checks: [] }}
          onApply={vi.fn()}
        />
      </ToastProvider>
    )
    clickTab('Validation')
    expect(screen.getByText(/Validation checks run automatically when inconsistencies are found/)).toBeInTheDocument()
  })

  // Validation tab
  it('switches to Validation tab and shows checks', () => {
    renderResults()
    clickTab('Validation')
    expect(screen.getByText('All checks passed')).toBeInTheDocument()
    expect(screen.getByText(/Timeline alignment/)).toBeInTheDocument()
  })
})
