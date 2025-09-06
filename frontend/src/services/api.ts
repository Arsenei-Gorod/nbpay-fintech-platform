import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

let accessToken = localStorage.getItem('access_token') || ''
let refreshToken = localStorage.getItem('refresh_token') || ''
let isRefreshing = false
let pendingQueue: Array<() => void> = []
let onUnauthorized: (() => void) | null = null

export function setOnUnauthorized(handler: () => void) {
  onUnauthorized = handler
}

export function setAuthTokens(access: string, refresh: string) {
  accessToken = access
  refreshToken = refresh
}

export function clearAuthTokens() {
  accessToken = ''
  refreshToken = ''
}

export const api = axios.create({ baseURL })

api.interceptors.request.use((config: any) => {
  if (accessToken) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original: any = error.config
    const isAuthEndpoint = typeof original?.url === 'string' && (original.url.includes('/auth/refresh') || original.url.includes('/auth/login'))
    if (error.response?.status === 401 && !original?._retry && refreshToken && !isAuthEndpoint) {
      if (isRefreshing) {
        await new Promise<void>((resolve) => pendingQueue.push(resolve))
        return api(original)
      }
      original._retry = true
      isRefreshing = true
      try {
        const { data } = await api.post('/auth/refresh', null, { params: { refresh_token: refreshToken } })
        accessToken = data.access_token
        refreshToken = data.refresh_token
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
        pendingQueue.forEach((fn) => fn())
        pendingQueue = []
        return api(original)
      } catch (e) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        accessToken = ''
        refreshToken = ''
        if (onUnauthorized) onUnauthorized()
        throw e
      } finally {
        isRefreshing = false
      }
    }
    // If we are here with 401 and cannot refresh, force logout
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      accessToken = ''
      refreshToken = ''
      if (onUnauthorized) onUnauthorized()
    }
    throw error
  }
)
