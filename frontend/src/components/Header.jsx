import React from 'react'
import { useTranslation } from 'react-i18next'
import { Bars3Icon } from '@heroicons/react/24/outline'
import LanguageSwitcher from './LanguageSwitcher'

export default function Header({ onMenuClick }) {
  const { t } = useTranslation()

  return (
    <div className="lg:hidden">
      <div className="flex items-center justify-between bg-white px-4 py-2 shadow-sm border-b border-gray-200">
        <div className="flex items-center">
          <button
            type="button"
            className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-navitest-500"
            onClick={onMenuClick}
          >
            <span className="sr-only">Open sidebar</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
          <h1 className="ml-3 text-lg font-semibold text-gray-900">
            {t('app.name')}
          </h1>
        </div>
        <LanguageSwitcher />
      </div>
    </div>
  )
}