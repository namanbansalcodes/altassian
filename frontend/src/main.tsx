import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
})

// Provide a minimal wait-until-ready helper for scripts
;(window as any).waitUntilAppReady = (timeout = 10000) => new Promise<void>((resolve, reject) => {
  if ((window as any).__APP_READY__) return resolve()
  const onReady = () => { cleanup(); resolve() }
  const onTimeout = () => { cleanup(); reject(new Error('waitUntilAppReady: timeout')) }
  const cleanup = () => { window.removeEventListener('app-ready', onReady); clearTimeout(t) }
  window.addEventListener('app-ready', onReady)
  const t = setTimeout(onTimeout, timeout)
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster
          position="bottom-right"
          toastOptions={{ duration: 3500 }}
          closeButton
          richColors
          theme="system"
          visibleToasts={3}
          offset="16px"
          mobileOffset="12px"
        />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
