import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import useJobPolling from './useJobPolling'

// Mock the API module
vi.mock('../services/api', () => ({
  submitJob: vi.fn(),
  getJobStatus: vi.fn(),
}))

import { submitJob, getJobStatus } from '../services/api'

// Mock localStorage
let store = {}
const mockLocalStorage = {
  getItem: vi.fn((key) => store[key] ?? null),
  setItem: vi.fn((key, value) => { store[key] = value }),
  removeItem: vi.fn((key) => { delete store[key] }),
}

describe('useJobPolling', () => {
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

  it('starts in idle state', () => {
    const { result } = renderHook(() => useJobPolling('test_type'))
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.isPolling).toBe(false)
  })

  it('submits a job and saves to localStorage', async () => {
    submitJob.mockResolvedValue({ job_id: 'job-123', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'running' })

    const { result } = renderHook(() => useJobPolling('test_type'))

    await act(async () => {
      await result.current.submit({ text: 'hello' })
    })

    expect(submitJob).toHaveBeenCalledWith('test_type', 'default', { text: 'hello' })
    expect(store['vpma_job_test_type']).toBe('job-123')
  })

  it('polls until completed and sets result', async () => {
    submitJob.mockResolvedValue({ job_id: 'job-456', status: 'pending' })
    getJobStatus
      .mockResolvedValueOnce({ status: 'running' })
      .mockResolvedValueOnce({ status: 'running' })
      .mockResolvedValueOnce({ status: 'completed', result: { suggestions: [] } })

    const { result } = renderHook(() => useJobPolling('test_type'))

    await act(async () => {
      await result.current.submit({ text: 'test' })
    })

    // First poll
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })
    expect(result.current.status).toBe('running')

    // Second poll
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    // Third poll — completes
    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(result.current.status).toBe('completed')
    expect(result.current.result).toEqual({ suggestions: [] })
    expect(result.current.isPolling).toBe(false)
    expect(store['vpma_job_test_type']).toBeUndefined()
  })

  it('sets error on job failure', async () => {
    submitJob.mockResolvedValue({ job_id: 'job-fail', status: 'pending' })
    getJobStatus.mockResolvedValueOnce({ status: 'failed', error_message: 'LLM error' })

    const { result } = renderHook(() => useJobPolling('test_type'))

    await act(async () => {
      await result.current.submit({ text: 'test' })
    })

    await act(async () => { await vi.advanceTimersByTimeAsync(1000) })

    expect(result.current.status).toBe('failed')
    expect(result.current.error).toBe('LLM error')
    expect(result.current.isPolling).toBe(false)
  })

  it('sets failed status on submit error', async () => {
    submitJob.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useJobPolling('test_type'))

    await act(async () => {
      await result.current.submit({ text: 'test' })
    })

    expect(result.current.status).toBe('failed')
    expect(result.current.error).toBe('Network error')
  })

  it('resumes polling from localStorage on mount', async () => {
    store['vpma_job_test_type'] = 'resume-job'
    getJobStatus.mockResolvedValueOnce({ status: 'completed', result: { data: 'here' } })

    let hookResult
    await act(async () => {
      const rendered = renderHook(() => useJobPolling('test_type'))
      hookResult = rendered.result
    })

    expect(getJobStatus).toHaveBeenCalledWith('resume-job')
    expect(hookResult.current.status).toBe('completed')
    expect(hookResult.current.result).toEqual({ data: 'here' })
  })

  it('clear resets all state', async () => {
    submitJob.mockResolvedValue({ job_id: 'job-clear', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'running' })

    const { result } = renderHook(() => useJobPolling('test_type'))

    await act(async () => {
      await result.current.submit({ text: 'test' })
    })

    act(() => {
      result.current.clear()
    })

    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
    expect(result.current.isPolling).toBe(false)
    expect(store['vpma_job_test_type']).toBeUndefined()
  })

  it('uses different localStorage keys for different job types', async () => {
    submitJob.mockResolvedValue({ job_id: 'job-a', status: 'pending' })
    getJobStatus.mockResolvedValue({ status: 'running' })

    const { result: result1 } = renderHook(() => useJobPolling('type_a'))

    await act(async () => {
      await result1.current.submit({ text: 'a' })
    })

    expect(store['vpma_job_type_a']).toBe('job-a')
    expect(store['vpma_job_type_b']).toBeUndefined()
  })
})
