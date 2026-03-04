import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import PassProgressBar from './PassProgressBar'

describe('PassProgressBar', () => {
  it('renders all 4 pass labels', () => {
    render(<PassProgressBar activePass={-1} />)
    expect(screen.getByText('Dependency Graph')).toBeInTheDocument()
    expect(screen.getByText('Inconsistencies')).toBeInTheDocument()
    expect(screen.getByText('Proposed Updates')).toBeInTheDocument()
    expect(screen.getByText('Cross-Validation')).toBeInTheDocument()
  })

  it('shows step numbers when not started', () => {
    render(<PassProgressBar activePass={-1} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
  })

  it('shows active pass with pulse animation', () => {
    const { container } = render(<PassProgressBar activePass={1} />)
    const circles = container.querySelectorAll('.rounded-full')
    // Second circle (index 1) should have animate-pulse
    expect(circles[1].className).toContain('animate-pulse')
    // First should not (it's complete)
    expect(circles[0].className).not.toContain('animate-pulse')
  })

  it('shows checkmark for completed passes', () => {
    render(<PassProgressBar activePass={2} />)
    // First two passes complete — should have SVG checkmarks instead of numbers
    expect(screen.queryByText('1')).not.toBeInTheDocument()
    expect(screen.queryByText('2')).not.toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument() // Active
    expect(screen.getByText('4')).toBeInTheDocument() // Pending
  })

  it('shows all complete when activePass is 4', () => {
    render(<PassProgressBar activePass={4} />)
    // No step numbers should be visible (all checkmarks)
    expect(screen.queryByText('1')).not.toBeInTheDocument()
    expect(screen.queryByText('2')).not.toBeInTheDocument()
    expect(screen.queryByText('3')).not.toBeInTheDocument()
    expect(screen.queryByText('4')).not.toBeInTheDocument()
  })
})
