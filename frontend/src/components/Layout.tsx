import { useState, useEffect, useCallback } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import {
  Menu, MenuButton, MenuItems, MenuItem,
  Dialog, DialogPanel, DialogBackdrop,
  Transition, TransitionChild,
} from '@headlessui/react'
import {
  Search, Home, BookOpen, Plus, ChevronDown,
  Menu as MenuIcon, X, LogOut, Moon, Sun
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import { toast } from '../lib/toast'
import Sidebar from './Sidebar'
import RouteLoadingBar from './RouteLoadingBar'

export default function Layout() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  // Close mobile drawer on route change (via navigate)
  const closeMobileDrawer = useCallback(() => setMobileDrawerOpen(false), [])

  // Close mobile drawer when viewport grows past lg breakpoint
  useEffect(() => {
    const mql = window.matchMedia('(min-width: 1024px)')
    const handler = (e: MediaQueryListEvent) => {
      if (e.matches) setMobileDrawerOpen(false)
    }
    mql.addEventListener('change', handler)
    return () => mql.removeEventListener('change', handler)
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-gray-950">
      <RouteLoadingBar />
      {/* Top navbar */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 h-14 flex items-center px-3 sm:px-4 gap-2 sm:gap-4 shrink-0 z-20" style={{ paddingTop: 'env(safe-area-inset-top)' }}>
        {/* Mobile hamburger (< lg) */}
        <button
          onClick={() => setMobileDrawerOpen(true)}
          className="lg:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 -ml-1 rounded-lg active:bg-gray-100 dark:active:bg-gray-800"
          aria-label="Open navigation menu"
        >
          <MenuIcon size={20} />
        </button>

        {/* Desktop sidebar toggle (lg+) */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="hidden lg:flex items-center justify-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 -ml-1 rounded-lg"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? <X size={20} /> : <MenuIcon size={20} />}
        </button>

        <Link to="/" className="text-xl font-bold text-blue-700 dark:text-blue-400 mr-2 sm:mr-4 shrink-0">Altassian</Link>

        <nav className="hidden md:flex items-center gap-1">
          <Link to="/" className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md flex items-center gap-1.5">
            <Home size={16} /> Home
          </Link>
          <Link to="/spaces" className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md flex items-center gap-1.5">
            <BookOpen size={16} /> Spaces
          </Link>
          <Link to="/spaces/create" className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md flex items-center gap-1.5">
            <Plus size={16} /> Create
          </Link>
        </nav>

        <form onSubmit={handleSearch} className="flex-1 min-w-0 max-w-xl mx-2 sm:mx-4">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-700 outline-none"
            />
          </div>
        </form>

        <button
          onClick={() => {
            toggleTheme()
            toast.info(theme === 'dark' ? 'Light mode' : 'Dark mode', { duration: 1500 })
          }}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 transition-colors shrink-0"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <Menu as="div" className="relative shrink-0">
          <MenuButton className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
            <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-medium">
              {user?.first_name?.[0] || user?.username?.[0] || 'U'}
            </div>
            <span className="hidden md:block text-sm text-gray-700 dark:text-gray-300 max-w-[120px] truncate">{user?.first_name || user?.username}</span>
            <ChevronDown size={14} className="hidden sm:block text-gray-400" />
          </MenuButton>
          <MenuItems className="absolute right-0 mt-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-30">
            <div className="px-3 py-2 border-b border-gray-100 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
            </div>
            <MenuItem>
              <button onClick={() => { logout(); toast.success('Signed out') }} className="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2 data-[focus]:bg-gray-50 dark:data-[focus]:bg-gray-700">
                <LogOut size={14} /> Sign out
              </button>
            </MenuItem>
          </MenuItems>
        </Menu>
      </header>

      {/* Mobile sidebar drawer (< lg) */}
      <Transition show={mobileDrawerOpen}>
        <Dialog onClose={closeMobileDrawer} className="relative z-40 lg:hidden">
          <TransitionChild
            enter="transition-opacity duration-200 ease-out"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity duration-150 ease-in"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <DialogBackdrop className="fixed inset-0 bg-black/40" />
          </TransitionChild>

          <div className="fixed inset-0 flex">
            <TransitionChild
              enter="transition-transform duration-200 ease-out"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition-transform duration-150 ease-in"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <DialogPanel className="relative flex w-72 max-w-[85vw] flex-col bg-white dark:bg-gray-900 h-full shadow-xl">
                {/* Drawer header */}
                <div className="flex items-center justify-between h-14 px-4 border-b border-gray-200 dark:border-gray-700 shrink-0">
                  <span className="text-lg font-bold text-blue-700 dark:text-blue-400">Altassian</span>
                  <button
                    onClick={closeMobileDrawer}
                    className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 active:bg-gray-200 dark:active:bg-gray-700"
                    aria-label="Close navigation menu"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Mobile nav links */}
                <nav className="flex flex-col px-3 py-2 border-b border-gray-200 dark:border-gray-700 gap-0.5 lg:hidden">
                  <Link to="/" onClick={closeMobileDrawer} className="px-3 py-2.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 active:bg-gray-200 dark:active:bg-gray-700 rounded-md flex items-center gap-2">
                    <Home size={16} /> Home
                  </Link>
                  <Link to="/spaces" onClick={closeMobileDrawer} className="px-3 py-2.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 active:bg-gray-200 dark:active:bg-gray-700 rounded-md flex items-center gap-2">
                    <BookOpen size={16} /> Spaces
                  </Link>
                  <Link to="/spaces/create" onClick={closeMobileDrawer} className="px-3 py-2.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 active:bg-gray-200 dark:active:bg-gray-700 rounded-md flex items-center gap-2">
                    <Plus size={16} /> Create
                  </Link>
                </nav>

                {/* Sidebar content */}
                <div className="flex-1 overflow-y-auto" onClick={closeMobileDrawer}>
                  <Sidebar />
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </Dialog>
      </Transition>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop sidebar (lg+) */}
        {sidebarOpen && (
          <div className="hidden lg:block">
            <Sidebar />
          </div>
        )}
        <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 bg-gray-50 dark:bg-gray-950">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
