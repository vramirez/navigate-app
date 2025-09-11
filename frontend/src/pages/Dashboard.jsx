import React from 'react'
import { useTranslation } from 'react-i18next'
import { 
  LightBulbIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon,
  NewspaperIcon 
} from '@heroicons/react/24/outline'

export default function Dashboard() {
  const { t } = useTranslation()

  // Mock data for dashboard
  const stats = [
    {
      name: t('dashboard.totalRecommendations'),
      value: '12',
      icon: LightBulbIcon,
      color: 'text-navitest-600',
      bgColor: 'bg-navitest-50'
    },
    {
      name: t('dashboard.highPriority'),
      value: '3',
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      name: t('dashboard.implemented'),
      value: '8',
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: t('dashboard.recentNews'),
      value: '24',
      icon: NewspaperIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('dashboard.welcome')}
        </h1>
        <p className="text-gray-600">
          {t('app.tagline')}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {t('recommendations.title')}
          </h2>
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 border rounded-lg">
              <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Aumentar inventario para maratón
                </p>
                <p className="text-xs text-gray-500">Alta prioridad • Hace 2 horas</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 border rounded-lg">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Contratar personal adicional
                </p>
                <p className="text-xs text-gray-500">Media prioridad • Hace 4 horas</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-3 border rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Promoción fin de semana
                </p>
                <p className="text-xs text-gray-500">Baja prioridad • Hace 1 día</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {t('dashboard.recentNews')}
          </h2>
          <div className="space-y-3">
            <div className="border-l-4 border-navitest-500 pl-4 py-2">
              <p className="text-sm font-medium text-gray-900">
                Maratón Internacional de Medellín 2025
              </p>
              <p className="text-xs text-gray-500">El Tiempo • Hace 3 horas</p>
            </div>
            <div className="border-l-4 border-gray-300 pl-4 py-2">
              <p className="text-sm font-medium text-gray-900">
                Festival Gastronómico en Zona Rosa
              </p>
              <p className="text-xs text-gray-500">El Espectador • Hace 6 horas</p>
            </div>
            <div className="border-l-4 border-gray-300 pl-4 py-2">
              <p className="text-sm font-medium text-gray-900">
                Nueva universidad abre sede en Bogotá
              </p>
              <p className="text-xs text-gray-500">Semana • Hace 1 día</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}