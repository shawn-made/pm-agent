import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import FolderBrowser from './FolderBrowser'

// Mock the API module
vi.mock('../services/api', () => ({
  browseFolders: vi.fn(),
}))

import { browseFolders } from '../services/api'

const mockResponse = {
  current_path: '/Users/test',
  parent_path: null,
  directories: [
    { name: 'Documents', path: '/Users/test/Documents' },
    { name: 'Projects', path: '/Users/test/Projects' },
    { name: 'Downloads', path: '/Users/test/Downloads' },
  ],
}

const mockSubResponse = {
  current_path: '/Users/test/Projects',
  parent_path: '/Users/test',
  directories: [
    { name: 'MyProject', path: '/Users/test/Projects/MyProject' },
  ],
}

describe('FolderBrowser', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner initially', () => {
    browseFolders.mockReturnValue(new Promise(() => {}))
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)
    expect(screen.getAllByText('Loading...').length).toBeGreaterThanOrEqual(1)
  })

  it('displays directories after loading', async () => {
    browseFolders.mockResolvedValue(mockResponse)
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Documents')).toBeInTheDocument()
      expect(screen.getByText('Projects')).toBeInTheDocument()
      expect(screen.getByText('Downloads')).toBeInTheDocument()
    })
  })

  it('shows current path', async () => {
    browseFolders.mockResolvedValue(mockResponse)
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('/Users/test')).toBeInTheDocument()
    })
  })

  it('navigates into subdirectory on click', async () => {
    browseFolders
      .mockResolvedValueOnce(mockResponse)
      .mockResolvedValueOnce(mockSubResponse)

    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Projects'))

    await waitFor(() => {
      expect(screen.getByText('MyProject')).toBeInTheDocument()
      expect(screen.getByText('/Users/test/Projects')).toBeInTheDocument()
    })

    expect(browseFolders).toHaveBeenCalledWith('/Users/test/Projects')
  })

  it('shows parent navigation when not at home', async () => {
    browseFolders.mockResolvedValue(mockSubResponse)
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('..')).toBeInTheDocument()
    })
  })

  it('hides parent navigation at home directory', async () => {
    browseFolders.mockResolvedValue(mockResponse)
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Documents')).toBeInTheDocument()
    })

    expect(screen.queryByText('..')).not.toBeInTheDocument()
  })

  it('calls onSelect with current path on Select button', async () => {
    browseFolders.mockResolvedValue(mockResponse)
    const onSelect = vi.fn()
    const onClose = vi.fn()
    render(<FolderBrowser onSelect={onSelect} onClose={onClose} />)

    await waitFor(() => {
      expect(screen.getByText('Documents')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Select This Folder'))

    expect(onSelect).toHaveBeenCalledWith('/Users/test')
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClose on Cancel button', async () => {
    browseFolders.mockResolvedValue(mockResponse)
    const onClose = vi.fn()
    render(<FolderBrowser onSelect={vi.fn()} onClose={onClose} />)

    await waitFor(() => {
      expect(screen.getByText('Documents')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Cancel'))
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onClose on X button', async () => {
    browseFolders.mockResolvedValue(mockResponse)
    const onClose = vi.fn()
    render(<FolderBrowser onSelect={vi.fn()} onClose={onClose} />)

    await waitFor(() => {
      expect(screen.getByText('Select Folder')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByLabelText('Close'))
    expect(onClose).toHaveBeenCalled()
  })

  it('shows error on API failure', async () => {
    browseFolders.mockRejectedValue(new Error('Permission denied'))
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Permission denied')).toBeInTheDocument()
    })
  })

  it('shows empty directory message', async () => {
    browseFolders.mockResolvedValue({
      current_path: '/Users/test/EmptyDir',
      parent_path: '/Users/test',
      directories: [],
    })
    render(<FolderBrowser onSelect={vi.fn()} onClose={vi.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Empty directory')).toBeInTheDocument()
    })
  })
})
