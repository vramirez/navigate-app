---
id: task-18.6
title: 'Create BusinessType ViewSet and Serializers'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - backend
  - api
dependencies: []
parent: task-18
priority: medium
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create public read-only API endpoint for BusinessType list. Allows frontend to fetch available business types for display purposes (e.g., showing icons, display names). Admin write access for future type management.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `backend/businesses/serializers.py`

Add DetailedBusinessTypeSerializer:
```python
class BusinessTypeSerializer(serializers.ModelSerializer):
    """Basic BusinessType serializer for nested relationships"""
    class Meta:
        model = BusinessType
        fields = ['code', 'display_name', 'display_name_es', 'icon']


class DetailedBusinessTypeSerializer(serializers.ModelSerializer):
    """Full BusinessType serializer with configuration"""
    business_count = serializers.IntegerField(read_only=True)
    keyword_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = BusinessType
        fields = [
            'id', 'code', 'display_name', 'display_name_es',
            'description', 'icon',
            'suitability_weight', 'keyword_weight',
            'event_scale_weight', 'neighborhood_weight',
            'min_relevance_threshold', 'min_suitability_threshold',
            'is_active', 'created_at', 'updated_at',
            'business_count', 'keyword_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
```

**File**: `backend/businesses/views.py`

Add BusinessTypeViewSet:
```python
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import BusinessType
from .serializers import DetailedBusinessTypeSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read for anyone, write for admins only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class BusinessTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BusinessType
    - Public read access (GET)
    - Admin write access (POST, PUT, PATCH, DELETE)
    """
    serializer_class = DetailedBusinessTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = BusinessType.objects.annotate(
            business_count=Count('businesses', distinct=True),
            keyword_count=Count('keywords', distinct=True)
        )

        # Filter by is_active if specified
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('display_name')

    @action(detail=True, methods=['get'])
    def keywords(self, request, pk=None):
        """Get keywords for a specific business type"""
        business_type = self.get_object()
        keywords = business_type.keywords.filter(is_active=True)

        data = [{
            'keyword': kw.keyword,
            'weight': kw.weight,
            'category': kw.category
        } for kw in keywords]

        return Response(data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a business type"""
        from news.models import ArticleBusinessTypeRelevance

        business_type = self.get_object()

        # Count articles by relevance ranges
        article_stats = ArticleBusinessTypeRelevance.objects.filter(
            business_type=business_type
        ).aggregate(
            total_articles=Count('article', distinct=True),
            high_relevance=Count('article', filter=Q(relevance_score__gte=0.7), distinct=True),
            medium_relevance=Count('article', filter=Q(relevance_score__gte=0.5, relevance_score__lt=0.7), distinct=True),
            low_relevance=Count('article', filter=Q(relevance_score__lt=0.5), distinct=True)
        )

        return Response({
            'business_type': business_type.code,
            'businesses': business_type.businesses.filter(is_active=True).count(),
            'keywords': business_type.keywords.filter(is_active=True).count(),
            'article_stats': article_stats
        })
```

**File**: `backend/businesses/urls.py`

Update URL patterns:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'businesses', views.BusinessViewSet)
router.register(r'business-types', views.BusinessTypeViewSet, basename='businesstype')  # NEW
router.register(r'admin-users', views.AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('keywords/', views.BusinessKeywordsListCreateView.as_view(), name='business-keywords'),
    path('auth/profile/', views.user_profile, name='user-profile'),
]
```

## Testing

### Test 1: List Business Types

```bash
# Public access (no auth)
curl http://localhost:8000/api/businesses/business-types/

# Should return all 4 business types with counts
```

### Test 2: Get Single Business Type

```bash
# Get pub type details
curl http://localhost:8000/api/businesses/business-types/1/

# Should include weights, thresholds, business_count, keyword_count
```

### Test 3: Get Type Keywords

```bash
# Get keywords for pub type
curl http://localhost:8000/api/businesses/business-types/1/keywords/

# Should return list of active keywords with weights
```

### Test 4: Get Type Statistics

```bash
# Get statistics for pub type
curl http://localhost:8000/api/businesses/business-types/1/statistics/

# Should return article counts by relevance range
```

### Python Test

```bash
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from rest_framework.test import APIClient

client = APIClient()

# Test list
response = client.get('/api/businesses/business-types/')
print(f'Status: {response.status_code}')
print(f'Count: {len(response.json())}')

for bt in response.json():
    print(f\"  {bt['code']}: {bt['display_name']} ({bt['business_count']} businesses)\")

# Test keywords endpoint
response = client.get('/api/businesses/business-types/1/keywords/')
print(f'\\nKeywords: {len(response.json())}')

# Test statistics endpoint
response = client.get('/api/businesses/business-types/1/statistics/')
print(f'\\nStatistics: {response.json()}')
"
```

## Acceptance Criteria

- [ ] GET /api/businesses/business-types/ returns all types
- [ ] Public access allowed (no authentication required)
- [ ] Each type includes business_count and keyword_count
- [ ] Filter by is_active parameter works
- [ ] GET /business-types/{id}/ returns single type details
- [ ] GET /business-types/{id}/keywords/ returns active keywords
- [ ] GET /business-types/{id}/statistics/ returns article stats
- [ ] POST/PUT/DELETE require admin authentication
- [ ] Response includes all weight and threshold fields
- [ ] Types ordered by display_name

## Notes

- Used for frontend to display available types
- Statistics endpoint useful for admin dashboard
- Keywords endpoint useful for debugging/reviewing type configuration
- Future: Frontend admin panel to manage types and keywords
