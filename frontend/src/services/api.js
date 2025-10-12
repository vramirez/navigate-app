/**
 * Base API Client Configuration
 *
 * Centralizes axios configuration for all API calls
 * TODO Phase 4: Add authentication token interceptors
 */

import axios from 'axios'

// Base API URL - defaults to localhost backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Request interceptor - can add auth tokens here later
apiClient.interceptors.request.use(
  (config) => {
    // TODO Phase 4: Add authentication token
    // const token = localStorage.getItem('auth_token')
    // if (token) {
    //   config.headers.Authorization = `Token ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle common errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common HTTP errors
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Unauthorized - redirect to login in Phase 4
          console.error('Unauthorized access')
          break
        case 403:
          // Forbidden
          console.error('Forbidden access')
          break
        case 404:
          // Not found
          console.error('Resource not found')
          break
        case 500:
          // Server error
          console.error('Server error:', data)
          break
        default:
          console.error('API error:', error.message)
      }
    } else if (error.request) {
      // Network error - no response received
      console.error('Network error - no response from server')
    } else {
      // Other errors
      console.error('Request error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default apiClient
