import React from 'react'
import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import LanguageSwitcher from '../components/LanguageSwitcher'

export default function Login() {
  const { t } = useTranslation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    // Mock login - in real app, this would authenticate with backend
    console.log('Login attempt:', { email, password })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-extrabold text-gray-900">
              {t('app.name')}
            </h2>
            <LanguageSwitcher />
          </div>
          <p className="text-center text-sm text-gray-600 mb-8">
            {t('app.tagline')}
          </p>
          <h3 className="text-2xl font-bold text-gray-900 text-center">
            {t('auth.welcome')}
          </h3>
          <p className="mt-2 text-center text-sm text-gray-600">
            {t('auth.createAccount')}
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                {t('auth.email')}
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input mt-1"
                placeholder={t('auth.email')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                {t('auth.password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="input mt-1"
                placeholder={t('auth.password')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-navitest-600 focus:ring-navitest-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                {t('auth.rememberMe')}
              </label>
            </div>

            <div className="text-sm">
              <a href="#" className="font-medium text-navitest-600 hover:text-navitest-500">
                {t('auth.forgotPassword')}
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 btn-primary"
            >
              {t('auth.login')}
            </button>
          </div>
          
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Demo: Use cualquier email y contraseña para acceder
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}