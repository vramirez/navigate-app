"""
Crawler Orchestrator Service for NaviGate

This service coordinates the entire news crawling process, managing RSS discovery,
manual crawling, and content processing for news sources.
"""

import logging
from typing import Dict, Optional, List
from django.utils import timezone
from django.db import transaction

from ..models import NewsSource, CrawlHistory
from .rss_discovery import RSSDiscoveryService
from .manual_crawler import ManualCrawlerService
from .content_processor import ContentProcessorService

logger = logging.getLogger(__name__)


class CrawlerOrchestratorService:
    """Main service for orchestrating news crawling operations"""

    def __init__(self):
        """Initialize crawler orchestrator with all required services"""
        self.rss_service = RSSDiscoveryService()
        self.manual_crawler = ManualCrawlerService()
        self.content_processor = ContentProcessorService()

    def setup_news_source(self, source: NewsSource) -> Dict[str, any]:
        """
        Set up a news source by discovering RSS feeds and site structure

        Args:
            source: NewsSource instance to set up

        Returns:
            Dict containing setup results
        """
        result = {
            'success': False,
            'source_id': source.id,
            'source_name': source.name,
            'rss_discovered': False,
            'site_structure_analyzed': False,
            'setup_actions': [],
            'recommendations': [],
            'errors': []
        }

        try:
            # Step 1: Try RSS discovery
            if source.crawler_url and not source.discovered_rss_url:
                logger.info(f"Discovering RSS feeds for {source.name}")

                rss_result = self.rss_service.discover_rss_feeds(source.crawler_url)

                if rss_result['success'] and rss_result['feeds']:
                    # Update source with discovered RSS using atomic transaction
                    with transaction.atomic():
                        source.rss_discovered = True
                        source.discovered_rss_url = rss_result['primary_feed']['url']
                        source.save()

                    result['rss_discovered'] = True
                    result['setup_actions'].append(f"RSS feed discovered: {source.discovered_rss_url}")

                    # Update website title if available
                    if rss_result['website_title'] and not source.name.strip():
                        with transaction.atomic():
                            source.name = rss_result['website_title']
                            source.save()
                        result['setup_actions'].append(f"Website title updated: {source.name}")

                else:
                    result['recommendations'].append("No RSS feeds found. Manual crawling will be used.")

            # Step 2: Analyze site structure for manual crawling
            if source.crawler_url:
                logger.info(f"Analyzing site structure for {source.name}")

                structure_result = self.manual_crawler.discover_site_structure(source.crawler_url)

                if structure_result['success']:
                    # Update source with discovered sections using atomic transaction
                    if structure_result['sections']:
                        with transaction.atomic():
                            source.crawl_sections = structure_result['sections']
                            source.manual_crawl_enabled = True
                            source.save()

                        result['site_structure_analyzed'] = True
                        result['setup_actions'].append(f"Site structure analyzed: {len(structure_result['sections'])} sections found")

                        # Add recommendations based on structure
                        if len(structure_result['sections']) > 5:
                            result['recommendations'].append("Many sections found. Consider limiting to most relevant ones.")

                else:
                    result['errors'].append(f"Site structure analysis failed: {structure_result['error']}")

            # Step 3: Determine best crawling strategy
            strategy_recommendation = self._recommend_crawling_strategy(source)
            result['recommendations'].append(strategy_recommendation)

            result['success'] = True

        except Exception as e:
            error_msg = f"Source setup failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    def crawl_source(self, source_id: int, force_manual: bool = False) -> Dict[str, any]:
        """
        Crawl a specific news source

        Args:
            source_id: ID of the NewsSource to crawl
            force_manual: Force manual crawling even if RSS is available

        Returns:
            Dict containing crawl results
        """
        try:
            source = NewsSource.objects.get(id=source_id, is_active=True)
        except NewsSource.DoesNotExist:
            return {
                'success': False,
                'error': f"News source with ID {source_id} not found or inactive"
            }

        logger.info(f"Starting crawl for source: {source.name} (ID: {source_id})")

        # Use content processor to handle the actual crawling
        result = self.content_processor.process_news_source(source, force_manual=force_manual)

        # Add orchestrator-specific information
        result['source_name'] = source.name
        result['crawl_timestamp'] = timezone.now().isoformat()

        return result

    def bulk_crawl(self, country_code: str = None, source_ids: List[int] = None) -> Dict[str, any]:
        """
        Perform bulk crawling of multiple sources

        Args:
            country_code: Limit crawling to sources from specific country
            source_ids: List of specific source IDs to crawl

        Returns:
            Dict containing bulk crawl results
        """
        result = {
            'success': False,
            'total_sources': 0,
            'processed_sources': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'total_articles': 0,
            'source_results': [],
            'errors': [],
            'crawl_timestamp': timezone.now().isoformat()
        }

        try:
            # Build query for sources
            sources_query = NewsSource.objects.filter(is_active=True)

            if country_code:
                sources_query = sources_query.filter(country=country_code)

            if source_ids:
                sources_query = sources_query.filter(id__in=source_ids)

            sources = list(sources_query.all())
            result['total_sources'] = len(sources)

            logger.info(f"Starting bulk crawl for {len(sources)} sources")

            # Process each source
            for source in sources:
                try:
                    logger.info(f"Processing source: {source.name}")

                    source_result = self.content_processor.process_news_source(source)
                    source_result['source_name'] = source.name

                    result['source_results'].append(source_result)
                    result['processed_sources'] += 1

                    if source_result['success']:
                        result['successful_crawls'] += 1
                        result['total_articles'] += source_result['articles_saved']
                    else:
                        result['failed_crawls'] += 1

                    # Add any errors from this source to the main error list
                    if source_result['errors']:
                        result['errors'].extend([f"{source.name}: {error}" for error in source_result['errors']])

                except Exception as e:
                    error_msg = f"Failed to process source {source.name}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed_crawls'] += 1

            result['success'] = result['successful_crawls'] > 0

            logger.info(f"Bulk crawl completed: {result['successful_crawls']}/{result['total_sources']} sources successful")

        except Exception as e:
            error_msg = f"Bulk crawl failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    def discover_rss_for_source(self, source_id: int) -> Dict[str, any]:
        """
        Discover RSS feeds for a specific source

        Args:
            source_id: ID of the NewsSource

        Returns:
            Dict containing RSS discovery results
        """
        try:
            source = NewsSource.objects.get(id=source_id)
        except NewsSource.DoesNotExist:
            return {
                'success': False,
                'error': f"News source with ID {source_id} not found"
            }

        if not source.crawler_url:
            return {
                'success': False,
                'error': "No crawler URL configured for this source"
            }

        logger.info(f"Discovering RSS feeds for {source.name}")

        # Perform RSS discovery
        discovery_result = self.rss_service.discover_rss_feeds(source.crawler_url)

        if discovery_result['success'] and discovery_result['feeds']:
            # Update source with discovered information using atomic transaction
            with transaction.atomic():
                source.rss_discovered = True
                source.discovered_rss_url = discovery_result['primary_feed']['url']

                if discovery_result['website_title']:
                    source.name = discovery_result['website_title']

                if discovery_result['discovered_sections']:
                    # Convert to format expected by crawl_sections field
                    sections = [
                        {'title': section, 'url': '', 'type': 'discovered'}
                        for section in discovery_result['discovered_sections']
                    ]
                    source.crawl_sections = sections

                source.save()

            discovery_result['source_updated'] = True
            discovery_result['source_name'] = source.name

        return discovery_result

    def analyze_site_structure(self, source_id: int) -> Dict[str, any]:
        """
        Analyze site structure for manual crawling

        Args:
            source_id: ID of the NewsSource

        Returns:
            Dict containing site structure analysis results
        """
        try:
            source = NewsSource.objects.get(id=source_id)
        except NewsSource.DoesNotExist:
            return {
                'success': False,
                'error': f"News source with ID {source_id} not found"
            }

        if not source.crawler_url:
            return {
                'success': False,
                'error': "No crawler URL configured for this source"
            }

        logger.info(f"Analyzing site structure for {source.name}")

        # Perform structure analysis
        structure_result = self.manual_crawler.discover_site_structure(source.crawler_url)

        if structure_result['success']:
            # Update source with discovered structure using atomic transaction
            with transaction.atomic():
                source.crawl_sections = structure_result['sections']
                source.manual_crawl_enabled = True
                source.save()

            structure_result['source_updated'] = True
            structure_result['source_name'] = source.name

        return structure_result

    def get_crawl_history(self, source_id: int, limit: int = 5) -> Dict[str, any]:
        """
        Get crawl history for a source

        Args:
            source_id: ID of the NewsSource
            limit: Number of recent crawl attempts to return

        Returns:
            Dict containing crawl history
        """
        try:
            source = NewsSource.objects.get(id=source_id)
        except NewsSource.DoesNotExist:
            return {
                'success': False,
                'error': f"News source with ID {source_id} not found"
            }

        crawl_history = CrawlHistory.objects.filter(
            source=source
        ).order_by('-crawl_date')[:limit]

        history_data = []
        for crawl in crawl_history:
            history_data.append({
                'id': crawl.id,
                'crawl_date': crawl.crawl_date.isoformat(),
                'status': crawl.status,
                'crawl_type': crawl.crawl_type,
                'articles_found': crawl.articles_found,
                'articles_saved': crawl.articles_saved,
                'error_message': crawl.error_message,
                'crawl_duration': crawl.crawl_duration.total_seconds() if crawl.crawl_duration else None
            })

        return {
            'success': True,
            'source_id': source_id,
            'source_name': source.name,
            'crawl_history': history_data,
            'total_crawls': CrawlHistory.objects.filter(source=source).count()
        }

    def get_system_status(self) -> Dict[str, any]:
        """
        Get overall system status and statistics

        Returns:
            Dict containing system status information
        """
        try:
            # Count sources by status
            total_sources = NewsSource.objects.filter(is_active=True).count()
            sources_with_rss = NewsSource.objects.filter(is_active=True, rss_discovered=True).count()
            sources_with_manual = NewsSource.objects.filter(is_active=True, manual_crawl_enabled=True).count()

            # Recent crawl statistics
            recent_crawls = CrawlHistory.objects.filter(
                crawl_date__gte=timezone.now() - timezone.timedelta(days=7)
            )

            successful_crawls = recent_crawls.filter(status='success').count()
            failed_crawls = recent_crawls.filter(status='failed').count()

            # Country breakdown
            country_stats = {}
            for source in NewsSource.objects.filter(is_active=True).values('country').distinct():
                country_code = source['country']
                country_count = NewsSource.objects.filter(is_active=True, country=country_code).count()
                country_stats[country_code] = country_count

            return {
                'success': True,
                'system_status': 'operational',
                'statistics': {
                    'total_active_sources': total_sources,
                    'sources_with_rss': sources_with_rss,
                    'sources_with_manual_crawl': sources_with_manual,
                    'recent_successful_crawls': successful_crawls,
                    'recent_failed_crawls': failed_crawls,
                    'success_rate': (successful_crawls / max(successful_crawls + failed_crawls, 1)) * 100,
                    'country_breakdown': country_stats
                },
                'last_updated': timezone.now().isoformat()
            }

        except Exception as e:
            logger.error(f"System status check failed: {str(e)}")
            return {
                'success': False,
                'system_status': 'error',
                'error': str(e),
                'last_updated': timezone.now().isoformat()
            }

    def reset_crawl_status(self, source_id: int) -> Dict[str, any]:
        """
        Reset crawl status for a source, allowing immediate retry

        Args:
            source_id: ID of the NewsSource

        Returns:
            Dict containing reset results
        """
        try:
            source = NewsSource.objects.get(id=source_id)
        except NewsSource.DoesNotExist:
            return {
                'success': False,
                'error': f"News source with ID {source_id} not found"
            }

        old_status = source.get_crawl_status_display()

        # Reset status fields using atomic transaction
        with transaction.atomic():
            source.crawl_status = 'unknown'
            source.crawl_retry_after = None
            source.failed_crawl_count = 0
            source.save()

        logger.info(f"Reset crawl status for {source.name} (was: {old_status})")

        return {
            'success': True,
            'source_id': source_id,
            'source_name': source.name,
            'old_status': old_status,
            'new_status': source.get_crawl_status_display(),
            'message': f"Crawl status reset from '{old_status}' to 'unknown'. Source can now be retried immediately."
        }

    def _recommend_crawling_strategy(self, source: NewsSource) -> str:
        """Recommend the best crawling strategy for a source"""
        if source.rss_discovered and source.discovered_rss_url:
            return "RSS feed available - recommended primary method"
        elif source.manual_crawl_enabled and source.crawl_sections:
            return f"Manual crawling configured with {len(source.crawl_sections)} sections"
        elif source.crawler_url:
            return "URL configured but needs analysis - run setup first"
        else:
            return "No crawling method configured - please add crawler URL"