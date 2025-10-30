from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from businesses.auth_views import login_view, logout_view

def health_check(request):
    """Health check endpoint for Docker and monitoring"""
    return JsonResponse({'status': 'healthy', 'service': 'navigate-api'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/auth/login/', login_view, name='api_login'),
    path('api/auth/logout/', logout_view, name='api_logout'),
    path('api/businesses/', include('businesses.urls')),
    path('api/news/', include('news.urls')),
    path('api/recommendations/', include('recommendations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)