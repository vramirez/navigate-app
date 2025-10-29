---
id: task-18.1
title: 'Remove business_relevance_score from NewsArticle Model'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - backend
  - database
  - migration
dependencies: []
parent: task-18
priority: high
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove the legacy `business_relevance_score` field from NewsArticle model and update all 9 file references throughout the codebase. This field is being replaced by the ArticleBusinessTypeRelevance table which stores separate scores per business type.
<!-- SECTION:DESCRIPTION:END -->

## Context

The old architecture had ONE global score per article (`business_relevance_score = max relevance across all businesses`). The new architecture has FOUR scores per article (one per business type: pub, restaurant, coffee_shop, bookstore).

**Current field definition** (news/models.py ~line 581):
```python
business_relevance_score = models.FloatField(
    default=-1.0,
    verbose_name='Puntuación de relevancia comercial',
    help_text='-1.0 = no procesado, 0.0+ = procesado con score de relevancia'
)
```

## Files to Update (9 total)

### 1. backend/news/models.py (line ~581)
Remove field definition from NewsArticle model:
```python
# DELETE THIS FIELD:
business_relevance_score = models.FloatField(...)
```

### 2. backend/news/serializers.py
Remove from NewsArticleSerializer fields list or Meta.

### 3. backend/news/views.py (line ~126-130)
Remove min_relevance filtering logic:
```python
# DELETE OR UPDATE THIS:
if min_relevance:
    try:
        queryset = queryset.filter(business_relevance_score__gte=float(min_relevance))
    except ValueError:
        pass
```

Note: This will be replaced in task-18.5 with per-type filtering.

### 4. backend/news/admin.py
Remove `business_relevance_score` from:
- `list_display`
- `list_filter`
- Any custom methods using this field

### 5. backend/ml_engine/services/ml_pipeline.py
Remove all references:
- Line ~1074: `article.business_relevance_score = max_relevance`
- Line ~1092: Return dict key

Replace with ArticleBusinessTypeRelevance logic (done in task-18.3).

### 6. backend/news/utils.py
Check for any utility functions using this field and remove/update.

### 7. backend/news/services/content_processor.py
Remove initialization if present.

### 8. backend/news/migrations/
Old migrations reference this field - leave them alone (historical).

### 9. Search for any remaining references:
```bash
grep -r "business_relevance_score" backend/ --exclude-dir=migrations
```

## Migration Steps

After updating model:

```bash
# 1. Create migration
docker exec docker-backend-1 python manage.py makemigrations news

# 2. Review migration file
# Should show: RemoveField operation

# 3. Run migration
docker exec docker-backend-1 python manage.py migrate news

# 4. Verify no errors
docker exec docker-backend-1 python manage.py check
```

## Testing

1. **Model Check**:
```python
from news.models import NewsArticle
# Should NOT have business_relevance_score attribute
hasattr(NewsArticle, 'business_relevance_score')  # Should be False
```

2. **No Import Errors**:
```bash
docker exec docker-backend-1 python -c "
from news.models import NewsArticle
from news.serializers import NewsArticleSerializer
from ml_engine.services.ml_pipeline import MLOrchestrator
print('All imports successful')
"
```

3. **Database Check**:
```bash
# Field should not exist in table
docker exec docker-db-1 psql -U navigate -d navigate -c "\d news_newsarticle" | grep business_relevance_score
# Should return no results
```

## Acceptance Criteria

- [ ] Field removed from NewsArticle model
- [ ] All 9 file references updated/removed
- [ ] Migration created and run successfully
- [ ] No ImportError or AttributeError
- [ ] grep search returns no results
- [ ] Application starts without errors

## Notes

- Do NOT remove ArticleBusinessTypeRelevance model (that's the replacement)
- Old migration files can reference the old field (that's fine)
- If views.py breaks, it's expected - task-18.5 will fix it
- This task focuses on MODEL cleanup only
