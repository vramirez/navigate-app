import React from 'react'
import { useTranslation } from 'react-i18next'

export default function LoadingSpinner({ size = 'md', text = null }) {
  const { t } = useTranslation()
  
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  }

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`spinner ${sizeClasses[size]}`}></div>
      {text && (
        <p className="mt-4 text-sm text-gray-600">
          {text}
        </p>
      )}
      {!text && (
        <p className="mt-4 text-sm text-gray-600">
          {t('common.loading')}
        </p>
      )}
    </div>
  )
}