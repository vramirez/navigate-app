import React, { useState, useMemo } from 'react'
import { useQuery } from 'react-query'
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
import { getCategoryBadgeClasses, getCategoryIcon } from '../utils/categoryUtils'
import { getDashboardArticles } from '../services/newsApi'
import { getRecommendationsByArticle } from '../services/recommendationsApi'
import { joinArticlesWithRecommendations, sortByRelevance } from '../utils/dataTransformers'
import RelevanceBadge from '../components/RelevanceBadge'

export default function Dashboard() {
  const { t } = useTranslation()

  // State for tracking user interactions
  const [newsLikes, setNewsLikes] = useState({})
  const [recommendations, setRecommendations] = useState({})

  // Filter state for low-relevance articles
  const [showLowRelevance, setShowLowRelevance] = useState(() => {
    const saved = localStorage.getItem('showLowRelevance')
    return saved !== null ? JSON.parse(saved) : true
  })

  // Fetch articles from API
  const { data: articlesData, isLoading: articlesLoading, error: articlesError } = useQuery(
    'dashboardArticles',
    getDashboardArticles,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      onError: (error) => {
        console.error('Dashboard: Error fetching articles:', error)
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
        })
      },
      onSuccess: (data) => {
        console.log('Dashboard: Articles fetched successfully:', data)
      },
    }
  )

  // Fetch recommendations from API
  const { data: recommendationsData, isLoading: recommendationsLoading } = useQuery(
    'articleRecommendations',
    () => getRecommendationsByArticle(1), // TODO: Get actual business ID from auth context
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    }
  )

  // Join articles with their recommendations and apply relevance filter
  const newsWithRecommendations = useMemo(() => {
    if (!articlesData || !recommendationsData) return []

    const joined = joinArticlesWithRecommendations(articlesData, recommendationsData)
    const sorted = sortByRelevance(joined)

    // Apply low-relevance filter if disabled
    if (!showLowRelevance) {
      return sorted.filter(news => news.relevanceScore >= 0.3)
    }

    return sorted
  }, [articlesData, recommendationsData, showLowRelevance])

  // Handle filter toggle
  const handleToggleLowRelevance = () => {
    const newValue = !showLowRelevance
    setShowLowRelevance(newValue)
    localStorage.setItem('showLowRelevance', JSON.stringify(newValue))
  }

  // Loading state
  if (articlesLoading || recommendationsLoading) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-3" style={{color: '#c01b1bff', opacity: 0.55}}>
            {t('dashboard.welcome')}
          </h1>
          <p className="text-lg" style={{color: '#f3e9e9ff', opacity: 0.55}}>
            Noticias relevantes y recomendaciones para tu negocio
          </p>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="news-card animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (articlesError) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-3" style={{color: '#c01b1bff', opacity: 0.55}}>
            {t('dashboard.welcome')}
          </h1>
        </div>
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-600 text-center py-8">
            Error al cargar las noticias. Por favor, intenta de nuevo más tarde.
          </p>
        </div>
      </div>
    )
  }

  // Empty state
  if (!newsWithRecommendations || newsWithRecommendations.length === 0) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-3" style={{color: '#c01b1bff', opacity: 0.55}}>
            {t('dashboard.welcome')}
          </h1>
        </div>
        <div className="card">
          <p className="text-gray-500 text-center py-8">
            No hay noticias disponibles en este momento.
          </p>
        </div>
      </div>
    )
  }

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

  const handleRecommendationReset = (recId) => {
    setRecommendations(prev => {
      const newState = { ...prev }
      delete newState[recId]
      return newState
    })
  }

  // Sort news based on like status: liked first, neutral middle, disliked last
  const sortedNews = [...newsWithRecommendations].sort((a, b) => {
    const aStatus = newsLikes[a.id]
    const bStatus = newsLikes[b.id]
    
    if (aStatus === 'like' && bStatus !== 'like') return -1
    if (bStatus === 'like' && aStatus !== 'like') return 1
    if (aStatus === 'dislike' && bStatus !== 'dislike') return 1
    if (bStatus === 'dislike' && aStatus !== 'dislike') return -1
    
    return 0 // Keep original order for same status
  })

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
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-4xl font-bold" style={{color: '#c01b1bff', opacity: 0.55}}>
            {t('dashboard.welcome')}
          </h1>

          {/* Relevance Filter Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showLowRelevance}
              onChange={handleToggleLowRelevance}
              className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">
              Mostrar baja relevancia
            </span>
          </label>
        </div>

        <p className="text-lg" style={{color: '#f3e9e9ff', opacity: 0.55}}>
          Noticias relevantes y recomendaciones para tu negocio
        </p>
      </div>

      {/* News Feed with Embedded Recommendations */}
      <div className="space-y-4">
        {sortedNews.map((news) => {
          const newsLikeStatus = newsLikes[news.id]
          
          // Render minimized version for disliked news
          if (newsLikeStatus === 'dislike') {
            return (
              <div key={news.id} className="news-card-minimized">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {news.category && (
                        <span className={getCategoryBadgeClasses(news.category)}>
                          <span>{getCategoryIcon(news.category)}</span>
                          <span>{t(`newsCategories.public.${news.category}`)}</span>
                        </span>
                      )}
                      <h2 className="text-base font-semibold text-gray-300 flex-1">
                        {news.title}
                      </h2>
                    </div>
                    <div className="flex items-center text-xs text-gray-500">
                      <span className="font-medium">{news.source}</span>
                      <span className="mx-2">•</span>
                      <span>{news.publishedAt}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handleNewsLike(news.id, true)}
                      className="p-2 rounded-lg bg-gray-700 text-gray-400 hover:text-green-400 hover:bg-gray-600 transition-colors"
                    >
                      <HandThumbUpIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleNewsLike(news.id, false)}
                      className="p-2 rounded-lg bg-red-900/50 text-red-400 transition-colors"
                    >
                      <HandThumbDownIconSolid className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            )
          }
          
          return (
            <div key={news.id} className="news-card">
              {/* News Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  {/* Category and Relevance Badges */}
                  <div className="mb-3 flex items-center gap-2 flex-wrap">
                    {news.category && (
                      <span className={getCategoryBadgeClasses(news.category)}>
                        <span>{getCategoryIcon(news.category)}</span>
                        <span>{t(`newsCategories.public.${news.category}`)}</span>
                      </span>
                    )}
                    <RelevanceBadge score={news.relevanceScore} />
                  </div>

                  {/* News Title */}
                  <h2 className="text-2xl font-bold text-gray-900 mb-2 leading-tight hover:text-blue-600 transition-colors cursor-pointer">
                    {news.title}
                  </h2>

                  {/* News Source Badge */}
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="font-medium">{news.source}</span>
                    <span>•</span>
                    <span>{news.publishedAt}</span>
                  </div>
                </div>
                
                {/* Like/Dislike Buttons */}
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => handleNewsLike(news.id, true)}
                    className={`p-2 rounded-lg transition-colors ${
                      newsLikeStatus === 'like'
                        ? 'text-green-600 bg-green-100'
                        : 'text-gray-400 bg-gray-100 hover:text-green-600 hover:bg-green-50'
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
                    className={`p-2 rounded-lg transition-colors ${
                      newsLikeStatus === 'dislike'
                        ? 'text-red-600 bg-red-100'
                        : 'text-gray-400 bg-gray-100 hover:text-red-600 hover:bg-red-50'
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
              <div className="news-content">
                <p className="text-base leading-relaxed">
                  {news.content}
                </p>
              </div>

              {/* Related Recommendations - Nested inside news card */}
              {news.recommendations.length > 0 && (
                <div className="recommendations-section">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        Recomendaciones relacionadas
                        <span className="text-xs font-semibold px-2 py-0.5 bg-purple-100 text-purple-800 rounded-full">
                          {news.recommendations.length}
                        </span>
                      </h3>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {news.recommendations.map((rec) => {
                      const recStatus = recommendations[rec.id]

                      return (
                        <div
                          key={rec.id}
                          className={`p-4 rounded-lg border-2 border-l-4 shadow-md transition-all duration-200 ${
                            recStatus === 'done'
                              ? 'bg-green-50 border-green-300 border-l-green-600'
                              : recStatus === 'ignored'
                              ? 'bg-gray-50 border-gray-300 border-l-gray-400 opacity-50'
                              : 'bg-white border-gray-300 border-l-purple-500 hover:shadow-lg hover:border-gray-400'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 min-w-0">
                              {/* Priority Badge, Title & Time - All on same line */}
                              <div className="flex items-center gap-3 mb-2">
                                <span className={`px-2 py-1 text-xs font-bold rounded-md uppercase flex-shrink-0 ${getPriorityColor(rec.priority)}`}>
                                  {getPriorityText(rec.priority)}
                                </span>
                                <div className="flex items-center gap-2 flex-1">
                                  <h4 className={`font-bold text-base ${
                                    recStatus === 'ignored' ? 'line-through text-gray-500' : 'text-gray-900'
                                  }`}>
                                    {rec.title}
                                  </h4>
                                  <div className="flex items-center text-xs text-gray-600 flex-shrink-0">
                                    <ClockIcon className="h-3.5 w-3.5 mr-1" />
                                    {rec.estimatedHours}h
                                  </div>
                                </div>
                              </div>

                              {/* Recommendation Description */}
                              <p className={`text-sm leading-relaxed ${
                                recStatus === 'ignored' ? 'text-gray-400' : 'text-gray-600'
                              }`}>
                                {rec.description}
                              </p>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex flex-col items-end gap-2 flex-shrink-0">
                              {recStatus === 'done' ? (
                                <>
                                  <div className="flex items-center text-green-700 bg-green-100 px-3 py-1.5 rounded-lg shadow-sm">
                                    <CheckCircleIcon className="h-4 w-4 mr-1.5" />
                                    <span className="text-xs font-bold uppercase tracking-wide">Completado</span>
                                  </div>
                                  <button
                                    onClick={() => handleRecommendationReset(rec.id)}
                                    className="text-xs font-medium text-gray-600 hover:text-gray-800 underline transition-colors"
                                  >
                                    Restablecer
                                  </button>
                                </>
                              ) : recStatus === 'ignored' ? (
                                <>
                                  <div className="flex items-center text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg shadow-sm">
                                    <XCircleIcon className="h-4 w-4 mr-1.5" />
                                    <span className="text-xs font-bold uppercase tracking-wide">Ignorado</span>
                                  </div>
                                  <button
                                    onClick={() => handleRecommendationReset(rec.id)}
                                    className="text-xs font-medium text-gray-600 hover:text-gray-800 underline transition-colors"
                                  >
                                    Restablecer
                                  </button>
                                </>
                              ) : (
                                <>
                                  <button
                                    onClick={() => handleRecommendationAction(rec.id, 'done')}
                                    className="flex items-center px-4 py-2 text-sm font-bold text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
                                  >
                                    <CheckIcon className="h-4 w-4 mr-1.5" />
                                    Completar
                                  </button>
                                  <button
                                    onClick={() => handleRecommendationAction(rec.id, 'ignored')}
                                    className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                                  >
                                    <XMarkIcon className="h-4 w-4 mr-1.5" />
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
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}