import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthContext, useAuthProvider } from './hooks/useAuth'
import { ThemeContext, useThemeProvider } from './hooks/useTheme'
import Layout from './components/Layout'
import {
  AppChromeSkeleton, DashboardSkeleton, PageViewSkeleton,
  EditorSkeleton, SpaceListSkeleton, SpaceViewSkeleton,
  HistorySkeleton, SettingsSkeleton,
} from './components/Skeleton'

// Lazy-loaded page components — each becomes its own chunk
const LandingPage = lazy(() => import('./pages/LandingPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const SpaceList = lazy(() => import('./pages/SpaceList'))
const SpaceView = lazy(() => import('./pages/SpaceView'))
const CreateSpace = lazy(() => import('./pages/CreateSpace'))
const SpaceSettings = lazy(() => import('./pages/SpaceSettings'))
const PageView = lazy(() => import('./pages/PageView'))
const PageEditor = lazy(() => import('./pages/PageEditor'))
const PageHistory = lazy(() => import('./pages/PageHistory'))
const SearchPage = lazy(() => import('./pages/SearchPage'))

export default function App() {
  const auth = useAuthProvider()
  const themeCtx = useThemeProvider()

  if (auth.isLoading) {
    return <AppChromeSkeleton />
  }

  return (
    <ThemeContext.Provider value={themeCtx}>
    <AuthContext.Provider value={auth}>
      <Routes>
        {/* Public landing page */}
        <Route path="/landing" element={<Suspense fallback={null}><LandingPage /></Suspense>} />
        <Route path="/login" element={!auth.isAuthenticated ? <Suspense fallback={null}><LoginPage /></Suspense> : <Navigate to="/" />} />
        <Route path="/register" element={!auth.isAuthenticated ? <Suspense fallback={null}><RegisterPage /></Suspense> : <Navigate to="/" />} />
        <Route element={auth.isAuthenticated ? <Layout /> : <Navigate to="/landing" />}>
          <Route path="/" element={<Suspense fallback={<DashboardSkeleton />}><Dashboard /></Suspense>} />
          <Route path="/spaces" element={<Suspense fallback={<SpaceListSkeleton />}><SpaceList /></Suspense>} />
          <Route path="/spaces/create" element={<Suspense fallback={null}><CreateSpace /></Suspense>} />
          <Route path="/spaces/:spaceKey" element={<Suspense fallback={<SpaceViewSkeleton />}><SpaceView /></Suspense>} />
          <Route path="/spaces/:spaceKey/settings" element={<Suspense fallback={<SettingsSkeleton />}><SpaceSettings /></Suspense>} />
          <Route path="/spaces/:spaceKey/pages/new" element={<Suspense fallback={<EditorSkeleton />}><PageEditor /></Suspense>} />
          <Route path="/spaces/:spaceKey/pages/:pageSlug" element={<Suspense fallback={<PageViewSkeleton />}><PageView /></Suspense>} />
          <Route path="/spaces/:spaceKey/pages/:pageSlug/edit" element={<Suspense fallback={<EditorSkeleton />}><PageEditor /></Suspense>} />
          <Route path="/spaces/:spaceKey/pages/:pageSlug/history" element={<Suspense fallback={<HistorySkeleton />}><PageHistory /></Suspense>} />
          <Route path="/search" element={<Suspense fallback={null}><SearchPage /></Suspense>} />
        </Route>
      </Routes>
    </AuthContext.Provider>
    </ThemeContext.Provider>
  )
}
