# NaviGate News Crawler System - Complete Guide

## Overview

The NaviGate News Crawler System is a comprehensive solution for automatically ingesting news content from websites worldwide. It supports both RSS feed discovery and manual website crawling, with intelligent content extraction and processing.

## Features

### 🤖 Automatic RSS Discovery
- Detects RSS/Atom feeds from any website
- Multiple discovery strategies (HTML parsing, common paths, CMS patterns)
- Validates and selects the best available feed
- Supports WordPress, Drupal, Joomla, and custom CMS

### 🕷️ Manual Website Crawling
- Crawls websites without RSS feeds
- Uses Trafilatura for high-quality content extraction
- Analyzes site structure and navigation
- Handles dynamic content and JavaScript-rendered pages

### 🌍 Global News Support
- Support for news websites from any country
- Country-based organization with Colombia prioritized
- Spanish and English content processing
- Handles various date formats and encodings

### 🛡️ Ethical Crawling
- Respects robots.txt directives
- Implements rate limiting and delays
- Proper user-agent identification
- Comprehensive error handling and logging

### 📊 Admin Management
- Visual crawler status indicators
- One-click setup and crawling operations
- Bulk operations for multiple sources
- Detailed crawl history and monitoring

## Quick Start Guide

### 1. Adding a News Source

1. **Access Admin Panel**: Navigate to http://localhost:8000/admin
2. **Go to News Sources**: Click "News sources" in the News section
3. **Add Source**: Click "Add News Source" button
4. **Configure**:
   ```
   Name: El Tiempo
   Source Type: Periódico
   Country: Colombia
   Crawler URL: https://www.eltiempo.com
   ```

### 2. Automatic Setup

After adding a source, click the **"Setup"** button to:
- Discover RSS feeds automatically
- Analyze website structure
- Configure crawling parameters
- Test initial content extraction

### 3. Manual Operations

Use individual buttons for specific operations:
- **"Discover RSS"**: Find RSS feeds only
- **"Analyze Site"**: Map website sections
- **"Crawl Now"**: Extract articles immediately

### 4. Bulk Operations

Select multiple sources and use admin actions:
- **"Setup selected sources"**: Batch RSS discovery
- **"Crawl selected sources"**: Batch article extraction
- **"Discover RSS feeds"**: Batch RSS discovery

## Technical Architecture

### Service Layer (`backend/news/services/`)

#### RSS Discovery Service
```python
from news.services.rss_discovery import RSSDiscoveryService

service = RSSDiscoveryService()
result = service.discover_rss_feeds("https://example-news.com")

if result['success']:
    print(f"Found {len(result['feeds'])} RSS feeds")
    print(f"Primary feed: {result['primary_feed']['url']}")
```

#### Manual Crawler Service
```python
from news.services.manual_crawler import ManualCrawlerService

crawler = ManualCrawlerService()
result = crawler.crawl_website("https://example-news.com")

print(f"Extracted {result['total_articles']} articles")
```

#### Content Processor Service
```python
from news.services.content_processor import ContentProcessorService

processor = ContentProcessorService()
result = processor.process_news_source(source)

print(f"Saved {result['articles_saved']} new articles")
```

#### Crawler Orchestrator Service
```python
from news.services.crawler_orchestrator import CrawlerOrchestratorService

orchestrator = CrawlerOrchestratorService()

# Setup a source
setup_result = orchestrator.setup_news_source(source)

# Crawl a source
crawl_result = orchestrator.crawl_source(source.id)

# Bulk crawl by country
bulk_result = orchestrator.bulk_crawl(country_code='CO')
```

### Database Models

#### NewsSource (Enhanced)
```python
class NewsSource(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    crawler_url = models.URLField(blank=True)
    rss_discovered = models.BooleanField(default=False)
    discovered_rss_url = models.URLField(blank=True)
    manual_crawl_enabled = models.BooleanField(default=False)
    crawl_sections = models.JSONField(default=list, blank=True)
    # ... other fields
```

#### CrawlHistory (New)
```python
class CrawlHistory(models.Model):
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    crawl_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    articles_found = models.PositiveIntegerField(default=0)
    articles_saved = models.PositiveIntegerField(default=0)
    crawl_duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(blank=True)
```

#### NewsArticle (Enhanced)
```python
class NewsArticle(models.Model):
    # ... existing fields
    crawl_section = models.CharField(max_length=200, blank=True)
    # Enhanced metadata fields for better ML processing
```

## API Reference

### Source Management Endpoints

#### Setup Source
```http
POST /api/news/sources/{id}/setup/
```
Performs complete source setup including RSS discovery and structure analysis.

**Response:**
```json
{
  "success": true,
  "message": "Source setup completed successfully",
  "setup_result": {
    "rss_discovered": true,
    "site_structure_analyzed": true,
    "setup_actions": [
      "RSS feed discovered: https://example.com/feed",
      "Site structure analyzed: 5 sections found"
    ],
    "recommendations": [
      "RSS feed available - recommended primary method"
    ]
  }
}
```

#### Discover RSS
```http
POST /api/news/sources/{id}/discover-rss/
```
Discovers RSS feeds for a specific source.

#### Crawl Source
```http
POST /api/news/sources/{id}/crawl/?force_manual=false
```
Extracts articles from a source using the best available method.

**Response:**
```json
{
  "success": true,
  "message": "Crawl completed successfully: 15 articles saved",
  "crawl_result": {
    "method_used": "rss",
    "articles_found": 20,
    "articles_saved": 15,
    "articles_updated": 2,
    "articles_skipped": 3,
    "processing_duration": 45.2
  }
}
```

#### Crawl History
```http
GET /api/news/sources/{id}/crawl-history/?limit=5
```
Retrieves recent crawl history for a source.

### System Operations

#### Bulk Crawl
```http
POST /api/news/crawler/bulk-crawl/?country=CO
Content-Type: application/json

{
  "source_ids": [1, 2, 3]
}
```

#### System Status
```http
GET /api/news/crawler/system-status/
```

**Response:**
```json
{
  "success": true,
  "system_status": "operational",
  "statistics": {
    "total_active_sources": 25,
    "sources_with_rss": 18,
    "sources_with_manual_crawl": 12,
    "recent_successful_crawls": 45,
    "recent_failed_crawls": 3,
    "success_rate": 93.8,
    "country_breakdown": {
      "CO": 15,
      "ES": 6,
      "MX": 4
    }
  }
}
```

#### Crawler Statistics
```http
GET /api/news/crawler/stats/?days=7
```

## Configuration Options

### Environment Variables
```bash
# Crawler settings
CRAWLER_TIMEOUT=15
CRAWLER_USER_AGENT="NaviGate-Bot/1.0"
CRAWLER_MAX_ARTICLES=50
CRAWLER_RATE_LIMIT=1.0

# Content processing
CONTENT_MIN_LENGTH=200
CONTENT_MAX_AGE_DAYS=30
DUPLICATE_CHECK_ENABLED=true
```

### Admin Configuration

#### Source Types
- **Periódico**: Traditional newspapers
- **Medio digital**: Digital-only news outlets
- **Redes sociales**: Social media sources
- **Feed RSS**: Direct RSS feeds
- **Entrada manual**: Manually entered content

#### Crawler Settings
- **Timeout**: Request timeout in seconds (default: 15)
- **User Agent**: Bot identification string
- **Rate Limiting**: Delay between requests
- **Content Validation**: Minimum article length
- **Error Handling**: Retry attempts and backoff

## Monitoring and Troubleshooting

### Admin Interface Monitoring

1. **Source List View**:
   - Visual status indicators (🟢 RSS, 🔵 Manual, 🟡 Setup Needed, 🔴 Not Configured)
   - Last crawl information
   - Quick action buttons

2. **Crawl History**:
   - Detailed logs of all crawl attempts
   - Success/failure rates
   - Performance metrics
   - Error messages

3. **System Dashboard**:
   - Overall crawler health
   - Performance statistics
   - Country breakdown

### Common Issues and Solutions

#### RSS Discovery Fails
**Problem**: No RSS feeds found for a website
**Solution**:
1. Check if the website has RSS feeds manually
2. Try manual crawling instead
3. Verify the website URL is correct

#### Manual Crawling Errors
**Problem**: Manual crawler can't extract articles
**Solutions**:
1. Check robots.txt permissions
2. Verify website structure
3. Increase timeout settings
4. Check for anti-bot measures

#### Content Quality Issues
**Problem**: Extracted content is poor quality
**Solutions**:
1. Adjust minimum content length
2. Check CSS selectors for manual crawling
3. Verify content extraction settings
4. Use RSS feeds when available

#### Performance Issues
**Problem**: Crawling is slow or times out
**Solutions**:
1. Increase timeout settings
2. Reduce concurrent crawls
3. Implement longer delays between requests
4. Check server resources

### Logging and Debugging

#### Enable Debug Logging
```python
import logging
logging.getLogger('news.services').setLevel(logging.DEBUG)
```

#### View Crawl Logs
```bash
# Docker environment
docker logs navigate-backend

# Check specific crawler logs
docker exec navigate-backend python manage.py shell
>>> from news.models import CrawlHistory
>>> CrawlHistory.objects.filter(status='failed').values('error_message')
```

## Best Practices

### Adding News Sources

1. **Verify URL**: Ensure the website is accessible and active
2. **Check robots.txt**: Verify crawling is allowed
3. **Test Setup**: Use the "Setup" button to validate configuration
4. **Monitor Initial Crawls**: Check first few crawl attempts
5. **Adjust Settings**: Fine-tune based on initial results

### Crawling Strategy

1. **Prefer RSS**: RSS feeds are more reliable and efficient
2. **Use Manual as Fallback**: Only when RSS is unavailable
3. **Respect Rate Limits**: Don't overwhelm source websites
4. **Monitor Performance**: Regular check of crawl success rates
5. **Handle Errors Gracefully**: Log and investigate failures

### Content Quality

1. **Set Minimum Length**: Filter out navigation and ads
2. **Validate Dates**: Ensure articles have proper timestamps
3. **Check Duplicates**: Monitor for duplicate content
4. **Review Extracted Text**: Verify content quality regularly
5. **Monitor ML Processing**: Ensure articles feed properly into ML pipeline

## Advanced Usage

### Custom Crawler Configuration

```python
# Custom crawler settings
from news.services.manual_crawler import ManualCrawlerService

crawler = ManualCrawlerService(
    timeout=30,
    max_articles=100,
    user_agent="CustomBot/1.0"
)
```

### Programmatic Source Management

```python
from news.models import NewsSource
from news.services.crawler_orchestrator import CrawlerOrchestratorService

# Create a new source
source = NewsSource.objects.create(
    name="Example News",
    country="CO",
    crawler_url="https://example-news.com",
    source_type="online"
)

# Setup and crawl
orchestrator = CrawlerOrchestratorService()
setup_result = orchestrator.setup_news_source(source)
crawl_result = orchestrator.crawl_source(source.id)
```

### Bulk Operations

```python
# Crawl all Colombian sources
result = orchestrator.bulk_crawl(country_code='CO')

# Crawl specific sources
result = orchestrator.bulk_crawl(source_ids=[1, 2, 3, 4, 5])
```

## Security Considerations

### Ethical Crawling
- Always respect robots.txt
- Implement reasonable rate limiting
- Use proper user-agent identification
- Handle errors gracefully without retrying excessively

### Data Privacy
- Store only publicly available content
- Respect copyright and attribution
- Implement data retention policies
- Allow source removal requests

### System Security
- Validate all input URLs
- Sanitize extracted content
- Implement request timeouts
- Monitor for abuse patterns

## Future Enhancements

### Planned Features
- **Automatic Scheduling**: Periodic crawling without manual intervention
- **Advanced ML Integration**: Real-time content classification
- **Multi-language Support**: Enhanced support for various languages
- **Performance Optimization**: Concurrent crawling and caching
- **Advanced Analytics**: Detailed performance metrics and insights

### Contribution Guidelines
- Follow existing code patterns
- Add comprehensive tests
- Update documentation
- Consider ethical implications
- Test with real-world scenarios

## Support and Maintenance

### Regular Maintenance Tasks
1. **Monitor Crawl Success Rates**: Weekly review of failed crawls
2. **Update Source Configurations**: Adjust settings based on performance
3. **Clean Old Crawl History**: Remove logs older than 30 days
4. **Verify Source Accessibility**: Check for dead or moved websites
5. **Update Dependencies**: Keep crawler libraries up to date

### Getting Help
- Check the admin interface for error messages
- Review crawl history for patterns
- Consult the API documentation
- Monitor system logs for issues
- Use the built-in recommendations system

---

*This guide covers the complete NaviGate News Crawler System. For specific implementation details, refer to the source code in `backend/news/services/` and `backend/news/api/`.*