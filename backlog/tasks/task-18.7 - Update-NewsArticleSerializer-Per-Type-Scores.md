---
id: task-18.7
title: 'Update NewsArticleSerializer to Include Per-Type Scores'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - backend
  - api
dependencies: [task-18.1, task-18.5]
parent: task-18
priority: high
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update NewsArticleSerializer to include user_relevance score (from queryset annotation) and remove business_relevance_score field. Add optional type_scores field showing relevance breakdown for all business types (useful for debugging).
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `backend/news/serializers.py`
**Class**: `NewsArticleSerializer`

### Current Implementation

Find the NewsArticleSerializer class (around line 50-120) and update it:

**Remove**: `business_relevance_score` from fields list

**Add**: New fields for per-type relevance

```python
class NewsArticleSerializer(serializers.ModelSerializer):
    """Serializer for NewsArticle with business type relevance"""

    # User's relevance score (from queryset annotation)
    user_relevance = serializers.FloatField(read_only=True, required=False)

    # Optional: All type scores for debugging/admin view
    type_scores = serializers.SerializerMethodField()

    # Source info
    news_source_name = serializers.CharField(source='news_source.name', read_only=True)
    news_source_url = serializers.URLField(source='news_source.base_url', read_only=True)

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'content', 'summary',
            'url', 'image_url', 'published_date',

            # Source info
            'news_source', 'news_source_name', 'news_source_url',

            # ML scores (NEW: user_relevance replaces business_relevance_score)
            'user_relevance',  # NEW: For current user's business type
            'business_suitability_score',

            # Event data
            'is_event', 'event_title', 'event_description',
            'event_start_datetime', 'event_end_datetime',
            'event_location', 'event_scale',

            # Geographic data
            'city', 'neighborhood', 'latitude', 'longitude',

            # Category
            'category', 'sentiment',

            # Metadata
            'processing_status', 'error_message',
            'created_at', 'updated_at',

            # Debug field (optional)
            'type_scores'  # NEW: For debugging/admin
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'processing_status',
            'business_suitability_score', 'user_relevance', 'type_scores'
        ]

    def get_type_scores(self, obj):
        """
        Return relevance scores for all business types
        Only included if ?include_type_scores=true query parameter
        """
        request = self.context.get('request')
        if not request or request.query_params.get('include_type_scores') != 'true':
            return None

        # Get all relevance scores for this article
        from news.models import ArticleBusinessTypeRelevance

        scores = ArticleBusinessTypeRelevance.objects.filter(
            article=obj
        ).select_related('business_type').order_by('-relevance_score')

        return [{
            'business_type': score.business_type.code,
            'display_name': score.business_type.display_name,
            'relevance_score': score.relevance_score,
            'components': {
                'suitability': score.suitability_component,
                'keyword': score.keyword_component,
                'event_scale': score.event_scale_component,
                'neighborhood': score.neighborhood_component
            },
            'matching_keywords': score.matching_keywords
        } for score in scores]
```

### Update ViewSet to Pass Request Context

**File**: `backend/news/views.py`
**Class**: `NewsArticleViewSet`

Ensure serializer context includes request:
```python
class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news articles"""
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        """Add request to context for type_scores method"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # ... rest of methods
```

## Testing

### Test 1: Basic Article Response

```bash
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User

user = User.objects.first()
client = APIClient()
client.force_authenticate(user=user)

# Get articles for pub type
response = client.get('/api/news/articles/?business_type=pub')
data = response.json()

print(f'Status: {response.status_code}')
print(f'Count: {len(data)}')

if len(data) > 0:
    article = data[0]
    print(f\"\\nFirst article:\")
    print(f\"  Title: {article['title'][:50]}...\")
    print(f\"  User relevance: {article.get('user_relevance', 'N/A')}\")
    print(f\"  Suitability: {article.get('business_suitability_score', 'N/A')}\")
    print(f\"  Has business_relevance_score: {'business_relevance_score' in article}\")
    print(f\"  Type scores: {article.get('type_scores', 'Not included')}\")
"
```

### Test 2: Include Type Scores

```bash
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User

user = User.objects.first()
client = APIClient()
client.force_authenticate(user=user)

# Get articles with type scores
response = client.get('/api/news/articles/?business_type=pub&include_type_scores=true')
data = response.json()

if len(data) > 0:
    article = data[0]
    print(f\"Article: {article['title'][:50]}...\")
    print(f\"\\nType Scores:\")
    for score in article.get('type_scores', []):
        print(f\"  {score['business_type']}: {score['relevance_score']:.2f}\")
        print(f\"    Keywords: {score['matching_keywords']}\")
"
```

### Test 3: Verify Ordering

```bash
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User

user = User.objects.first()
client = APIClient()
client.force_authenticate(user=user)

# Get articles
response = client.get('/api/news/articles/?business_type=pub')
data = response.json()

print('Articles ordered by user_relevance:')
for article in data[:5]:
    print(f\"  {article.get('user_relevance', 0):.2f}: {article['title'][:50]}...\")
"
```

## Acceptance Criteria

- [ ] user_relevance field included in response
- [ ] business_relevance_score field removed from response
- [ ] type_scores only included when ?include_type_scores=true
- [ ] type_scores shows all business types with components
- [ ] type_scores includes matching_keywords array
- [ ] Serializer handles missing user_relevance gracefully
- [ ] No N+1 queries (use select_related/prefetch_related)
- [ ] All existing fields still present
- [ ] Response ordered by user_relevance DESC

## Notes

- Requires task-18.1 (remove business_relevance_score field)
- Requires task-18.5 (user_relevance annotation in queryset)
- type_scores optional to avoid performance impact
- Future: Cache type_scores in article for faster access
