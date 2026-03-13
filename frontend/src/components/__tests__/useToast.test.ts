import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    dismiss: vi.fn(),
  },
}))

import { toast as sonnerToast } from 'sonner'
import { useToast } from '../../hooks/useToast'

describe('useToast hook', () => {
  beforeEach(() => vi.clearAllMocks())

  it('returns stable references across renders', () => {
    const { result, rerender } = renderHook(() => useToast())
    const first = result.current
    rerender()
    expect(result.current.toast).toBe(first.toast)
    expect(result.current.toastSuccess).toBe(first.toastSuccess)
    expect(result.current.toastError).toBe(first.toastError)
    expect(result.current.dismissAll).toBe(first.dismissAll)
  })

  it('toast() dispatches variant-driven toasts', () => {
    const { result } = renderHook(() => useToast())
    act(() => result.current.toast({ title: 'Page saved', variant: 'success' }))
    expect(sonnerToast.success).toHaveBeenCalledWith('Page saved', {})
  })

  it('toastSuccess() delegates correctly', () => {
    const { result } = renderHook(() => useToast())
    act(() => result.current.toastSuccess('Done'))
    expect(sonnerToast.success).toHaveBeenCalledWith('Done', undefined)
  })

  it('toastError() delegates correctly', () => {
    const { result } = renderHook(() => useToast())
    act(() => result.current.toastError('Failed'))
    expect(sonnerToast.error).toHaveBeenCalledWith('Failed', undefined)
  })

  it('toastInfo() delegates correctly', () => {
    const { result } = renderHook(() => useToast())
    act(() => result.current.toastInfo('Note'))
    expect(sonnerToast.info).toHaveBeenCalledWith('Note', undefined)
  })

  it('toastWarning() delegates correctly', () => {
    const { result } = renderHook(() => useToast())
    act(() => result.current.toastWarning('Careful'))
    expect(sonnerToast.warning).toHaveBeenCalledWith('Careful', undefined)
  })

  it('dismissAll() clears all toasts', () => {
    const { result } = renderHook(() => useToast())
    act(() => result.current.dismissAll())
    expect(sonnerToast.dismiss).toHaveBeenCalled()
  })
})
