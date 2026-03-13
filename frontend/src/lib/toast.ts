import { toast as sonnerToast } from 'sonner'

export type ToastVariant = 'success' | 'error' | 'info' | 'warning'

export interface ToastOptions {
  duration?: number
  description?: string
}

export interface ToastParams {
  title: string
  description?: string
  variant?: ToastVariant
  duration?: number
}

/** Thin wrapper around sonner — keeps the API consistent and type-safe. */
export const toast = {
  success(message: string, opts?: ToastOptions): void {
    sonnerToast.success(message, opts)
  },
  error(message: string, opts?: ToastOptions): void {
    sonnerToast.error(message, opts)
  },
  info(message: string, opts?: ToastOptions): void {
    sonnerToast.info(message, opts)
  },
  warning(message: string, opts?: ToastOptions): void {
    sonnerToast.warning(message, opts)
  },
  /** Variant-driven toast for the useToast() hook. */
  show({ title, description, variant = 'info', duration }: ToastParams): void {
    const opts: ToastOptions = {}
    if (description) opts.description = description
    if (duration) opts.duration = duration
    switch (variant) {
      case 'success': sonnerToast.success(title, opts); break
      case 'error':   sonnerToast.error(title, opts);   break
      case 'warning': sonnerToast.warning(title, opts);  break
      default:        sonnerToast.info(title, opts);     break
    }
  },
  /** Dismiss all visible toasts. */
  dismissAll(): void {
    sonnerToast.dismiss()
  },
}

/** Convenience helpers — importable anywhere without the `toast.` prefix. */
export const toastSuccess = (msg: string, opts?: ToastOptions): void => toast.success(msg, opts)
export const toastError   = (msg: string, opts?: ToastOptions): void => toast.error(msg, opts)
export const toastInfo    = (msg: string, opts?: ToastOptions): void => toast.info(msg, opts)
export const toastWarning = (msg: string, opts?: ToastOptions): void => toast.warning(msg, opts)

/** Extract a human-readable error message from an Axios error or generic Error. */
export function getErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const data = (err as { response?: { data?: unknown } }).response?.data
    if (data && typeof data === 'object') {
      const values = Object.values(data as Record<string, unknown>).flat()
      const msg = values.filter(v => typeof v === 'string').join('. ')
      if (msg) return msg
    }
    if (typeof data === 'string') return data
  }
  if (err instanceof Error) return err.message
  return 'Something went wrong'
}
