---
id: task-18.9
title: 'Update Frontend newsApi.js for Business Type Filtering'
status: Done
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - frontend
  - api
dependencies: [task-18.5, task-18.8]
parent: task-18
priority: high
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update newsApi.js to always pass business_type parameter when fetching articles. Remove days_ago parameter. Use businessTypeCode from AuthContext. Update response handling for user_relevance field.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `frontend/src/services/newsApi.js`

### Current Implementation (lines ~100-130)

**OLD Code**:
```javascript
export const fetchArticles = async (options = {}) => {
  try {
    const response = await api.get('/news/articles/', {
      params: {
        days_ago: options.daysAgo ?? 30,
        min_relevance: options.minRelevance ?? 0.3,
        exclude_past_events: options.excludePastEvents ?? true,
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching articles:', error);
    throw error;
  }
};
```

**NEW Code**:
```javascript
/**
 * Fetch articles filtered by business type
 * @param {Object} options
 * @param {string} options.businessType - REQUIRED: Business type code (pub, restaurant, etc.)
 * @param {number} [options.minRelevance] - Optional: Override business type default threshold
 * @param {boolean} [options.excludePastEvents=true] - Filter out events older than 7 days
 * @param {boolean} [options.includeTypeScores=false] - Include relevance breakdown for all types
 * @returns {Promise<Array>} Array of articles with user_relevance score
 */
export const fetchArticles = async (options = {}) => {
  try {
    // Validate required parameter
    if (!options.businessType) {
      throw new Error('businessType is required for fetchArticles');
    }

    const params = {
      business_type: options.businessType,
      exclude_past_events: options.excludePastEvents ?? true,
    };

    // Optional parameters
    if (options.minRelevance !== undefined) {
      params.min_relevance = options.minRelevance;
    }

    if (options.includeTypeScores) {
      params.include_type_scores = 'true';
    }

    const response = await api.get('/news/articles/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching articles:', error);
    throw error;
  }
};
```

### Add Business Type Fetcher

Add new function to fetch available business types:
```javascript
/**
 * Fetch all available business types
 * @param {boolean} [activeOnly=true] - Only return active business types
 * @returns {Promise<Array>} Array of business types
 */
export const fetchBusinessTypes = async (activeOnly = true) => {
  try {
    const params = activeOnly ? { is_active: 'true' } : {};
    const response = await api.get('/businesses/business-types/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching business types:', error);
    throw error;
  }
};

/**
 * Fetch statistics for a business type
 * @param {number} businessTypeId - Business type ID
 * @returns {Promise<Object>} Statistics object
 */
export const fetchBusinessTypeStatistics = async (businessTypeId) => {
  try {
    const response = await api.get(`/businesses/business-types/${businessTypeId}/statistics/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching business type statistics:', error);
    throw error;
  }
};
```

### Update Other API Functions

Update any other functions that reference business_relevance_score:

```javascript
// OLD
article.business_relevance_score >= threshold

// NEW
article.user_relevance >= threshold
```

## Testing

### Test 1: Fetch Articles with Business Type

Create test file: `frontend/src/services/newsApi.test.js`
```javascript
import { fetchArticles, fetchBusinessTypes } from './newsApi';

describe('newsApi', () => {
  it('requires businessType parameter', async () => {
    await expect(fetchArticles({})).rejects.toThrow('businessType is required');
  });

  it('fetches articles for business type', async () => {
    const articles = await fetchArticles({ businessType: 'pub' });
    expect(Array.isArray(articles)).toBe(true);
  });

  it('fetches business types', async () => {
    const types = await fetchBusinessTypes();
    expect(Array.isArray(types)).toBe(true);
    expect(types.length).toBeGreaterThan(0);
  });
});
```

### Test 2: Manual Browser Test

Create test page: `frontend/src/pages/ApiTest.jsx`
```jsx
import { useState } from 'react';
import { fetchArticles, fetchBusinessTypes } from '../services/newsApi';

export default function ApiTest() {
  const [articles, setArticles] = useState([]);
  const [types, setTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('pub');
  const [loading, setLoading] = useState(false);

  const loadTypes = async () => {
    const data = await fetchBusinessTypes();
    setTypes(data);
  };

  const loadArticles = async () => {
    setLoading(true);
    try {
      const data = await fetchArticles({
        businessType: selectedType,
        includeTypeScores: true
      });
      setArticles(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>News API Test</h1>

      <section>
        <h2>Business Types</h2>
        <button onClick={loadTypes}>Load Types</button>
        <ul>
          {types.map(type => (
            <li key={type.code}>
              {type.display_name} ({type.code}) - {type.business_count} businesses
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Articles</h2>
        <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)}>
          <option value="pub">Pub</option>
          <option value="restaurant">Restaurant</option>
          <option value="coffee_shop">Coffee Shop</option>
          <option value="bookstore">Bookstore</option>
        </select>
        <button onClick={loadArticles} disabled={loading}>
          {loading ? 'Loading...' : 'Load Articles'}
        </button>

        <p>Found {articles.length} articles</p>
        <ul>
          {articles.slice(0, 5).map(article => (
            <li key={article.id}>
              <strong>{article.title}</strong>
              <br />
              Relevance: {article.user_relevance?.toFixed(2) ?? 'N/A'}
              {article.type_scores && (
                <details>
                  <summary>Type Scores</summary>
                  <pre>{JSON.stringify(article.type_scores, null, 2)}</pre>
                </details>
              )}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
```

### Test 3: Console Test

```javascript
// In browser console
import { fetchArticles } from './services/newsApi';

// Test error handling
fetchArticles({}).catch(console.error); // Should throw error

// Test valid call
fetchArticles({ businessType: 'pub' }).then(console.log);

// Test with options
fetchArticles({
  businessType: 'pub',
  minRelevance: 0.6,
  includeTypeScores: true
}).then(console.log);
```

## Acceptance Criteria

- [x] fetchArticles requires businessType parameter (getDashboardArticles)
- [x] fetchArticles throws error if businessType missing
- [x] days_ago parameter removed (uses exclude_past_events)
- [x] business_type sent to backend
- [x] min_relevance is optional
- [x] include_type_scores parameter works
- [x] Response includes user_relevance field
- [x] fetchBusinessTypes function added (getBusinessTypes)
- [x] fetchBusinessTypeStatistics function added (getBusinessTypeStatistics)
- [x] All references to business_relevance_score updated
- [x] Error handling preserved

## Progress Log

### 2025-10-29 - Implementation Found Complete ✅

**Status**: Task already fully implemented prior to verification

**Implementation Details**:
- Function `getDashboardArticles()` in [newsApi.js:105-149](frontend/src/services/newsApi.js#L105-L149) implements all requirements
- Function `getBusinessTypes()` in [newsApi.js:156-165](frontend/src/services/newsApi.js#L156-L165)
- Function `getBusinessTypeStatistics()` in [newsApi.js:173-181](frontend/src/services/newsApi.js#L173-L181)

**Key Features**:
- Validates businessType parameter is required (throws error if missing)
- Sends business_type to backend API
- No days_ago parameter (uses exclude_past_events instead)
- Supports optional minRelevance override
- Supports includeTypeScores for detailed breakdown
- Includes comprehensive console logging for debugging
- Returns user_relevance from backend response

**Verification**:
- All 11 acceptance criteria verified as complete
- Implementation exceeds task specifications
- Ready for use by Dashboard component (task-18.10)

## Notes

- Requires task-18.5 (backend filtering) complete ✅
- Requires task-18.8 (AuthContext) for businessType value ✅
- Breaking change: All components using fetchArticles must pass businessType
- Components should get businessType from useAuth() hook
