import React, { createContext, useContext, useMemo, useState } from 'react'
import { api, setAuthTokens, clearAuthTokens, setOnUnauthorized } from '../services/api'

type User = {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

type AuthContextType = {
  accessToken: string
  refreshToken: string
  user: User | null
  loading: boolean
  error: string
  isAuthenticated: boolean
  initFromStorage: () => void
  login: (username: string, password: string) => Promise<void>
  register: (email: string, fullName: string, password: string) => Promise<void>
  fetchMe: () => Promise<void>
  logout: () => Promise<void>
  requestPasswordReset: (email: string) => Promise<string | null>
  confirmPasswordReset: (token: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string>(localStorage.getItem('access_token') || '')
  const [refreshToken, setRefreshToken] = useState<string>(localStorage.getItem('refresh_token') || '')
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isAuthenticated = !!accessToken

  function initFromStorage() {
    if (accessToken) setAuthTokens(accessToken, refreshToken)
  }

  async function login(username: string, password: string) {
    setError('')
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)
      params.append('grant_type', 'password')
      const { data } = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      setAccessToken(data.access_token)
      setRefreshToken(data.refresh_token)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      setAuthTokens(data.access_token, data.refresh_token)
      await fetchMe()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Ошибка входа')
      throw e
    } finally {
      setLoading(false)
    }
  }

  async function register(email: string, fullName: string, password: string) {
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/register', { email, full_name: fullName, password })
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Ошибка регистрации')
      throw e
    } finally {
      setLoading(false)
    }
  }

  async function fetchMe() {
    if (!accessToken) return
    try {
      const { data } = await api.get('/auth/me')
      setUser(data)
    } catch {
      // ignore
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout', null, { params: { token: accessToken, refresh_token: refreshToken } })
    } catch {}
    setAccessToken('')
    setRefreshToken('')
    setUser(null)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    clearAuthTokens()
  }

  async function requestPasswordReset(email: string) {
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post('/auth/forgot-password', { email })
      return data?.token || null
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Не удалось запросить сброс пароля')
      throw e
    } finally {
      setLoading(false)
    }
  }

  async function confirmPasswordReset(token: string, password: string) {
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/reset-password', { token, password })
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Не удалось сменить пароль')
      throw e
    } finally {
      setLoading(false)
    }
  }

  // Register unauthorized handler immediately so interceptors can call it even on first requests
  setOnUnauthorized(() => {
    // Clear auth state
    setAccessToken('')
    setRefreshToken('')
    setUser(null)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    clearAuthTokens()
    // Force redirect to login with return URL (avoid relying only on React effects)
    try {
      const { pathname, search } = window.location
      const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/register')
      if (!isAuthPage) {
        const redirect = encodeURIComponent(pathname + search)
        window.location.assign(`/login?redirect=${redirect}`)
      }
    } catch {}
  })

  const value = useMemo<AuthContextType>(() => ({
    accessToken, refreshToken, user, loading, error, isAuthenticated,
    initFromStorage, login, register, fetchMe, logout, requestPasswordReset, confirmPasswordReset,
  }), [accessToken, refreshToken, user, loading, error, isAuthenticated, requestPasswordReset, confirmPasswordReset])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
