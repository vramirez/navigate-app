from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RecommendationViewSet)
router.register(r'feedback', views.RecommendationFeedbackViewSet)
router.register(r'templates', views.RecommendationTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]