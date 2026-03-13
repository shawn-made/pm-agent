import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import DeepStrategy from './DeepStrategy'

// Mock API
vi.mock('../services/api', () => ({
  deepStrategyAnalyze: vi.fn(),
  deepStrategyApply: vi.fn(),
}))

import { deepStrategyAnalyze, deepStrategyApply } from '../services/api'

// Mock toast
const mockToast = { success: vi.fn(), error: vi.fn() }
vi.mock('../components/ToastContext', () => ({
  useToast: () => mockToast,
}))

// Mock child components to isolate page logic
vi.mock('../components/ArtifactUploader', () => ({
  default: ({ onAnalyze, isLoading }) => (
    <div data-testid="artifact-uploader">
      <button
        data-testid="analyze-btn"
        onClick={() => onAnalyze([{ name: 'A', content: 'text', priority: 1 }])}
        disabled={isLoading}
      >
        Analyze
      </button>
    </div>
  ),
}))

vi.mock('../components/DeepStrategyResults', () => ({
  default: ({ results, onApply, isApplying }) => (
    <div data-testid="results-panel">
      <span data-testid="inconsistency-count">
        {results.summary.inconsistencies_found}
      </span>
      <button
        data-testid="apply-btn"
        onClick={() => onApply([{ target: 'A', change_type: 'modify' }])}
        disabled={isApplying}
      >
        Apply
      </button>
    </div>
  ),
}))

vi.mock('../components/PassProgressBar', () => ({
  default: ({ activePass }) => (
    <div data-testid="progress-bar">Pass: {activePass}</div>
  ),
}))

function makeResult(inconsistencies = 2, updates = 3) {
  return {
    summary: {
      inconsistencies_found: inconsistencies,
      updates_proposed: updates,
      artifacts_analyzed: 2,
      consistency_score: 0.85,
    },
    inconsistencies: [],
    proposed_updates: [],
    validation: {},
  }
}

/** Helper: check if the uploader wrapper has the 'hidden' class */
function uploaderIsHidden() {
  return screen.getByTestId('artifact-uploader').closest('div[class]')?.classList.contains('hidden')
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('DeepStrategy page', () => {
  it('renders page heading and description', () => {
    render(<DeepStrategy />)
    expect(screen.getByText('Deep Strategy')).toBeInTheDocument()
    expect(screen.getByText(/Upload 2\+ project artifacts/)).toBeInTheDocument()
  })

  it('shows ArtifactUploader initially (not hidden)', () => {
    render(<DeepStrategy />)
    expect(screen.getByTestId('artifact-uploader')).toBeInTheDocument()
    expect(uploaderIsHidden()).toBe(false)
  })

  it('hides uploader during analysis and shows progress', async () => {
    let resolve
    deepStrategyAnalyze.mockReturnValue(new Promise(r => { resolve = r }))
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    expect(screen.getByTestId('progress-bar')).toBeInTheDocument()
    expect(screen.getByText('Analyzing artifacts...')).toBeInTheDocument()
    // Uploader is still in DOM but hidden (preserves content)
    expect(uploaderIsHidden()).toBe(true)

    await act(async () => { resolve(makeResult()) })
  })

  it('shows results after successful analysis with inconsistencies', async () => {
    const result = makeResult(3, 2)
    deepStrategyAnalyze.mockResolvedValue(result)
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    await waitFor(() => {
      expect(screen.getByTestId('results-panel')).toBeInTheDocument()
    })
    expect(mockToast.success).toHaveBeenCalledWith(
      'Found 3 inconsistencies, 2 updates proposed'
    )
  })

  it('shows success toast with singular forms when counts are 1', async () => {
    const result = makeResult(1, 1)
    deepStrategyAnalyze.mockResolvedValue(result)
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith(
        'Found 1 inconsistency, 1 update proposed'
      )
    })
  })

  it('shows different toast when no inconsistencies found', async () => {
    const result = makeResult(0, 0)
    deepStrategyAnalyze.mockResolvedValue(result)
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith(
        'Analysis complete — no inconsistencies found'
      )
    })
  })

  it('shows error panel when analysis fails and keeps uploader visible', async () => {
    deepStrategyAnalyze.mockRejectedValue(new Error('LLM timeout'))
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    await waitFor(() => {
      expect(screen.getByText('LLM timeout')).toBeInTheDocument()
    })
    expect(screen.getByText('Try again')).toBeInTheDocument()
    expect(mockToast.error).toHaveBeenCalledWith('Deep Strategy analysis failed')
    // Uploader is visible (not hidden) so user can retry with same content
    expect(uploaderIsHidden()).toBe(false)
  })

  it('clears error on Try Again', async () => {
    deepStrategyAnalyze.mockRejectedValue(new Error('LLM timeout'))
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await waitFor(() => expect(screen.getByText('Try again')).toBeInTheDocument())

    fireEvent.click(screen.getByText('Try again'))

    expect(screen.queryByText('LLM timeout')).not.toBeInTheDocument()
    expect(uploaderIsHidden()).toBe(false)
  })

  it('shows "Start new analysis" button with results and resets on click', async () => {
    deepStrategyAnalyze.mockResolvedValue(makeResult())
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await waitFor(() => expect(screen.getByTestId('results-panel')).toBeInTheDocument())

    expect(uploaderIsHidden()).toBe(true)
    const newBtn = screen.getByText('Start new analysis')
    expect(newBtn).toBeInTheDocument()

    fireEvent.click(newBtn)

    expect(screen.queryByTestId('results-panel')).not.toBeInTheDocument()
    expect(uploaderIsHidden()).toBe(false)
  })

  it('calls deepStrategyApply and shows success toast on apply', async () => {
    deepStrategyAnalyze.mockResolvedValue(makeResult())
    deepStrategyApply.mockResolvedValue({
      applied: [{ status: 'applied' }, { status: 'applied' }],
      copied_to_clipboard: ['Risk Log'],
    })
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await waitFor(() => expect(screen.getByTestId('results-panel')).toBeInTheDocument())

    await act(async () => {
      fireEvent.click(screen.getByTestId('apply-btn'))
    })

    await waitFor(() => {
      expect(deepStrategyApply).toHaveBeenCalledWith([
        { target: 'A', change_type: 'modify' },
      ])
      expect(mockToast.success).toHaveBeenCalledWith(
        'Applied 2 updates. 1 artifact available for clipboard'
      )
    })
  })

  it('shows error toast when apply fails', async () => {
    deepStrategyAnalyze.mockResolvedValue(makeResult())
    deepStrategyApply.mockRejectedValue(new Error('Apply failed'))
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await waitFor(() => expect(screen.getByTestId('results-panel')).toBeInTheDocument())

    await act(async () => {
      fireEvent.click(screen.getByTestId('apply-btn'))
    })

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith(
        'Failed to apply updates: Apply failed'
      )
    })
  })

  it('simulates pass progress during analysis', async () => {
    vi.useFakeTimers()
    let resolve
    deepStrategyAnalyze.mockReturnValue(new Promise(r => { resolve = r }))
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    expect(screen.getByText('Pass: 0')).toBeInTheDocument()

    act(() => { vi.advanceTimersByTime(15000) })
    expect(screen.getByText('Pass: 1')).toBeInTheDocument()

    act(() => { vi.advanceTimersByTime(20000) }) // total 35s
    expect(screen.getByText('Pass: 2')).toBeInTheDocument()

    act(() => { vi.advanceTimersByTime(20000) }) // total 55s
    expect(screen.getByText('Pass: 3')).toBeInTheDocument()

    // Clean up
    await act(async () => { resolve(makeResult()) })
    vi.useRealTimers()
  })
})
