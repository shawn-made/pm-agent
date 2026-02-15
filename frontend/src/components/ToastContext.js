import { createContext, useContext } from 'react'

const ToastContext = createContext(null)

/**
 * Hook to access toast methods (success, error, info) from any component.
 * @returns {{success: function, error: function, info: function}} Toast trigger methods
 */
export function useToast() {
  return useContext(ToastContext)
}

export default ToastContext
