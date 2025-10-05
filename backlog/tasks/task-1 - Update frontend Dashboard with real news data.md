---
id: task-1
title: Update frontend Dashboard with real news data
status: To Do
assignee:
  - '@claude'
reporter: '@victor'
createdDate: '2025-10-05 15:00'
labels:
  - frontend
  - phase-3
  - integration
priority: high
dependencies: []
parent: task-9
milestone: Phase 3
---

## Description

Replace the mock news data in the React Dashboard component with real news data from the Django API crawler system. This is a critical Phase 3 task to transition from demo data to production-ready news ingestion.

The dashboard currently displays mock news scenarios created during Phase 1. Now that Phase 2 has delivered a fully functional news crawler system with RSS discovery, manual crawling, and content processing, we need to integrate these real news articles into the frontend.

## Implementation Plan

1. Create new API service module for news fetching (`src/services/newsApi.js`)
2. Update Dashboard component to use real API instead of mock data
3. Add loading states for API calls (skeleton screens)
4. Implement error handling for failed API requests
5. Update article card components to handle real news data structure
6. Remove mock data imports from Dashboard
7. Test with real Colombian news sources from database
8. Update documentation and component comments

## Acceptance Criteria

- [ ] Dashboard fetches news from `/api/news/articles/` endpoint
- [ ] Real news displays with proper formatting (title, date, source, content preview)
- [ ] Loading states implemented with skeleton screens or spinners
- [ ] Error handling displays user-friendly messages for API failures
- [ ] No mock data references remain in Dashboard component
- [ ] Article dates display correctly in Spanish format
- [ ] News source attribution visible for each article
- [ ] Responsive design maintained on mobile devices
- [ ] Performance: Initial load < 2 seconds

## Notes

**API Endpoint Details:**
- Backend endpoint: `http://localhost:8000/api/news/articles/`
- Returns paginated list of NewsArticle objects
- Includes fields: title, content, url, published_date, news_source, crawl_date

**Design Considerations:**
- Maintain existing UI/UX patterns from mock version
- Handle Spanish content properly (accents, ñ, date formats)
- Consider pagination for large news volumes
- Real articles may have varying content lengths - handle gracefully

**Testing Strategy:**
- Test with Colombian news sources (El Tiempo, El Espectador)
- Test with empty state (no articles in database)
- Test error states (backend down, network issues)
- Validate Spanish date formatting

## Related Tasks

- Depends on: None (Phase 2 crawler already complete)
- Blocks: task-4 (ML integration needs real news in frontend)
- Related: task-2 (legacy mock data preservation)
