import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProjectProvider, useProject } from './ProjectContext'

function TestConsumer() {
  const { projectId } = useProject()
  return <div data-testid="pid">{projectId}</div>
}

describe('ProjectContext', () => {
  it('provides default project ID', () => {
    render(
      <ProjectProvider>
        <TestConsumer />
      </ProjectProvider>
    )
    expect(screen.getByTestId('pid').textContent).toBe('default')
  })

  it('accepts initial project ID', () => {
    render(
      <ProjectProvider initialProjectId="custom-project">
        <TestConsumer />
      </ProjectProvider>
    )
    expect(screen.getByTestId('pid').textContent).toBe('custom-project')
  })

  it('throws when used outside provider', () => {
    const consoleError = console.error
    console.error = () => {} // suppress React error boundary output
    expect(() => render(<TestConsumer />)).toThrow(
      'useProject must be used within a ProjectProvider'
    )
    console.error = consoleError
  })
})
