/**
 * ProjectProvider — provides the current project ID to all components.
 *
 * Replaces hardcoded 'default' project IDs throughout the app.
 * MVP: single project, but the context pattern supports multi-project later.
 *
 * Context object is in ./projectContext.js (separate for fast-refresh).
 * useProject hook is in ./useProject.js (separate for fast-refresh).
 */
import { useState } from 'react'
import { ProjectContext } from './ProjectContextDef'

export function ProjectProvider({ children, initialProjectId = 'default' }) {
  const [projectId, setProjectId] = useState(initialProjectId)

  return (
    <ProjectContext.Provider value={{ projectId, setProjectId }}>
      {children}
    </ProjectContext.Provider>
  )
}
