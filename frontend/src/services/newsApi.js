/**
 * News API Service
 *
 * Handles all API calls related to news articles and sources
 */

import apiClient from './api'

/**
 * Fetch all news articles with optional filters
 * @param {Object} params - Query parameters
 * @param {string} params.city - Filter by city
 * @param {string} params.event_type - Filter by event type
 * @param {number} params.days_ago - Filter articles from last N days
 * @param {number} params.min_relevance - Minimum relevance score (0.0-1.0)
 * @param {number} params.limit - Number of articles to fetch
 * @returns {Promise<Object>} Paginated article list
 */
export const getArticles = async (params = {}) => {
  try {
    const response = await apiClient.get('/api/news/articles/', {
      params: {
        ...params,
        // Default to 20 articles if not specified
        limit: params.limit || 20,
      },
    })
    return response.data
  } catch (error) {
    console.error('Error fetching articles:', error)
    throw error
  }
}

/**
 * Fetch recent articles from the last 7 days
 * @returns {Promise<Array>} List of recent articles
 */
export const getRecentArticles = async () => {
  try {
    const response = await apiClient.get('/api/news/articles/recent/')
    return response.data
  } catch (error) {
    console.error('Error fetching recent articles:', error)
    throw error
  }
}

/**
 * Fetch high relevance articles (score > 0.7)
 * @returns {Promise<Array>} List of high relevance articles
 */
export const getHighRelevanceArticles = async () => {
  try {
    const response = await apiClient.get('/api/news/articles/high_relevance/')
    return response.data
  } catch (error) {
    console.error('Error fetching high relevance articles:', error)
    throw error
  }
}

/**
 * Fetch a single article by ID
 * @param {number} articleId - Article ID
 * @returns {Promise<Object>} Article details
 */
export const getArticleById = async (articleId) => {
  try {
    const response = await apiClient.get(`/api/news/articles/${articleId}/`)
    return response.data
  } catch (error) {
    console.error(`Error fetching article ${articleId}:`, error)
    throw error
  }
}

/**
 * Fetch news sources
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Paginated source list
 */
export const getSources = async (params = {}) => {
  try {
    const response = await apiClient.get('/api/news/sources/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching sources:', error)
    throw error
  }
}

/**
 * Fetch articles for Dashboard filtered by business type
 * Returns articles with per-type relevance scoring
 * @param {Object} options - Filter options
 * @param {string} options.businessType - REQUIRED: Business type code (pub, restaurant, coffee_shop, bookstore)
 * @param {number} [options.minRelevance] - Optional: Override business type default relevance threshold
 * @param {boolean} [options.excludePastEvents=true] - Exclude events older than 7 days
 * @param {boolean} [options.includeTypeScores=false] - Include relevance breakdown for all types
 * @param {string} [options.sourceCountry='CO'] - Filter by source country code
 * @param {number} [options.limit=20] - Maximum number of articles to return
 * @returns {Promise<Array>} Filtered article list with user_relevance scores
 */
export const getDashboardArticles = async (options = {}) => {
  try {
    // Validate required parameter
    if (!options.businessType) {
      throw new Error('businessType is required for getDashboardArticles')
    }

    console.log('newsApi: Fetching dashboard articles with options:', options)

    const params = {
      business_type: options.businessType,
      exclude_past_events: options.excludePastEvents ?? true,
      source_country: options.sourceCountry ?? 'CO',
      limit: options.limit ?? 20,
    }

    // Optional parameters
    if (options.minRelevance !== undefined) {
      params.min_relevance = options.minRelevance
    }

    if (options.includeTypeScores) {
      params.include_type_scores = 'true'
    }

    const response = await apiClient.get('/api/news/articles/', { params })

    console.log('newsApi: Response received:', {
      status: response.status,
      count: response.data.count,
      resultsLength: response.data.results?.length,
      filters: params
    })
    return response.data.results || response.data
  } catch (error) {
    console.error('newsApi: Error fetching dashboard articles:', error)
    console.error('newsApi: Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url
    })
    throw error
  }
}

/**
 * Fetch all available business types
 * @param {boolean} [activeOnly=true] - Only return active business types
 * @returns {Promise<Array>} Array of business types with metadata
 */
export const getBusinessTypes = async (activeOnly = true) => {
  try {
    const params = activeOnly ? { is_active: 'true' } : {}
    const response = await apiClient.get('/api/businesses/business-types/', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching business types:', error)
    throw error
  }
}

/**
 * Fetch statistics for a specific business type
 * Returns distribution of article relevance scores for the type
 * @param {string} businessTypeCode - Business type code (pub, restaurant, etc.)
 * @returns {Promise<Object>} Statistics object with score distribution
 */
export const getBusinessTypeStatistics = async (businessTypeCode) => {
  try {
    const response = await apiClient.get(`/api/businesses/business-types/${businessTypeCode}/statistics/`)
    return response.data
  } catch (error) {
    console.error(`Error fetching statistics for business type ${businessTypeCode}:`, error)
    throw error
  }
}

export default {
  getArticles,
  getRecentArticles,
  getHighRelevanceArticles,
  getArticleById,
  getSources,
  getDashboardArticles,
  getBusinessTypes,
  getBusinessTypeStatistics,
}
