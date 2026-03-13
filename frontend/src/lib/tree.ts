import type { Page } from '../types'

/** Flattened node used for keyboard navigation and virtualized rendering. */
export interface FlatTreeNode {
  id: number
  page: Page
  depth: number
  spaceKey: string
  hasChildren: boolean
  isExpanded: boolean
}

/**
 * Flatten a nested page tree into a list, respecting expanded state.
 * Only children of expanded nodes are included, keeping render O(visible).
 */
export function flattenTree(
  pages: Page[],
  spaceKey: string,
  expandedIds: Set<number>,
  depth: number = 0,
): FlatTreeNode[] {
  const result: FlatTreeNode[] = []
  for (const page of pages) {
    const hasChildren = !!(page.children && page.children.length > 0)
    const isExpanded = hasChildren && expandedIds.has(page.id)
    result.push({ id: page.id, page, depth, spaceKey, hasChildren, isExpanded })
    if (isExpanded) {
      result.push(...flattenTree(page.children!, spaceKey, expandedIds, depth + 1))
    }
  }
  return result
}

/** Find a page by id in a nested tree (DFS). */
export function findPageInTree(pages: Page[], id: number): Page | undefined {
  for (const page of pages) {
    if (page.id === id) return page
    if (page.children) {
      const found = findPageInTree(page.children, id)
      if (found) return found
    }
  }
  return undefined
}

/** Collect all ancestor ids of a page with the given slug in a nested tree. */
export function getAncestorIds(pages: Page[], slug: string, ancestors: number[] = []): number[] | null {
  for (const page of pages) {
    if (page.slug === slug) return ancestors
    if (page.children && page.children.length > 0) {
      const found = getAncestorIds(page.children, slug, [...ancestors, page.id])
      if (found) return found
    }
  }
  return null
}

// --- localStorage persistence ---

const STORAGE_PREFIX = 'altassian:sidebar:'

export function loadExpandedSpaces(): Set<string> {
  try {
    const raw = localStorage.getItem(`${STORAGE_PREFIX}spaces`)
    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch {
    return new Set()
  }
}

export function saveExpandedSpaces(keys: Set<string>): void {
  localStorage.setItem(`${STORAGE_PREFIX}spaces`, JSON.stringify([...keys]))
}

export function loadExpandedPages(spaceKey: string): Set<number> {
  try {
    const raw = localStorage.getItem(`${STORAGE_PREFIX}${spaceKey}`)
    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch {
    return new Set()
  }
}

export function saveExpandedPages(spaceKey: string, ids: Set<number>): void {
  localStorage.setItem(`${STORAGE_PREFIX}${spaceKey}`, JSON.stringify([...ids]))
}
