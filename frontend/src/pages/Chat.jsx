/**
 * ChatPanel — floating multi-turn conversational PM assistant.
 * Renders as a fixed right-side overlay accessible from any page.
 * Brain dump mode available for freeform capture and triage.
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import {
  sendChatMessage,
  listConversations,
  getConversation,
  deleteConversation,
  applySuggestionByType,
} from '../services/api'
import { useToast } from '../components/ToastContext'
import { useChat } from '../context/ChatContext'

function SuggestionCard({ suggestion, projectId, onApplied, toast }) {
  const [applying, setApplying] = useState(false)
  const [applied, setApplied] = useState(false)
  const [error, setError] = useState(null)

  const handleApply = async (changeType) => {
    try {
      setApplying(true)
      setError(null)
      // Ensure required fields have defaults for chat-generated suggestions
      const payload = {
        artifact_type: suggestion.artifact_type || 'RAID Log',
        section: suggestion.section || '',
        change_type: changeType,
        proposed_text: suggestion.proposed_text,
        confidence: suggestion.confidence || 0.8,
        reasoning: suggestion.reasoning || '',
      }
      const result = await applySuggestionByType(payload, projectId)
      setApplied(true)
      const section = result?.lpd_change?.section
      if (toast) {
        if (result?.status === 'duplicate') {
          toast('Already applied', 'info')
        } else if (changeType === 'update') {
          toast(section ? `Replaced "${section}"` : 'Section replaced', 'success')
        } else {
          toast(section ? `Applied to ${section}` : 'Applied successfully', 'success')
        }
      }
      if (onApplied) onApplied(result)
    } catch (err) {
      const msg = err?.message || 'Failed to apply'
      setError(msg)
      if (toast) toast(msg, 'error')
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 mt-2">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs font-medium text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
          {suggestion.artifact_type}
        </span>
        <span className="text-xs text-gray-400">{suggestion.section}</span>
        <span className="text-xs text-gray-400 ml-auto">
          {Math.round(suggestion.confidence * 100)}% confidence
        </span>
      </div>
      <p className="text-sm text-gray-700 whitespace-pre-wrap">{suggestion.proposed_text}</p>
      {suggestion.reasoning && (
        <p className="text-xs text-gray-500 mt-1">{suggestion.reasoning}</p>
      )}
      {error && (
        <p className="text-xs text-red-500 mt-1">{error}</p>
      )}
      <div className="flex gap-2 mt-2">
        <button
          onClick={() => handleApply('add')}
          disabled={applying || applied}
          className={`text-xs px-2.5 py-1 rounded ${
            applied
              ? 'bg-green-100 text-green-700'
              : 'bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-gray-300'
          }`}
        >
          {applied ? 'Applied' : applying ? 'Applying...' : 'Append'}
        </button>
        {!applied && (
          <button
            onClick={() => handleApply('update')}
            disabled={applying}
            className="text-xs px-2.5 py-1 rounded border border-indigo-300 text-indigo-700 hover:bg-indigo-50 disabled:text-gray-300 disabled:border-gray-200"
          >
            Replace
          </button>
        )}
        <button
          onClick={() => navigator.clipboard.writeText(suggestion.proposed_text)}
          className="text-xs px-2.5 py-1 rounded border border-gray-300 text-gray-600 hover:bg-gray-100"
        >
          Copy
        </button>
      </div>
    </div>
  )
}

function ChatMessage({ message, projectId, toast }) {
  const isUser = message.role === 'user'
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
      .then(() => {
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      })
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} group`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-white border border-gray-200 text-gray-800'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>

        {/* Copy button for assistant messages */}
        {!isUser && (
          <button
            onClick={handleCopy}
            className={`text-xs mt-2 px-2 py-0.5 rounded border transition-colors ${
              copied
                ? 'bg-green-50 text-green-600 border-green-200'
                : 'text-gray-400 hover:text-gray-600 border-gray-200 hover:bg-gray-50'
            }`}
          >
            {copied ? 'Copied' : 'Copy'}
          </button>
        )}

        {/* Suggestion cards for assistant messages */}
        {!isUser && message.suggestions?.length > 0 && (
          <div className="mt-2 space-y-2">
            {message.suggestions.map((sugg, idx) => (
              <SuggestionCard key={idx} suggestion={sugg} projectId={projectId} toast={toast} />
            ))}
          </div>
        )}

        {/* LPD refs */}
        {!isUser && message.lpd_sections_referenced?.length > 0 && (
          <div className="mt-2 flex gap-1 flex-wrap">
            {message.lpd_sections_referenced.map((ref, idx) => (
              <span key={idx} className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                {ref}
              </span>
            ))}
          </div>
        )}

        <p className={`text-xs mt-1 ${isUser ? 'text-indigo-200' : 'text-gray-400'}`}>
          {(() => {
            const d = new Date(message.timestamp)
            const now = new Date()
            const isToday = d.toDateString() === now.toDateString()
            const time = d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
            return isToday ? time : `${d.toLocaleDateString([], { month: 'short', day: 'numeric' })} ${time}`
          })()}
        </p>
      </div>
    </div>
  )
}

function Chat() {
  const { isOpen, closeChat } = useChat()
  const { showToast } = useToast()
  const [conversations, setConversations] = useState([])
  const [activeConversationId, setActiveConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [isBrainDump, setIsBrainDump] = useState(false)
  const [showConvList, setShowConvList] = useState(true)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const projectId = 'default'

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, [])

  // Scroll on new messages
  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Persist active conversation in localStorage
  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem('vpma_active_conversation', activeConversationId)
    }
  }, [activeConversationId])

  // Restore active conversation on mount
  useEffect(() => {
    const saved = localStorage.getItem('vpma_active_conversation')
    if (saved) {
      loadConversation(saved)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadConversations = async () => {
    try {
      const data = await listConversations(projectId)
      setConversations(data.conversations || [])
    } catch {
      // Silent fail — conversations list is not critical
    }
  }

  const loadConversation = async (convId) => {
    try {
      setLoadingHistory(true)
      const data = await getConversation(projectId, convId)
      if (data) {
        setActiveConversationId(convId)
        setMessages(data.messages || [])
        setIsBrainDump(data.mode === 'brain_dump')
        setShowConvList(false)
      }
    } catch {
      showToast('Failed to load conversation', 'error')
    } finally {
      setLoadingHistory(false)
    }
  }

  const handleNewConversation = () => {
    setActiveConversationId(null)
    setMessages([])
    setIsBrainDump(false)
    setInput('')
    setShowConvList(false)
    inputRef.current?.focus()
  }

  const handleDeleteConversation = async (convId, e) => {
    e.stopPropagation()
    try {
      await deleteConversation(projectId, convId)
      setConversations(prev => prev.filter(c => c.conversation_id !== convId))
      if (activeConversationId === convId) {
        setActiveConversationId(null)
        setMessages([])
      }
      showToast('Conversation deleted', 'success')
    } catch {
      showToast('Failed to delete conversation', 'error')
    }
  }

  const handleSend = async () => {
    const text = input.trim()
    if (!text || sending) return

    // Add user message to UI immediately
    const userMessage = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setSending(true)

    try {
      // Prepend brain dump instruction if in brain dump mode
      const messageText = isBrainDump
        ? `[BRAIN DUMP] The following is a brain dump of unstructured thoughts. Please triage each thought into the appropriate category and suggest where it should go:\n\n${text}`
        : text

      const response = await sendChatMessage(
        projectId,
        messageText,
        activeConversationId,
      )

      // Update conversation ID (may be new)
      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id)
      }

      // Add assistant response
      const assistantMessage = {
        message_id: response.message_id,
        role: 'assistant',
        content: response.response,
        suggestions: response.suggestions || [],
        lpd_sections_referenced: response.lpd_sections_referenced || [],
        timestamp: new Date().toISOString(),
      }
      setMessages(prev => [...prev, assistantMessage])

      // Refresh conversation list
      loadConversations()
    } catch (err) {
      showToast(`Chat error: ${err.message}`, 'error')
      // Remove the optimistic user message on failure
      setMessages(prev => prev.filter(m => m.message_id !== userMessage.message_id))
      setInput(text) // Restore input
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end pointer-events-none">
      {/* Backdrop — only captures clicks, panel is pointer-events-auto */}
      <div
        className="absolute inset-0 bg-black/20 pointer-events-auto"
        onClick={closeChat}
      />

      {/* Panel */}
      <div className="relative w-[480px] max-w-full h-full bg-white shadow-2xl flex flex-col pointer-events-auto">
        {/* Panel header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 flex-shrink-0">
          <div>
            <h2 className="text-sm font-semibold text-gray-900">Assistant</h2>
            <p className="text-xs text-gray-400">Ask questions, explore risks, brain dump</p>
          </div>
          <button
            onClick={closeChat}
            className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
            title="Close"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

      <div className="flex gap-4 flex-1 min-h-0 p-3">
        {/* Conversation sidebar */}
        <div className={`${showConvList ? 'w-48' : 'w-8'} flex-shrink-0 transition-all`}>
          {showConvList ? (
            <div className="bg-white rounded-lg border border-gray-200 h-full flex flex-col">
              <div className="px-3 py-2 border-b border-gray-100 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500 uppercase">Conversations</span>
                <button
                  onClick={() => setShowConvList(false)}
                  className="text-gray-400 hover:text-gray-600"
                  title="Collapse"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m18.75 4.5-7.5 7.5 7.5 7.5m-6-15L5.25 12l7.5 7.5" />
                  </svg>
                </button>
              </div>

              <button
                onClick={handleNewConversation}
                className="mx-2 mt-2 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                New Chat
              </button>

              <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
                {conversations.map(conv => (
                  <div
                    key={conv.conversation_id}
                    onClick={() => loadConversation(conv.conversation_id)}
                    className={`group px-2.5 py-2 rounded-lg cursor-pointer transition-colors flex items-start gap-1 ${
                      activeConversationId === conv.conversation_id
                        ? 'bg-indigo-50 text-indigo-800'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {conv.title || 'Untitled'}
                      </p>
                      <p className="text-xs text-gray-400">
                        {conv.message_count} messages
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(conv.conversation_id, e)}
                      className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 p-0.5"
                      title="Delete conversation"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                      </svg>
                    </button>
                  </div>
                ))}
                {conversations.length === 0 && (
                  <p className="text-xs text-gray-400 text-center py-4">No conversations yet</p>
                )}
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowConvList(true)}
              className="bg-white rounded-lg border border-gray-200 h-10 w-10 flex items-center justify-center text-gray-400 hover:text-gray-600"
              title="Show conversations"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m5.25 4.5 7.5 7.5-7.5 7.5m6-15 7.5 7.5-7.5 7.5" />
              </svg>
            </button>
          )}
        </div>

        {/* Chat area */}
        <div className="flex-1 bg-white rounded-lg border border-gray-200 flex flex-col min-w-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {loadingHistory ? (
              <div className="flex items-center justify-center h-full">
                <p className="text-sm text-gray-400">Loading conversation...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                  </svg>
                  <p className="text-sm text-gray-500 mb-1">Start a conversation with VPMA</p>
                  <p className="text-xs text-gray-400">Ask about your project, explore risks, or use Brain Dump mode</p>
                </div>
              </div>
            ) : (
              messages.map(msg => (
                <ChatMessage key={msg.message_id} message={msg} projectId={projectId} toast={showToast} />
              ))
            )}
            {/* Thinking indicator */}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 max-w-[80%]">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-xs text-gray-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="border-t border-gray-200 p-3">
            {/* Brain dump toggle */}
            <div className="flex items-center gap-2 mb-2">
              <button
                onClick={() => setIsBrainDump(!isBrainDump)}
                className={`text-xs px-2.5 py-1 rounded-full transition-colors ${
                  isBrainDump
                    ? 'bg-purple-100 text-purple-700 border border-purple-300'
                    : 'bg-gray-100 text-gray-500 border border-gray-200 hover:bg-gray-200'
                }`}
              >
                {isBrainDump ? 'Brain Dump ON' : 'Brain Dump'}
              </button>
              {isBrainDump && (
                <span className="text-xs text-gray-400">
                  Dump your thoughts — VPMA will triage and route them
                </span>
              )}
            </div>

            <div className="flex gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isBrainDump
                  ? 'Dump your thoughts here... (press Enter to send, Shift+Enter for new line)'
                  : 'Ask VPMA anything about your project... (Enter to send)'
                }
                rows={isBrainDump ? 4 : 2}
                className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                disabled={sending}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || sending}
                className="self-end px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium"
              >
                {sending ? (
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}

export default Chat
