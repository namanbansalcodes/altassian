import { useState, useCallback, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import type { Page } from '../types'
import {
  flattenTree,
  getAncestorIds,
  loadExpandedSpaces,
  saveExpandedSpaces,
  loadExpandedPages,
  saveExpandedPages,
  type FlatTreeNode,
} from '../lib/tree'

export interface SpaceTreeState {
  expandedPageIds: Set<number>
  flatNodes: FlatTreeNode[]
  pages: Page[] | undefined
  isLoading: boolean
}

/**
 * Hook managing which spaces are expanded, with localStorage persistence.
 */
export function useExpandedSpaces() {
  const [expandedSpaces, setExpandedSpaces] = useState<Set<string>>(() => loadExpandedSpaces())

  const toggleSpace = useCallback((key: string) => {
    setExpandedSpaces(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      saveExpandedSpaces(next)
      return next
    })
  }, [])

  const expandSpace = useCallback((key: string) => {
    setExpandedSpaces(prev => {
      if (prev.has(key)) return prev
      const next = new Set(prev)
      next.add(key)
      saveExpandedSpaces(next)
      return next
    })
  }, [])

  return { expandedSpaces, toggleSpace, expandSpace }
}

/**
 * Hook managing the page tree for a single space.
 * Fetches pages only when the space is expanded.
 * Persists expanded page ids to localStorage.
 */
export function useSpaceTree(spaceKey: string, isExpanded: boolean) {
  const params = useParams()
  const [expandedPageIds, setExpandedPageIds] = useState<Set<number>>(
    () => loadExpandedPages(spaceKey),
  )
  const hasAutoExpanded = useRef(false)

  const { data: pages, isLoading } = useQuery({
    queryKey: ['pages', spaceKey],
    queryFn: () => api.getPages(spaceKey),
    enabled: isExpanded,
    staleTime: 30_000,
  })

  // Auto-expand ancestors of the active page so it's visible
  useEffect(() => {
    if (!pages || !params.pageSlug || hasAutoExpanded.current) return
    if (params.spaceKey !== spaceKey) return
    const ancestors = getAncestorIds(pages, params.pageSlug)
    if (ancestors && ancestors.length > 0) {
      setExpandedPageIds(prev => {
        const next = new Set(prev)
        let changed = false
        for (const id of ancestors) {
          if (!next.has(id)) { next.add(id); changed = true }
        }
        if (changed) saveExpandedPages(spaceKey, next)
        return changed ? next : prev
      })
    }
    hasAutoExpanded.current = true
  }, [pages, params.pageSlug, params.spaceKey, spaceKey])

  // Reset auto-expand tracking when slug changes
  useEffect(() => {
    hasAutoExpanded.current = false
  }, [params.pageSlug])

  const togglePage = useCallback((pageId: number) => {
    setExpandedPageIds(prev => {
      const next = new Set(prev)
      if (next.has(pageId)) next.delete(pageId)
      else next.add(pageId)
      saveExpandedPages(spaceKey, next)
      return next
    })
  }, [spaceKey])

  const expandPage = useCallback((pageId: number) => {
    setExpandedPageIds(prev => {
      if (prev.has(pageId)) return prev
      const next = new Set(prev)
      next.add(pageId)
      saveExpandedPages(spaceKey, next)
      return next
    })
  }, [spaceKey])

  const collapsePage = useCallback((pageId: number) => {
    setExpandedPageIds(prev => {
      if (!prev.has(pageId)) return prev
      const next = new Set(prev)
      next.delete(pageId)
      saveExpandedPages(spaceKey, next)
      return next
    })
  }, [spaceKey])

  const rootPages = pages?.filter((p: Page) => !p.parent) ?? []
  const flatNodes = flattenTree(rootPages, spaceKey, expandedPageIds)

  return {
    expandedPageIds,
    flatNodes,
    pages,
    isLoading,
    togglePage,
    expandPage,
    collapsePage,
  }
}
