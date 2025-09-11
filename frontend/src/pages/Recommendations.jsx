import React from 'react'
import { useTranslation } from 'react-i18next'

export default function Recommendations() {
  const { t } = useTranslation()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('recommendations.title')}
        </h1>
        <p className="text-gray-600">
          Recomendaciones inteligentes para tu negocio
        </p>
      </div>

      <div className="card">
        <p className="text-gray-500 text-center py-8">
          Las recomendaciones aparecerán aquí una vez que el sistema ML esté configurado
        </p>
      </div>
    </div>
  )
}