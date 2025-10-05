---
id: task-4
title: Integrate real news data with ML recommendation pipeline
status: To Do
assignee:
  - '@claude'
reporter: '@victor'
createdDate: '2025-10-05 15:15'
labels:
  - backend
  - ml
  - phase-3
  - integration
priority: high
dependencies:
  - task-3
milestone: Phase 3
---

## Description

Connect the Phase 2 news crawler system with the existing ML recommendation engine to generate business recommendations from real Colombian news articles instead of mock scenarios.

Currently, the ML engine (backend/ml_engine/) processes mock news data. This task adapts it to work with real news articles from the crawler, leveraging spaCy Spanish NLP for entity extraction, event detection, and business relevance scoring.

## Implementation Plan

1. **Audit Current ML Pipeline:**
   - Review ml_engine/services/ to understand current processing flow
   - Identify mock data touchpoints to be replaced
   - Document existing recommendation algorithm

2. **Adapt News Article Processing:**
   - Update ML pipeline to consume NewsArticle model from news app
   - Ensure spaCy Spanish model processes real content correctly
   - Validate entity extraction works with varied news sources

3. **Event Detection Enhancement:**
   - Improve event extraction from real news (dates, locations, keywords)
   - Handle different article structures from various sources
   - Extract business-relevant signals (events, trends, opportunities)

4. **Business Matching Logic:**
   - Update keyword matching to work with real articles
   - Enhance relevance scoring for actual news content
   - Consider article source authority in scoring

5. **Recommendation Generation:**
   - Adapt recommendation templates for real-world scenarios
   - Ensure recommendations link to actual news URLs
   - Add confidence scores based on real article analysis

6. **Performance Optimization:**
   - Batch processing for multiple articles
   - Cache NLP results to avoid reprocessing
   - Optimize spaCy pipeline for production load

7. **Testing & Validation:**
   - Create test suite with real Colombian news samples
   - Validate recommendation quality and relevance
   - Compare results with mock data baseline

8. **Admin Interface Update:**
   - Update Django Admin to show real recommendations
   - Add debugging tools for ML pipeline
   - Display recommendation generation logs

## Acceptance Criteria

- [ ] ML pipeline processes real NewsArticle objects (not mock data)
- [ ] spaCy Spanish NLP extracts entities from real news correctly
- [ ] Event detection identifies relevant business events from articles
- [ ] Business keyword matching works with actual content
- [ ] Recommendations generated link to real news URLs
- [ ] Confidence scores accurately reflect article relevance
- [ ] System handles articles without clear business relevance gracefully
- [ ] Performance: Process 100 articles in < 5 minutes
- [ ] Test coverage: 80%+ for new integration code
- [ ] Admin interface displays real recommendations with source articles

## Notes

**Current ML Components:**
- Location: `backend/ml_engine/`
- NLP Engine: spaCy Spanish model (es_core_news_sm or es_core_news_md)
- Current input: Mock news dictionaries
- Output: Recommendation objects with action_type, description, priority

**Integration Points:**
- News articles: `backend/news/models.py::NewsArticle`
- Businesses: `backend/businesses/models.py::Business`
- Recommendations: `backend/recommendations/models.py::Recommendation`

**Challenges to Address:**
- Real news may not always have clear business implications
- Article quality varies by source
- Spanish NLP may need tuning for Colombian dialect
- Performance with large article volumes

**Success Metrics:**
- Recommendation relevance: 80%+ (manual validation)
- False positive rate: < 20%
- Processing speed: 100+ articles/minute
- Entity extraction accuracy: 85%+

## Testing Strategy

**Unit Tests:**
- Entity extraction from Colombian news samples
- Event detection with various article types
- Business matching algorithm accuracy
- Recommendation scoring consistency

**Integration Tests:**
- End-to-end: Crawled article → ML processing → Recommendation
- Multiple sources → Deduplication → Single recommendation
- Business with specific keywords → Relevant recommendations only

**Validation Data:**
- Use 50 real articles from El Tiempo, El Espectador
- Mix of event news, business news, general news
- Manually label expected business relevance
- Compare ML output with expected results

## Related Tasks

- Depends on: task-3 (needs validated Colombian news articles)
- Blocks: None (enables Phase 3 completion)
- Related: task-1 (frontend displays these recommendations)
- Related: task-5 (enhanced ML features build on this integration)
