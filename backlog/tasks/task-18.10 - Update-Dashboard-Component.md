---
id: task-18.10
title: 'Update Dashboard Component for Business Type Context'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - frontend
  - react
dependencies: [task-18.8, task-18.9]
parent: task-18
priority: high
estimated_hours: 3
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update Dashboard.jsx to use businessTypeCode from AuthContext when fetching articles. Remove days_ago filter controls. Update article display to show user_relevance instead of business_relevance_score. Add business type indicator in header.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `frontend/src/pages/Dashboard.jsx`

### Update Imports and Hooks

```jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchArticles } from '../services/newsApi';
import ArticleCard from '../components/ArticleCard';
import FilterBar from '../components/FilterBar';

export default function Dashboard() {
  const { businessTypeCode, business, loading: authLoading, isAuthenticated } = useAuth();

  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filter state (removed: daysAgo)
  const [minRelevance, setMinRelevance] = useState(null); // null = use business type default
  const [excludePastEvents, setExcludePastEvents] = useState(true);

  // Load articles when business type is available
  useEffect(() => {
    if (businessTypeCode && !authLoading) {
      loadArticles();
    }
  }, [businessTypeCode, minRelevance, excludePastEvents, authLoading]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchArticles({
        businessType: businessTypeCode,
        minRelevance: minRelevance,
        excludePastEvents: excludePastEvents
      });

      setArticles(data);
    } catch (err) {
      console.error('Failed to load articles:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Show loading state while auth loads
  if (authLoading) {
    return (
      <div className="dashboard-loading">
        <p>Loading your profile...</p>
      </div>
    );
  }

  // Show message if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="dashboard-error">
        <h2>Please log in to view your dashboard</h2>
        <a href="/login">Go to Login</a>
      </div>
    );
  }

  // Show message if no business
  if (!business) {
    return (
      <div className="dashboard-error">
        <h2>No business found for your account</h2>
        <p>Please contact support to set up your business profile.</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>News Dashboard</h1>
        <div className="business-info">
          <span className="business-name">{business.name}</span>
          <span className="business-type">
            <i className={`fa ${business.business_type_details?.icon || 'fa-building'}`} />
            {business.business_type_details?.display_name}
          </span>
        </div>
      </header>

      <FilterBar
        minRelevance={minRelevance}
        onMinRelevanceChange={setMinRelevance}
        excludePastEvents={excludePastEvents}
        onExcludePastEventsChange={setExcludePastEvents}
        businessType={business.business_type_details}
      />

      {error && (
        <div className="error-message">
          <p>Error loading articles: {error}</p>
          <button onClick={loadArticles}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="articles-loading">
          <p>Loading articles...</p>
        </div>
      ) : (
        <div className="articles-container">
          {articles.length === 0 ? (
            <div className="no-articles">
              <p>No articles found matching your criteria.</p>
              <p>Try adjusting the filters or check back later.</p>
            </div>
          ) : (
            <>
              <div className="articles-count">
                Found {articles.length} relevant article{articles.length !== 1 ? 's' : ''}
              </div>
              <div className="articles-grid">
                {articles.map(article => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                    businessType={business.business_type_details}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
```

### Update FilterBar Component

**File**: `frontend/src/components/FilterBar.jsx`

```jsx
export default function FilterBar({
  minRelevance,
  onMinRelevanceChange,
  excludePastEvents,
  onExcludePastEventsChange,
  businessType
}) {
  return (
    <div className="filter-bar">
      <div className="filter-group">
        <label htmlFor="min-relevance">
          Minimum Relevance
          {businessType && (
            <span className="default-value">
              (default: {businessType.min_relevance_threshold || 0.5})
            </span>
          )}
        </label>
        <select
          id="min-relevance"
          value={minRelevance ?? ''}
          onChange={(e) => onMinRelevanceChange(e.target.value ? parseFloat(e.target.value) : null)}
        >
          <option value="">Use default</option>
          <option value="0.3">0.3 - Low</option>
          <option value="0.5">0.5 - Medium</option>
          <option value="0.7">0.7 - High</option>
          <option value="0.9">0.9 - Very High</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="exclude-past">
          <input
            type="checkbox"
            id="exclude-past"
            checked={excludePastEvents}
            onChange={(e) => onExcludePastEventsChange(e.target.checked)}
          />
          Only show events from last 7 days or upcoming
        </label>
      </div>

      <div className="filter-info">
        <p>
          Showing articles relevant to <strong>{businessType?.display_name || 'your business'}</strong>
        </p>
      </div>
    </div>
  );
}
```

### Update ArticleCard Component

**File**: `frontend/src/components/ArticleCard.jsx`

Update to use user_relevance instead of business_relevance_score:

```jsx
export default function ArticleCard({ article, businessType }) {
  const relevanceScore = article.user_relevance ?? article.business_relevance_score ?? 0;
  const relevanceLevel = relevanceScore >= 0.7 ? 'high' : relevanceScore >= 0.5 ? 'medium' : 'low';

  return (
    <div className={`article-card relevance-${relevanceLevel}`}>
      <div className="article-header">
        <h3>{article.title}</h3>
        <div className="relevance-badge" title="Relevance score">
          {relevanceScore.toFixed(2)}
        </div>
      </div>

      {article.image_url && (
        <img src={article.image_url} alt={article.title} className="article-image" />
      )}

      <div className="article-content">
        <p>{article.summary || article.content?.substring(0, 200) + '...'}</p>
      </div>

      <div className="article-meta">
        {article.is_event && article.event_start_datetime && (
          <div className="event-info">
            <i className="fa fa-calendar" />
            {new Date(article.event_start_datetime).toLocaleDateString()}
          </div>
        )}

        {article.neighborhood && (
          <div className="location-info">
            <i className="fa fa-map-marker" />
            {article.neighborhood}
          </div>
        )}

        <div className="source-info">
          <i className="fa fa-newspaper" />
          {article.news_source_name}
        </div>
      </div>

      <div className="article-actions">
        <a href={article.url} target="_blank" rel="noopener noreferrer" className="btn-primary">
          Read Full Article
        </a>
      </div>
    </div>
  );
}
```

## Testing

### Manual Browser Test

1. Start frontend: `npm run dev`
2. Navigate to http://localhost:3001/dashboard
3. Verify:
   - Business name and type displayed in header
   - Articles load automatically
   - Filter controls work (min relevance, exclude past)
   - Article cards show user_relevance score
   - No errors in console

### Test Different Business Types

```bash
# In backend, change user's business type
docker exec docker-backend-1 python manage.py shell

from django.contrib.auth.models import User
from businesses.models import Business, BusinessType

user = User.objects.first()
business = user.businesses.first()

# Change to restaurant
restaurant_type = BusinessType.objects.get(code='restaurant')
business.business_type = restaurant_type
business.save()

print(f"Changed {business.name} to {restaurant_type.display_name}")
```

Reload dashboard and verify different articles appear.

## Acceptance Criteria

- [ ] Dashboard uses businessTypeCode from AuthContext
- [ ] Articles load automatically when businessTypeCode available
- [ ] Business name and type displayed in header
- [ ] Business type icon displayed
- [ ] Filter bar shows default relevance threshold
- [ ] Min relevance filter works
- [ ] Exclude past events filter works (7-day window)
- [ ] days_ago filter removed
- [ ] Article cards show user_relevance score
- [ ] Relevance badge color-coded (high/medium/low)
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Message shown if no business
- [ ] Message shown if not authenticated

## Notes

- Requires task-18.8 (AuthContext) and task-18.9 (newsApi updates)
- Users see only articles relevant to THEIR business type
- Future: Support multiple businesses per user (business switcher)
- Future: Save filter preferences to localStorage
