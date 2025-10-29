---
id: task-18.15
title: 'Documentation and Cleanup for Per-Type System'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - documentation
  - cleanup
dependencies: [task-18.1, task-18.14]
parent: task-18
priority: medium
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Final documentation and code cleanup for the per-business-type relevance system. Update README, document API changes, clean up deprecated code, and create migration guide for any future developers. Ensures system is maintainable and understandable.
<!-- SECTION:DESCRIPTION:END -->

## Documentation Updates

### 1. Update README.md

**File**: `README.md`

Add section about business type system:

```markdown
## Business Type Relevance System

NaviGate uses a per-business-type relevance scoring system to personalize news recommendations.

### How It Works

1. **Business Types**: System supports multiple business types (pub, restaurant, coffee_shop, bookstore)
2. **Per-Type Scoring**: Each article is scored for relevance to EACH business type
3. **User-Specific Feed**: Users see only articles relevant to THEIR business type
4. **Configurable**: All business types, keywords, and thresholds stored in database

### Relevance Calculation

For each article and business type, relevance score (0.0-1.0) is calculated from:

- **Suitability (30%)**: Base business suitability score from ML
- **Keywords (20%)**: Matching business type keywords in article text
- **Event Scale (20%)**: Bonus for large-scale events
- **Neighborhood (30%)**: Geographic proximity (for individual business matching)

Weights and thresholds are configurable per business type in the database.

### Key Models

- `BusinessType`: Defines business types with weights and thresholds
- `BusinessTypeKeyword`: Keywords for matching articles to types
- `ArticleBusinessTypeRelevance`: Stores relevance scores per article per type
- `Business`: Links to a BusinessType (FK relationship)

### API Endpoints

**Get Articles for Business Type:**
```bash
GET /api/news/articles/?business_type=pub&min_relevance=0.5
```

**Get Business Types:**
```bash
GET /api/businesses/business-types/
```

**Get User Profile (includes business type):**
```bash
GET /api/businesses/auth/profile/
```

### Admin Interface

Manage business types and keywords via Django admin:
- http://localhost:8000/admin/businesses/businesstype/
- http://localhost:8000/admin/businesses/businesstypekeyword/

### Management Commands

**Seed business type keywords:**
```bash
docker exec docker-backend-1 python manage.py seed_business_keywords
```

**Reprocess articles with per-type scoring:**
```bash
docker exec docker-backend-1 python manage.py process_articles --reprocess
```
```

### 2. Create API Documentation

**File**: `docs/API.md` (NEW)

```markdown
# NaviGate API Documentation

## Authentication

All endpoints require token authentication:
```
Authorization: Token <your-token>
```

## Endpoints

### User Profile

**GET /api/businesses/auth/profile/**

Returns authenticated user's profile including business type.

Response:
```json
{
  "user": {
    "id": 1,
    "username": "pubowner",
    "email": "pub@example.com"
  },
  "business": {
    "id": 1,
    "name": "My Pub",
    "business_type": 1,
    "business_type_details": {
      "code": "pub",
      "display_name": "Pub/Bar",
      "icon": "fa-beer"
    }
  },
  "business_type_code": "pub"
}
```

### News Articles

**GET /api/news/articles/**

Fetch articles relevant to a business type.

Query Parameters:
- `business_type` (required): Business type code (pub, restaurant, coffee_shop, bookstore)
- `min_relevance` (optional): Minimum relevance score (0.0-1.0). Defaults to business type's threshold.
- `exclude_past_events` (optional): Filter out events older than 7 days. Default: true.
- `include_type_scores` (optional): Include relevance breakdown for all types. Default: false.

Response:
```json
[
  {
    "id": 123,
    "title": "Beer Festival This Weekend",
    "content": "...",
    "user_relevance": 0.85,
    "business_suitability_score": 0.80,
    "is_event": true,
    "event_start_datetime": "2025-10-30T18:00:00Z",
    "city": "medellin",
    "neighborhood": "El Poblado"
  }
]
```

### Business Types

**GET /api/businesses/business-types/**

Get all available business types.

Query Parameters:
- `is_active` (optional): Filter by active status. Default: all.

Response:
```json
[
  {
    "id": 1,
    "code": "pub",
    "display_name": "Pub/Bar",
    "display_name_es": "Pub/Bar",
    "icon": "fa-beer",
    "min_relevance_threshold": 0.5,
    "min_suitability_threshold": 0.5,
    "business_count": 3,
    "keyword_count": 25
  }
]
```

**GET /api/businesses/business-types/{id}/keywords/**

Get keywords for a business type.

**GET /api/businesses/business-types/{id}/statistics/**

Get statistics for a business type (article counts, etc).
```

### 3. Create Migration Guide

**File**: `docs/MIGRATION_GUIDE.md` (NEW)

```markdown
# Migration Guide: Business Relevance to Per-Type System

This guide documents the migration from single `business_relevance_score` to per-business-type relevance system.

## What Changed

### Database Schema

**Removed:**
- `NewsArticle.business_relevance_score` field

**Added:**
- `BusinessType` model
- `BusinessTypeKeyword` model
- `ArticleBusinessTypeRelevance` model
- `Business.business_type` FK (was CharField)

### API Changes

**Breaking Changes:**

1. **articles/ endpoint now requires business_type parameter:**
   ```python
   # OLD
   GET /api/news/articles/?days_ago=30&min_relevance=0.3

   # NEW
   GET /api/news/articles/?business_type=pub&min_relevance=0.5
   ```

2. **Article response field changed:**
   ```python
   # OLD
   article.business_relevance_score

   # NEW
   article.user_relevance  # Specific to requested business type
   ```

3. **days_ago parameter removed:**
   Use event_start_datetime filtering instead (7-day window by default).

### Code Changes

**Frontend:**

1. **Use AuthContext for business type:**
   ```jsx
   import { useAuth } from '../contexts/AuthContext';

   const { businessTypeCode } = useAuth();
   fetchArticles({ businessType: businessTypeCode });
   ```

2. **Update article display:**
   ```jsx
   // OLD
   {article.business_relevance_score}

   // NEW
   {article.user_relevance}
   ```

**Backend:**

1. **BusinessMatcher has new method:**
   ```python
   # NEW method
   result = business_matcher.calculate_relevance_for_type(article, business_type)
   ```

2. **MLOrchestrator creates type scores:**
   ```python
   # Creates ArticleBusinessTypeRelevance records
   result = orchestrator.process_article(article, save=True)
   print(result['type_scores'])  # Dict of scores per type
   ```

## Migration Steps

If migrating an existing deployment:

1. Run migrations: `python manage.py migrate`
2. Seed business types: Already done in migration 0007
3. Seed keywords: `python manage.py seed_business_keywords`
4. Reprocess articles: `python manage.py process_articles --reprocess`
5. Update frontend code to use AuthContext
6. Deploy frontend with new API calls

## Rollback Plan

To rollback (not recommended):

1. Restore `business_relevance_score` field to NewsArticle
2. Create migration to populate from max(type_relevance_scores)
3. Revert Business.business_type to CharField
4. Update frontend to use old API

This requires database restore and is complex. Test thoroughly before deploying.
```

## Code Cleanup

### Files to Remove/Update

1. **Remove deprecated code:**

**File**: `backend/ml_engine/services/ml_pipeline.py`

Search for and remove any commented-out old code related to `business_relevance_score`.

2. **Remove old tests:**

If any test files reference `business_relevance_score`, update them:
```bash
# Find references
grep -r "business_relevance_score" backend/
```

3. **Clean up imports:**

Check for unused imports in modified files:
```bash
# Run linter
docker exec docker-backend-1 flake8 backend/businesses/ backend/news/ backend/ml_engine/
```

4. **Remove temporary files:**

Clean up any test scripts or temporary files:
```bash
rm -f test/temp_*.py
rm -f backend/*.pyc
rm -f backend/*/__pycache__/*
```

## Final Verification

### Run Full Test Suite

```bash
# Backend tests
docker exec docker-backend-1 python manage.py test

# Frontend tests
cd frontend && npm test
```

### Performance Check

```bash
# Measure API response time
time curl "http://localhost:8000/api/news/articles/?business_type=pub"

# Check database query count (should use select_related/prefetch_related)
# Enable Django Debug Toolbar if available
```

### Security Review

- Verify all endpoints have proper authentication
- Check that users can only see their own business data
- Ensure admin endpoints require staff permissions

## Acceptance Criteria

- [ ] README.md updated with business type system docs
- [ ] API.md created with endpoint documentation
- [ ] MIGRATION_GUIDE.md created with breaking changes
- [ ] All deprecated code removed
- [ ] No references to business_relevance_score in code
- [ ] Tests updated and passing
- [ ] Linter passes with no errors
- [ ] Performance acceptable (< 500ms for article list)
- [ ] Security review complete
- [ ] Git history clean (squash WIP commits if needed)

## Notes

- Keep test scripts in `test/` directory for future regression testing
- Update CLAUDE.md if any new workflows or conventions established
- Consider adding this documentation to a wiki or Confluence page
- Archive completed task files: `backlog cleanup` (Victor runs this)
