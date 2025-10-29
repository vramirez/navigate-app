from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Separate routers to avoid conflicts
business_router = DefaultRouter()
business_router.register(r'', views.BusinessViewSet, basename='business')

business_type_router = DefaultRouter()
business_type_router.register(r'', views.BusinessTypeViewSet, basename='businesstype')

urlpatterns = [
    path('business-types/', include(business_type_router.urls)),  # /api/businesses/business-types/
    path('keywords/', views.BusinessKeywordsListCreateView.as_view(), name='business-keywords'),
    path('auth/profile/', views.user_profile, name='user-profile'),
    path('', include(business_router.urls)),  # /api/businesses/ - keep this last to not catch everything
]