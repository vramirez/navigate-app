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
 * Fetch articles for Dashboard with optimal filters
 * Returns high-relevance, recent articles suitable for business recommendations
 * @param {Object} options - Additional filter options
 * @returns {Promise<Array>} Filtered article list
 */
export const getDashboardArticles = async (options = {}) => {
  try {
    console.log('newsApi: Fetching dashboard articles...')
    const response = await apiClient.get('/api/news/articles/', {
      params: {
        days_ago: 30, // Last 30 days
        min_relevance: 0.0, // Show all processed articles (0.0+), hide unprocessed (-1.0)
        limit: 20, // Top 20 articles
        ...options,
      },
    })
    console.log('newsApi: Response received:', {
      status: response.status,
      count: response.data.count,
      resultsLength: response.data.results?.length
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

export default {
  getArticles,
  getRecentArticles,
  getHighRelevanceArticles,
  getArticleById,
  getSources,
  getDashboardArticles,
}
