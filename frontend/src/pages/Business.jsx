import React from 'react'
import { useTranslation } from 'react-i18next'

export default function Business() {
  const { t } = useTranslation()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('business.profile')}
        </h1>
        <p className="text-gray-600">
          Gestiona la información de tu negocio
        </p>
      </div>

      <div className="card">
        <p className="text-gray-500 text-center py-8">
          Formulario de perfil del negocio se implementará en la siguiente fase
        </p>
      </div>
    </div>
  )
}