import { useCallback } from 'react'
import { toast, type ToastParams, type ToastOptions } from '../lib/toast'

export interface UseToastReturn {
  toast: (params: ToastParams) => void
  toastSuccess: (msg: string, opts?: ToastOptions) => void
  toastError: (msg: string, opts?: ToastOptions) => void
  toastInfo: (msg: string, opts?: ToastOptions) => void
  toastWarning: (msg: string, opts?: ToastOptions) => void
  dismissAll: () => void
}

/**
 * React hook providing the full toast API.
 *
 * Usage:
 *   const { toast, toastSuccess, toastError } = useToast()
 *   toast({ title: 'Saved', variant: 'success' })
 *   toastSuccess('Done!')
 */
export function useToast(): UseToastReturn {
  const show = useCallback((params: ToastParams) => toast.show(params), [])
  const success = useCallback((msg: string, opts?: ToastOptions) => toast.success(msg, opts), [])
  const error = useCallback((msg: string, opts?: ToastOptions) => toast.error(msg, opts), [])
  const info = useCallback((msg: string, opts?: ToastOptions) => toast.info(msg, opts), [])
  const warning = useCallback((msg: string, opts?: ToastOptions) => toast.warning(msg, opts), [])
  const dismissAll = useCallback(() => toast.dismissAll(), [])

  return {
    toast: show,
    toastSuccess: success,
    toastError: error,
    toastInfo: info,
    toastWarning: warning,
    dismissAll,
  }
}
