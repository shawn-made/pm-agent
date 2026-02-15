/**
 * Toast notification system using React context for app-wide success/error/info messages.
 */
import { useState, useEffect, useCallback, createContext, useContext } from 'react'

const ToastContext = createContext(null)

/**
 * Hook to access toast methods (success, error, info) from any component.
 * @returns {{success: function, error: function, info: function}} Toast trigger methods
 */
export function useToast() {
  return useContext(ToastContext)
}

/**
 * Wraps the app to provide toast notification context. Renders toast stack in bottom-right.
 * @param {Object} props
 * @param {React.ReactNode} props.children - App content to wrap
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)
  }, [])

  const toast = {
    success: (msg) => addToast(msg, 'success'),
    error: (msg) => addToast(msg, 'error', 5000),
    info: (msg) => addToast(msg, 'info'),
  }

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
        {toasts.map(t => (
          <div
            key={t.id}
            className={`px-4 py-3 rounded-lg shadow-lg text-sm font-medium transition-all animate-slide-up ${
              t.type === 'success' ? 'bg-green-600 text-white' :
              t.type === 'error' ? 'bg-red-600 text-white' :
              'bg-gray-800 text-white'
            }`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
