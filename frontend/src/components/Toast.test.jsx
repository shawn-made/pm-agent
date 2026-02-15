import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { ToastProvider, useToast } from './Toast'

function ToastTrigger({ type = 'success', message = 'Test message' }) {
  const toast = useToast()
  return (
    <button onClick={() => toast[type](message)}>
      trigger
    </button>
  )
}

function renderWithToast(props = {}) {
  return render(
    <ToastProvider>
      <ToastTrigger {...props} />
    </ToastProvider>
  )
}

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('shows a success toast', () => {
    renderWithToast({ type: 'success', message: 'Saved!' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    expect(screen.getByText('Saved!')).toBeInTheDocument()
  })

  it('shows an error toast', () => {
    renderWithToast({ type: 'error', message: 'Something broke' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    expect(screen.getByText('Something broke')).toBeInTheDocument()
  })

  it('shows an info toast', () => {
    renderWithToast({ type: 'info', message: 'FYI' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    expect(screen.getByText('FYI')).toBeInTheDocument()
  })

  it('auto-dismisses success toast after ~3 seconds', () => {
    renderWithToast({ type: 'success', message: 'Will disappear' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    expect(screen.getByText('Will disappear')).toBeInTheDocument()

    act(() => {
      vi.advanceTimersByTime(3100)
    })
    expect(screen.queryByText('Will disappear')).not.toBeInTheDocument()
  })

  it('auto-dismisses error toast after ~5 seconds', () => {
    renderWithToast({ type: 'error', message: 'Error msg' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })

    act(() => {
      vi.advanceTimersByTime(3100)
    })
    expect(screen.getByText('Error msg')).toBeInTheDocument()

    act(() => {
      vi.advanceTimersByTime(2100)
    })
    expect(screen.queryByText('Error msg')).not.toBeInTheDocument()
  })

  it('applies success styling class', () => {
    renderWithToast({ type: 'success', message: 'green toast' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    const toast = screen.getByText('green toast')
    expect(toast.className).toContain('bg-green-600')
  })

  it('applies error styling class', () => {
    renderWithToast({ type: 'error', message: 'red toast' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    const toast = screen.getByText('red toast')
    expect(toast.className).toContain('bg-red-600')
  })

  it('applies info styling class', () => {
    renderWithToast({ type: 'info', message: 'gray toast' })
    act(() => {
      fireEvent.click(screen.getByText('trigger'))
    })
    const toast = screen.getByText('gray toast')
    expect(toast.className).toContain('bg-gray-800')
  })
})
