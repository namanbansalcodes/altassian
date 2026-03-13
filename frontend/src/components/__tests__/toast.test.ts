import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock sonner before importing toast helpers
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
import { toast, toastSuccess, toastError, toastInfo, toastWarning, getErrorMessage } from '../../lib/toast'

describe('toast helper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('delegates success() to sonner', () => {
    toast.success('Saved')
    expect(sonnerToast.success).toHaveBeenCalledWith('Saved', undefined)
  })

  it('delegates error() to sonner', () => {
    toast.error('Oops')
    expect(sonnerToast.error).toHaveBeenCalledWith('Oops', undefined)
  })

  it('delegates info() to sonner', () => {
    toast.info('Heads up')
    expect(sonnerToast.info).toHaveBeenCalledWith('Heads up', undefined)
  })

  it('delegates warning() to sonner', () => {
    toast.warning('Careful')
    expect(sonnerToast.warning).toHaveBeenCalledWith('Careful', undefined)
  })

  it('passes options through', () => {
    toast.success('Done', { duration: 5000 })
    expect(sonnerToast.success).toHaveBeenCalledWith('Done', { duration: 5000 })
  })

  it('show() dispatches by variant', () => {
    toast.show({ title: 'OK', variant: 'success' })
    expect(sonnerToast.success).toHaveBeenCalledWith('OK', {})

    toast.show({ title: 'Bad', variant: 'error', description: 'Details' })
    expect(sonnerToast.error).toHaveBeenCalledWith('Bad', { description: 'Details' })

    toast.show({ title: 'Note', variant: 'warning', duration: 2000 })
    expect(sonnerToast.warning).toHaveBeenCalledWith('Note', { duration: 2000 })

    toast.show({ title: 'FYI' })
    expect(sonnerToast.info).toHaveBeenCalledWith('FYI', {})
  })

  it('dismissAll() calls sonner dismiss', () => {
    toast.dismissAll()
    expect(sonnerToast.dismiss).toHaveBeenCalled()
  })
})

describe('convenience helpers', () => {
  beforeEach(() => vi.clearAllMocks())

  it('toastSuccess delegates to sonner.success', () => {
    toastSuccess('Yay')
    expect(sonnerToast.success).toHaveBeenCalledWith('Yay', undefined)
  })

  it('toastError delegates to sonner.error', () => {
    toastError('Nope')
    expect(sonnerToast.error).toHaveBeenCalledWith('Nope', undefined)
  })

  it('toastInfo delegates to sonner.info', () => {
    toastInfo('Note')
    expect(sonnerToast.info).toHaveBeenCalledWith('Note', undefined)
  })

  it('toastWarning delegates to sonner.warning', () => {
    toastWarning('Watch out')
    expect(sonnerToast.warning).toHaveBeenCalledWith('Watch out', undefined)
  })
})

describe('getErrorMessage', () => {
  it('extracts message from axios-style error', () => {
    const err = { response: { data: { detail: 'Not found' } } }
    expect(getErrorMessage(err)).toBe('Not found')
  })

  it('joins multiple field errors', () => {
    const err = { response: { data: { name: ['Required'], key: ['Already exists'] } } }
    expect(getErrorMessage(err)).toBe('Required. Already exists')
  })

  it('handles string response data', () => {
    const err = { response: { data: 'Server error' } }
    expect(getErrorMessage(err)).toBe('Server error')
  })

  it('falls back to Error.message', () => {
    expect(getErrorMessage(new Error('boom'))).toBe('boom')
  })

  it('returns default for unknown errors', () => {
    expect(getErrorMessage(null)).toBe('Something went wrong')
    expect(getErrorMessage(42)).toBe('Something went wrong')
  })
})
