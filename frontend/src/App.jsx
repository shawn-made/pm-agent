/**
 * Root application component — provides layout, navigation, toast context, and backend health check.
 */
import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import { ToastProvider } from './components/Toast.jsx'
import { ProjectProvider } from './components/ProjectContext.jsx'
import ArtifactSync from './pages/ArtifactSync.jsx'
import ProjectDoc from './pages/ProjectDoc.jsx'
import Intake from './pages/Intake.jsx'
import DeepStrategy from './pages/DeepStrategy.jsx'
import Settings from './pages/Settings.jsx'
import { healthCheck } from './services/api'

/** App shell with header, two-tab navigation, and footer. Checks backend health on mount. */
function App() {
  const [backendStatus, setBackendStatus] = useState('checking') // 'checking', 'ok', 'error'

  useEffect(() => {
    healthCheck()
      .then(() => setBackendStatus('ok'))
      .catch(() => setBackendStatus('error'))
  }, [])

  return (
    <ProjectProvider>
    <ToastProvider>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Backend connection warning */}
        {backendStatus === 'error' && (
          <div className="bg-amber-50 border-b border-amber-200 px-6 py-2">
            <p className="text-xs text-amber-700 text-center">
              Backend not connected. Start it with: <code className="bg-amber-100 px-1 rounded">cd backend && uvicorn app.main:app --reload</code>
            </p>
          </div>
        )}

        {/* Header */}
        <header className="border-b border-gray-200 bg-white">
          <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900">VPMA</h1>
            <nav className="flex gap-1">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                Artifact Sync
              </NavLink>
              <NavLink
                to="/project"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                Knowledge Base
              </NavLink>
              <NavLink
                to="/deep-strategy"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                Deep Strategy
              </NavLink>
              <NavLink
                to="/settings"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`
                }
              >
                Settings
              </NavLink>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-5xl mx-auto px-6 py-8 w-full flex-1">
          <Routes>
            <Route path="/" element={<ArtifactSync />} />
            <Route path="/project" element={<ProjectDoc />} />
            <Route path="/intake" element={<Intake />} />
            <Route path="/deep-strategy" element={<DeepStrategy />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 bg-white">
          <div className="max-w-5xl mx-auto px-6 py-3 text-xs text-gray-400 text-center">
            VPMA v0.3.0 — Phase 1B
          </div>
        </footer>
      </div>
    </ToastProvider>
    </ProjectProvider>
  )
}

export default App
