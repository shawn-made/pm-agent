import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ProcessModeCards from './ProcessModeCards'

describe('ProcessModeCards', () => {
  it('renders three mode cards', () => {
    render(<ProcessModeCards mode="extract" onModeChange={() => {}} />)
    expect(screen.getByText('Extract')).toBeInTheDocument()
    expect(screen.getByText('Analyze')).toBeInTheDocument()
    expect(screen.getByText('Log Session')).toBeInTheDocument()
  })

  it('renders descriptions for each mode', () => {
    render(<ProcessModeCards mode="extract" onModeChange={() => {}} />)
    expect(screen.getByText('Pull updates from notes and transcripts')).toBeInTheDocument()
    expect(screen.getByText('Get feedback on a draft document')).toBeInTheDocument()
    expect(screen.getByText('Record decisions and update your KB')).toBeInTheDocument()
  })

  it('highlights the active mode card', () => {
    render(<ProcessModeCards mode="analyze" onModeChange={() => {}} />)
    const analyzeButton = screen.getByText('Analyze').closest('button')
    expect(analyzeButton.className).toContain('border-indigo-400')
  })

  it('calls onModeChange when a card is clicked', () => {
    const handleChange = vi.fn()
    render(<ProcessModeCards mode="extract" onModeChange={handleChange} />)
    fireEvent.click(screen.getByText('Analyze'))
    expect(handleChange).toHaveBeenCalledWith('analyze')
  })

  it('calls onModeChange with log_session when Log Session clicked', () => {
    const handleChange = vi.fn()
    render(<ProcessModeCards mode="extract" onModeChange={handleChange} />)
    fireEvent.click(screen.getByText('Log Session'))
    expect(handleChange).toHaveBeenCalledWith('log_session')
  })
})
