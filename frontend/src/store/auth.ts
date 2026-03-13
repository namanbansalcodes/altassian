// Simple module-level auth state (unused). We rely on React context in hooks/useAuth.
import type { User } from '../types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
}

let state: AuthState = { user: null, isAuthenticated: false }
const listeners = new Set<() => void>()

export function getAuthState() { return state }

export function setAuthState(newState: Partial<AuthState>) {
  state = { ...state, ...newState }
  listeners.forEach(fn => fn())
}

export function subscribe(fn: () => void) {
  listeners.add(fn)
  return () => { listeners.delete(fn) }
}
