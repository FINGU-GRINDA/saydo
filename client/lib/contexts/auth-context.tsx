'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { apiClient } from '../api-client'

interface User {
  id: string
  email: string
  name: string
  picture?: string
  google_credentials?: any
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('auth_token')
    if (token) {
      apiClient.setToken(token)
      // Try to get current user
      apiClient.getCurrentUser()
        .then(userData => {
          setUser(userData)
        })
        .catch(() => {
          // Token is invalid, clear it
          localStorage.removeItem('auth_token')
          apiClient.clearToken()
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // Use the demo login endpoint
      const response = await apiClient.demoLogin(email, password)
      
      // Set token and user
      localStorage.setItem('auth_token', response.access_token)
      apiClient.setToken(response.access_token)
      setUser(response.user)
      
    } catch (error: any) {
      // Handle different error types
      if (error.message.includes('404')) {
        throw new Error('Demo account not found. Please run the setup script.')
      } else if (error.message.includes('401')) {
        throw new Error('Invalid credentials. Use demo/demo')
      } else {
        throw new Error('Login failed. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await apiClient.logout()
    } catch (error) {
      // Ignore logout errors
    } finally {
      setUser(null)
      setIsLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 