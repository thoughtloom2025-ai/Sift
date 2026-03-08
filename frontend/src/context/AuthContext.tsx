import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'
import type { User, AuthContextType } from '../types'

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('access_token')
      if (storedToken) {
        try {
          const response = await api.get('/auth/me')
          setUser(response.data)
          setToken(storedToken)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          setToken(null)
        }
      }
      setIsLoading(false)
    }
    initAuth()
  }, [])

  const login = async (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const { access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    setToken(access_token)
    const userResponse = await api.get('/auth/me')
    setUser(userResponse.data)
  }

  const register = async (email: string, password: string, fullName: string) => {
    await api.post('/auth/register', { email, password, full_name: fullName })
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
