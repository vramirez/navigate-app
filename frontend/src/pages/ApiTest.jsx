import React, { useState } from 'react'
import axios from 'axios'

export default function ApiTest() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const testAPI = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.get('http://localhost:8000/api/news/articles/', {
        params: {
          days_ago: 30,
          min_relevance: 0.6,
          limit: 5,
        },
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        timeout: 10000,
      })

      setResult({
        status: response.status,
        count: response.data.count,
        resultsLength: response.data.results?.length || 0,
        firstArticle: response.data.results?.[0]?.title || 'N/A',
        fullData: response.data,
      })
    } catch (err) {
      setError({
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        hasResponse: !!err.response,
        hasRequest: !!err.request,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">API Connection Test</h1>

      <button
        onClick={testAPI}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>

      {result && (
        <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
          <h2 className="text-xl font-bold text-green-800 mb-4">✓ Success!</h2>
          <pre className="text-sm overflow-auto max-h-96 bg-white p-4 rounded border">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      {error && (
        <div className="mt-6 p-6 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-xl font-bold text-red-800 mb-4">✗ Error!</h2>
          <pre className="text-sm overflow-auto max-h-96 bg-white p-4 rounded border">
            {JSON.stringify(error, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
