"""
RSS Discovery Service for NaviGate News Crawler

This service automatically discovers RSS feeds from news websites using multiple strategies:
1. Looking for RSS links in HTML head
2. Checking common RSS feed locations
3. Parsing HTML content for feed references
"""

import logging
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
import feedparser

logger = logging.getLogger(__name__)


class RSSDiscoveryService:
    """Service for discovering RSS feeds from news websites"""

    def __init__(self, timeout: int = 10, user_agent: str = None):
        """
        Initialize RSS discovery service

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "NaviGate-Bot/1.0 (+https://github.com/vramirez/navigate-app) "
            "RSS Discovery Service"
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        })

    def discover_rss_feeds(self, website_url: str) -> Dict[str, any]:
        """
        Discover RSS feeds for a given website

        Args:
            website_url: Main website URL to analyze

        Returns:
            Dict containing discovery results with feeds, errors, and metadata
        """
        result = {
            'success': False,
            'feeds': [],
            'primary_feed': None,
            'discovery_methods': [],
            'error': None,
            'website_title': None,
            'analyzed_url': website_url,
            'robots_txt_allowed': True,
            'discovered_sections': []
        }

        try:
            # Check robots.txt first
            result['robots_txt_allowed'] = self._check_robots_txt(website_url)
            if not result['robots_txt_allowed']:
                result['error'] = "Crawling not allowed by robots.txt"
                return result

            # Try multiple discovery methods
            feeds = []

            # Method 1: Parse HTML for RSS links
            html_feeds = self._discover_from_html(website_url)
            if html_feeds:
                feeds.extend(html_feeds)
                result['discovery_methods'].append('html_parsing')

            # Method 2: Try common RSS locations
            common_feeds = self._try_common_locations(website_url)
            if common_feeds:
                feeds.extend(common_feeds)
                result['discovery_methods'].append('common_locations')

            # Method 3: Try WordPress/CMS specific patterns
            cms_feeds = self._try_cms_patterns(website_url)
            if cms_feeds:
                feeds.extend(cms_feeds)
                result['discovery_methods'].append('cms_patterns')

            # Remove duplicates and validate feeds
            unique_feeds = self._deduplicate_and_validate_feeds(feeds)

            if unique_feeds:
                result['success'] = True
                result['feeds'] = unique_feeds
                result['primary_feed'] = self._select_primary_feed(unique_feeds)

                # Get website title and sections
                title, sections = self._extract_website_info(website_url)
                result['website_title'] = title
                result['discovered_sections'] = sections
            else:
                result['error'] = "No valid RSS feeds found"

        except Exception as e:
            logger.error(f"RSS discovery failed for {website_url}: {str(e)}")
            result['error'] = f"Discovery failed: {str(e)}"

        return result

    def _check_robots_txt(self, website_url: str) -> bool:
        """Check if crawling is allowed by robots.txt"""
        try:
            parsed_url = urlparse(website_url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            return rp.can_fetch(self.user_agent, website_url)
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {website_url}: {e}")
            return True  # Allow crawling if robots.txt check fails

    def _discover_from_html(self, website_url: str) -> List[Dict]:
        """Discover RSS feeds by parsing HTML head section"""
        feeds = []

        try:
            response = self.session.get(website_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for RSS/Atom links in head
            rss_links = soup.find_all('link', {
                'type': ['application/rss+xml', 'application/atom+xml', 'application/xml']
            })

            for link in rss_links:
                href = link.get('href')
                if href:
                    absolute_url = urljoin(website_url, href)
                    title = link.get('title', 'RSS Feed')
                    feed_type = link.get('type', 'application/rss+xml')

                    feeds.append({
                        'url': absolute_url,
                        'title': title,
                        'type': feed_type,
                        'discovery_method': 'html_head'
                    })

            # Also look for RSS links in the page content
            rss_text_links = soup.find_all('a', href=True)
            for link in rss_text_links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()

                if any(keyword in href or keyword in text for keyword in ['rss', 'feed', 'xml', 'atom']):
                    absolute_url = urljoin(website_url, link['href'])
                    feeds.append({
                        'url': absolute_url,
                        'title': link.get_text() or 'RSS Feed',
                        'type': 'application/rss+xml',
                        'discovery_method': 'html_content'
                    })

        except Exception as e:
            logger.warning(f"HTML parsing failed for {website_url}: {e}")

        return feeds

    def _try_common_locations(self, website_url: str) -> List[Dict]:
        """Try common RSS feed locations"""
        feeds = []
        common_paths = [
            '/feed/',
            '/feeds/',
            '/rss/',
            '/rss.xml',
            '/feed.xml',
            '/atom.xml',
            '/index.xml',
            '/news/feed/',
            '/blog/feed/',
            '/noticias/feed/',
            '/feed/rss/',
            '/feed/atom/',
        ]

        base_url = website_url.rstrip('/')

        for path in common_paths:
            try:
                feed_url = base_url + path
                response = self.session.head(feed_url, timeout=5)

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if any(t in content_type for t in ['xml', 'rss', 'atom']):
                        feeds.append({
                            'url': feed_url,
                            'title': f'RSS Feed ({path})',
                            'type': 'application/rss+xml',
                            'discovery_method': 'common_location'
                        })

                time.sleep(0.5)  # Be respectful to the server

            except Exception:
                continue  # Silently skip failed attempts

        return feeds

    def _try_cms_patterns(self, website_url: str) -> List[Dict]:
        """Try CMS-specific RSS patterns (WordPress, Drupal, etc.)"""
        feeds = []
        base_url = website_url.rstrip('/')

        cms_patterns = [
            # WordPress
            '/?feed=rss2',
            '/?feed=atom',
            '/wp-rss2.php',
            '/wp-atom.php',
            '/wp-rdf.php',
            # Drupal
            '/rss.xml',
            '/node/feed',
            # Joomla
            '/component/content/article.xml',
            # Generic CMS
            '/feeds/all.atom.xml',
            '/feeds/all.rss.xml',
        ]

        for pattern in cms_patterns:
            try:
                feed_url = base_url + pattern
                response = self.session.head(feed_url, timeout=3)

                if response.status_code == 200:
                    feeds.append({
                        'url': feed_url,
                        'title': f'CMS Feed ({pattern})',
                        'type': 'application/rss+xml',
                        'discovery_method': 'cms_pattern'
                    })

                time.sleep(0.3)

            except Exception:
                continue

        return feeds

    def _deduplicate_and_validate_feeds(self, feeds: List[Dict]) -> List[Dict]:
        """Remove duplicates and validate feeds"""
        seen_urls = set()
        valid_feeds = []

        for feed in feeds:
            url = feed['url']
            if url in seen_urls:
                continue

            seen_urls.add(url)

            # Validate feed by fetching and parsing
            if self._validate_feed(url):
                valid_feeds.append(feed)

        return valid_feeds

    def _validate_feed(self, feed_url: str) -> bool:
        """Validate that a URL actually contains a valid RSS/Atom feed"""
        try:
            response = self.session.get(feed_url, timeout=5)
            if response.status_code != 200:
                return False

            # Use feedparser to validate
            feed = feedparser.parse(response.content)

            # Check if it's a valid feed with entries
            return (
                hasattr(feed, 'version') and
                feed.version and
                len(feed.entries) > 0
            )

        except Exception:
            return False

    def _select_primary_feed(self, feeds: List[Dict]) -> Optional[Dict]:
        """Select the primary/best RSS feed from discovered feeds"""
        if not feeds:
            return None

        # Priority order for selection
        priority_methods = ['html_head', 'common_location', 'cms_pattern', 'html_content']
        priority_paths = ['/feed/', '/rss/', '/atom.xml']

        # First, try to find feed by discovery method priority
        for method in priority_methods:
            for feed in feeds:
                if feed.get('discovery_method') == method:
                    return feed

        # Then by path priority
        for path in priority_paths:
            for feed in feeds:
                if path in feed['url']:
                    return feed

        # Finally, just return the first one
        return feeds[0]

    def _extract_website_info(self, website_url: str) -> Tuple[Optional[str], List[str]]:
        """Extract website title and discover main sections"""
        try:
            response = self.session.get(website_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Get title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else None

            # Discover main navigation sections
            sections = []
            nav_selectors = [
                'nav ul li a',
                '.navbar ul li a',
                '.menu ul li a',
                '.navigation ul li a',
                'header nav a',
                '.main-menu a'
            ]

            for selector in nav_selectors:
                nav_links = soup.select(selector)
                for link in nav_links[:10]:  # Limit to first 10
                    text = link.get_text().strip()
                    href = link.get('href')

                    if text and href and len(text) < 50:
                        # Filter out common non-section links
                        skip_keywords = ['home', 'inicio', 'contacto', 'contact', 'about', 'acerca']
                        if not any(keyword in text.lower() for keyword in skip_keywords):
                            sections.append(text)

                if sections:  # If we found sections, stop trying other selectors
                    break

            # Remove duplicates and limit
            sections = list(dict.fromkeys(sections))[:8]

            return title, sections

        except Exception as e:
            logger.warning(f"Could not extract website info for {website_url}: {e}")
            return None, []

    def get_feed_info(self, feed_url: str) -> Dict[str, any]:
        """Get detailed information about a specific RSS feed"""
        result = {
            'success': False,
            'title': None,
            'description': None,
            'language': None,
            'last_updated': None,
            'entry_count': 0,
            'recent_entries': [],
            'error': None
        }

        try:
            response = self.session.get(feed_url, timeout=self.timeout)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo and feed.bozo_exception:
                result['error'] = f"Feed parsing error: {feed.bozo_exception}"
                return result

            # Extract feed information
            result['success'] = True
            result['title'] = feed.feed.get('title', '')
            result['description'] = feed.feed.get('description', '')
            result['language'] = feed.feed.get('language', '')
            result['entry_count'] = len(feed.entries)

            # Get recent entries (last 5)
            for entry in feed.entries[:5]:
                entry_info = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else ''
                }
                result['recent_entries'].append(entry_info)

        except Exception as e:
            result['error'] = f"Failed to analyze feed: {str(e)}"
            logger.error(f"Feed analysis failed for {feed_url}: {e}")

        return result