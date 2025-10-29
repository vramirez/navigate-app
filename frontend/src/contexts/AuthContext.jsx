/**
 * Authentication Context
 *
 * Provides user authentication state and business information throughout the app.
 * Automatically loads user profile on mount if token exists.
 *
 * Usage:
 *   import { useAuth } from '../contexts/AuthContext'
 *   const { user, business, businessTypeCode, isAuthenticated, loading } = useAuth()
 */

import { createContext, useState, useContext, useEffect } from 'react'
import apiClient from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [business, setBusiness] = useState(null)
  const [businessTypeCode, setBusinessTypeCode] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load user profile from API
  const loadUserProfile = async () => {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await apiClient.get('/api/businesses/auth/profile/')
      const data = response.data

      setUser(data.user)
      setBusiness(data.business)
      setBusinessTypeCode(data.business_type_code)
      setIsAuthenticated(true)
    } catch (err) {
      console.error('Failed to load user profile:', err)
      setError(err.message)

      // Clear invalid token
      if (err.response?.status === 401) {
        localStorage.removeItem('auth_token')
        setIsAuthenticated(false)
      }
    } finally {
      setLoading(false)
    }
  }

  // Login with token
  const login = async (token) => {
    localStorage.setItem('auth_token', token)
    await loadUserProfile()
  }

  // Logout
  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
    setBusiness(null)
    setBusinessTypeCode(null)
    setIsAuthenticated(false)
    setError(null)
  }

  // Reload profile (useful after updating business info)
  const reloadProfile = async () => {
    await loadUserProfile()
  }

  // Load profile on mount and listen for global logout events
  useEffect(() => {
    loadUserProfile()

    // Listen for global logout events (e.g., from 401 responses in api.js)
    const handleGlobalLogout = () => {
      setUser(null)
      setBusiness(null)
      setBusinessTypeCode(null)
      setIsAuthenticated(false)
      setError(null)
    }

    window.addEventListener('auth:logout', handleGlobalLogout)
    return () => {
      window.removeEventListener('auth:logout', handleGlobalLogout)
    }
  }, [])

  const value = {
    user,
    business,
    businessTypeCode,
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    reloadProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
