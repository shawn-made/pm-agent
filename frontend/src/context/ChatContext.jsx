/* eslint-disable react-refresh/only-export-components */
/**
 * ChatContext — provides global open/close state for the floating chat panel.
 */
import { createContext, useContext, useState } from 'react'

const ChatContext = createContext(null)

export function ChatProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false)

  const toggleChat = () => setIsOpen(v => !v)
  const openChat = () => setIsOpen(true)
  const closeChat = () => setIsOpen(false)

  return (
    <ChatContext.Provider value={{ isOpen, toggleChat, openChat, closeChat }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error('useChat must be used inside ChatProvider')
  return ctx
}
