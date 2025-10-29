---
id: task-18.4
title: 'Create User Profile API Endpoint'
status: Review
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - backend
  - api
dependencies: []
parent: task-18
priority: high
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create /api/auth/profile/ endpoint that returns authenticated user's business information including business_type. Frontend needs this to determine which business type filter to apply when fetching articles.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `backend/businesses/serializers.py`

Add BusinessTypeSerializer:
```python
class BusinessTypeSerializer(serializers.ModelSerializer):
    """Serializer for BusinessType"""
    class Meta:
        model = BusinessType
        fields = ['code', 'display_name', 'display_name_es', 'icon']
```

Update BusinessSerializer to include business_type details:
```python
class BusinessSerializer(serializers.ModelSerializer):
    business_type_details = BusinessTypeSerializer(source='business_type', read_only=True)

    class Meta:
        model = Business
        fields = [
            'id', 'name', 'business_type', 'business_type_details',
            'city', 'address', 'neighborhood', 'latitude', 'longitude',
            'description', 'phone', 'email', 'website',
            'target_audience', 'is_active', 'created_at'
        ]
```

**File**: `backend/businesses/views.py`

Add new endpoint:
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get authenticated user's profile including their business

    Returns:
        {
            'user': { 'id', 'username', 'email' },
            'business': { 'id', 'name', 'business_type', 'business_type_details', ... },
            'business_type_code': 'pub'  # Quick access to type code
        }
    """
    user = request.user

    # Get user's business (assuming one business per user for now)
    try:
        business = Business.objects.select_related('business_type').get(
            owner=user,
            is_active=True
        )
        business_data = BusinessSerializer(business).data
        business_type_code = business.business_type.code
    except Business.DoesNotExist:
        business_data = None
        business_type_code = None

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'business': business_data,
        'business_type_code': business_type_code
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
router.register(r'admin-users', views.AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('keywords/', views.BusinessKeywordsListCreateView.as_view(), name='business-keywords'),
    path('auth/profile/', views.user_profile, name='user-profile'),  # NEW
]
```

## Testing

### Manual Test

```bash
# Test with authenticated user
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Get test user
user = User.objects.first()
print(f'Testing with user: {user.username}')

# Create API client
client = APIClient()
client.force_authenticate(user=user)

# Call endpoint
response = client.get('/api/businesses/auth/profile/')
print(f'Status: {response.status_code}')
print(f'Data: {response.json()}')
"
```

### cURL Test

```bash
# First get auth token
TOKEN=$(docker exec docker-backend-1 python manage.py shell -c "
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
user = User.objects.first()
token, _ = Token.objects.get_or_create(user=user)
print(token.key)
")

# Call profile endpoint
curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/businesses/auth/profile/
```

## Acceptance Criteria

- [ ] Endpoint returns 200 for authenticated users
- [ ] Response includes user data (id, username, email)
- [ ] Response includes business data with business_type_details nested
- [ ] Response includes business_type_code for quick access
- [ ] Returns appropriate error for unauthenticated requests
- [ ] Handles users without businesses gracefully (business: null)
- [ ] business_type_details includes code, display_name, icon

## Notes

- Assumes one business per user (future: handle multiple businesses)
- Frontend will use business_type_code to filter articles
- select_related used for performance (avoid N+1 queries)

## Progress Log

### 2025-10-29 - Implementation Found and Tests Added

**Status**: Endpoint was already fully implemented ✅

**Findings**:
- `/api/businesses/auth/profile/` endpoint already exists in `backend/businesses/views.py:73-110`
- `user_profile` function-based view correctly implemented with:
  - IsAuthenticated permission
  - Returns user data (id, username, email, first_name, last_name)
  - Returns business data with business_type_details nested
  - Returns business_type_code for quick access
  - Handles users without businesses gracefully (returns null)
  - Uses select_related('business_type') for performance
- URL already registered in `backend/businesses/urls.py:15`
- BusinessTypeSerializer already exists in `backend/businesses/serializers.py:6-10`
- BusinessSerializer already includes business_type_details field

**Work Completed**:
- Created `backend/businesses/tests/` directory
- Added `test_profile_api.py` with comprehensive pytest tests:
  - test_authenticated_user_with_business ✅
  - test_authenticated_user_without_business ✅
  - test_unauthenticated_request ✅
  - test_inactive_business_not_returned ✅
  - test_multiple_businesses_returns_active_one ✅
  - test_response_structure ✅
- All 6 tests pass successfully

**Files Modified**:
- Created: `backend/businesses/tests/__init__.py`
- Created: `backend/businesses/tests/test_profile_api.py` (208 lines)

**Acceptance Criteria Status**:
- [x] Endpoint returns 200 for authenticated users
- [x] Response includes user data (id, username, email)
- [x] Response includes business data with business_type_details nested
- [x] Response includes business_type_code for quick access
- [x] Returns appropriate error for unauthenticated requests (403 Forbidden)
- [x] Handles users without businesses gracefully (business: null)
- [x] business_type_details includes code, display_name, icon

**Next Steps**:
- Task ready for review
- Frontend tasks (18.9, 18.10) can now proceed once this is merged
