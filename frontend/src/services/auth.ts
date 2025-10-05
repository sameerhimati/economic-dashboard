import { apiClient } from './api'
import type { AuthResponse, LoginCredentials, RegisterCredentials, User } from '@/types'

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      email: credentials?.username, // Backend uses email field
      password: credentials?.password,
    })

    if (!response?.data) {
      throw new Error('Invalid response from server')
    }

    return response.data
  },

  async register(credentials: RegisterCredentials): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', {
      email: credentials.email,
      password: credentials.password,
      full_name: credentials.username, // Backend uses full_name, not username
    })

    if (!response?.data) {
      throw new Error('Invalid response from server')
    }

    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')

    if (!response?.data) {
      throw new Error('Invalid response from server')
    }

    return response.data
  },

  logout(): void {
    localStorage.removeItem('token')
  },
}
