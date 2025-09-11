import React from 'react'
import { useTranslation } from 'react-i18next'

export default function News() {
  const { t } = useTranslation()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('news.title')}
        </h1>
        <p className="text-gray-600">
          Noticias relevantes para tu negocio
        </p>
      </div>

      <div className="card">
        <p className="text-gray-500 text-center py-8">
          Las noticias aparecerán aquí una vez que se integren las fuentes de datos
        </p>
      </div>
    </div>
  )
}