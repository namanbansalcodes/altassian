import { useEffect, useRef, type RefObject } from 'react'

/**
 * Observes a scrollable container and sets `data-scrollable` when its content
 * overflows, enabling the CSS gradient mask defined on `.breadcrumb-scroll`.
 */
export function useScrollHint<T extends HTMLElement>(): RefObject<T | null> {
  const ref = useRef<T | null>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    function update(): void {
      if (!el) return
      if (el.scrollWidth > el.clientWidth) {
        el.setAttribute('data-scrollable', '')
      } else {
        el.removeAttribute('data-scrollable')
      }
    }

    update()

    const ro = new ResizeObserver(update)
    ro.observe(el)

    el.addEventListener('scroll', update, { passive: true })

    return () => {
      ro.disconnect()
      el.removeEventListener('scroll', update)
    }
  }, [])

  return ref
}
