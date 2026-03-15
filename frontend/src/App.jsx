/**
 * Root application component — provides layout, navigation, toast context, and backend health check.
 * Uses a left sidebar for navigation with icon + label + description for each tab.
 */
import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { ToastProvider } from './components/Toast.jsx'
import { ProjectProvider } from './components/ProjectContext.jsx'
import ArtifactSync from './pages/ArtifactSync.jsx'
import ProjectDoc from './pages/ProjectDoc.jsx'
import Intake from './pages/Intake.jsx'
import DeepStrategy from './pages/DeepStrategy.jsx'
import Settings from './pages/Settings.jsx'
import { healthCheck } from './services/api'

const COLOR_BORDERS = {
  blue: 'border-blue-400',
  indigo: 'border-indigo-400',
  amber: 'border-amber-400',
  emerald: 'border-emerald-400',
}

function SidebarLink({ to, end, icon, label, description, color }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors border-l-[3px] ${
          isActive
            ? `bg-gray-100 ${COLOR_BORDERS[color] || 'border-gray-400'}`
            : 'border-transparent hover:bg-gray-50'
        }`
      }
    >
      <span className="mt-0.5 flex-shrink-0">{icon}</span>
      <div className="min-w-0">
        <span className="text-sm font-medium text-gray-900 block">{label}</span>
        {description && <p className="text-xs text-gray-400 mt-0.5 leading-tight">{description}</p>}
      </div>
    </NavLink>
  )
}

/** App shell with sidebar navigation and footer. Checks backend health on mount. */
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
      <div className="min-h-screen bg-gray-50 flex">
        {/* Sidebar */}
        <aside className="w-60 bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0 flex-shrink-0">
          {/* Branding */}
          <div className="px-5 py-4 border-b border-gray-100">
            <h1 className="text-lg font-semibold text-gray-900 leading-tight">VPMA</h1>
            <p className="text-xs text-gray-400">Project Intelligence</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1">
            <SidebarLink
              to="/import"
              color="blue"
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
              }
              label="Import"
              description="Bring files into your project"
            />
            <SidebarLink
              to="/process"
              color="indigo"
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                </svg>
              }
              label="Process"
              description="Extract, analyze, and log"
            />
            <SidebarLink
              to="/audit"
              color="amber"
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
              }
              label="Audit"
              description="Check document consistency"
            />
            <SidebarLink
              to="/"
              end
              color="emerald"
              icon={
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
                </svg>
              }
              label="Knowledge Base"
              description="Your project intelligence"
            />
          </nav>

          {/* Settings at bottom */}
          <div className="px-3 py-3 border-t border-gray-100">
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                }`
              }
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 0 1 1.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.56.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.893.149c-.425.07-.765.383-.93.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 0 1-1.449.12l-.738-.527c-.35-.25-.806-.272-1.204-.107-.397.165-.71.505-.78.929l-.15.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 0 1-.12-1.45l.527-.737c.25-.35.272-.806.108-1.204-.165-.397-.506-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.108-1.204l-.526-.738a1.125 1.125 0 0 1 .12-1.45l.773-.773a1.125 1.125 0 0 1 1.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
              <span className="text-sm font-medium">Settings</span>
            </NavLink>
          </div>
        </aside>

        {/* Main content area */}
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Backend connection warning */}
          {backendStatus === 'error' && (
            <div className="bg-amber-50 border-b border-amber-200 px-6 py-2">
              <p className="text-xs text-amber-700 text-center">
                Backend not connected. Start it with: <code className="bg-amber-100 px-1 rounded">cd backend && uvicorn app.main:app --reload</code>
              </p>
            </div>
          )}

          {/* Main Content */}
          <main className="max-w-5xl mx-auto px-6 py-8 w-full flex-1">
            <Routes>
              <Route path="/" element={<ProjectDoc />} />
              <Route path="/import" element={<Intake />} />
              <Route path="/process" element={<ArtifactSync />} />
              <Route path="/audit" element={<DeepStrategy />} />
              <Route path="/settings" element={<Settings />} />
              {/* Redirects for old routes */}
              <Route path="/kb" element={<Navigate to="/" replace />} />
              <Route path="/project" element={<Navigate to="/" replace />} />
              <Route path="/intake" element={<Navigate to="/import" replace />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="border-t border-gray-200 bg-white">
            <div className="max-w-5xl mx-auto px-6 py-3 text-xs text-gray-400 text-center">
              VPMA v0.6.0 — Phase 3A
            </div>
          </footer>
        </div>
      </div>
    </ToastProvider>
    </ProjectProvider>
  )
}

export default App
