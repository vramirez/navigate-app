# Duplicate Recommendations Fix - Summary

**Date**: 2025-10-15
**Issue**: Duplicate recommendations created when reprocessing articles
**Status**: ✅ Fixed and tested
**Branch**: task-9.4-generic-recommendations

---

## Problem Report

### Issue Description
User screenshot showed the Copa América 2025 article with **6 recommendations instead of 3** - each recommendation appeared twice:

- "Contratar personal adicional" (2x)
- "Campaña de marketing para Copa América..." (2x)
- "Aumentar inventario de bebidas" (2x)

### Root Cause
Running `python manage.py process_articles --reprocess` multiple times created duplicates because:
1. **No deduplication check**: System didn't check for existing recommendations
2. **Multiple reprocessing runs**: We ran `--limit 20` then `--limit 100`, both included same articles
3. **Database evidence**: Recommendations created at 16:40:59 and 16:41:33 (34 seconds apart)

### Impact
- 3 duplicate groups found in database
- Each Copa América recommendation duplicated
- Total: 41 recommendations instead of 38 unique ones
- Same issue would occur on full reprocessing (task-9.5)

---

## Solution Implemented

### Code Changes

**File**: `backend/ml_engine/services/ml_pipeline.py` (lines 661-671)

Added automatic deduplication logic:

```python
def generate(self, article: NewsArticle, business: Business, relevance_score: float):
    # ... existing code ...

    article_content_type = ContentType.objects.get_for_model(NewsArticle)

    # NEW: Check for existing recommendations to avoid duplicates
    existing_recs = Recommendation.objects.filter(
        business=business,
        content_type=article_content_type,
        object_id=article.id
    )
    if existing_recs.exists():
        logger.info(f"Deleting {existing_recs.count()} existing recommendations for article {article.id}, business {business.id}")
        existing_recs.delete()

    # NOW generate fresh recommendations
    # ...
```

**Logic**:
1. Before generating recommendations, query for existing ones
2. If any exist for this article-business pair, delete them
3. Then generate fresh recommendations
4. Result: Always have exactly the intended number, no duplicates

### Database Cleanup

One-time operation to clean existing duplicates:

```python
# Found 3 duplicate groups
# Kept newest (IDs: 689, 690, 691)
# Deleted older duplicates (IDs: 686, 687, 688)
# Result: 0 duplicates remaining
```

**Before**: 41 recommendations (with 3 duplicates)
**After**: 38 recommendations (all unique)

---

## Testing Results

### Test Scenario
Process same 10 articles twice to verify no duplicates created:

**Test Run 1**:
```
Articles: 10
Suitable: 5
Recommendations created: 3
Total in DB: 38
```

**Test Run 2** (reprocess same articles):
```
Articles: 10
Suitable: 5
Recommendations created: 3
Total in DB: 38 (same as before!)
```

**Duplicate Check**:
```sql
SELECT business_id, object_id, action_type, COUNT(*)
FROM recommendations
GROUP BY business_id, object_id, action_type
HAVING COUNT(*) > 1;

Result: 0 rows (no duplicates)
```

### Verification
✅ Running process twice produces same count
✅ No new duplicates created
✅ System logs show deletions working
✅ Safe to reprocess anytime

---

## Task-9.5 Created

**File**: `backlog/tasks/task-9.5 - Reprocess-all-articles-with-stable-recommendation-system.md`

### Purpose
Full reprocessing of all 699 articles once system is stable.

### Key Features
- Detailed implementation steps
- Pre-flight safety checks
- Validation criteria
- Expected results (based on testing)
- Rollback plan

### Prerequisites
- [x] Duplicate issue fixed ✅
- [ ] System tested with sample articles (done, awaiting user approval)
- [ ] Ready for production reprocessing

### Execution (when ready)
```bash
# Clean all recommendations
docker exec docker-backend-1 python manage.py shell -c "
from recommendations.models import Recommendation
Recommendation.objects.all().delete()
"

# Reprocess all 699 articles
docker exec docker-backend-1 python manage.py process_articles --reprocess --verbose
```

**Expected Results**:
- ~699 articles processed
- ~200-250 suitable (30-40%)
- ~100-200 recommendations
- 0 duplicates
- 0 errors
- ~4-7 minutes processing time

---

## Benefits

### For Development
- ✅ Can reprocess articles safely anytime
- ✅ No cleanup needed between runs
- ✅ Easier testing and development
- ✅ Cleaner database

### For Production
- ✅ Safe to update recommendation templates
- ✅ Can regenerate all recommendations with new logic
- ✅ No risk of duplicate accumulation
- ✅ System self-healing on reprocessing

### For Users
- ✅ No duplicate recommendations in UI
- ✅ Clean, professional experience
- ✅ Confidence in recommendation quality

---

## Technical Details

### Why Delete Instead of Update?
**Decision**: Delete existing and regenerate fresh

**Reasoning**:
1. **Template changes**: When we update recommendation templates, old recommendations may be obsolete
2. **Feature changes**: New article features may change which recommendations apply
3. **Business logic**: Priority, impact, or effort calculations may change
4. **Simplicity**: Cleaner than complex update logic
5. **Performance**: Delete + insert is fast (0.33s per article)

### Alternative Considered: Unique Constraint
Could add database constraint:
```python
class Meta:
    unique_together = [['business', 'content_type', 'object_id', 'action_type']]
```

**Not implemented because**:
- Deduplication handles all cases (including template changes)
- Constraint would prevent regeneration (need to delete first anyway)
- Current solution is more flexible

---

## Commit History

1. **5f7fbd2**: task-9.4: Add testing results documentation
2. **75e06a8**: task-9.4: Mark as ready for review
3. **1268b68**: task-9.4: Implement generic business recommendations system
4. **ab92f2f**: task-9.4: Fix duplicate recommendations issue ← Current

---

## Next Steps

### Immediate
- [x] Fix duplicate issue ✅
- [x] Test with sample articles ✅
- [x] Create task-9.5 ✅

### User Decision Required
- [ ] Review fix and approve
- [ ] Execute task-9.5 (full reprocessing)
- [ ] Merge feature branch to main

### Future
- [ ] Monitor for any edge cases
- [ ] Collect user feedback
- [ ] Iterate on templates based on usage

---

## Files Changed

1. **backend/ml_engine/services/ml_pipeline.py**
   - Added deduplication logic (lines 661-671)

2. **backlog/tasks/task-9.5 - Reprocess-all-articles-with-stable-recommendation-system.md**
   - New task for full reprocessing

3. **docs/duplicate-fix-summary.md**
   - This document

---

**Status**: ✅ Fixed, tested, and ready for production
**Confidence**: High (tested successfully)
**Risk**: Low (safe to execute task-9.5)
