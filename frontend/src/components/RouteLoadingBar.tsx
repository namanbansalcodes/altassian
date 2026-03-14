import { useEffect, useState, useRef } from 'react'

/**
 * Thin progress bar shown at the top of the viewport during navigations or data loads.
 * Uses a simple global event mechanism to avoid React Router version coupling.
 * Trigger window.dispatchEvent(new CustomEvent('route-loading', { detail: true|false }))
 */
export default function RouteLoadingBar() {
  const [visible, setVisible] = useState(false)
  const [progress, setProgress] = useState(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    const onLoading = (e: Event) => {
      const detail = (e as CustomEvent<boolean>).detail
      if (detail) {
        setVisible(true)
        setProgress(20)
        timerRef.current && clearInterval(timerRef.current)
        timerRef.current = setInterval(() => {
          setProgress(prev => (prev >= 90 ? prev : prev + (90 - prev) * 0.1))
        }, 200)
      } else {
        setProgress(100)
        if (timerRef.current) clearInterval(timerRef.current)
        const t = setTimeout(() => {
          setVisible(false)
          setProgress(0)
        }, 300)
        return () => clearTimeout(t)
      }
    }
    window.addEventListener('route-loading', onLoading as any)
    return () => {
      window.removeEventListener('route-loading', onLoading as any)
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  if (!visible) return null

  return (
    <div
      className="fixed top-0 left-0 right-0 z-50 h-0.5 bg-transparent pointer-events-none"
      role="progressbar"
      aria-label="Page loading"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(progress)}
    >
      <div
        className="h-full bg-blue-500 dark:bg-blue-400 transition-all duration-200 ease-out"
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}
