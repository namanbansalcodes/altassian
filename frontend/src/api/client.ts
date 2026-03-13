import axios from 'axios'
import { toast } from '../lib/toast'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  headers: { 'Content-Type': 'application/json' },
})

let accessToken: string | null = null

// Bootstrap access token early from localStorage to avoid 401s before refresh completes
const bootAccess = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
if (bootAccess) accessToken = bootAccess

export function setAccessToken(token: string | null) {
  accessToken = token
  if (typeof window !== 'undefined') {
    if (token) localStorage.setItem('access_token', token)
    else localStorage.removeItem('access_token')
  }
}

export function getAccessToken() {
  return accessToken
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as any
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${import.meta.env.VITE_API_BASE || '/api'}/auth/token/refresh/`, { refresh })
          setAccessToken(data.access)
          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('refresh_token')
          setAccessToken(null)
          window.location.href = '/login'
        }
      }
    }
    if (!error.response) {
      toast.error('Network error — please check your connection')
    } else if (error.response.status >= 500) {
      toast.error('Server error — please try again later')
    }
    return Promise.reject(error)
  }
)

export default api
