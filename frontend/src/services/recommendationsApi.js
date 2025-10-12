/**
 * Recommendations API Service
 *
 * Handles all API calls related to business recommendations
 */

import apiClient from './api'

/**
 * Fetch all recommendations with optional filters
 * @param {Object} params - Query parameters
 * @param {number} params.business_id - Filter by business ID
 * @param {string} params.category - Filter by category
 * @param {string} params.priority - Filter by priority
 * @param {string} params.status - Filter by status
 * @param {number} params.min_confidence - Minimum confidence score
 * @returns {Promise<Object>} Paginated recommendation list
 */
export const getRecommendations = async (params = {}) => {
  try {
    const response = await apiClient.get('/api/recommendations/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching recommendations:', error)
    throw error
  }
}

/**
 * Fetch recommendations for a specific business
 * @param {number} businessId - Business ID
 * @returns {Promise<Array>} List of recommendations for the business
 */
export const getRecommendationsByBusiness = async (businessId) => {
  try {
    const response = await apiClient.get('/api/recommendations/by_business/', {
      params: { business_id: businessId },
    })
    return response.data
  } catch (error) {
    console.error(`Error fetching recommendations for business ${businessId}:`, error)
    throw error
  }
}

/**
 * Fetch urgent recommendations
 * @returns {Promise<Array>} List of urgent recommendations
 */
export const getUrgentRecommendations = async () => {
  try {
    const response = await apiClient.get('/api/recommendations/urgent/')
    return response.data
  } catch (error) {
    console.error('Error fetching urgent recommendations:', error)
    throw error
  }
}

/**
 * Fetch high impact recommendations
 * @returns {Promise<Array>} List of high impact recommendations
 */
export const getHighImpactRecommendations = async () => {
  try {
    const response = await apiClient.get('/api/recommendations/high_impact/')
    return response.data
  } catch (error) {
    console.error('Error fetching high impact recommendations:', error)
    throw error
  }
}

/**
 * Mark a recommendation as read
 * @param {number} recommendationId - Recommendation ID
 * @returns {Promise<Object>} Updated recommendation
 */
export const markRecommendationAsRead = async (recommendationId) => {
  try {
    const response = await apiClient.post(`/api/recommendations/${recommendationId}/mark_read/`)
    return response.data
  } catch (error) {
    console.error(`Error marking recommendation ${recommendationId} as read:`, error)
    throw error
  }
}

/**
 * Archive a recommendation
 * @param {number} recommendationId - Recommendation ID
 * @returns {Promise<Object>} Updated recommendation
 */
export const archiveRecommendation = async (recommendationId) => {
  try {
    const response = await apiClient.post(`/api/recommendations/${recommendationId}/archive/`)
    return response.data
  } catch (error) {
    console.error(`Error archiving recommendation ${recommendationId}:`, error)
    throw error
  }
}

/**
 * Get recommendation statistics
 * @returns {Promise<Object>} Recommendation statistics
 */
export const getRecommendationStats = async () => {
  try {
    const response = await apiClient.get('/api/recommendations/stats/')
    return response.data
  } catch (error) {
    console.error('Error fetching recommendation stats:', error)
    throw error
  }
}

/**
 * Fetch recommendations grouped by their source article
 * Returns a map of article_id -> recommendations[]
 * @param {number} businessId - Optional business ID filter
 * @returns {Promise<Object>} Map of article IDs to recommendations
 */
export const getRecommendationsByArticle = async (businessId = null) => {
  try {
    const params = {}
    if (businessId) {
      params.business_id = businessId
    }

    const response = await apiClient.get('/api/recommendations/', { params })
    const recommendations = response.data.results || response.data

    // Group recommendations by source article ID
    // Backend stores article ID in 'object_id' field (GenericForeignKey)
    const recommendationsByArticle = {}

    recommendations.forEach((rec) => {
      // Check if recommendation is linked to a news article
      if (rec.content_type_name === 'newsarticle') {
        const articleId = rec.object_id
        if (!recommendationsByArticle[articleId]) {
          recommendationsByArticle[articleId] = []
        }
        recommendationsByArticle[articleId].push(rec)
      }
    })

    return recommendationsByArticle
  } catch (error) {
    console.error('Error fetching recommendations by article:', error)
    throw error
  }
}

export default {
  getRecommendations,
  getRecommendationsByBusiness,
  getUrgentRecommendations,
  getHighImpactRecommendations,
  markRecommendationAsRead,
  archiveRecommendation,
  getRecommendationStats,
  getRecommendationsByArticle,
}
