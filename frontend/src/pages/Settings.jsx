import React from 'react'
import { useTranslation } from 'react-i18next'

export default function Settings() {
  const { t } = useTranslation()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('nav.settings')}
        </h1>
        <p className="text-gray-600">
          Configura tus preferencias
        </p>
      </div>

      <div className="card">
        <p className="text-gray-500 text-center py-8">
          Configuraciones de usuario y preferencias se implementarán próximamente
        </p>
      </div>
    </div>
  )
}