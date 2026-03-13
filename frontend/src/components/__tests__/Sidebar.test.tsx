import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Sidebar from '../Sidebar'
import {
  flattenTree,
  getAncestorIds,
  loadExpandedSpaces,
  saveExpandedSpaces,
  loadExpandedPages,
  saveExpandedPages,
} from '../../lib/tree'
import type { Page } from '../../types'

// ─── Tree utility unit tests ─────────────────────────────────────────────────

const makePage = (id: number, title: string, slug: string, children: Page[] = []): Page => ({
  id,
  title,
  slug,
  space: 1,
  children,
  parent: null,
  created_at: '',
  updated_at: '',
})

const sampleTree: Page[] = [
  makePage(1, 'Getting Started', 'getting-started', [
    makePage(2, 'Installation', 'installation'),
    makePage(3, 'Configuration', 'configuration', [
      makePage(4, 'Advanced Config', 'advanced-config'),
    ]),
  ]),
  makePage(5, 'API Reference', 'api-reference'),
]

describe('flattenTree', () => {
  it('returns only root nodes when nothing is expanded', () => {
    const result = flattenTree(sampleTree, 'DOCS', new Set())
    expect(result).toHaveLength(2)
    expect(result[0].id).toBe(1)
    expect(result[0].depth).toBe(0)
    expect(result[0].hasChildren).toBe(true)
    expect(result[0].isExpanded).toBe(false)
    expect(result[1].id).toBe(5)
  })

  it('includes children of expanded nodes', () => {
    const result = flattenTree(sampleTree, 'DOCS', new Set([1]))
    expect(result).toHaveLength(4) // root(1) + children(2,3) + root(5)
    expect(result[0].isExpanded).toBe(true)
    expect(result[1].id).toBe(2)
    expect(result[1].depth).toBe(1)
    expect(result[2].id).toBe(3)
    expect(result[2].depth).toBe(1)
  })

  it('handles deeply nested expansion', () => {
    const result = flattenTree(sampleTree, 'DOCS', new Set([1, 3]))
    expect(result).toHaveLength(5) // 1, 2, 3, 4, 5
    expect(result[3].id).toBe(4)
    expect(result[3].depth).toBe(2)
  })

  it('returns empty array for empty tree', () => {
    expect(flattenTree([], 'DOCS', new Set())).toHaveLength(0)
  })
})

describe('getAncestorIds', () => {
  it('returns empty array for root-level page', () => {
    expect(getAncestorIds(sampleTree, 'getting-started')).toEqual([])
  })

  it('returns parent ids for nested page', () => {
    expect(getAncestorIds(sampleTree, 'installation')).toEqual([1])
  })

  it('returns full ancestor chain for deeply nested page', () => {
    expect(getAncestorIds(sampleTree, 'advanced-config')).toEqual([1, 3])
  })

  it('returns null for non-existent slug', () => {
    expect(getAncestorIds(sampleTree, 'non-existent')).toBeNull()
  })
})

// ─── localStorage persistence tests ──────────────────────────────────────────

describe('localStorage persistence', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saveExpandedSpaces and loadExpandedSpaces round-trip', () => {
    const keys = new Set(['DOCS', 'ENG'])
    saveExpandedSpaces(keys)
    const loaded = loadExpandedSpaces()
    expect(loaded).toEqual(keys)
  })

  it('loadExpandedSpaces returns empty set when nothing stored', () => {
    expect(loadExpandedSpaces()).toEqual(new Set())
  })

  it('loadExpandedSpaces handles corrupt data gracefully', () => {
    localStorage.setItem('altassian:sidebar:spaces', 'not-json')
    expect(loadExpandedSpaces()).toEqual(new Set())
  })

  it('saveExpandedPages and loadExpandedPages round-trip', () => {
    const ids = new Set([1, 3, 7])
    saveExpandedPages('DOCS', ids)
    const loaded = loadExpandedPages('DOCS')
    expect(loaded).toEqual(ids)
  })

  it('loadExpandedPages returns empty set when nothing stored', () => {
    expect(loadExpandedPages('DOCS')).toEqual(new Set())
  })

  it('different spaces have independent storage', () => {
    saveExpandedPages('DOCS', new Set([1, 2]))
    saveExpandedPages('ENG', new Set([10]))
    expect(loadExpandedPages('DOCS')).toEqual(new Set([1, 2]))
    expect(loadExpandedPages('ENG')).toEqual(new Set([10]))
  })
})

// ─── Sidebar component tests ────────────────────────────────────────────────

// Mock API
vi.mock('../../api', () => ({
  getSpaces: vi.fn(),
  getPages: vi.fn(),
}))

import * as api from '../../api'
const mockGetSpaces = vi.mocked(api.getSpaces)
const mockGetPages = vi.mocked(api.getPages)

function renderSidebar(route: string = '/') {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path="*" element={<Sidebar />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('Sidebar component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    mockGetSpaces.mockResolvedValue([
      { id: 1, key: 'DOCS', name: 'Documentation' },
      { id: 2, key: 'ENG', name: 'Engineering' },
    ])
    mockGetPages.mockResolvedValue(sampleTree)
  })

  it('renders spaces after loading', async () => {
    renderSidebar()
    expect(await screen.findByText('Documentation')).toBeTruthy()
    expect(screen.getByText('Engineering')).toBeTruthy()
  })

  it('renders "Spaces" heading with create link', async () => {
    renderSidebar()
    expect(await screen.findByText('Spaces')).toBeTruthy()
    expect(screen.getByLabelText('Create space')).toBeTruthy()
  })

  it('has tree ARIA role on container', async () => {
    renderSidebar()
    await screen.findByText('Documentation')
    expect(screen.getByRole('tree')).toBeTruthy()
  })

  it('expands space on chevron click and shows pages', async () => {
    renderSidebar()
    await screen.findByText('Documentation')

    // Click the expand button for Documentation
    const expandBtn = screen.getByLabelText('Expand Documentation')
    fireEvent.click(expandBtn)

    // Pages should load and appear
    expect(await screen.findByText('Getting Started')).toBeTruthy()
    expect(screen.getByText('API Reference')).toBeTruthy()
  })

  it('collapses space on second chevron click', async () => {
    renderSidebar()
    await screen.findByText('Documentation')

    const expandBtn = screen.getByLabelText('Expand Documentation')
    fireEvent.click(expandBtn)
    await screen.findByText('Getting Started')

    const collapseBtn = screen.getByLabelText('Collapse Documentation')
    fireEvent.click(collapseBtn)

    // Pages should no longer be visible
    expect(screen.queryByText('Getting Started')).toBeNull()
  })

  it('persists expanded space state to localStorage', async () => {
    renderSidebar()
    await screen.findByText('Documentation')

    fireEvent.click(screen.getByLabelText('Expand Documentation'))
    await screen.findByText('Getting Started')

    const stored = loadExpandedSpaces()
    expect(stored.has('DOCS')).toBe(true)
  })

  it('shows "Add page" link under expanded space', async () => {
    renderSidebar()
    await screen.findByText('Documentation')

    fireEvent.click(screen.getByLabelText('Expand Documentation'))
    expect(await screen.findByText('Add page')).toBeTruthy()
  })

  it('shows "No spaces yet" when spaces list is empty', async () => {
    mockGetSpaces.mockResolvedValue([])
    renderSidebar()
    expect(await screen.findByText('No spaces yet')).toBeTruthy()
  })

  it('shows empty state with CTA when space has no pages', async () => {
    mockGetPages.mockResolvedValue([])
    renderSidebar()
    await screen.findByText('Documentation')

    fireEvent.click(screen.getByLabelText('Expand Documentation'))
    expect(await screen.findByText('No pages yet')).toBeTruthy()
    expect(screen.getByText('Create first page')).toBeTruthy()
  })
})
