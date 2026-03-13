import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  Skeleton,
  SkeletonLine,
  SkeletonCircle,
  SkeletonTitle,
  SkeletonIcon,
  SkeletonText,
  SkeletonListItem,
  SkeletonToolbar,
  SkeletonCard,
  SidebarSkeleton,
  PageViewSkeleton,
  EditorSkeleton,
  DashboardSkeleton,
  SpaceListSkeleton,
  SpaceViewSkeleton,
  HistorySkeleton,
  SearchResultsSkeleton,
  SettingsSkeleton,
  AppChromeSkeleton,
} from '../Skeleton'

describe('Skeleton components', () => {
  // ── Base primitives ──

  it('renders base Skeleton with role and aria-label', () => {
    render(<Skeleton width={100} height={20} />)
    const el = screen.getByRole('status')
    expect(el).toBeTruthy()
    expect(el.getAttribute('aria-label')).toBe('Loading')
  })

  it('applies shimmer class', () => {
    render(<Skeleton width={50} height={10} />)
    const el = screen.getByRole('status')
    expect(el.className).toContain('skeleton-shimmer')
  })

  it('renders SkeletonLine with correct dimensions', () => {
    const { container } = render(<SkeletonLine width="80%" height={16} />)
    const el = container.firstElementChild!
    expect(el.getAttribute('style')).toContain('width: 80%')
    expect(el.getAttribute('style')).toContain('height: 16px')
  })

  it('renders SkeletonLine with size presets', () => {
    const { container: sm } = render(<SkeletonLine size="sm" />)
    expect(sm.firstElementChild!.getAttribute('style')).toContain('height: 10px')

    const { container: lg } = render(<SkeletonLine size="lg" />)
    expect(lg.firstElementChild!.getAttribute('style')).toContain('height: 20px')
  })

  it('renders SkeletonCircle as rounded-full', () => {
    const { container } = render(<SkeletonCircle diameter={40} />)
    const el = container.firstElementChild!
    expect(el.className).toContain('rounded-full')
    expect(el.getAttribute('style')).toContain('width: 40px')
    expect(el.getAttribute('style')).toContain('height: 40px')
  })

  it('renders SkeletonCircle with size presets', () => {
    const { container: sm } = render(<SkeletonCircle size="sm" />)
    expect(sm.firstElementChild!.getAttribute('style')).toContain('width: 24px')

    const { container: lg } = render(<SkeletonCircle size="lg" />)
    expect(lg.firstElementChild!.getAttribute('style')).toContain('width: 48px')
  })

  it('renders SkeletonTitle with size presets', () => {
    const { container: sm } = render(<SkeletonTitle size="sm" />)
    expect(sm.firstElementChild!.getAttribute('style')).toContain('height: 16px')

    const { container: lg } = render(<SkeletonTitle size="lg" />)
    expect(lg.firstElementChild!.getAttribute('style')).toContain('height: 32px')
  })

  it('renders SkeletonIcon with size presets', () => {
    const { container: sm } = render(<SkeletonIcon size="sm" />)
    expect(sm.firstElementChild!.getAttribute('style')).toContain('width: 14px')

    const { container: md } = render(<SkeletonIcon size="md" />)
    expect(md.firstElementChild!.getAttribute('style')).toContain('width: 20px')
  })

  // ── Compositions ──

  it('renders SkeletonText with correct number of lines', () => {
    const { container } = render(<SkeletonText lines={5} />)
    const lines = container.querySelectorAll('.skeleton-shimmer')
    expect(lines.length).toBe(5)
  })

  it('renders SkeletonListItem with avatar and text', () => {
    const { container } = render(<SkeletonListItem />)
    const shimmers = container.querySelectorAll('.skeleton-shimmer')
    expect(shimmers.length).toBeGreaterThanOrEqual(3) // circle + 2 lines
  })

  it('renders SkeletonToolbar with dividers', () => {
    const { container } = render(<SkeletonToolbar />)
    const shimmers = container.querySelectorAll('.skeleton-shimmer')
    expect(shimmers.length).toBeGreaterThan(5)
  })

  it('renders SkeletonCard', () => {
    const { container } = render(<SkeletonCard />)
    expect(container.querySelectorAll('.skeleton-shimmer').length).toBeGreaterThan(0)
  })

  // ── Page-level skeleton compositions ──

  const pageLevelSkeletons = [
    { name: 'SidebarSkeleton', Component: SidebarSkeleton, label: 'Loading sidebar' },
    { name: 'PageViewSkeleton', Component: PageViewSkeleton, label: 'Loading page' },
    { name: 'EditorSkeleton', Component: EditorSkeleton, label: 'Loading editor' },
    { name: 'DashboardSkeleton', Component: DashboardSkeleton, label: 'Loading dashboard' },
    { name: 'SpaceListSkeleton', Component: SpaceListSkeleton, label: 'Loading spaces' },
    { name: 'SpaceViewSkeleton', Component: SpaceViewSkeleton, label: 'Loading space' },
    { name: 'HistorySkeleton', Component: HistorySkeleton, label: 'Loading history' },
    { name: 'SearchResultsSkeleton', Component: SearchResultsSkeleton, label: 'Loading search results' },
    { name: 'SettingsSkeleton', Component: SettingsSkeleton, label: 'Loading settings' },
    { name: 'AppChromeSkeleton', Component: AppChromeSkeleton, label: 'Loading application' },
  ]

  pageLevelSkeletons.forEach(({ name, Component, label }) => {
    it(`renders ${name} with accessible label "${label}"`, () => {
      render(<Component />)
      const elements = screen.getAllByRole('status')
      const wrapper = elements.find(el => el.getAttribute('aria-label') === label)
      expect(wrapper).toBeTruthy()
    })
  })
})
