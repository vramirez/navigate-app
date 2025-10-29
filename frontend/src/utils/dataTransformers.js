/**
 * Data Transformation Utilities
 *
 * Transforms API data structures to match frontend component expectations
 */

import { formatDistanceToNow, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'

/**
 * Map event type from backend to frontend category
 * @param {string} eventType - Backend event type
 * @returns {string} Frontend category
 */
const mapEventTypeToCategory = (eventType) => {
  const mapping = {
    'sports': 'eventos',
    'cultural': 'eventos',
    'food': 'gastronomia',
    'festival': 'eventos',
    'entertainment': 'eventos',
    'business': 'economia',
    'politics': 'comunidad',
    'weather': 'clima-alertas',
  }
  return mapping[eventType?.toLowerCase()] || 'comunidad'
}

/**
 * Format published date to relative time in Spanish
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted relative time (e.g., "Hace 3 horas")
 */
export const formatRelativeTime = (dateString) => {
  try {
    const date = parseISO(dateString)
    return `Hace ${formatDistanceToNow(date, { locale: es })}`
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Fecha desconocida'
  }
}

/**
 * Transform backend article to Dashboard news format
 * @param {Object} article - Backend NewsArticle object
 * @returns {Object} Transformed news object
 */
export const transformArticleToNews = (article) => {
  return {
    id: article.id,
    title: article.title,
    source: article.source_name || 'Fuente desconocida',
    publishedAt: formatRelativeTime(article.published_date),
    category: mapEventTypeToCategory(article.event_type),
    subcategory: article.event_type || 'general',
    content: article.content || '',
    firstParagraph: article.first_paragraph || article.content || '',
    url: article.url,
    // task-18.10: Use user_relevance (per-type score) with fallback to old field
    relevanceScore: article.user_relevance ?? article.business_relevance_score ?? 0,
    keywords: article.extracted_keywords || [],
    recommendations: [], // Will be populated by joining with recommendations
  }
}

/**
 * Map backend priority to frontend priority
 * @param {string} priority - Backend priority (low, medium, high, urgent)
 * @returns {string} Frontend priority
 */
const mapPriority = (priority) => {
  const mapping = {
    'urgent': 'urgent',
    'high': 'high',
    'medium': 'medium',
    'low': 'low',
  }
  return mapping[priority?.toLowerCase()] || 'medium'
}

/**
 * Transform backend recommendation to Dashboard recommendation format
 * @param {Object} recommendation - Backend Recommendation object
 * @returns {Object} Transformed recommendation object
 */
export const transformRecommendation = (recommendation) => {
  return {
    id: `rec${recommendation.id}`,
    title: recommendation.title,
    priority: mapPriority(recommendation.priority),
    description: recommendation.description,
    estimatedHours: recommendation.estimated_duration_hours || 0,
    category: recommendation.category,
    confidenceScore: recommendation.confidence_score,
    impactScore: recommendation.impact_score,
    effortScore: recommendation.effort_score,
  }
}

/**
 * Join articles with their recommendations
 * @param {Array} articles - List of articles
 * @param {Object} recommendationsByArticle - Map of article_id -> recommendations[]
 * @returns {Array} Articles with nested recommendations
 */
export const joinArticlesWithRecommendations = (articles, recommendationsByArticle) => {
  return articles.map((article) => {
    const articleRecs = recommendationsByArticle[article.id] || []
    return {
      ...transformArticleToNews(article),
      recommendations: articleRecs.map(transformRecommendation),
    }
  })
}

/**
 * Sort articles by relevance score (descending)
 * @param {Array} articles - List of articles
 * @returns {Array} Sorted articles
 */
export const sortByRelevance = (articles) => {
  return [...articles].sort((a, b) => {
    const scoreA = a.relevanceScore || 0
    const scoreB = b.relevanceScore || 0
    return scoreB - scoreA
  })
}

export default {
  transformArticleToNews,
  transformRecommendation,
  joinArticlesWithRecommendations,
  formatRelativeTime,
  sortByRelevance,
}
