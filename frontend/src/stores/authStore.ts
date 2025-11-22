/**
 * Authentication store using Zustand.
 * Manages user authentication state, login, logout, and token management.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '@/services/api'

interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  email_verified: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => void
  setAccessToken: (token: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        try {
          const { data } = await api.post('/auth/login', { email, password })
          const { access_token, refresh_token, user } = data.data

          // Store refresh token in localStorage
          localStorage.setItem('refreshToken', refresh_token)

          set({
            user: user,
            accessToken: access_token,
            isAuthenticated: true,
          })
        } catch (error: any) {
          const message = error.response?.data?.error?.message || 'Login failed'
          throw new Error(message)
        }
      },

      register: async (email: string, username: string, password: string) => {
        try {
          await api.post('/auth/register', { email, username, password })
          // After successful registration, automatically login
          // Or redirect to login page
        } catch (error: any) {
          const message = error.response?.data?.error?.message || 'Registration failed'
          throw new Error(message)
        }
      },

      logout: () => {
        localStorage.removeItem('refreshToken')
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
        })
      },

      setAccessToken: (token: string) => {
        set({ accessToken: token })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }), // Only persist user, not tokens
    }
  )
)
