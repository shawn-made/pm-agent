/**
 * Ingest page — unified entry point for getting content into the Knowledge Base.
 *
 * Two sub-tabs:
 *   From Files — upload or paste existing documents (Intake)
 *   From Text  — paste notes, transcripts, or ideas for LLM analysis (ArtifactSync)
 */
import { useState } from 'react'
import Intake from './Intake'
import ArtifactSync from './ArtifactSync'

const TABS = [
  {
    key: 'files',
    label: 'From Files',
    subtitle: 'Upload or paste existing documents',
  },
  {
    key: 'text',
    label: 'From Text',
    subtitle: 'Paste notes, transcripts, or ideas',
  },
]

export default function Ingest() {
  const [activeTab, setActiveTab] = useState('files')

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="border-l-4 border-blue-400 pl-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Add to Knowledge Base</h2>
        <p className="text-sm text-gray-500">
          Bring content into your project — from files or freeform text.
        </p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 border-b border-gray-200">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab.key
                ? 'border-blue-500 text-blue-700'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <span>{tab.label}</span>
            <span className="ml-2 text-xs font-normal text-gray-400">{tab.subtitle}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'files' ? <Intake /> : <ArtifactSync />}
    </div>
  )
}
