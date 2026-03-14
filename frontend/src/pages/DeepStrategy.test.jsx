import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import DeepStrategy from './DeepStrategy'

// Mock API
vi.mock('../services/api', () => ({
  deepStrategyApply: vi.fn(),
  submitJob: vi.fn(),
  getJobStatus: vi.fn(),
}))

import { deepStrategyApply, submitJob, getJobStatus } from '../services/api'

// Mock toast
const mockToast = { success: vi.fn(), error: vi.fn(), info: vi.fn() }
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

vi.mock('../components/ReconciliationPanel', () => ({
  default: ({ onClose }) => (
    <div data-testid="reconciliation-panel">
      <button onClick={onClose}>Close</button>
    </div>
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

/** Helper: simulate full job lifecycle (submit → poll → complete) */
async function submitAndComplete(result) {
  submitJob.mockResolvedValue({ job_id: 'test-job', status: 'pending' })
  getJobStatus.mockResolvedValue({ status: 'completed', result })
}

// Mock localStorage
let store = {}
const mockLocalStorage = {
  getItem: vi.fn((key) => store[key] ?? null),
  setItem: vi.fn((key, value) => { store[key] = value }),
  removeItem: vi.fn((key) => { delete store[key] }),
}

beforeEach(() => {
  store = {}
  vi.stubGlobal('localStorage', mockLocalStorage)
  vi.clearAllMocks()
  vi.useFakeTimers()
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('DeepStrategy page', () => {
  it('renders page heading and description', () => {
    render(<DeepStrategy />)
    expect(screen.getByText('Audit')).toBeInTheDocument()
    expect(screen.getByText(/Check your documents for inconsistencies/)).toBeInTheDocument()
  })

  it('shows ArtifactUploader initially (not hidden)', () => {
    render(<DeepStrategy />)
    expect(screen.getByTestId('artifact-uploader')).toBeInTheDocument()
    expect(uploaderIsHidden()).toBe(false)
  })

  it('hides uploader during analysis and shows progress', async () => {
    submitJob.mockResolvedValue({ job_id: 'test-job', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'running' })

    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    // First poll
    await act(async () => { vi.advanceTimersByTime(1000) })

    expect(screen.getByTestId('progress-bar')).toBeInTheDocument()
    expect(screen.getByText('Analyzing artifacts...')).toBeInTheDocument()
    expect(uploaderIsHidden()).toBe(true)
  })

  it('shows results after successful analysis with inconsistencies', async () => {
    const result = makeResult(3, 2)
    await submitAndComplete(result)

    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    // Poll completes — use async version to flush microtasks from poll promise
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByTestId('results-panel')).toBeInTheDocument()
    expect(mockToast.success).toHaveBeenCalledWith(
      'Found 3 inconsistencies, 2 updates proposed'
    )
  })

  it('shows different toast when no inconsistencies found', async () => {
    const result = makeResult(0, 0)
    await submitAndComplete(result)

    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(mockToast.success).toHaveBeenCalledWith(
      'Analysis complete — no inconsistencies found'
    )
  })

  it('shows error panel when analysis fails', async () => {
    submitJob.mockResolvedValue({ job_id: 'fail-job', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'failed', error_message: 'LLM timeout' })

    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })

    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByText('LLM timeout')).toBeInTheDocument()
    expect(screen.getByText('Try again')).toBeInTheDocument()
    expect(mockToast.error).toHaveBeenCalledWith('Document consistency analysis failed')
  })

  it('shows "Start new analysis" button with results and resets on click', async () => {
    await submitAndComplete(makeResult())
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(screen.getByTestId('results-panel')).toBeInTheDocument()

    const newBtn = screen.getByText('Start new analysis')
    expect(newBtn).toBeInTheDocument()

    fireEvent.click(newBtn)

    expect(screen.queryByTestId('results-panel')).not.toBeInTheDocument()
    expect(uploaderIsHidden()).toBe(false)
  })

  it('calls deepStrategyApply and shows success toast on apply', async () => {
    await submitAndComplete(makeResult())
    deepStrategyApply.mockResolvedValue({
      applied: [{ status: 'applied' }, { status: 'applied' }],
      copied_to_clipboard: ['Risk Log'],
    })
    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })
    expect(screen.getByTestId('results-panel')).toBeInTheDocument()

    await act(async () => {
      fireEvent.click(screen.getByTestId('apply-btn'))
    })

    expect(deepStrategyApply).toHaveBeenCalledWith([
      { target: 'A', change_type: 'modify' },
    ])
    expect(mockToast.success).toHaveBeenCalledWith(
      'Applied 2 updates. 1 artifact available for clipboard'
    )
  })

  it('tells user they can switch tabs during analysis', async () => {
    submitJob.mockResolvedValue({ job_id: 'test-job', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'running' })

    render(<DeepStrategy />)

    await act(async () => {
      fireEvent.click(screen.getByTestId('analyze-btn'))
    })
    await act(async () => { vi.advanceTimersByTime(1000) })

    expect(screen.getByText(/You can switch tabs/)).toBeInTheDocument()
  })

  it('renders Document Consistency and Reconciliation sections', () => {
    render(<DeepStrategy />)
    expect(screen.getByText('Document Consistency')).toBeInTheDocument()
    expect(screen.getByText('Reconciliation')).toBeInTheDocument()
    expect(screen.getByText('Run Reconciliation')).toBeInTheDocument()
  })

  it('opens and closes reconciliation panel', () => {
    render(<DeepStrategy />)
    fireEvent.click(screen.getByText('Run Reconciliation'))
    expect(screen.getByTestId('reconciliation-panel')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Close'))
    expect(screen.queryByTestId('reconciliation-panel')).not.toBeInTheDocument()
  })
})
