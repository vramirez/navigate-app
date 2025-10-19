import React, { useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import { useTranslation } from 'react-i18next'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'
import {
  ArrowLeftIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
  MapPinIcon,
  UserGroupIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/solid'
import { getArticleById } from '../services/newsApi'
import { getRecommendationsByArticle } from '../services/recommendationsApi'
import { getCategoryBadgeClasses, getCategoryIcon } from '../utils/categoryUtils'
import RelevanceBadge from '../components/RelevanceBadge'
import ScoreIndicator from '../components/ScoreIndicator'
import KeywordTags from '../components/KeywordTags'
import EventMap from '../components/EventMap'
import ArticleDebugPanel from '../components/ArticleDebugPanel'

export default function ArticleDetail() {
  const { articleId } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()

  // Collapsible section states
  const [isProcessingExpanded, setIsProcessingExpanded] = useState(false)
  const [isContentExpanded, setIsContentExpanded] = useState(false)

  // Fetch article data
  const { data: article, isLoading, error } = useQuery(
    ['article', articleId],
    () => getArticleById(articleId),
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      retry: 1,
      onError: (error) => {
        console.error('ArticleDetail: Error fetching article:', error)
      }
    }
  )

  // Fetch recommendations data
  const { data: recommendationsData } = useQuery(
    'articleRecommendations',
    () => getRecommendationsByArticle(1), // TODO: Get actual business ID from auth context
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    }
  )

  // Filter recommendations for this specific article
  const articleRecommendations = useMemo(() => {
    if (!recommendationsData || !articleId) return []
    return recommendationsData[articleId] || []
  }, [recommendationsData, articleId])

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-12 bg-gray-200 rounded w-3/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  // Error state - 404 or other errors
  if (error) {
    const is404 = error.response?.status === 404
    return (
      <div className="max-w-5xl mx-auto">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-6 transition-colors"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Volver al Dashboard
        </button>

        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start gap-4">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 flex-shrink-0" />
            <div>
              <h2 className="text-2xl font-bold text-red-900 mb-2">
                {is404 ? 'Artículo no encontrado' : 'Error al cargar el artículo'}
              </h2>
              <p className="text-red-700 mb-4">
                {is404
                  ? `No se encontró el artículo con ID ${articleId}.`
                  : 'Ocurrió un error al cargar los datos del artículo. Por favor, intenta de nuevo más tarde.'}
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Volver al Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // No article data
  if (!article) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="card">
          <p className="text-gray-500 text-center py-8">
            No se encontraron datos para este artículo.
          </p>
        </div>
      </div>
    )
  }

  // Format publication date
  const publishedDate = article.published_date
    ? formatDistanceToNow(new Date(article.published_date), {
        addSuffix: true,
        locale: es
      })
    : 'Fecha desconocida'

  // Check if article has event information
  const hasEventInfo = article.event_type_detected || article.latitude || article.primary_city

  // Check if article has location data
  const hasLocation = article.latitude && article.longitude

  // Format event dates
  const formatEventDate = (dateString) => {
    if (!dateString) return null
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('es-CO', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (e) {
      return dateString
    }
  }

  // Calculate reading time (rough estimate: 200 words per minute)
  const calculateReadingTime = (content) => {
    if (!content) return null
    const wordCount = content.split(/\s+/).length
    const minutes = Math.ceil(wordCount / 200)
    return minutes
  }

  const readingTime = calculateReadingTime(article.content)

  // Priority color helpers (matching Dashboard)
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
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center text-blue-600 hover:text-blue-800 transition-colors font-medium"
      >
        <ArrowLeftIcon className="h-5 w-5 mr-2" />
        Volver al Dashboard
      </button>

      {/* SECTION A: Article Header */}
      <div className="card">
        {/* Badges */}
        <div className="mb-4 flex items-center gap-2 flex-wrap">
          {article.category && (
            <span className={getCategoryBadgeClasses(article.category)}>
              <span>{getCategoryIcon(article.category)}</span>
              <span>{t(`newsCategories.public.${article.category}`)}</span>
            </span>
          )}
          {article.subcategory && (
            <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-md border border-gray-300">
              {article.subcategory}
            </span>
          )}
          <RelevanceBadge score={article.business_relevance_score ?? -1} />
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">
          {article.url ? (
            <button
              onClick={() => window.open(article.url, '_blank', 'noopener,noreferrer')}
              className="text-left hover:text-blue-600 transition-colors cursor-pointer w-full"
            >
              {article.title}
            </button>
          ) : (
            article.title
          )}
        </h1>

        {/* Source and Date */}
        <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold">{article.source_name || 'Fuente desconocida'}</span>
            {article.source_country && (
              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                {article.source_country}
              </span>
            )}
          </div>
          <span>•</span>
          <span>{publishedDate}</span>
          {article.author && (
            <>
              <span>•</span>
              <span>Por {article.author}</span>
            </>
          )}
          {readingTime && (
            <>
              <span>•</span>
              <span>{readingTime} min de lectura</span>
            </>
          )}
        </div>
      </div>

      {/* SECTION B: Article Content */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Contenido del artículo</h2>

        {/* First Paragraph (always visible) */}
        {article.first_paragraph && (
          <div className="prose prose-lg max-w-none mb-4">
            <p className="text-gray-700 leading-relaxed">{article.first_paragraph}</p>
          </div>
        )}

        {/* Full Content (collapsible if long) */}
        {article.content && article.content !== article.first_paragraph && (
          <div>
            {!isContentExpanded && article.content.length > 500 && (
              <button
                onClick={() => setIsContentExpanded(true)}
                className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium transition-colors"
              >
                <span>Leer más</span>
                <ChevronDownIcon className="h-4 w-4" />
              </button>
            )}

            {(isContentExpanded || article.content.length <= 500) && (
              <div className="prose prose-lg max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {article.content}
                </p>
                {article.content.length > 500 && (
                  <button
                    onClick={() => setIsContentExpanded(false)}
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-800 font-medium transition-colors mt-4"
                  >
                    <span>Leer menos</span>
                    <ChevronUpIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {!article.first_paragraph && !article.content && (
          <p className="text-gray-400 italic">No hay contenido disponible.</p>
        )}
      </div>

      {/* SECTION C: Event Information */}
      {hasEventInfo && (
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Información del evento</h2>

          <div className="space-y-6">
            {/* Event Type */}
            {article.event_type_detected && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">Tipo de evento</h3>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-semibold text-gray-900">
                    {article.event_type_detected}
                  </span>
                  {article.event_subtype && (
                    <>
                      <span className="text-gray-400">→</span>
                      <span className="text-lg text-gray-700">{article.event_subtype}</span>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Event Dates */}
            {(article.event_start_datetime || article.event_end_datetime) && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <CalendarIcon className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
                  <div className="space-y-2">
                    {article.event_start_datetime && (
                      <div>
                        <p className="text-sm font-medium text-blue-900">Inicio</p>
                        <p className="text-blue-700">{formatEventDate(article.event_start_datetime)}</p>
                      </div>
                    )}
                    {article.event_end_datetime && (
                      <div>
                        <p className="text-sm font-medium text-blue-900">Fin</p>
                        <p className="text-blue-700">{formatEventDate(article.event_end_datetime)}</p>
                      </div>
                    )}
                    {article.event_duration_hours && (
                      <p className="text-sm text-blue-600">
                        Duración: {article.event_duration_hours} horas
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Location Information */}
            {(article.primary_city || article.neighborhood || article.venue_name) && (
              <div>
                <div className="flex items-start gap-3 mb-4">
                  <MapPinIcon className="h-6 w-6 text-gray-600 flex-shrink-0 mt-1" />
                  <div className="space-y-1">
                    {article.venue_name && (
                      <p className="text-lg font-semibold text-gray-900">{article.venue_name}</p>
                    )}
                    {article.venue_address && (
                      <p className="text-gray-700">{article.venue_address}</p>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      {article.neighborhood && <span>{article.neighborhood}</span>}
                      {article.neighborhood && article.primary_city && <span>•</span>}
                      {article.primary_city && <span>{article.primary_city}</span>}
                    </div>
                  </div>
                </div>

                {/* Map */}
                {hasLocation && (
                  <EventMap
                    latitude={article.latitude}
                    longitude={article.longitude}
                    venueName={article.venue_name}
                    city={article.primary_city}
                    neighborhood={article.neighborhood}
                    address={article.venue_address}
                    className="mt-4"
                  />
                )}
              </div>
            )}

            {/* Event Scale and Attendance */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {article.event_scale && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Escala del evento</h3>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {article.event_scale}
                  </p>
                </div>
              )}
              {article.expected_attendance && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <UserGroupIcon className="h-5 w-5 text-gray-500" />
                    <h3 className="text-sm font-medium text-gray-500">Asistencia esperada</h3>
                  </div>
                  <p className="text-lg font-semibold text-gray-900">
                    {article.expected_attendance.toLocaleString()} personas
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SECTION D: ML Extraction Details */}
      {article.features_extracted && (
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Análisis de Machine Learning</h2>

          <div className="space-y-6">
            {/* Main Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ScoreIndicator
                score={article.business_relevance_score}
                label={t('articleDetail.relevanceScore')}
                description={t('articleDetail.relevanceScoreDesc')}
              />
              <ScoreIndicator
                score={article.business_suitability_score}
                label={t('articleDetail.suitabilityScore')}
                description={t('articleDetail.suitabilityScoreDesc')}
              />
              <ScoreIndicator
                score={article.urgency_score}
                label="Urgencia"
                description="Qué tan urgente es tomar acción sobre esta noticia"
              />
              <ScoreIndicator
                score={article.sentiment_score}
                label="Sentimiento"
                description="Tono general del artículo (-1 negativo, 0 neutral, +1 positivo)"
              />
            </div>

            {/* Extraction Metadata */}
            {article.feature_extraction_date && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500 font-medium">Fecha de extracción</p>
                    <p
                      className="text-gray-900 cursor-help"
                      title={formatDistanceToNow(new Date(article.feature_extraction_date), {
                        addSuffix: true,
                        locale: es
                      })}
                    >
                      {new Date(article.feature_extraction_date).toLocaleString('es-CO', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                      })}
                    </p>
                  </div>
                  {article.feature_extraction_confidence && (
                    <div>
                      <p className="text-gray-500 font-medium">Confianza del análisis</p>
                      <p className="text-gray-900">
                        {(article.feature_extraction_confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Warning if features not extracted */}
      {!article.features_extracted && (
        <div className="card bg-yellow-50 border-yellow-200">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-yellow-900 mb-1">Procesamiento pendiente</h3>
              <p className="text-sm text-yellow-700">
                Este artículo aún no ha sido procesado por el sistema de Machine Learning.
                Las características y recomendaciones estarán disponibles pronto.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* SECTION E: Keywords & Entities */}
      {(article.extracted_keywords || article.entities) && (
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Palabras clave y entidades</h2>

          <div className="space-y-6">
            {/* Keywords */}
            {article.extracted_keywords && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-3">Palabras clave extraídas</h3>
                <KeywordTags keywords={article.extracted_keywords} type="keyword" />
              </div>
            )}

            {/* Entities */}
            {article.entities && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-3">Entidades detectadas</h3>
                <KeywordTags keywords={article.entities} type="entity" />
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION G: Related Recommendations */}
      {articleRecommendations.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-shrink-0 w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
              <LightBulbIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Recomendaciones generadas</h2>
              <p className="text-sm text-gray-600">
                Acciones sugeridas basadas en este artículo
              </p>
            </div>
            <span className="ml-auto text-sm font-semibold px-3 py-1 bg-purple-100 text-purple-800 rounded-full">
              {articleRecommendations.length}
            </span>
          </div>

          <div className="space-y-4">
            {articleRecommendations.map((rec) => (
              <div
                key={rec.id}
                className="p-5 rounded-lg border-2 border-l-4 border-gray-200 border-l-purple-500 bg-white hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Priority Badge & Title */}
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`px-2.5 py-1 text-xs font-bold rounded-md uppercase flex-shrink-0 ${getPriorityColor(rec.priority)}`}>
                        {getPriorityText(rec.priority)}
                      </span>
                      <h3 className="font-bold text-lg text-gray-900">
                        {rec.title}
                      </h3>
                    </div>

                    {/* Description */}
                    <p className="text-gray-700 leading-relaxed mb-4">
                      {rec.description}
                    </p>

                    {/* Metadata Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      {rec.category && (
                        <div>
                          <p className="text-gray-500 font-medium mb-1">Categoría</p>
                          <p className="text-gray-900 capitalize">{rec.category}</p>
                        </div>
                      )}
                      {rec.action_type && (
                        <div>
                          <p className="text-gray-500 font-medium mb-1">Tipo de acción</p>
                          <p className="text-gray-900 capitalize">{rec.action_type.replace(/_/g, ' ')}</p>
                        </div>
                      )}
                      {rec.estimated_duration_hours && (
                        <div>
                          <p className="text-gray-500 font-medium mb-1">Duración estimada</p>
                          <div className="flex items-center text-gray-900">
                            <ClockIcon className="h-4 w-4 mr-1 text-gray-500" />
                            {rec.estimated_duration_hours}h
                          </div>
                        </div>
                      )}
                      {rec.confidence_score !== undefined && (
                        <div>
                          <p className="text-gray-500 font-medium mb-1">Confianza</p>
                          <p className="text-gray-900">{(rec.confidence_score * 100).toFixed(0)}%</p>
                        </div>
                      )}
                    </div>

                    {/* Status Badges */}
                    <div className="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100">
                      {rec.is_viewed && (
                        <div className="flex items-center text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md text-xs font-medium">
                          <CheckCircleIcon className="h-3.5 w-3.5 mr-1" />
                          Vista
                        </div>
                      )}
                      {rec.is_accepted && (
                        <div className="flex items-center text-green-700 bg-green-50 px-2.5 py-1 rounded-md text-xs font-medium">
                          <CheckCircleIcon className="h-3.5 w-3.5 mr-1" />
                          Aceptada
                        </div>
                      )}
                      {rec.is_implemented && (
                        <div className="flex items-center text-purple-700 bg-purple-50 px-2.5 py-1 rounded-md text-xs font-medium">
                          <CheckCircleIcon className="h-3.5 w-3.5 mr-1" />
                          Implementada
                        </div>
                      )}
                      {!rec.is_viewed && !rec.is_accepted && !rec.is_implemented && (
                        <div className="flex items-center text-gray-500 bg-gray-50 px-2.5 py-1 rounded-md text-xs font-medium">
                          Pendiente
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION F: Processing Status (Collapsible) */}
      <div className="card">
        <button
          onClick={() => setIsProcessingExpanded(!isProcessingExpanded)}
          className="w-full flex items-center justify-between text-left"
        >
          <h2 className="text-xl font-bold text-gray-900">Estado del procesamiento</h2>
          {isProcessingExpanded ? (
            <ChevronUpIcon className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-gray-500" />
          )}
        </button>

        {isProcessingExpanded && (
          <div className="mt-4 space-y-4">
            {/* Processing Status */}
            <div className="grid grid-cols-2 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Features extraídas</p>
                <p className={`font-semibold ${article.features_extracted ? 'text-green-600' : 'text-red-600'}`}>
                  {article.features_extracted ? 'Sí' : 'No'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">ID del artículo</p>
                <p className="font-mono text-sm text-gray-900">{article.id}</p>
              </div>
            </div>

            {/* Processing Error */}
            {article.processing_error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="font-bold text-red-900 mb-2">Error de procesamiento</h3>
                <p className="text-sm text-red-700">{article.processing_error}</p>
              </div>
            )}

            {/* Timestamps */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              {article.created_at && (
                <div>
                  <p className="text-gray-500 font-medium">Creado</p>
                  <p className="text-gray-900">
                    {new Date(article.created_at).toLocaleString('es-CO')}
                  </p>
                </div>
              )}
              {article.updated_at && (
                <div>
                  <p className="text-gray-500 font-medium">Actualizado</p>
                  <p className="text-gray-900">
                    {new Date(article.updated_at).toLocaleString('es-CO')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* DEBUG: All ML Features - Self-contained component, safe to remove later */}
      <ArticleDebugPanel article={article} />
    </div>
  )
}
