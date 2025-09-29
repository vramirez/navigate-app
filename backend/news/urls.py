from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import crawler

router = DefaultRouter()
router.register(r'articles', views.NewsArticleViewSet)
router.register(r'sources', views.NewsSourceViewSet)
router.register(r'social', views.SocialMediaPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('manual/', views.ManualNewsEntryListCreateView.as_view(), name='manual-news'),

    # Crawler management API endpoints
    path('sources/<int:source_id>/discover-rss/', crawler.discover_rss, name='source-discover-rss'),
    path('sources/<int:source_id>/analyze-structure/', crawler.analyze_structure, name='source-analyze-structure'),
    path('sources/<int:source_id>/setup/', crawler.setup_source, name='source-setup'),
    path('sources/<int:source_id>/crawl/', crawler.crawl_source, name='source-crawl'),
    path('sources/<int:source_id>/crawl-history/', crawler.crawl_history, name='source-crawl-history'),
    path('sources/<int:source_id>/recommendations/', crawler.source_recommendations, name='source-recommendations'),

    # System-wide crawler endpoints
    path('crawler/bulk-crawl/', crawler.bulk_crawl, name='crawler-bulk-crawl'),
    path('crawler/system-status/', crawler.system_status, name='crawler-system-status'),
    path('crawler/stats/', crawler.crawler_stats, name='crawler-stats'),
]