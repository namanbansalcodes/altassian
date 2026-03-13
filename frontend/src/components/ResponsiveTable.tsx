import { useRef, useState, useEffect, useCallback } from 'react'

interface ResponsiveTableProps {
  children: React.ReactNode
  className?: string
  /** Label for screen-reader users describing the scrollable region */
  label?: string
}

export default function ResponsiveTable({ children, className = '', label = 'Scrollable table' }: ResponsiveTableProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(false)

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current
    if (!el) return
    setCanScrollLeft(el.scrollLeft > 1)
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1)
  }, [])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    updateScrollState()
    el.addEventListener('scroll', updateScrollState, { passive: true })
    const ro = new ResizeObserver(updateScrollState)
    ro.observe(el)
    return () => {
      el.removeEventListener('scroll', updateScrollState)
      ro.disconnect()
    }
  }, [updateScrollState])

  return (
    <div className={`relative ${className}`} role="region" aria-label={label}>
      {canScrollLeft && (
        <div className="absolute left-0 top-0 bottom-0 w-6 bg-gradient-to-r from-gray-50 dark:from-gray-950 to-transparent z-10 pointer-events-none" />
      )}
      {canScrollRight && (
        <div className="absolute right-0 top-0 bottom-0 w-6 bg-gradient-to-l from-gray-50 dark:from-gray-950 to-transparent z-10 pointer-events-none" />
      )}
      <div
        ref={scrollRef}
        tabIndex={0}
        className="overflow-x-auto -mx-4 sm:-mx-6 md:mx-0 scrollbar-thin"
        style={{ WebkitOverflowScrolling: 'touch' }}
      >
        <div className="inline-block min-w-full px-4 sm:px-6 md:px-0 align-middle">
          {children}
        </div>
      </div>
    </div>
  )
}
