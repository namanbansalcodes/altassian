import { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import * as authApi from '../api'
import { setAccessToken } from '../api/client'
import type { User } from '../types'

export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: { username: string; email: string; password: string; password_confirm: string; first_name: string; last_name: string }) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | null>(null)

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function useAuthProvider(): AuthContextType {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  useEffect(() => {
    // Demo mode: bypass auth for local screenshots
    if (localStorage.getItem('demo_open') === '1') {
      setUser({ id: 0, username: 'demo' })
      setIsLoading(false)
      // Signal app ready for headless scripts
      ;(window as any).__APP_READY__ = true
      window.dispatchEvent(new Event('app-ready'))
      return
    }
    const boot = async () => {
      const refreshed = await authApi.refreshFromStorage()
      if (refreshed) {
        try {
          const me = await authApi.getMe()
          setUser(me)
        } catch {
          localStorage.removeItem('refresh_token')
          setAccessToken(null)
        }
      }
      setIsLoading(false)
      // Mark app ready after first auth bootstrap completes and first paint
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          ;(window as any).__APP_READY__ = true
          window.dispatchEvent(new Event('app-ready'))
        })
      })
    }
    boot()
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    await authApi.login({ username, password })
    const me = await authApi.getMe()
    setUser(me)
  }, [])

  const register = useCallback(async (data: { username: string; email: string; password: string; password_confirm: string; first_name: string; last_name: string }) => {
    await authApi.register(data)
  }, [])

  const logoutFn = useCallback(async () => {
    await authApi.logout()
    setUser(null)
    queryClient.clear()
  }, [queryClient])

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout: logoutFn,
  }
}
