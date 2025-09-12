import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  HandThumbUpIcon,
  HandThumbDownIcon,
  CheckIcon,
  XMarkIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import {
  HandThumbUpIcon as HandThumbUpIconSolid,
  HandThumbDownIcon as HandThumbDownIconSolid,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/solid'

export default function Dashboard() {
  const { t } = useTranslation()
  
  // State for tracking user interactions
  const [newsLikes, setNewsLikes] = useState({})
  const [recommendations, setRecommendations] = useState({})

  // Mock data for news with embedded recommendations
  const newsWithRecommendations = [
    {
      id: 1,
      title: 'Medellín se prepara para el Maratón Internacional 2025 con más de 15,000 participantes',
      source: 'El Tiempo',
      publishedAt: 'Hace 3 horas',
      content: 'La capital antioqueña se alista para recibir el próximo 15 de octubre el Maratón Internacional de Medellín 2025, uno de los eventos deportivos más importantes del país. Se esperan más de 15,000 corredores nacionales e internacionales. El evento incluirá tres modalidades: maratón completo (42K), media maratón (21K) y carrera recreativa (10K)...',
      recommendations: [
        {
          id: 'rec1',
          title: 'Aumentar inventario de bebidas isotónicas en 200%',
          priority: 'high',
          description: 'El evento deportivo generará alta demanda de bebidas isotónicas y agua. Recomendamos incrementar significativamente el stock.',
          estimatedHours: 4
        },
        {
          id: 'rec2', 
          title: 'Preparar menú especial para corredores (desayunos 5:00-7:00 AM)',
          priority: 'medium',
          description: 'Ofrecer opciones saludables y energéticas antes del evento. Considerar abrir más temprano.',
          estimatedHours: 8
        }
      ]
    },
    {
      id: 2,
      title: 'Colombia clasifica a la final de la Copa América: el partido decisivo contra Brasil',
      source: 'El Espectador',
      publishedAt: 'Hace 5 horas',
      content: 'La Selección Colombia logró clasificar a la final de la Copa América 2025 y enfrentará a Brasil el próximo 10 de diciembre en el Estadio Metropolitano de Barranquilla. Las autoridades esperan que más de 50,000 hinchas llenen el estadio, mientras que millones de colombianos seguirán el partido desde bares y restaurantes...',
      recommendations: [
        {
          id: 'rec3',
          title: 'Crear promoción especial "Final Copa América" - 2x1 en cervezas nacionales',
          priority: 'urgent',
          description: '¡Oportunidad histórica! Preparar campaña especial con decoración temática y promociones en cervezas.',
          estimatedHours: 12
        },
        {
          id: 'rec4',
          title: 'Aumentar stock de cerveza en 400% para el día del partido',
          priority: 'high', 
          description: 'Evento de altísima demanda. Contactar proveedores inmediatamente para asegurar stock suficiente.',
          estimatedHours: 6
        },
        {
          id: 'rec5',
          title: 'Contratar 2 meseros adicionales para el evento',
          priority: 'medium',
          description: 'El volumen de clientes será excepcional. Personal adicional garantizará mejor servicio.',
          estimatedHours: 3
        }
      ]
    },
    {
      id: 3,
      title: 'Festival Gastronómico Internacional llega a Bogotá con 200 restaurantes',
      source: 'Caracol Radio',
      publishedAt: 'Hace 1 día',
      content: 'Del 20 al 25 de noviembre, la Zona Rosa de Bogotá será el epicentro del Festival Gastronómico Internacional. El festival incluirá cenas especiales, talleres de cocina, degustaciones y competencias entre chefs. Se esperan más de 50,000 visitantes...',
      recommendations: [
        {
          id: 'rec6',
          title: 'Considerar participación como expositor en el festival',
          priority: 'low',
          description: 'Oportunidad de visibilidad y networking con otros restaurantes. Evaluar costos vs beneficios.',
          estimatedHours: 20
        }
      ]
    }
  ]

  const handleNewsLike = (newsId, isLike) => {
    setNewsLikes(prev => ({
      ...prev,
      [newsId]: prev[newsId] === (isLike ? 'like' : 'dislike') ? null : (isLike ? 'like' : 'dislike')
    }))
  }

  const handleRecommendationAction = (recId, action) => {
    setRecommendations(prev => ({
      ...prev,
      [recId]: action
    }))
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-50'
      case 'high': return 'text-orange-600 bg-orange-50' 
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getPriorityText = (priority) => {
    switch (priority) {
      case 'urgent': return 'URGENTE'
      case 'high': return 'ALTA'
      case 'medium': return 'MEDIA'
      case 'low': return 'BAJA'
      default: return 'MEDIA'
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {t('dashboard.welcome')}
        </h1>
        <p className="text-gray-600">
          Noticias relevantes y recomendaciones para tu negocio
        </p>
      </div>

      {/* News Feed with Embedded Recommendations */}
      <div className="space-y-6">
        {newsWithRecommendations.map((news) => {
          const newsLikeStatus = newsLikes[news.id]
          
          return (
            <div key={news.id} className="card">
              {/* News Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    {news.title}
                  </h2>
                  <div className="flex items-center text-sm text-gray-500 mb-3">
                    <span className="font-medium">{news.source}</span>
                    <span className="mx-2">•</span>
                    <span>{news.publishedAt}</span>
                  </div>
                </div>
                
                {/* Like/Dislike Buttons */}
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleNewsLike(news.id, true)}
                    className={`p-2 rounded-full transition-colors ${
                      newsLikeStatus === 'like' 
                        ? 'text-green-600 bg-green-50' 
                        : 'text-gray-400 hover:text-green-600 hover:bg-green-50'
                    }`}
                  >
                    {newsLikeStatus === 'like' ? (
                      <HandThumbUpIconSolid className="h-5 w-5" />
                    ) : (
                      <HandThumbUpIcon className="h-5 w-5" />
                    )}
                  </button>
                  <button
                    onClick={() => handleNewsLike(news.id, false)}
                    className={`p-2 rounded-full transition-colors ${
                      newsLikeStatus === 'dislike' 
                        ? 'text-red-600 bg-red-50' 
                        : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
                    }`}
                  >
                    {newsLikeStatus === 'dislike' ? (
                      <HandThumbDownIconSolid className="h-5 w-5" />
                    ) : (
                      <HandThumbDownIcon className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* News Content */}
              <p className="text-gray-700 mb-6 leading-relaxed">
                {news.content}
              </p>

              {/* Related Recommendations */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  💡 Recomendaciones relacionadas ({news.recommendations.length})
                </h3>
                
                <div className="space-y-4">
                  {news.recommendations.map((rec) => {
                    const recStatus = recommendations[rec.id]
                    
                    return (
                      <div 
                        key={rec.id} 
                        className={`p-4 border rounded-lg transition-all ${
                          recStatus === 'done' 
                            ? 'bg-green-50 border-green-200' 
                            : recStatus === 'ignored'
                            ? 'bg-gray-50 border-gray-200 opacity-60'
                            : 'bg-white border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            {/* Priority Badge */}
                            <div className="flex items-center mb-2">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(rec.priority)}`}>
                                {getPriorityText(rec.priority)}
                              </span>
                              <div className="flex items-center ml-3 text-sm text-gray-500">
                                <ClockIcon className="h-4 w-4 mr-1" />
                                {rec.estimatedHours}h estimadas
                              </div>
                            </div>
                            
                            {/* Recommendation Title and Description */}
                            <h4 className={`font-medium mb-2 ${
                              recStatus === 'ignored' ? 'line-through text-gray-500' : 'text-gray-900'
                            }`}>
                              {rec.title}
                            </h4>
                            <p className={`text-sm ${
                              recStatus === 'ignored' ? 'text-gray-400' : 'text-gray-600'
                            }`}>
                              {rec.description}
                            </p>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex items-center space-x-2 ml-4">
                            {recStatus === 'done' ? (
                              <div className="flex items-center text-green-600 bg-green-100 px-3 py-1 rounded-full">
                                <CheckCircleIcon className="h-4 w-4 mr-1" />
                                <span className="text-sm font-medium">Completado</span>
                              </div>
                            ) : recStatus === 'ignored' ? (
                              <div className="flex items-center text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                                <XCircleIcon className="h-4 w-4 mr-1" />
                                <span className="text-sm font-medium">Ignorado</span>
                              </div>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleRecommendationAction(rec.id, 'done')}
                                  className="flex items-center px-3 py-1 text-sm font-medium text-green-700 bg-green-100 rounded-full hover:bg-green-200 transition-colors"
                                >
                                  <CheckIcon className="h-4 w-4 mr-1" />
                                  Completar
                                </button>
                                <button
                                  onClick={() => handleRecommendationAction(rec.id, 'ignored')}
                                  className="flex items-center px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                                >
                                  <XMarkIcon className="h-4 w-4 mr-1" />
                                  Ignorar
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}