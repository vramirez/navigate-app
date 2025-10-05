---
id: task-3
title: Test crawler system with real Colombian news websites
status: To Do
assignee:
  - '@victor'
reporter: '@victor'
createdDate: '2025-10-05 15:10'
labels:
  - backend
  - phase-3
  - testing
  - crawler
priority: high
dependencies: []
parent: task-9
milestone: Phase 3
---

## Description

Thoroughly test the Phase 2 crawler system (RSS discovery, manual crawling, content processing) with real Colombian news websites to ensure production readiness.

This task validates that the advanced crawler infrastructure works reliably with actual Colombian news sources, handling various website structures, RSS formats, and content types.

## Test Targets - Colombian News Sources

### Major National Newspapers
1. **El Tiempo** (https://www.eltiempo.com/) - Colombia's largest newspaper
2. **El Espectador** (https://www.elespectador.com/) - Major national daily
3. **Semana** (https://www.semana.com/) - News magazine
4. **Portafolio** (https://www.portafolio.co/) - Business/economic news

### Regional News (Medellín Focus)
5. **El Colombiano** (https://www.elcolombiano.com/) - Medellín's main newspaper
6. **Metro de Medellín** (https://www.metrodemedellin.gov.co/al-dia/noticias) - Local transit news
7. **Telemedellín** (https://telemedellin.tv/) - Local TV news

### Specialty Sources
8. **La República** (https://www.larepublica.co/) - Business focus
9. **RCN Noticias** (https://www.canalrcn.com/noticias) - National TV news
10. **Caracol Noticias** (https://noticias.caracoltv.com/) - National TV news

## Implementation Plan

1. **Add News Sources via Admin:**
   - Use Django Admin to create NewsSource entries
   - Add all 10 Colombian sources listed above
   - Set country='Colombia' for all

2. **Test RSS Discovery:**
   - Run RSS discovery for each source
   - Document which sources have RSS vs require manual crawling
   - Verify RSS feeds are correctly detected and stored

3. **Test Manual Crawling:**
   - For sources without RSS, test manual crawler
   - Verify article extraction quality
   - Check metadata extraction (title, date, author)

4. **Test Content Processing:**
   - Verify deduplication works
   - Check Spanish content handling
   - Validate date parsing for Colombian formats

5. **Performance Testing:**
   - Measure crawl duration per source
   - Check rate limiting respects robots.txt
   - Monitor memory/CPU usage during bulk crawls

6. **Error Handling:**
   - Test with unreachable URLs
   - Test with malformed HTML
   - Verify graceful failure and logging

7. **Documentation:**
   - Document RSS availability per source
   - Create troubleshooting guide
   - Note any source-specific quirks

## Acceptance Criteria

- [ ] All 10 Colombian sources added to database
- [ ] RSS discovery attempted for all sources (results documented)
- [ ] Manual crawling tested for non-RSS sources
- [ ] At least 50 real Colombian news articles extracted
- [ ] No errors in Spanish content (accents, ñ, special characters)
- [ ] Crawl history logs show successful operations
- [ ] Performance metrics documented (avg crawl time per source)
- [ ] Error handling validated with edge cases
- [ ] robots.txt compliance verified for all sources
- [ ] Documentation updated with source-specific notes

## Notes

**Expected Outcomes:**
- RSS availability: ~70-80% of major sources
- Manual crawling: Required for government/local sites
- Article quality: 95%+ should have complete metadata

**Common Issues to Watch:**
- Colombian date formats: "5 de octubre de 2025"
- Paywalls on premium sources
- Dynamic content loading (JavaScript-heavy sites)
- Cloudflare protection on some sites

**Performance Targets:**
- RSS crawl: <10 seconds per source
- Manual crawl: <30 seconds per source
- Bulk crawl (10 sources): <5 minutes total

## Testing Checklist

### Per Source Testing
- [ ] El Tiempo - RSS discovery + crawl
- [ ] El Espectador - RSS discovery + crawl
- [ ] Semana - RSS discovery + crawl
- [ ] Portafolio - RSS discovery + crawl
- [ ] El Colombiano - RSS discovery + crawl
- [ ] Metro de Medellín - RSS discovery + crawl
- [ ] Telemedellín - RSS discovery + crawl
- [ ] La República - RSS discovery + crawl
- [ ] RCN Noticias - RSS discovery + crawl
- [ ] Caracol Noticias - RSS discovery + crawl

### System Testing
- [ ] Bulk crawl operation (all sources)
- [ ] Deduplication across multiple sources
- [ ] Error recovery from network failures
- [ ] Content quality validation (Spanish)
- [ ] Admin interface usability test

## Related Tasks

- Blocks: task-4 (ML integration needs tested real data)
- Related: task-1 (frontend needs validated news articles)
