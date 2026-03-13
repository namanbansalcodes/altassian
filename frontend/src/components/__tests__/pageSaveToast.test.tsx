import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider, useMutation } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'

// Mock sonner
const mockSuccess = vi.fn()
const mockError = vi.fn()
vi.mock('sonner', () => ({
  toast: {
    success: (...args: unknown[]) => mockSuccess(...args),
    error: (...args: unknown[]) => mockError(...args),
    info: vi.fn(),
    warning: vi.fn(),
    dismiss: vi.fn(),
  },
}))

// Mock API
const mockUpdatePage = vi.fn()
vi.mock('../../api', () => ({
  updatePage: (...args: unknown[]) => mockUpdatePage(...args),
}))

import * as api from '../../api'
import { toast, getErrorMessage } from '../../lib/toast'

/**
 * Minimal component simulating the PageEditor save flow.
 * Uses the same useMutation pattern as the real PageEditor.
 */
function SaveButton() {
  const saveMut = useMutation({
    mutationFn: async () => api.updatePage('TEAM', 'intro', { title: 'Intro', content: '<p>Hi</p>' }),
    onSuccess: () => toast.success('Page updated'),
    onError: (err: unknown) => toast.error(getErrorMessage(err)),
  })

  return (
    <button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>
      {saveMut.isPending ? 'Saving...' : 'Save'}
    </button>
  )
}

function renderWithProviders(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('Page save → toast integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows success toast on save', async () => {
    mockUpdatePage.mockResolvedValueOnce({ slug: 'intro', title: 'Intro' })
    renderWithProviders(<SaveButton />)

    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      expect(mockSuccess).toHaveBeenCalledWith('Page updated', undefined)
    })
  })

  it('shows error toast on save failure', async () => {
    mockUpdatePage.mockRejectedValueOnce({
      response: { data: { detail: 'Permission denied' } },
    })
    renderWithProviders(<SaveButton />)

    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      expect(mockError).toHaveBeenCalledWith('Permission denied', undefined)
    })
  })
})
