import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthContext, useAuthProvider } from './hooks/useAuth'
import { ThemeContext, useThemeProvider } from './hooks/useTheme'
import Layout from './components/Layout'
import { AppChromeSkeleton } from './components/Skeleton'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import SpaceList from './pages/SpaceList'
import SpaceView from './pages/SpaceView'
import CreateSpace from './pages/CreateSpace'
import SpaceSettings from './pages/SpaceSettings'
import PageView from './pages/PageView'
import PageEditor from './pages/PageEditor'
import PageHistory from './pages/PageHistory'
import SearchPage from './pages/SearchPage'
import LandingPage from './pages/LandingPage'

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
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/login" element={!auth.isAuthenticated ? <LoginPage /> : <Navigate to="/" />} />
        <Route path="/register" element={!auth.isAuthenticated ? <RegisterPage /> : <Navigate to="/" />} />
        <Route element={auth.isAuthenticated ? <Layout /> : <Navigate to="/landing" />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/spaces" element={<SpaceList />} />
          <Route path="/spaces/create" element={<CreateSpace />} />
          <Route path="/spaces/:spaceKey" element={<SpaceView />} />
          <Route path="/spaces/:spaceKey/settings" element={<SpaceSettings />} />
          <Route path="/spaces/:spaceKey/pages/new" element={<PageEditor />} />
          <Route path="/spaces/:spaceKey/pages/:pageSlug" element={<PageView />} />
          <Route path="/spaces/:spaceKey/pages/:pageSlug/edit" element={<PageEditor />} />
          <Route path="/spaces/:spaceKey/pages/:pageSlug/history" element={<PageHistory />} />
          <Route path="/search" element={<SearchPage />} />
        </Route>
      </Routes>
    </AuthContext.Provider>
    </ThemeContext.Provider>
  )
}
