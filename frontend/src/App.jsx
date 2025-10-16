import React, { Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Layout from './components/Layout'
import LoadingSpinner from './components/LoadingSpinner'

// Lazy load pages for better performance
const Dashboard = React.lazy(() => import('./pages/Dashboard'))
const Recommendations = React.lazy(() => import('./pages/Recommendations'))
const Business = React.lazy(() => import('./pages/Business'))
const News = React.lazy(() => import('./pages/News'))
const ArticleDetail = React.lazy(() => import('./pages/ArticleDetail'))
const Settings = React.lazy(() => import('./pages/Settings'))
const Login = React.lazy(() => import('./pages/Login'))
const ApiTest = React.lazy(() => import('./pages/ApiTest'))

// Mock authentication hook - replace with real auth later
const useAuth = () => {
  // For demo purposes, always return authenticated
  return {
    isAuthenticated: true,
    user: {
      id: 1,
      name: 'Demo User',
      email: 'demo@navigate.com'
    }
  }
}

function App() {
  const { i18n } = useTranslation()
  const { isAuthenticated } = useAuth()

  // Update HTML lang attribute when language changes
  React.useEffect(() => {
    document.documentElement.lang = i18n.language
  }, [i18n.language])

  if (!isAuthenticated) {
    return (
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Suspense>
    )
  }

  return (
    <Layout>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/business" element={<Business />} />
          <Route path="/news" element={<News />} />
          <Route path="/news/:articleId" element={<ArticleDetail />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/api-test" element={<ApiTest />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </Layout>
  )
}

export default App