import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ChevronRight,
  ChevronDown,
  FileText,
  BookOpen,
  Plus,
  GripVertical,
} from 'lucide-react'
import * as api from '../api'
import { SidebarSkeleton } from './Skeleton'
import { useExpandedSpaces, useSpaceTree } from '../hooks/useSidebarTree'
import type { FlatTreeNode } from '../lib/tree'

// ─── Feature flag: drag-and-drop reorder (UI-only until backend supports it) ──
const ENABLE_DND = true

export default function Sidebar() {
  const { data: spaces, isLoading } = useQuery({
    queryKey: ['spaces'],
    queryFn: api.getSpaces,
  })
  const { expandedSpaces, toggleSpace, expandSpace } = useExpandedSpaces()
  const params = useParams()

  // Auto-expand the space the user is currently viewing
  if (params.spaceKey && !expandedSpaces.has(params.spaceKey)) {
    expandSpace(params.spaceKey)
  }

  return (
    <aside className="w-64 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 overflow-y-auto shrink-0">
      <div className="p-3" role="tree" aria-label="Spaces and pages">
        {isLoading ? (
          <SidebarSkeleton />
        ) : (
          <>
            <div className="flex items-center justify-between mb-2 px-2">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Spaces
              </span>
              <Link
                to="/spaces/create"
                className="text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                aria-label="Create space"
              >
                <Plus size={14} />
              </Link>
            </div>
            {spaces?.map(space => (
              <SpaceItem
                key={space.id}
                spaceKey={space.key}
                spaceName={space.name}
                isExpanded={expandedSpaces.has(space.key)}
                onToggle={() => toggleSpace(space.key)}
              />
            ))}
            {spaces?.length === 0 && (
              <p className="text-sm text-gray-400 dark:text-gray-500 px-2 py-4">
                No spaces yet
              </p>
            )}
          </>
        )}
      </div>
    </aside>
  )
}

// ─── SpaceItem ───────────────────────────────────────────────────────────────

interface SpaceItemProps {
  spaceKey: string
  spaceName: string
  isExpanded: boolean
  onToggle: () => void
}

function SpaceItem({ spaceKey, spaceName, isExpanded, onToggle }: SpaceItemProps) {
  const params = useParams()
  const isActiveSpace = params.spaceKey === spaceKey
  const {
    flatNodes,
    isLoading,
    togglePage,
    expandPage,
    collapsePage,
  } = useSpaceTree(spaceKey, isExpanded)

  // Keyboard nav state — index into flatNodes (-1 = space header focused)
  const [focusIdx, setFocusIdx] = useState(-1)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isExpanded) {
        if (e.key === 'ArrowRight' || e.key === 'Enter') {
          e.preventDefault()
          onToggle()
        }
        return
      }

      const maxIdx = flatNodes.length - 1
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setFocusIdx(prev => Math.min(prev + 1, maxIdx))
          break
        case 'ArrowUp':
          e.preventDefault()
          setFocusIdx(prev => Math.max(prev - 1, -1))
          break
        case 'ArrowRight': {
          e.preventDefault()
          if (focusIdx >= 0 && focusIdx <= maxIdx) {
            const node = flatNodes[focusIdx]
            if (node.hasChildren && !node.isExpanded) expandPage(node.id)
          }
          break
        }
        case 'ArrowLeft': {
          e.preventDefault()
          if (focusIdx === -1) {
            onToggle() // collapse space
          } else if (focusIdx >= 0 && focusIdx <= maxIdx) {
            const node = flatNodes[focusIdx]
            if (node.hasChildren && node.isExpanded) collapsePage(node.id)
            else setFocusIdx(-1) // go back to space header
          }
          break
        }
        case 'Enter': {
          e.preventDefault()
          if (focusIdx >= 0 && focusIdx <= maxIdx) {
            const node = flatNodes[focusIdx]
            const link = containerRef.current?.querySelector<HTMLAnchorElement>(
              `[data-page-id="${node.id}"] a`,
            )
            link?.click()
          }
          break
        }
        case 'Home':
          e.preventDefault()
          setFocusIdx(-1)
          break
        case 'End':
          e.preventDefault()
          setFocusIdx(maxIdx)
          break
      }
    },
    [isExpanded, flatNodes, focusIdx, onToggle, expandPage, collapsePage],
  )

  return (
    <div
      className="mb-1"
      role="treeitem"
      aria-expanded={isExpanded}
      aria-label={spaceName}
      ref={containerRef}
      onKeyDown={handleKeyDown}
    >
      {/* Space header row */}
      <div
        data-compact-touch
        className={`flex items-center gap-1 px-2 py-1.5 rounded-md cursor-pointer text-sm
          hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
          ${isActiveSpace ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'}
          ${focusIdx === -1 ? 'ring-1 ring-blue-400/50' : ''}`}
        tabIndex={0}
        onFocus={() => setFocusIdx(-1)}
      >
        <button
          data-compact-touch
          onClick={onToggle}
          className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
          aria-label={isExpanded ? `Collapse ${spaceName}` : `Expand ${spaceName}`}
        >
          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        <BookOpen size={14} className="shrink-0" />
        <Link data-compact-touch to={`/spaces/${spaceKey}`} className="truncate flex-1 font-medium">
          {spaceName}
        </Link>
      </div>

      {/* Expanded page tree */}
      {isExpanded && (
        <div className="ml-4" role="group">
          {isLoading ? (
            <div className="py-2 px-2 text-xs text-gray-400 dark:text-gray-500">Loading…</div>
          ) : (
            <>
              {flatNodes.length === 0 ? (
                <div className="px-2 py-3 text-center">
                  <FileText size={24} className="mx-auto text-gray-300 dark:text-gray-600 mb-1" />
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">No pages yet</p>
                  <Link
                    to={`/spaces/${spaceKey}/pages/new`}
                    className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    <Plus size={12} /> Create first page
                  </Link>
                </div>
              ) : (
                <>
                  {flatNodes.map((node, idx) => (
                    <PageTreeRow
                      key={node.id}
                      node={node}
                      isFocused={focusIdx === idx}
                      onToggle={() => togglePage(node.id)}
                      onFocus={() => setFocusIdx(idx)}
                    />
                  ))}
                  <Link
                    to={`/spaces/${spaceKey}/pages/new`}
                    className="flex items-center gap-1.5 px-2 py-1 text-xs text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 mt-1"
                  >
                    <Plus size={12} /> Add page
                  </Link>
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

// ─── PageTreeRow ─────────────────────────────────────────────────────────────

interface PageTreeRowProps {
  node: FlatTreeNode
  isFocused: boolean
  onToggle: () => void
  onFocus: () => void
}

function PageTreeRow({ node, isFocused, onToggle, onFocus }: PageTreeRowProps) {
  const params = useParams()
  const navigate = useNavigate()
  const isActive = params.pageSlug === node.page.slug && params.spaceKey === node.spaceKey
  const rowRef = useRef<HTMLDivElement>(null)

  // Auto-scroll active page into view when route changes
  useEffect(() => {
    if (isActive && rowRef.current) {
      rowRef.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [isActive])

  // ── Drag-and-drop (UI-only, guarded by feature flag) ──
  const [isDragOver, setIsDragOver] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  const handleDragStart = useCallback(
    (e: React.DragEvent) => {
      if (!ENABLE_DND) return
      e.dataTransfer.setData('text/plain', String(node.id))
      e.dataTransfer.effectAllowed = 'move'
      setIsDragging(true)
    },
    [node.id],
  )

  const handleDragEnd = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      if (!ENABLE_DND) return
      e.preventDefault()
      e.dataTransfer.dropEffect = 'move'
      setIsDragOver(true)
    },
    [],
  )

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      if (!ENABLE_DND) return
      e.preventDefault()
      setIsDragOver(false)
      const sourceId = e.dataTransfer.getData('text/plain')
      if (sourceId && sourceId !== String(node.id)) {
        // UI-only: log the intended move. Backend endpoint not yet available.
        console.info(
          `[DnD] Would move page ${sourceId} under parent ${node.id} in space ${node.spaceKey}`,
        )
      }
    },
    [node.id, node.spaceKey],
  )

  return (
    <div
      ref={rowRef}
      data-page-id={node.id}
      role="treeitem"
      aria-expanded={node.hasChildren ? node.isExpanded : undefined}
      aria-level={node.depth + 2}
      aria-selected={isActive}
      data-compact-touch
      className={`group flex items-center gap-1 px-2 py-1 rounded text-sm transition-colors
        hover:bg-gray-100 dark:hover:bg-gray-800
        ${isActive ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold' : 'text-gray-600 dark:text-gray-400'}
        ${isFocused ? 'ring-1 ring-blue-400/50' : ''}
        ${isDragOver ? 'bg-blue-100 dark:bg-blue-900/50' : ''}
        ${isDragging ? 'opacity-50' : ''}`}
      style={{ paddingLeft: `${node.depth * 12 + 8}px` }}
      tabIndex={isFocused ? 0 : -1}
      onFocus={onFocus}
      onClick={() => navigate(`/spaces/${node.spaceKey}/pages/${node.page.slug}`)}
      draggable={ENABLE_DND}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag handle */}
      {ENABLE_DND && (
        <span className="opacity-0 group-hover:opacity-60 hover:opacity-100 cursor-grab text-gray-400 -ml-1 mr-0.5 touch-none">
          <GripVertical size={12} />
        </span>
      )}

      {/* Chevron toggle */}
      {node.hasChildren ? (
        <button
          data-compact-touch
          onClick={e => {
            e.stopPropagation()
            onToggle()
          }}
          className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
          aria-label={node.isExpanded ? 'Collapse' : 'Expand'}
        >
          {node.isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </button>
      ) : (
        <span className="w-4" />
      )}

      <FileText size={13} className="shrink-0" />
      <Link
        data-compact-touch
        to={`/spaces/${node.spaceKey}/pages/${node.page.slug}`}
        className="truncate flex-1"
        onClick={e => e.stopPropagation()}
        tabIndex={-1}
      >
        {node.page.title}
      </Link>
    </div>
  )
}
