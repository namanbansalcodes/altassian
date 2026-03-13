/**
 * Skeleton loading components.
 *
 * Base primitives: <Skeleton />, <SkeletonLine />, <SkeletonCircle />, <SkeletonTitle />, <SkeletonIcon />
 * Compositions:    <SkeletonText />, <SkeletonListItem />, <SkeletonToolbar />,
 *                  <SkeletonCard />, <SidebarSkeleton />, <PageViewSkeleton />,
 *                  <EditorSkeleton />, <DashboardSkeleton />, <SpaceListSkeleton />,
 *                  <SpaceViewSkeleton />, <HistorySkeleton />, <SearchResultsSkeleton />,
 *                  <SettingsSkeleton />, <AppChromeSkeleton />
 */

// ── Size presets ────────────────────────────────────────────

type SkeletonSize = 'sm' | 'md' | 'lg'

const LINE_HEIGHTS: Record<SkeletonSize, number> = { sm: 10, md: 14, lg: 20 }
const TITLE_HEIGHTS: Record<SkeletonSize, number> = { sm: 16, md: 24, lg: 32 }
const ICON_SIZES: Record<SkeletonSize, number> = { sm: 14, md: 20, lg: 28 }
const AVATAR_SIZES: Record<SkeletonSize, number> = { sm: 24, md: 32, lg: 48 }

// ── Base primitives ──────────────────────────────────────────

export interface SkeletonProps {
  width?: string | number
  height?: string | number
  rounded?: string
  className?: string
}

export function Skeleton({ width, height, rounded = 'rounded', className = '' }: SkeletonProps) {
  return (
    <div
      className={`skeleton-shimmer ${rounded} ${className}`}
      style={{ width, height }}
      role="status"
      aria-label="Loading"
    />
  )
}

export function SkeletonLine({ width = '100%', height, size = 'md' }: { width?: string | number; height?: number; size?: SkeletonSize }) {
  return <Skeleton width={width} height={height ?? LINE_HEIGHTS[size]} rounded="rounded" />
}

export function SkeletonCircle({ size = 'md', diameter }: { size?: SkeletonSize; diameter?: number }) {
  const d = diameter ?? AVATAR_SIZES[size]
  return <Skeleton width={d} height={d} rounded="rounded-full" className="shrink-0" />
}

/** Heading / title placeholder */
export function SkeletonTitle({ width = '60%', size = 'md' }: { width?: string | number; size?: SkeletonSize }) {
  return <Skeleton width={width} height={TITLE_HEIGHTS[size]} rounded="rounded" />
}

/** Small square icon placeholder */
export function SkeletonIcon({ size = 'md' }: { size?: SkeletonSize }) {
  const s = ICON_SIZES[size]
  return <Skeleton width={s} height={s} rounded="rounded-sm" className="shrink-0" />
}

// ── Compositions ─────────────────────────────────────────────

/** Multiple text lines with a shorter last line */
export function SkeletonText({ lines = 3, size = 'md' }: { lines?: number; size?: SkeletonSize }) {
  return (
    <div className="space-y-2.5">
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonLine key={i} width={i === lines - 1 ? '60%' : '100%'} size={size} />
      ))}
    </div>
  )
}

/** Avatar + two text lines */
export function SkeletonListItem() {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <SkeletonCircle size="md" />
      <div className="flex-1 space-y-2">
        <SkeletonLine width="70%" />
        <SkeletonLine width="40%" size="sm" />
      </div>
    </div>
  )
}

/** Icon-sized square + one text line (for sidebar tree items) */
export function SkeletonTreeItem({ indent = 0 }: { indent?: number }) {
  return (
    <div className="flex items-center gap-2 px-2 py-1.5" style={{ paddingLeft: `${indent * 12 + 8}px` }}>
      <SkeletonIcon size="sm" />
      <SkeletonLine width={`${50 + Math.random() * 40}%`} size="sm" />
    </div>
  )
}

/** Row of small boxes mimicking a formatting toolbar */
export function SkeletonToolbar() {
  return (
    <div className="flex items-center gap-1 px-4 py-2.5 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
      {[28, 28, 28, 28, 0, 28, 28, 28, 0, 28, 28, 28].map((w, i) =>
        w === 0
          ? <div key={i} className="w-px h-5 bg-gray-300 dark:bg-gray-600 mx-1" />
          : <Skeleton key={i} width={w} height={28} rounded="rounded" />
      )}
    </div>
  )
}

/** Space card skeleton (for SpaceList grid) */
export function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
      <div className="flex items-start gap-4">
        <Skeleton width={48} height={48} rounded="rounded-lg" className="shrink-0" />
        <div className="flex-1 space-y-2.5">
          <SkeletonLine width="60%" size="lg" />
          <SkeletonLine width="90%" size="sm" />
          <SkeletonLine width="35%" size="sm" />
        </div>
      </div>
    </div>
  )
}

// ── Page-level skeletons ─────────────────────────────────────

export function SidebarSkeleton() {
  return (
    <div className="p-3 space-y-3" role="status" aria-label="Loading sidebar">
      <div className="flex items-center justify-between mb-2 px-2">
        <SkeletonLine width={60} size="sm" />
        <SkeletonIcon size="sm" />
      </div>
      {[1, 2, 3].map(i => (
        <div key={i} className="space-y-1">
          <SkeletonTreeItem />
          {i <= 2 && (
            <>
              <SkeletonTreeItem indent={1} />
              <SkeletonTreeItem indent={1} />
            </>
          )}
        </div>
      ))}
    </div>
  )
}

/** Full app chrome skeleton: topbar + sidebar placeholder */
export function AppChromeSkeleton() {
  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-gray-950" role="status" aria-label="Loading application">
      {/* Top navbar skeleton */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 h-14 flex items-center px-4 gap-4 shrink-0">
        <SkeletonIcon size="md" />
        <Skeleton width={100} height={22} rounded="rounded" />
        <div className="hidden md:flex items-center gap-2 ml-2">
          <Skeleton width={60} height={28} rounded="rounded-md" />
          <Skeleton width={60} height={28} rounded="rounded-md" />
          <Skeleton width={60} height={28} rounded="rounded-md" />
        </div>
        <div className="flex-1 max-w-xl mx-4">
          <Skeleton width="100%" height={32} rounded="rounded-lg" />
        </div>
        <SkeletonIcon size="md" />
        <SkeletonCircle size="sm" />
      </header>

      {/* Body: sidebar + content */}
      <div className="flex flex-1 overflow-hidden">
        <aside className="hidden lg:block w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 shrink-0">
          <SidebarSkeleton />
        </aside>
        <main className="flex-1 p-6 bg-gray-50 dark:bg-gray-950">
          <div className="max-w-4xl mx-auto space-y-4">
            <SkeletonTitle width={250} size="lg" />
            <SkeletonLine width={200} size="sm" />
            <div className="mt-8">
              <SkeletonText lines={4} />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export function PageViewSkeleton() {
  return (
    <div className="max-w-4xl mx-auto" role="status" aria-label="Loading page">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-4">
        <SkeletonLine width={80} size="sm" />
        <SkeletonLine width={12} size="sm" />
        <SkeletonLine width={120} size="sm" />
      </div>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="space-y-2 flex-1">
          <SkeletonTitle width="55%" size="lg" />
          <SkeletonLine width="30%" size="sm" />
        </div>
        <div className="flex gap-2">
          <Skeleton width={70} height={32} rounded="rounded-lg" />
          <Skeleton width={80} height={32} rounded="rounded-lg" />
        </div>
      </div>
      {/* Content block */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-8 mb-8 space-y-4">
        <SkeletonTitle width="80%" size="md" />
        <SkeletonText lines={4} />
        <SkeletonLine width="45%" />
        <SkeletonText lines={3} />
      </div>
      {/* Attachments */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <SkeletonLine width={120} size="lg" />
      </div>
      {/* Comments */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <SkeletonLine width={110} size="lg" />
        <SkeletonListItem />
        <SkeletonListItem />
      </div>
    </div>
  )
}

export function EditorSkeleton() {
  return (
    <div className="max-w-4xl mx-auto" role="status" aria-label="Loading editor">
      <div className="flex items-center justify-between mb-4">
        <SkeletonTitle width={100} size="sm" />
        <div className="flex gap-2">
          <Skeleton width={70} height={36} rounded="rounded-lg" />
          <Skeleton width={70} height={36} rounded="rounded-lg" />
        </div>
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Title area */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <SkeletonTitle width="40%" size="lg" />
        </div>
        {/* Toolbar */}
        <SkeletonToolbar />
        {/* Content area */}
        <div className="p-6 space-y-4">
          <SkeletonText lines={6} />
        </div>
      </div>
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="max-w-6xl mx-auto" role="status" aria-label="Loading dashboard">
      <div className="mb-8 space-y-2">
        <SkeletonTitle width={250} size="lg" />
        <SkeletonLine width={200} size="md" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Recent pages */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <SkeletonLine width={130} size="lg" />
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="flex items-center gap-3 px-4 py-3">
                  <SkeletonIcon size="sm" />
                  <div className="flex-1 space-y-1.5">
                    <SkeletonLine width={`${55 + i * 5}%`} />
                    <SkeletonLine width="35%" size="sm" />
                  </div>
                </div>
              ))}
            </div>
          </div>
          {/* Activity */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <SkeletonLine width={140} size="lg" />
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              {[1, 2, 3].map(i => <SkeletonListItem key={i} />)}
            </div>
          </div>
        </div>
        {/* Sidebar cards */}
        <div className="space-y-6">
          {[1, 2].map(n => (
            <div key={n} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <SkeletonLine width={120} size="lg" />
              </div>
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {[1, 2].map(i => (
                  <div key={i} className="flex items-center gap-3 px-4 py-3">
                    <Skeleton width={32} height={32} rounded="rounded" className="shrink-0" />
                    <div className="flex-1 space-y-1.5">
                      <SkeletonLine width="65%" />
                      <SkeletonLine width="30%" size="sm" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/** Grid of space cards with header */
export function SpaceListSkeleton() {
  return (
    <div className="max-w-4xl mx-auto" role="status" aria-label="Loading spaces">
      <div className="flex items-center justify-between mb-6">
        <SkeletonTitle width={100} size="lg" />
        <Skeleton width={120} height={36} rounded="rounded-lg" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[1, 2, 3, 4].map(i => <SkeletonCard key={i} />)}
      </div>
    </div>
  )
}

export function SpaceViewSkeleton() {
  return (
    <div className="max-w-4xl mx-auto" role="status" aria-label="Loading space">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          <Skeleton width={56} height={56} rounded="rounded-xl" className="shrink-0" />
          <div className="space-y-2">
            <SkeletonTitle width={180} size="md" />
            <SkeletonLine width={120} size="sm" />
          </div>
        </div>
        <div className="flex gap-2">
          <Skeleton width={90} height={32} rounded="rounded-lg" />
          <Skeleton width={36} height={32} rounded="rounded-lg" />
        </div>
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <SkeletonLine width={50} />
        </div>
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="flex items-center gap-3 px-4 py-3">
              <SkeletonIcon size="sm" />
              <div className="flex-1 space-y-1.5">
                <SkeletonLine width={`${50 + i * 8}%`} />
                <SkeletonLine width="30%" size="sm" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function HistorySkeleton() {
  return (
    <div className="max-w-5xl mx-auto" role="status" aria-label="Loading history">
      <div className="flex items-center gap-3 mb-6">
        <SkeletonIcon size="md" />
        <SkeletonTitle width={140} size="md" />
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <SkeletonLine width={60} />
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {[1, 2, 3].map(i => (
              <div key={i} className="p-3 space-y-2">
                <div className="flex items-center gap-2">
                  <SkeletonLine width={30} />
                  <SkeletonLine width={70} size="sm" />
                </div>
                <SkeletonLine width="50%" size="sm" />
              </div>
            ))}
          </div>
        </div>
        <div className="col-span-2 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <SkeletonLine width={160} />
          </div>
          <div className="p-6 space-y-3">
            <SkeletonText lines={5} />
          </div>
        </div>
      </div>
    </div>
  )
}

export function SearchResultsSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-800 overflow-hidden" role="status" aria-label="Loading search results">
      {[1, 2, 3].map(i => (
        <div key={i} className="flex items-start gap-3 px-5 py-4">
          <SkeletonIcon size="md" />
          <div className="flex-1 space-y-2">
            <SkeletonLine width={`${40 + i * 10}%`} />
            <SkeletonLine width="85%" size="sm" />
            <SkeletonLine width="30%" size="sm" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function SettingsSkeleton() {
  return (
    <div className="max-w-lg mx-auto" role="status" aria-label="Loading settings">
      <div className="flex items-center gap-3 mb-6">
        <SkeletonIcon size="md" />
        <SkeletonTitle width={140} size="md" />
      </div>
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-5">
        {[1, 2, 3].map(i => (
          <div key={i} className="space-y-1.5">
            <SkeletonLine width={90} size="sm" />
            <Skeleton width="100%" height={38} rounded="rounded-lg" />
          </div>
        ))}
        <div className="flex justify-end">
          <Skeleton width={110} height={36} rounded="rounded-lg" />
        </div>
      </div>
    </div>
  )
}
