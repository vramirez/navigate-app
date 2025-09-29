"""
Content Processing Pipeline for NaviGate News Crawler

This service processes crawled news content, standardizes data from both RSS and manual crawling,
handles content validation, deduplication, and prepares articles for ML processing.
"""

import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.utils import timezone
from django.db import transaction

import feedparser
from bs4 import BeautifulSoup

from ..models import NewsSource, NewsArticle, CrawlHistory
from .rss_discovery import RSSDiscoveryService
from .manual_crawler import ManualCrawlerService

logger = logging.getLogger(__name__)


class ContentProcessorService:
    """Service for processing and standardizing crawled news content"""

    def __init__(self):
        """Initialize content processor"""
        self.rss_service = RSSDiscoveryService()
        self.manual_crawler = ManualCrawlerService()

    def process_news_source(self, source: NewsSource, force_manual: bool = False) -> Dict[str, any]:
        """
        Process a news source by discovering feeds or crawling manually

        Args:
            source: NewsSource instance to process
            force_manual: Force manual crawling even if RSS is available

        Returns:
            Dict containing processing results
        """
        result = {
            'success': False,
            'source_id': source.id,
            'source_name': source.name,
            'method_used': None,
            'articles_found': 0,
            'articles_saved': 0,
            'articles_updated': 0,
            'articles_skipped': 0,
            'errors': [],
            'processing_duration': 0,
            'crawl_history_id': None
        }

        start_time = timezone.now()

        try:
            with transaction.atomic():
                # Create crawl history entry
                crawl_history = CrawlHistory.objects.create(
                    source=source,
                    status='success',  # Will update if errors occur
                    crawl_type='manual' if force_manual else 'auto'
                )
                result['crawl_history_id'] = crawl_history.id

                # Try RSS first (unless forced manual)
                if not force_manual and (source.rss_url or source.discovered_rss_url):
                    rss_result = self._process_rss_feed(source)
                    if rss_result['success']:
                        result.update(rss_result)
                        result['method_used'] = 'rss'
                        crawl_history.crawl_type = 'rss'
                    else:
                        result['errors'].extend(rss_result['errors'])

                # If RSS failed or forced manual, try manual crawling
                if not result['success'] or force_manual:
                    manual_result = self._process_manual_crawl(source)
                    if manual_result['success']:
                        if result['success']:  # Combine results if both methods worked
                            result['articles_found'] += manual_result['articles_found']
                            result['articles_saved'] += manual_result['articles_saved']
                            result['articles_updated'] += manual_result['articles_updated']
                            result['articles_skipped'] += manual_result['articles_skipped']
                            result['method_used'] = 'rss+manual'
                        else:
                            result.update(manual_result)
                            result['method_used'] = 'manual'
                        crawl_history.crawl_type = 'manual'
                    else:
                        result['errors'].extend(manual_result['errors'])

                # Update crawl history
                crawl_history.articles_found = result['articles_found']
                crawl_history.articles_saved = result['articles_saved']
                crawl_history.status = 'success' if result['success'] else 'failed'
                crawl_history.error_message = '; '.join(result['errors']) if result['errors'] else ''

                # Update source last_fetched timestamp
                if result['success']:
                    source.last_fetched = timezone.now()
                    source.save()

        except Exception as e:
            error_msg = f"Source processing failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

            # Update crawl history on error
            if result['crawl_history_id']:
                try:
                    crawl_history = CrawlHistory.objects.get(id=result['crawl_history_id'])
                    crawl_history.status = 'failed'
                    crawl_history.error_message = error_msg
                    crawl_history.save()
                except CrawlHistory.DoesNotExist:
                    pass

        finally:
            result['processing_duration'] = (timezone.now() - start_time).total_seconds()

        return result

    def _process_rss_feed(self, source: NewsSource) -> Dict[str, any]:
        """Process articles from RSS feed"""
        result = {
            'success': False,
            'articles_found': 0,
            'articles_saved': 0,
            'articles_updated': 0,
            'articles_skipped': 0,
            'errors': []
        }

        try:
            feed_url = source.discovered_rss_url or source.rss_url

            if not feed_url:
                result['errors'].append("No RSS URL available")
                return result

            # Fetch and parse RSS feed
            response = self.rss_service.session.get(feed_url, timeout=15)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo and feed.bozo_exception:
                result['errors'].append(f"RSS parsing error: {feed.bozo_exception}")
                return result

            result['articles_found'] = len(feed.entries)

            # Process each entry
            for entry in feed.entries:
                try:
                    article_data = self._standardize_rss_entry(entry, source)
                    if article_data:
                        save_result = self._save_article(article_data, source)
                        if save_result == 'created':
                            result['articles_saved'] += 1
                        elif save_result == 'updated':
                            result['articles_updated'] += 1
                        else:
                            result['articles_skipped'] += 1

                except Exception as e:
                    error_msg = f"RSS entry processing failed: {str(e)}"
                    logger.warning(error_msg)
                    result['errors'].append(error_msg)

            result['success'] = True

        except Exception as e:
            error_msg = f"RSS feed processing failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    def _process_manual_crawl(self, source: NewsSource) -> Dict[str, any]:
        """Process articles from manual crawling"""
        result = {
            'success': False,
            'articles_found': 0,
            'articles_saved': 0,
            'articles_updated': 0,
            'articles_skipped': 0,
            'errors': []
        }

        try:
            if not source.crawler_url:
                result['errors'].append("No crawler URL configured")
                return result

            # Use existing sections or discover new ones
            sections_to_crawl = []
            if source.crawl_sections:
                sections_to_crawl = [s['url'] for s in source.crawl_sections if isinstance(s, dict) and 'url' in s]

            if not sections_to_crawl:
                # Discover sections first
                structure = self.manual_crawler.discover_site_structure(source.crawler_url)
                if structure['success']:
                    sections_to_crawl = [s['url'] for s in structure['sections'][:3]]  # Limit to 3 sections

                    # Update source with discovered sections
                    source.crawl_sections = structure['sections']
                    source.save()
                else:
                    # Fallback to main page
                    sections_to_crawl = [source.crawler_url]

            # Crawl sections
            all_articles = []
            for section_url in sections_to_crawl:
                crawl_result = self.manual_crawler.crawl_section(section_url, max_articles=20)

                if crawl_result['success']:
                    all_articles.extend(crawl_result['articles'])

                result['errors'].extend(crawl_result['errors'])

            result['articles_found'] = len(all_articles)

            # Process crawled articles
            for article_data in all_articles:
                try:
                    standardized_data = self._standardize_manual_article(article_data, source)
                    if standardized_data:
                        save_result = self._save_article(standardized_data, source)
                        if save_result == 'created':
                            result['articles_saved'] += 1
                        elif save_result == 'updated':
                            result['articles_updated'] += 1
                        else:
                            result['articles_skipped'] += 1

                except Exception as e:
                    error_msg = f"Manual article processing failed: {str(e)}"
                    logger.warning(error_msg)
                    result['errors'].append(error_msg)

            result['success'] = True

        except Exception as e:
            error_msg = f"Manual crawl processing failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    def _standardize_rss_entry(self, entry: any, source: NewsSource) -> Optional[Dict]:
        """Standardize RSS entry data"""
        try:
            # Extract basic information
            title = entry.get('title', '').strip()
            link = entry.get('link', '').strip()
            content = self._extract_content_from_rss(entry)

            if not title or not link or not content or len(content) < 100:
                return None

            # Extract metadata
            author = entry.get('author', '').strip()
            published_date = self._parse_rss_date(entry)
            section = self._extract_section_from_entry(entry)

            return {
                'title': title,
                'content': content,
                'url': link,
                'author': author,
                'published_date': published_date,
                'section': section,
                'crawl_section': '',
                'source_type': 'rss'
            }

        except Exception as e:
            logger.warning(f"RSS entry standardization failed: {str(e)}")
            return None

    def _standardize_manual_article(self, article_data: Dict, source: NewsSource) -> Optional[Dict]:
        """Standardize manually crawled article data"""
        try:
            # Validate required fields
            if not all(key in article_data for key in ['title', 'content', 'url']):
                return None

            if len(article_data['content']) < 100:
                return None

            return {
                'title': article_data['title'].strip(),
                'content': article_data['content'].strip(),
                'url': article_data['url'].strip(),
                'author': article_data.get('author', '').strip(),
                'published_date': article_data.get('published_date') or timezone.now(),
                'section': article_data.get('section', '').strip(),
                'crawl_section': article_data.get('crawl_section', '').strip(),
                'source_type': 'manual'
            }

        except Exception as e:
            logger.warning(f"Manual article standardization failed: {str(e)}")
            return None

    def _extract_content_from_rss(self, entry: any) -> str:
        """Extract content from RSS entry"""
        # Try different content fields
        content_fields = ['content', 'summary', 'description']

        for field in content_fields:
            if hasattr(entry, field):
                content_data = getattr(entry, field)

                if isinstance(content_data, list) and content_data:
                    content_data = content_data[0]

                if isinstance(content_data, dict):
                    content = content_data.get('value', '')
                else:
                    content = str(content_data)

                if content:
                    # Clean HTML tags
                    soup = BeautifulSoup(content, 'html.parser')
                    clean_content = soup.get_text().strip()

                    if len(clean_content) > 100:
                        return clean_content

        return ''

    def _parse_rss_date(self, entry: any) -> datetime:
        """Parse publication date from RSS entry"""
        date_fields = ['published', 'updated', 'created']

        for field in date_fields:
            if hasattr(entry, field + '_parsed'):
                date_tuple = getattr(entry, field + '_parsed')
                if date_tuple:
                    try:
                        return datetime(*date_tuple[:6]).replace(tzinfo=timezone.utc)
                    except (ValueError, TypeError):
                        continue

        # Fallback to current time
        return timezone.now()

    def _extract_section_from_entry(self, entry: any) -> str:
        """Extract section from RSS entry"""
        # Try tags/categories first
        if hasattr(entry, 'tags') and entry.tags:
            return entry.tags[0].get('term', '')

        if hasattr(entry, 'category') and entry.category:
            return entry.category

        # Try to extract from link
        if hasattr(entry, 'link'):
            from urllib.parse import urlparse
            path = urlparse(entry.link).path
            segments = [s for s in path.split('/') if s]
            if segments:
                return segments[0]

        return ''

    def _save_article(self, article_data: Dict, source: NewsSource) -> str:
        """
        Save article to database with deduplication

        Returns:
            'created', 'updated', or 'skipped'
        """
        try:
            # Check for existing article by URL
            existing_article = NewsArticle.objects.filter(url=article_data['url']).first()

            if existing_article:
                # Check if content has changed significantly
                if self._has_content_changed(existing_article, article_data):
                    # Update existing article
                    for field, value in article_data.items():
                        if field != 'url':  # Don't update URL
                            setattr(existing_article, field, value)

                    existing_article.updated_at = timezone.now()
                    existing_article.save()
                    return 'updated'
                else:
                    return 'skipped'

            else:
                # Create new article
                article = NewsArticle.objects.create(
                    source=source,
                    **article_data
                )
                return 'created'

        except Exception as e:
            logger.error(f"Article save failed: {str(e)}")
            return 'error'

    def _has_content_changed(self, existing_article: NewsArticle, new_data: Dict) -> bool:
        """Check if article content has changed significantly"""
        # Compare content hashes
        existing_hash = hashlib.md5(existing_article.content.encode()).hexdigest()
        new_hash = hashlib.md5(new_data['content'].encode()).hexdigest()

        if existing_hash != new_hash:
            return True

        # Check if title changed
        if existing_article.title != new_data['title']:
            return True

        return False

    def clean_old_articles(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean old articles to prevent database bloat"""
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        deleted_count = NewsArticle.objects.filter(
            created_at__lt=cutoff_date,
            business_relevance_score__lt=0.3  # Only delete low-relevance articles
        ).delete()[0]

        return {'deleted_articles': deleted_count}

    def get_processing_stats(self, source: NewsSource, days: int = 7) -> Dict[str, any]:
        """Get processing statistics for a source"""
        since_date = timezone.now() - timedelta(days=days)

        crawl_history = CrawlHistory.objects.filter(
            source=source,
            crawl_date__gte=since_date
        ).order_by('-crawl_date')

        recent_articles = NewsArticle.objects.filter(
            source=source,
            created_at__gte=since_date
        )

        return {
            'source_name': source.name,
            'total_crawls': crawl_history.count(),
            'successful_crawls': crawl_history.filter(status='success').count(),
            'failed_crawls': crawl_history.filter(status='failed').count(),
            'articles_in_period': recent_articles.count(),
            'avg_articles_per_crawl': recent_articles.count() / max(crawl_history.count(), 1),
            'last_crawl': crawl_history.first().crawl_date if crawl_history.exists() else None,
            'last_successful_crawl': crawl_history.filter(status='success').first().crawl_date if crawl_history.filter(status='success').exists() else None
        }

    def bulk_process_sources(self, country_code: str = None) -> Dict[str, any]:
        """Process multiple news sources in bulk"""
        result = {
            'total_sources': 0,
            'successful_sources': 0,
            'failed_sources': 0,
            'total_articles': 0,
            'errors': [],
            'processing_duration': 0
        }

        start_time = timezone.now()

        try:
            # Get sources to process
            sources = NewsSource.objects.filter(is_active=True)

            if country_code:
                sources = sources.filter(country=country_code)

            result['total_sources'] = sources.count()

            # Process each source
            for source in sources:
                try:
                    source_result = self.process_news_source(source)

                    if source_result['success']:
                        result['successful_sources'] += 1
                        result['total_articles'] += source_result['articles_saved']
                    else:
                        result['failed_sources'] += 1
                        result['errors'].extend(source_result['errors'])

                except Exception as e:
                    error_msg = f"Bulk processing failed for source {source.name}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['failed_sources'] += 1

        except Exception as e:
            error_msg = f"Bulk processing failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        finally:
            result['processing_duration'] = (timezone.now() - start_time).total_seconds()

        return result