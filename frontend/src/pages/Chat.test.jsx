import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Chat from './Chat'
import { ToastProvider } from '../components/Toast'

vi.mock('../services/api', () => ({
  sendChatMessage: vi.fn(),
  listConversations: vi.fn(),
  getConversation: vi.fn(),
  deleteConversation: vi.fn(),
  applySuggestionByType: vi.fn(),
}))

import {
  sendChatMessage,
  listConversations,
  getConversation,
} from '../services/api'

function renderChat() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Chat />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('Chat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.localStorage = { getItem: vi.fn(() => null), setItem: vi.fn(), removeItem: vi.fn(), clear: vi.fn() }
    window.HTMLElement.prototype.scrollIntoView = vi.fn()
    listConversations.mockResolvedValue({ conversations: [] })
  })

  it('renders the chat page with empty state', async () => {
    renderChat()
    await waitFor(() => {
      expect(screen.getByText('Assistant')).toBeTruthy()
    })
    expect(screen.getByText(/Start a conversation with VPMA/)).toBeTruthy()
    expect(screen.getByText('Brain Dump')).toBeTruthy()
  })

  it('shows conversation list', async () => {
    listConversations.mockResolvedValue({
      conversations: [
        {
          conversation_id: 'conv-1',
          title: 'Risk Discussion',
          mode: 'chat',
          created_at: '2026-03-16T10:00:00',
          last_message_at: '2026-03-16T10:15:00',
          message_count: 4,
        },
      ],
    })

    renderChat()

    await waitFor(() => {
      expect(screen.getByText('Risk Discussion')).toBeTruthy()
    })
    expect(screen.getByText('4 messages')).toBeTruthy()
  })

  it('sends a message and displays response', async () => {
    sendChatMessage.mockResolvedValue({
      conversation_id: 'conv-new',
      message_id: 'msg-1',
      response: 'Here are three risks I found.',
      suggestions: [],
      lpd_sections_referenced: ['Risks'],
      session_id: 'sess-1',
      pii_detected: 0,
      token_count: 100,
    })

    renderChat()

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask VPMA anything/)).toBeTruthy()
    })

    const input = screen.getByPlaceholderText(/Ask VPMA anything/)
    fireEvent.change(input, { target: { value: 'What are the risks?' } })
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith(
        'default',
        'What are the risks?',
        null,
      )
    })

    await waitFor(() => {
      expect(screen.getByText('Here are three risks I found.')).toBeTruthy()
    })
  })

  it('toggles brain dump mode', async () => {
    renderChat()

    await waitFor(() => {
      expect(screen.getByText('Brain Dump')).toBeTruthy()
    })

    // Click brain dump toggle
    fireEvent.click(screen.getByText('Brain Dump'))

    expect(screen.getByText('Brain Dump ON')).toBeTruthy()
    expect(screen.getByPlaceholderText(/Dump your thoughts here/)).toBeTruthy()
  })

  it('loads conversation when clicked', async () => {
    listConversations.mockResolvedValue({
      conversations: [
        {
          conversation_id: 'conv-1',
          title: 'Old Chat',
          mode: 'chat',
          created_at: '2026-03-16T10:00:00',
          last_message_at: '2026-03-16T10:15:00',
          message_count: 2,
        },
      ],
    })

    getConversation.mockResolvedValue({
      conversation_id: 'conv-1',
      title: 'Old Chat',
      mode: 'chat',
      messages: [
        {
          message_id: 'msg-1',
          role: 'user',
          content: 'Hello',
          timestamp: '2026-03-16T10:00:00',
        },
        {
          message_id: 'msg-2',
          role: 'assistant',
          content: 'Hi there!',
          timestamp: '2026-03-16T10:00:01',
          suggestions: [],
          lpd_sections_referenced: [],
        },
      ],
    })

    renderChat()

    await waitFor(() => {
      expect(screen.getByText('Old Chat')).toBeTruthy()
    })

    fireEvent.click(screen.getByText('Old Chat'))

    await waitFor(() => {
      expect(getConversation).toHaveBeenCalledWith('default', 'conv-1')
    })

    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeTruthy()
      expect(screen.getByText('Hi there!')).toBeTruthy()
    })
  })

  it('creates new conversation on button click', async () => {
    renderChat()

    await waitFor(() => {
      expect(screen.getByText('New Chat')).toBeTruthy()
    })

    fireEvent.click(screen.getByText('New Chat'))

    expect(screen.getByText(/Start a conversation with VPMA/)).toBeTruthy()
  })

  it('renders suggestion cards in assistant messages', async () => {
    sendChatMessage.mockResolvedValue({
      conversation_id: 'conv-new',
      message_id: 'msg-1',
      response: 'I found a risk.',
      suggestions: [
        {
          artifact_type: 'RAID Log',
          change_type: 'add',
          section: 'Risks',
          proposed_text: 'New risk identified',
          confidence: 0.85,
          reasoning: 'Found in discussion',
        },
      ],
      lpd_sections_referenced: [],
      session_id: 'sess-1',
      pii_detected: 0,
      token_count: 150,
    })

    renderChat()

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask VPMA anything/)).toBeTruthy()
    })

    const input = screen.getByPlaceholderText(/Ask VPMA anything/)
    fireEvent.change(input, { target: { value: 'Find risks' } })
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(screen.getByText('I found a risk.')).toBeTruthy()
    })
    expect(screen.getByText('RAID Log')).toBeTruthy()
    expect(screen.getByText('New risk identified')).toBeTruthy()
    expect(screen.getByText('Apply')).toBeTruthy()
  })
})
