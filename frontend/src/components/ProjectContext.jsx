/**
 * ProjectContext — provides the current project ID to all components.
 *
 * Replaces hardcoded 'default' project IDs throughout the app.
 * MVP: single project, but the context pattern supports multi-project later.
 */
import { createContext, useContext, useState } from 'react'

const ProjectContext = createContext(null)

export function ProjectProvider({ children, initialProjectId = 'default' }) {
  const [projectId, setProjectId] = useState(initialProjectId)

  return (
    <ProjectContext.Provider value={{ projectId, setProjectId }}>
      {children}
    </ProjectContext.Provider>
  )
}

export function useProject() {
  const ctx = useContext(ProjectContext)
  if (!ctx) {
    throw new Error('useProject must be used within a ProjectProvider')
  }
  return ctx
}
