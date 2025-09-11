from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'articles', views.NewsArticleViewSet)
router.register(r'sources', views.NewsSourceViewSet)
router.register(r'social', views.SocialMediaPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('manual/', views.ManualNewsEntryListCreateView.as_view(), name='manual-news'),
]