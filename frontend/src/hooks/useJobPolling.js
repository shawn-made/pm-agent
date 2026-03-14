/**
 * Hook for fire-and-forget job submission with polling (Task 57).
 *
 * Submits a job via POST /api/jobs, saves job_id to localStorage,
 * and polls GET /api/jobs/{job_id} until completion. Survives page
 * navigation — on mount, resumes polling for any in-progress job.
 *
 * @param {string} jobType - Job type key (e.g., 'deep_strategy', 'artifact_sync')
 * @returns {{ submit, status, result, error, isPolling, clear }}
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { submitJob, getJobStatus } from '../services/api'

const INITIAL_INTERVAL = 1000     // 1s for first 10 polls
const SLOW_INTERVAL = 3000        // then 3s
const SLOW_AFTER_POLLS = 10

function storageKey(jobType) {
  return `vpma_job_${jobType}`
}

export default function useJobPolling(jobType) {
  const [status, setStatus] = useState('idle')  // idle | pending | running | completed | failed
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isPolling, setIsPolling] = useState(false)
  const timerRef = useRef(null)
  const pollCountRef = useRef(0)
  const jobIdRef = useRef(null)
  const pollRef = useRef(null)

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    setIsPolling(false)
    pollCountRef.current = 0
  }, [])

  // Store poll in a ref so setTimeout can always call the latest version
  const poll = useCallback(async () => {
    const jobId = jobIdRef.current
    if (!jobId) return

    try {
      const data = await getJobStatus(jobId)
      setStatus(data.status)

      if (data.status === 'completed') {
        setResult(data.result)
        localStorage.removeItem(storageKey(jobType))
        stopPolling()
        return
      }

      if (data.status === 'failed') {
        setError(data.error_message || 'Job failed')
        localStorage.removeItem(storageKey(jobType))
        stopPolling()
        return
      }

      // Still pending/running — schedule next poll via ref
      pollCountRef.current += 1
      const interval = pollCountRef.current >= SLOW_AFTER_POLLS ? SLOW_INTERVAL : INITIAL_INTERVAL
      timerRef.current = setTimeout(() => pollRef.current(), interval)
    } catch {
      // Network error — keep trying (the server may just be slow)
      pollCountRef.current += 1
      const interval = pollCountRef.current >= SLOW_AFTER_POLLS ? SLOW_INTERVAL : INITIAL_INTERVAL
      timerRef.current = setTimeout(() => pollRef.current(), interval)
    }
  }, [jobType, stopPolling])

  // Keep ref in sync + handle mount resume
  useEffect(() => {
    pollRef.current = poll
  }, [poll])

  const startPolling = useCallback((jobId) => {
    jobIdRef.current = jobId
    pollCountRef.current = 0
    setIsPolling(true)
    timerRef.current = setTimeout(() => pollRef.current(), INITIAL_INTERVAL)
  }, [])

  // On mount: check localStorage for an in-progress job
  useEffect(() => {
    const savedJobId = localStorage.getItem(storageKey(jobType))
    if (savedJobId) {
      jobIdRef.current = savedJobId
      // eslint-disable-next-line react-hooks/set-state-in-effect -- initializing from persisted state on mount
      setStatus('running')
      setIsPolling(true)
      // Poll immediately on resume
      pollRef.current?.()
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [jobType])

  const submit = useCallback(async (payload, projectId = 'default') => {
    // Reset state
    setResult(null)
    setError(null)
    setStatus('pending')

    try {
      const data = await submitJob(jobType, projectId, payload)
      localStorage.setItem(storageKey(jobType), data.job_id)
      startPolling(data.job_id)
    } catch (submitErr) {
      setStatus('failed')
      setError(submitErr.message)
    }
  }, [jobType, startPolling])

  const clear = useCallback(() => {
    stopPolling()
    localStorage.removeItem(storageKey(jobType))
    jobIdRef.current = null
    setStatus('idle')
    setResult(null)
    setError(null)
  }, [jobType, stopPolling])

  return { submit, status, result, error, isPolling, clear }
}
