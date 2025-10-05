import { create } from 'zustand'
import { authService } from '@/services/auth'
import type { User, LoginCredentials, RegisterCredentials } from '@/types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (credentials: LoginCredentials) => {
    try {
      set({ isLoading: true, error: null })
      const response = await authService.login(credentials)

      if (!response?.access_token) {
        throw new Error('Invalid login response')
      }

      localStorage.setItem('token', response.access_token)

      // Fetch user data
      const user = await authService.getCurrentUser()

      set({
        token: response.access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      set({
        error: error?.message || 'Login failed',
        isLoading: false,
        isAuthenticated: false,
      })
      throw error
    }
  },

  register: async (credentials: RegisterCredentials) => {
    try {
      set({ isLoading: true, error: null })
      await authService.register(credentials)

      // Auto-login after registration (use email, not username)
      await get().login({
        username: credentials?.email || '',
        password: credentials?.password || '',
      })
    } catch (error: any) {
      set({
        error: error?.message || 'Registration failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: () => {
    authService.logout()
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null })
      return
    }

    try {
      const user = await authService.getCurrentUser()
      set({
        user,
        token,
        isAuthenticated: true,
      })
    } catch (error) {
      // Token is invalid
      localStorage.removeItem('token')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      })
    }
  },

  clearError: () => set({ error: null }),
}))
