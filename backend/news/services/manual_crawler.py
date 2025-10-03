"""
Manual News Crawler Service for NaviGate

This service performs manual crawling of news websites that don't have RSS feeds,
using content extraction libraries like Trafilatura and BeautifulSoup to extract
articles, metadata, and site structure.
"""

import logging
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
import urllib.robotparser

import requests
from bs4 import BeautifulSoup
import trafilatura
from trafilatura.settings import use_config
import htmldate

logger = logging.getLogger(__name__)


class ManualCrawlerService:
    """Service for manually crawling news websites without RSS feeds"""

    def __init__(self, timeout: int = 15, user_agent: str = None, max_articles: int = 50):
        """
        Initialize manual crawler service

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
            max_articles: Maximum articles to crawl per session
        """
        self.timeout = timeout
        self.max_articles = max_articles
        self.user_agent = user_agent or (
            "NaviGate-Bot/1.0 (+https://github.com/vramirez/navigate-app) "
            "News Crawler Service"
        )

        # Setup requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        })

        # Setup trafilatura config for better Spanish content extraction
        self.trafilatura_config = use_config()
        self.trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "10")
        self.trafilatura_config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "200")

    def discover_site_structure(self, website_url: str) -> Dict[str, any]:
        """
        Discover the structure of a news website including sections and article patterns

        Args:
            website_url: Main website URL to analyze

        Returns:
            Dict containing site structure information
        """
        result = {
            'success': False,
            'website_title': None,
            'sections': [],
            'article_patterns': [],
            'pagination_patterns': [],
            'error': None,
            'robots_txt_allowed': True,
        }

        try:
            # Check robots.txt
            result['robots_txt_allowed'] = self._check_robots_txt(website_url)
            if not result['robots_txt_allowed']:
                result['error'] = "Crawling not allowed by robots.txt"
                return result

            response = self.session.get(website_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract website title
            title_tag = soup.find('title')
            result['website_title'] = title_tag.get_text().strip() if title_tag else None

            # Discover navigation sections
            sections = self._discover_sections(soup, website_url)
            result['sections'] = sections

            # Analyze article link patterns
            article_patterns = self._analyze_article_patterns(soup, website_url)
            result['article_patterns'] = article_patterns

            # Look for pagination patterns
            pagination_patterns = self._discover_pagination_patterns(soup, website_url)
            result['pagination_patterns'] = pagination_patterns

            result['success'] = True

        except Exception as e:
            logger.error(f"Site structure discovery failed for {website_url}: {str(e)}")
            result['error'] = f"Structure discovery failed: {str(e)}"

        return result

    def crawl_section(self, section_url: str, max_articles: int = None) -> Dict[str, any]:
        """
        Crawl a specific section of a news website

        Args:
            section_url: URL of the section to crawl
            max_articles: Maximum number of articles to extract

        Returns:
            Dict containing crawl results
        """
        max_articles = max_articles or self.max_articles
        result = {
            'success': False,
            'section_url': section_url,
            'articles': [],
            'total_found': 0,
            'total_extracted': 0,
            'errors': [],
            'crawl_duration': 0,
        }

        start_time = time.time()

        try:
            # Get robots.txt permission
            if not self._check_robots_txt(section_url):
                result['errors'].append("Crawling not allowed by robots.txt")
                return result

            # Get section page
            response = self.session.get(section_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find article links
            article_links = self._extract_article_links(soup, section_url)
            result['total_found'] = len(article_links)

            # Limit articles to crawl
            article_links = article_links[:max_articles]

            # Extract articles
            articles = []
            for link_info in article_links:
                try:
                    article = self._extract_article(link_info['url'], link_info.get('section'))
                    if article:
                        articles.append(article)
                        result['total_extracted'] += 1

                    # Be respectful - wait between requests
                    time.sleep(1)

                except Exception as e:
                    error_msg = f"Failed to extract article {link_info['url']}: {str(e)}"
                    logger.warning(error_msg)
                    result['errors'].append(error_msg)

            result['articles'] = articles
            result['success'] = True

        except Exception as e:
            error_msg = f"Section crawl failed for {section_url}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        finally:
            result['crawl_duration'] = time.time() - start_time

        return result

    def crawl_website(self, website_url: str, sections: List[str] = None) -> Dict[str, any]:
        """
        Crawl an entire website or specified sections

        Args:
            website_url: Main website URL
            sections: Optional list of section URLs to crawl

        Returns:
            Dict containing full website crawl results
        """
        result = {
            'success': False,
            'website_url': website_url,
            'sections_crawled': [],
            'total_articles': 0,
            'total_errors': 0,
            'crawl_duration': 0,
            'articles': [],
            'errors': []
        }

        start_time = time.time()

        try:
            # If no sections provided, discover them
            if not sections:
                structure = self.discover_site_structure(website_url)
                if not structure['success']:
                    result['errors'].append(f"Could not discover site structure: {structure['error']}")
                    return result

                sections = [s['url'] for s in structure['sections'][:5]]  # Limit to 5 sections

            # Crawl each section
            all_articles = []
            for section_url in sections:
                logger.info(f"Crawling section: {section_url}")

                section_result = self.crawl_section(section_url)
                result['sections_crawled'].append({
                    'url': section_url,
                    'success': section_result['success'],
                    'articles_found': section_result['total_found'],
                    'articles_extracted': section_result['total_extracted'],
                    'errors': section_result['errors']
                })

                if section_result['success']:
                    all_articles.extend(section_result['articles'])

                result['total_errors'] += len(section_result['errors'])
                result['errors'].extend(section_result['errors'])

                # Respectful delay between sections
                time.sleep(2)

            result['articles'] = all_articles
            result['total_articles'] = len(all_articles)
            result['success'] = True

        except Exception as e:
            error_msg = f"Website crawl failed for {website_url}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        finally:
            result['crawl_duration'] = time.time() - start_time

        return result

    def detect_spa_framework(self, website_url: str) -> Dict[str, any]:
        """
        Detect if a website is a Single Page Application (SPA) using JavaScript frameworks

        Args:
            website_url: URL of the website to analyze

        Returns:
            Dict containing detection results
        """
        result = {
            'is_spa': False,
            'framework': None,
            'confidence': 'low',
            'indicators': [],
            'article_link_ratio': 0.0
        }

        try:
            response = self.session.get(website_url, timeout=self.timeout)
            response.raise_for_status()

            content = response.text.lower()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for JavaScript framework indicators
            frameworks_detected = []

            if 'react' in content or '__react' in content or 'data-reactroot' in content:
                frameworks_detected.append('React')
            if 'vue' in content or 'v-app' in content or '__vue' in content:
                frameworks_detected.append('Vue')
            if 'ng-app' in content or 'angular' in content or 'ng-version' in content:
                frameworks_detected.append('Angular')
            if '__next' in content or '_next' in content:
                frameworks_detected.append('Next.js')

            # Check for minimal HTML content (typical of SPAs)
            body_text = soup.find('body')
            if body_text:
                visible_text = body_text.get_text(strip=True)
                # If body has very little text but page loads in browser, likely SPA
                if len(visible_text) < 500:
                    result['indicators'].append('minimal_body_content')

            # Check script to content ratio
            scripts = soup.find_all('script')
            script_size = sum(len(str(script)) for script in scripts)
            body_size = len(str(soup.find('body'))) if soup.find('body') else 0

            if body_size > 0 and script_size > body_size * 2:
                result['indicators'].append('high_script_ratio')

            # Check for article-like links
            total_links = len(soup.find_all('a', href=True))
            article_patterns = [
                'article', 'post', 'noticia', 'news', 'story'
            ]
            article_like_links = 0
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                if any(pattern in href or pattern in text for pattern in article_patterns):
                    article_like_links += 1

            if total_links > 10:
                result['article_link_ratio'] = article_like_links / total_links
                if result['article_link_ratio'] < 0.05:  # Less than 5% article links
                    result['indicators'].append('low_article_link_ratio')

            # Determine if it's a SPA
            if frameworks_detected:
                result['is_spa'] = True
                result['framework'] = ', '.join(frameworks_detected)
                result['confidence'] = 'high'
            elif len(result['indicators']) >= 2:
                result['is_spa'] = True
                result['framework'] = 'Unknown JavaScript framework'
                result['confidence'] = 'medium'

        except Exception as e:
            logger.warning(f"SPA detection failed for {website_url}: {e}")

        return result

    def _check_robots_txt(self, url: str) -> bool:
        """Check if crawling is allowed by robots.txt"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True

    def _discover_sections(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Discover navigation sections from the homepage"""
        sections = []

        # Common navigation selectors
        nav_selectors = [
            'nav ul li a',
            '.navbar ul li a',
            '.menu ul li a',
            '.navigation ul li a',
            'header nav a',
            '.main-menu a',
            '.primary-menu a',
            '.nav-menu a'
        ]

        for selector in nav_selectors:
            nav_links = soup.select(selector)

            for link in nav_links:
                text = link.get_text().strip()
                href = link.get('href')

                if not text or not href:
                    continue

                # Skip non-section links
                skip_keywords = [
                    'home', 'inicio', 'contacto', 'contact', 'about', 'acerca',
                    'buscar', 'search', 'suscribir', 'subscribe', 'login',
                    'facebook', 'twitter', 'instagram', 'youtube'
                ]

                if any(keyword in text.lower() for keyword in skip_keywords):
                    continue

                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)

                # Only include URLs from the same domain
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    sections.append({
                        'title': text,
                        'url': absolute_url,
                        'type': 'navigation'
                    })

            if sections:  # If we found sections, stop trying other selectors
                break

        # Remove duplicates
        seen_urls = set()
        unique_sections = []
        for section in sections:
            if section['url'] not in seen_urls:
                seen_urls.add(section['url'])
                unique_sections.append(section)

        return unique_sections[:10]  # Limit to 10 sections

    def _analyze_article_patterns(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Analyze patterns in article links to understand site structure"""
        patterns = []

        # Look for common article link patterns
        article_selectors = [
            'article h2 a',
            'article h3 a',
            '.post-title a',
            '.entry-title a',
            '.article-title a',
            '.news-title a',
            'h2.title a',
            'h3.title a',
            '.headline a'
        ]

        for selector in article_selectors:
            links = soup.select(selector)
            if len(links) >= 3:  # If we find at least 3 matching links, it's likely a pattern
                urls = [urljoin(base_url, link.get('href')) for link in links if link.get('href')]

                # Analyze URL patterns
                pattern_info = self._analyze_url_pattern(urls)
                if pattern_info:
                    patterns.append({
                        'selector': selector,
                        'sample_count': len(links),
                        'url_pattern': pattern_info,
                        'confidence': 'high' if len(links) >= 5 else 'medium'
                    })

        return patterns

    def _analyze_url_pattern(self, urls: List[str]) -> Optional[Dict]:
        """Analyze a list of URLs to find common patterns"""
        if len(urls) < 2:
            return None

        # Extract path patterns
        paths = [urlparse(url).path for url in urls]

        # Look for common path structure
        path_segments = [path.strip('/').split('/') for path in paths]

        if not path_segments:
            return None

        # Find common prefixes
        min_segments = min(len(segments) for segments in path_segments)
        common_prefix = []

        for i in range(min_segments):
            segment_values = [segments[i] for segments in path_segments if i < len(segments)]
            if len(set(segment_values)) == 1:  # All segments are the same
                common_prefix.append(segment_values[0])
            else:
                break

        return {
            'common_prefix': '/'.join(common_prefix) if common_prefix else '',
            'sample_urls': urls[:5],
            'total_urls': len(urls)
        }

    def _discover_pagination_patterns(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Discover pagination patterns for navigating through article lists"""
        patterns = []

        # Common pagination selectors
        pagination_selectors = [
            '.pagination a',
            '.pager a',
            '.page-numbers a',
            '.nav-links a',
            'nav[aria-label="pagination"] a'
        ]

        for selector in pagination_selectors:
            links = soup.select(selector)
            if links:
                next_links = []
                for link in links:
                    text = link.get_text().strip().lower()
                    href = link.get('href')

                    if href and any(keyword in text for keyword in ['next', 'siguiente', '>', '»']):
                        next_links.append(urljoin(base_url, href))

                if next_links:
                    patterns.append({
                        'selector': selector,
                        'next_urls': next_links,
                        'type': 'next_page'
                    })

        return patterns

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract article links from a section page"""
        article_links = []

        # Try multiple strategies to find article links
        strategies = [
            # Strategy 1: Article tags with headlines
            {
                'selector': 'article h2 a, article h3 a, article h1 a',
                'priority': 'high'
            },
            # Strategy 2: Common news site patterns
            {
                'selector': '.post-title a, .entry-title a, .article-title a, .news-title a',
                'priority': 'high'
            },
            # Strategy 3: Generic headline patterns
            {
                'selector': 'h2 a, h3 a',
                'priority': 'medium'
            },
            # Strategy 4: Links within news containers
            {
                'selector': '.news a, .article a, .post a',
                'priority': 'low'
            }
        ]

        seen_urls = set()

        for strategy in strategies:
            links = soup.select(strategy['selector'])

            for link in links:
                href = link.get('href')
                text = link.get_text().strip()

                if not href or not text or len(text) < 10:
                    continue

                absolute_url = urljoin(base_url, href)

                # Skip if already seen
                if absolute_url in seen_urls:
                    continue

                # Only include URLs from the same domain
                if urlparse(absolute_url).netloc != urlparse(base_url).netloc:
                    continue

                # Skip non-article URLs
                skip_patterns = [
                    r'/(tag|tags|categoria|category|autor|author)/',
                    r'/page/\d+',
                    r'/#',
                    r'\.(jpg|jpeg|png|gif|pdf|doc|docx)$'
                ]

                if any(re.search(pattern, absolute_url) for pattern in skip_patterns):
                    continue

                seen_urls.add(absolute_url)
                article_links.append({
                    'url': absolute_url,
                    'title': text,
                    'section': self._extract_section_from_url(absolute_url),
                    'priority': strategy['priority']
                })

                # Limit number of articles per strategy
                if len(article_links) >= self.max_articles:
                    break

            if len(article_links) >= self.max_articles:
                break

        # Sort by priority (high priority first)
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        article_links.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)

        return article_links

    def _extract_section_from_url(self, url: str) -> Optional[str]:
        """Extract section name from article URL"""
        try:
            path = urlparse(url).path.strip('/')
            segments = path.split('/')

            # Look for common section indicators
            section_indicators = ['noticias', 'news', 'deportes', 'sports', 'economia', 'economia',
                                  'politica', 'politics', 'cultura', 'culture', 'tecnologia', 'tech']

            for segment in segments:
                if segment.lower() in section_indicators:
                    return segment

            # Return first meaningful segment
            if segments and segments[0]:
                return segments[0]

        except Exception:
            pass

        return None

    def _extract_article(self, article_url: str, section: str = None) -> Optional[Dict]:
        """Extract full article content from URL"""
        try:
            response = self.session.get(article_url, timeout=self.timeout)
            response.raise_for_status()

            # Use trafilatura for main content extraction
            article_text = trafilatura.extract(
                response.content,
                config=self.trafilatura_config,
                include_comments=False,
                include_tables=True
            )

            if not article_text or len(article_text) < 200:
                logger.warning(f"Article too short or empty: {article_url}")
                return None

            # Extract metadata using trafilatura
            metadata = trafilatura.extract_metadata(response.content)

            # Parse HTML for additional metadata
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = None
            if metadata and metadata.title:
                title = metadata.title
            else:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()

            # Extract author
            author = None
            if metadata and metadata.author:
                author = metadata.author
            else:
                # Try common author selectors
                author_selectors = [
                    '.author', '.byline', '.writer', '.journalist',
                    '[rel="author"]', '.post-author', '.article-author'
                ]
                for selector in author_selectors:
                    author_element = soup.select_one(selector)
                    if author_element:
                        author = author_element.get_text().strip()
                        break

            # Extract publication date
            published_date = None
            if metadata and metadata.date:
                published_date = metadata.date
            else:
                # Use htmldate for date extraction
                date_result = htmldate.find_date(response.content, original_date=True)
                if date_result:
                    try:
                        published_date = datetime.strptime(date_result, '%Y-%m-%d')
                    except ValueError:
                        pass

            # If no date found, try manual extraction
            if not published_date:
                date_selectors = [
                    'time[datetime]', '.date', '.publish-date', '.article-date',
                    '.post-date', '[itemprop="datePublished"]'
                ]
                for selector in date_selectors:
                    date_element = soup.select_one(selector)
                    if date_element:
                        date_text = date_element.get('datetime') or date_element.get_text()
                        published_date = self._parse_date_text(date_text)
                        if published_date:
                            break

            # Default to current date if no date found
            if not published_date:
                published_date = datetime.now()

            return {
                'title': title or 'Sin título',
                'content': article_text,
                'url': article_url,
                'author': author or '',
                'published_date': published_date,
                'section': section or '',
                'crawl_section': section or self._extract_section_from_url(article_url) or '',
                'extracted_metadata': {
                    'word_count': len(article_text.split()),
                    'extraction_method': 'trafilatura',
                    'has_metadata': bool(metadata)
                }
            }

        except Exception as e:
            logger.error(f"Article extraction failed for {article_url}: {str(e)}")
            return None

    def _parse_date_text(self, date_text: str) -> Optional[datetime]:
        """Parse various date formats commonly found in Spanish news sites"""
        if not date_text:
            return None

        # Common Spanish date patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2}) de (\w+) de (\d{4})',  # DD de MMMM de YYYY
        ]

        spanish_months = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        for pattern in patterns:
            match = re.search(pattern, date_text.lower())
            if match:
                try:
                    if 'de' in pattern:  # Spanish format
                        day, month_name, year = match.groups()
                        month = spanish_months.get(month_name.lower())
                        if month:
                            return datetime(int(year), month, int(day))
                    else:
                        # Numeric formats
                        if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                            year, month, day = match.groups()
                        else:  # DD/MM/YYYY
                            day, month, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                except ValueError:
                    continue

        # Try parsing with dateutil as fallback
        try:
            from dateutil import parser
            return parser.parse(date_text)
        except Exception:
            pass

        return None