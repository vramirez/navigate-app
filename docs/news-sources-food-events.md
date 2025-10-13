c# Food & Events News Sources Configuration

**Date**: 2025-10-06
**Purpose**: Configure Colombian news sources focused on food, gastronomy, restaurants, and events relevant for pub/restaurant business intelligence.

## Summary

Successfully configured **6 new specialized sources** focused on food and events:
- **4 El Tiempo specialized RSS feeds** (gastronomy, culture, entertainment, music)
- **1 Medellín hyper-local source** (Vivir en El Poblado)
- **1 premium gastronomy source** (Revista Diners - currently blocked by robots.txt)

**Total articles collected**: 51 food/events articles from new sources

## New Sources Configuration

### 1. El Tiempo - Gastronomía (ID: 8)
- **Type**: RSS Feed
- **URL**: https://www.eltiempo.com/cultura/gastronomia
- **RSS**: https://www.eltiempo.com/rss/cultura_gastronomia.xml
- **Status**: ✅ Active - 11 articles collected
- **Content**: Restaurant reviews, food trends, gastronomy news, chef profiles
- **Coverage**: National (Colombia)
- **Relevance**: HIGH - Direct restaurant and food industry coverage

### 2. El Tiempo - Cultura (ID: 9)
- **Type**: RSS Feed
- **URL**: https://www.eltiempo.com/cultura
- **RSS**: https://www.eltiempo.com/rss/cultura.xml
- **Status**: ✅ Active - 10 articles collected
- **Content**: Cultural events, festivals, art exhibitions, theater
- **Coverage**: National (Colombia)
- **Relevance**: HIGH - Events that drive foot traffic to businesses

### 3. El Tiempo - Entretenimiento (ID: 10)
- **Type**: RSS Feed
- **URL**: https://www.eltiempo.com/cultura/entretenimiento
- **RSS**: https://www.eltiempo.com/rss/cultura_entretenimiento.xml
- **Status**: ✅ Active - 10 articles collected
- **Content**: Entertainment news, cinema, TV, celebrity events
- **Coverage**: National (Colombia)
- **Relevance**: MEDIUM - Entertainment events affecting business traffic

### 4. El Tiempo - Música y Libros (ID: 11)
- **Type**: RSS Feed
- **URL**: https://www.eltiempo.com/cultura/musica-y-libros
- **RSS**: https://www.eltiempo.com/rss/cultura_musica-y-libros.xml
- **Status**: ✅ Active - 10 articles collected
- **Content**: Music concerts, book fairs, literary events
- **Coverage**: National (Colombia)
- **Relevance**: MEDIUM - Relevant for pubs with live music and bookstores

### 5. Vivir en El Poblado (ID: 13)
- **Type**: RSS Feed (auto-discovered)
- **URL**: https://vivirenelpoblado.com
- **RSS**: Auto-discovered during setup
- **Status**: ✅ Active - 10 articles collected
- **Content**: Hyper-local news for El Poblado neighborhood (Medellín's main entertainment district)
- **Coverage**: Medellín - El Poblado neighborhood
- **Relevance**: VERY HIGH - Primary hospitality zone in Medellín
- **Special**: Community newspaper with "Vivir con Sazón" gastronomy section

### 6. Revista Diners (ID: 12)
- **Type**: Manual Crawler
- **URL**: https://revistadiners.com.co/gastronomia
- **RSS**: None
- **Status**: ⚠️ Blocked - robots.txt restriction + Vue SPA
- **Content**: Premium gastronomy, top restaurant rankings, food festivals, chef interviews
- **Coverage**: National (Bogotá, Medellín, Cartagena focus)
- **Relevance**: VERY HIGH - Most authoritative Colombian gastronomy source (60+ years)
- **Issue**: Requires Selenium/headless browser due to Vue.js SPA. Blocked by robots.txt until 2025-10-07.
- **Recommendation**: Consider reaching out to Revista Diners for API access or RSS feed

## Existing Sources Analysis

### Sources with Food/Events Sections (Already Configured)

| Source | Gastronomy Section | Events/Culture | RSS Available | Action Needed |
|--------|-------------------|----------------|---------------|---------------|
| **El Espectador** (ID: 2) | ✅ /entretenimiento/gastronomia | ✅ /el-magazin-cultural | ❌ Main RSS returns 404 | Fix RSS or use manual crawler |
| **El Heraldo** (ID: 5) | ✅ /gastronomia | ✅ /cultura | ❌ No RSS | Add manual crawler for sections |
| **El Colombiano** (ID: 3) | ❌ No dedicated section | ✅ /cultura, /entretenimiento | ❌ No RSS | Add manual crawler for culture |
| **El Universal** (ID: 6) | ⚠️ /ocio (recipes) | ✅ /cultural | ❌ No RSS | Add manual crawler for sections |

### Sources Requiring Investigation

| Source | Status | Action |
|--------|--------|--------|
| **Caracol Radio** (ID: 4) | Blocked automated access | Manual investigation or direct contact |
| **W Radio** (ID: 7) | Blocked automated access | Manual investigation or direct contact |

## Additional El Tiempo RSS Feeds Available (Not Yet Added)

These feeds are available but not yet configured. Add if needed:

- **Cinema & TV**: https://www.eltiempo.com/rss/cultura_cine-y-tv.xml
- **Art & Theater**: https://www.eltiempo.com/rss/cultura_arte-y-teatro.xml
- **People/Celebrities**: https://www.eltiempo.com/rss/cultura_gente.xml
- **Vida (Lifestyle)**: https://www.eltiempo.com/rss/vida.xml
- **Travel**: https://www.eltiempo.com/rss/vida_viajar.xml

## Article Statistics

### Current Count (as of 2025-10-06)

```
Total Colombian sources: 13
Active sources: 12 (1 blocked)
Total articles collected: 349

Food & Events sources (new): 5 active
Food & Events articles: 51

Breakdown by source:
- El Tiempo Gastronomía: 11
- El Tiempo Cultura: 10
- El Tiempo Entretenimiento: 10
- El Tiempo Música y Libros: 10
- Vivir en El Poblado: 10
- Revista Diners: 0 (blocked)
```

## Implementation Notes

### What Was Done

1. ✅ Created 4 specialized El Tiempo RSS feeds
2. ✅ Added Vivir en El Poblado (Medellín hyper-local)
3. ✅ Added Revista Diners (premium gastronomy)
4. ✅ Tested all new feeds successfully
5. ✅ Collected 51 food/events articles
6. ✅ Identified existing sources with food/events sections

### What's Next

#### Priority 1: Configure Existing Sources
- Add manual crawler URLs for food/events sections of existing sources:
  - El Espectador → /entretenimiento/gastronomia
  - El Heraldo → /gastronomia and /cultura
  - El Colombiano → /cultura and /entretenimiento
  - El Universal → /ocio and /cultural

#### Priority 2: Troubleshooting
- **Revista Diners**: Requires Selenium/headless browser support or direct RSS/API access
- **Caracol/W Radio**: Investigate blocking issues or contact for API access

#### Priority 3: Additional Specialized Sources (from research)
Consider adding these high-value sources:
- **Visit Bogotá** (visitbogota.co) - Official Bogotá events calendar
- **Cambio Colombia Gastronomía** - Food festivals with dates/prices
- **Cartagena de Indias Travel** - Cartagena cultural calendar
- **LikeBarranquilla** - Barranquilla culture and events

## Technical Details

### Database Structure

Each news source has:
- `id`: Unique identifier
- `name`: Display name
- `source_type`: 'rss', 'online', 'newspaper', etc.
- `country`: 'CO' for Colombia
- `website_url`: Main website
- `rss_url`: RSS feed URL (if available)
- `crawler_url`: URL for manual crawling
- `crawl_status`: Status of crawlability
- `rss_discovered`: Boolean for auto-discovered RSS
- `manual_crawl_enabled`: Boolean for manual crawling

### Crawling Methods Used

1. **RSS Feeds**: Primary method for El Tiempo specialized sources
2. **RSS Discovery**: Auto-discovered RSS for Vivir en El Poblado
3. **Manual Crawling**: Attempted for Revista Diners (blocked)

### Commands Used

```python
from news.services.crawler_orchestrator import CrawlerOrchestratorService
from news.models import NewsSource

orchestrator = CrawlerOrchestratorService()

# Setup source (discover RSS and structure)
source = NewsSource.objects.get(id=13)
result = orchestrator.setup_news_source(source)

# Crawl source for articles
result = orchestrator.crawl_source(source_id)
```

## Key Findings from Research

1. **El Tiempo is most comprehensive**: Multiple specialized RSS feeds for food and culture
2. **Most sources lack accessible RSS**: Manual crawling required for many sources
3. **Premium sources are protected**: Revista Diners blocks automated crawling
4. **Hyper-local sources exist**: Vivir en El Poblado provides neighborhood-level intel
5. **Government portals available**: Official city tourism sites have event calendars

## Recommendations for Business Value

### For Restaurants & Pubs
- **HIGH**: Monitor gastronomy articles for food trends and competitor openings
- **HIGH**: Track cultural events and festivals that drive foot traffic
- **MEDIUM**: Follow entertainment news for major concerts and shows
- **HIGH**: Hyper-local sources like Vivir en El Poblado for neighborhood dynamics

### For Bookstores
- **HIGH**: Music and books section for book fairs and literary events
- **MEDIUM**: Culture section for author appearances and readings
- **LOW**: Gastronomy (unless bookstore has café)

### For Coffee Shops
- **HIGH**: Gastronomy trends and specialty coffee features
- **HIGH**: Cultural events near coffee shop location
- **MEDIUM**: Entertainment events for demographic insights

## Related Documentation

- Main project roadmap: `/home/vramirez/projects/navigate-app/backlog.md`
- Crawler system documentation: `/home/vramirez/projects/navigate-app/backend/news/services/`
- Full research report: Available in Claude conversation (2025-10-06)

## Contact & Support

For issues with specific sources:
- **Revista Diners**: Consider requesting official API access
- **Caracol/W Radio**: May require direct contact for RSS feeds
- **Government portals**: Usually have publicly documented APIs

---

**Last Updated**: 2025-10-06
**Status**: ✅ Implemented and tested
**Next Review**: When adding new cities or business types
