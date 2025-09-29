"""
API endpoints for news crawler management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..models import NewsSource, CrawlHistory
from ..services.crawler_orchestrator import CrawlerOrchestratorService
from ..serializers import NewsSourceSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def discover_rss(request, source_id):
    """
    Discover RSS feeds for a news source

    POST /api/news/sources/{id}/discover-rss/
    """
    source = get_object_or_404(NewsSource, id=source_id)
    orchestrator = CrawlerOrchestratorService()

    result = orchestrator.discover_rss_for_source(source_id)

    if result['success']:
        # Return updated source data
        serializer = NewsSourceSerializer(source)
        return Response({
            'success': True,
            'message': 'RSS discovery completed successfully',
            'discovery_result': result,
            'source': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'RSS discovery failed',
            'error': result.get('error', 'Unknown error'),
            'discovery_result': result
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def analyze_structure(request, source_id):
    """
    Analyze site structure for manual crawling

    POST /api/news/sources/{id}/analyze-structure/
    """
    source = get_object_or_404(NewsSource, id=source_id)
    orchestrator = CrawlerOrchestratorService()

    result = orchestrator.analyze_site_structure(source_id)

    if result['success']:
        # Refresh source from database to get updated data
        source.refresh_from_db()
        serializer = NewsSourceSerializer(source)
        return Response({
            'success': True,
            'message': 'Site structure analysis completed successfully',
            'analysis_result': result,
            'source': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Site structure analysis failed',
            'error': result.get('error', 'Unknown error'),
            'analysis_result': result
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def setup_source(request, source_id):
    """
    Setup a news source (discover RSS + analyze structure)

    POST /api/news/sources/{id}/setup/
    """
    source = get_object_or_404(NewsSource, id=source_id)
    orchestrator = CrawlerOrchestratorService()

    result = orchestrator.setup_news_source(source)

    if result['success']:
        # Refresh source from database to get updated data
        source.refresh_from_db()
        serializer = NewsSourceSerializer(source)
        return Response({
            'success': True,
            'message': 'Source setup completed successfully',
            'setup_result': result,
            'source': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Source setup failed',
            'errors': result.get('errors', []),
            'setup_result': result
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def crawl_source(request, source_id):
    """
    Crawl a specific news source

    POST /api/news/sources/{id}/crawl/

    Query parameters:
    - force_manual: boolean, force manual crawling even if RSS is available
    """
    source = get_object_or_404(NewsSource, id=source_id)
    orchestrator = CrawlerOrchestratorService()

    force_manual = request.query_params.get('force_manual', '').lower() == 'true'
    result = orchestrator.crawl_source(source_id, force_manual=force_manual)

    if result['success']:
        return Response({
            'success': True,
            'message': f'Crawl completed successfully: {result["articles_saved"]} articles saved',
            'crawl_result': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Crawl failed',
            'errors': result.get('errors', []),
            'crawl_result': result
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_crawl(request):
    """
    Perform bulk crawling of multiple sources

    POST /api/news/crawler/bulk-crawl/

    Query parameters:
    - country: string, filter sources by country code

    Request body:
    - source_ids: array of integers, specific source IDs to crawl
    """
    orchestrator = CrawlerOrchestratorService()

    # Get parameters
    country_code = request.query_params.get('country')
    source_ids = request.data.get('source_ids')

    if source_ids and not isinstance(source_ids, list):
        return Response({
            'success': False,
            'message': 'source_ids must be an array of integers'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = orchestrator.bulk_crawl(
        country_code=country_code,
        source_ids=source_ids
    )

    if result['success']:
        return Response({
            'success': True,
            'message': f'Bulk crawl completed: {result["successful_crawls"]}/{result["total_sources"]} sources successful',
            'bulk_result': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Bulk crawl completed with errors',
            'bulk_result': result
        }, status=status.HTTP_207_MULTI_STATUS)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def crawl_history(request, source_id):
    """
    Get crawl history for a source

    GET /api/news/sources/{id}/crawl-history/

    Query parameters:
    - limit: integer, number of recent crawls to return (default: 5)
    """
    source = get_object_or_404(NewsSource, id=source_id)
    orchestrator = CrawlerOrchestratorService()

    limit = int(request.query_params.get('limit', 5))
    result = orchestrator.get_crawl_history(source_id, limit=limit)

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def system_status(request):
    """
    Get overall crawler system status and statistics

    GET /api/news/crawler/system-status/
    """
    orchestrator = CrawlerOrchestratorService()
    result = orchestrator.get_system_status()

    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crawler_stats(request):
    """
    Get crawler statistics for dashboard

    GET /api/news/crawler/stats/

    Query parameters:
    - days: integer, number of days to include in stats (default: 7)
    """
    days = int(request.query_params.get('days', 7))
    since_date = timezone.now() - timezone.timedelta(days=days)

    # Count sources by configuration
    total_sources = NewsSource.objects.filter(is_active=True).count()
    sources_with_rss = NewsSource.objects.filter(
        is_active=True,
        rss_discovered=True
    ).count()
    sources_with_manual = NewsSource.objects.filter(
        is_active=True,
        manual_crawl_enabled=True
    ).count()

    # Recent crawl statistics
    recent_crawls = CrawlHistory.objects.filter(crawl_date__gte=since_date)
    successful_crawls = recent_crawls.filter(status='success').count()
    failed_crawls = recent_crawls.filter(status='failed').count()
    total_articles = sum(crawl.articles_saved for crawl in recent_crawls.filter(status='success'))

    # Success rate
    total_recent_crawls = successful_crawls + failed_crawls
    success_rate = (successful_crawls / max(total_recent_crawls, 1)) * 100

    # Country breakdown
    country_stats = {}
    sources_by_country = NewsSource.objects.filter(is_active=True).values_list('country', flat=True)
    for country in set(sources_by_country):
        country_stats[country] = sources_by_country.filter(country=country).count()

    return Response({
        'success': True,
        'period_days': days,
        'statistics': {
            'total_active_sources': total_sources,
            'sources_with_rss': sources_with_rss,
            'sources_with_manual_crawl': sources_with_manual,
            'recent_successful_crawls': successful_crawls,
            'recent_failed_crawls': failed_crawls,
            'total_articles_crawled': total_articles,
            'success_rate': round(success_rate, 1),
            'country_breakdown': country_stats
        },
        'last_updated': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def source_recommendations(request, source_id):
    """
    Get recommendations for improving a news source configuration

    GET /api/news/sources/{id}/recommendations/
    """
    source = get_object_or_404(NewsSource, id=source_id)

    recommendations = []

    # Check if source needs setup
    if source.crawler_url and not (source.rss_discovered or source.manual_crawl_enabled):
        recommendations.append({
            'type': 'setup',
            'priority': 'high',
            'message': 'Source needs initial setup. Run RSS discovery and site structure analysis.',
            'action': 'setup_source'
        })

    # Check if RSS discovery hasn't been tried
    if source.crawler_url and not source.rss_discovered:
        recommendations.append({
            'type': 'rss_discovery',
            'priority': 'medium',
            'message': 'RSS feeds not yet discovered. Try RSS discovery to enable automatic crawling.',
            'action': 'discover_rss'
        })

    # Check if manual crawling isn't configured but could be useful
    if source.crawler_url and not source.manual_crawl_enabled:
        recommendations.append({
            'type': 'manual_crawl',
            'priority': 'medium',
            'message': 'Manual crawling not configured. Analyze site structure for comprehensive coverage.',
            'action': 'analyze_structure'
        })

    # Check crawl frequency based on recent history
    recent_crawls = CrawlHistory.objects.filter(
        source=source,
        crawl_date__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()

    if recent_crawls == 0 and (source.rss_discovered or source.manual_crawl_enabled):
        recommendations.append({
            'type': 'crawl_frequency',
            'priority': 'low',
            'message': 'No recent crawls detected. Consider running a test crawl.',
            'action': 'crawl_source'
        })

    # Check for failed crawls
    recent_failed = CrawlHistory.objects.filter(
        source=source,
        status='failed',
        crawl_date__gte=timezone.now() - timezone.timedelta(days=3)
    ).count()

    if recent_failed > 0:
        recommendations.append({
            'type': 'crawl_errors',
            'priority': 'high',
            'message': f'{recent_failed} failed crawls in the last 3 days. Check source configuration.',
            'action': 'check_errors'
        })

    return Response({
        'success': True,
        'source_id': source_id,
        'source_name': source.name,
        'recommendations': recommendations,
        'total_recommendations': len(recommendations)
    }, status=status.HTTP_200_OK)