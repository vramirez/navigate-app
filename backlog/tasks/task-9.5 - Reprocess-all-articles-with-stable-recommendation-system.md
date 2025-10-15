---
id: task-9.5
title: Reprocess all articles with stable recommendation system
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-15 17:00'
labels:
  - phase-3
  - ml-engine
  - recommendations
dependencies:
  - task-9.4
parent_task_id: task-9
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the recommendation system is stable and the duplicate issue is fixed, reprocess all 699 articles to generate a complete, clean recommendation dataset for production use.
<!-- SECTION:DESCRIPTION:END -->

## Prerequisites

- [x] task-9.4 complete (generic recommendations system)
- [x] Duplicate recommendation issue fixed
- [ ] System tested with sample articles (no duplicates)
- [ ] No errors in processing

## Implementation Steps

### 1. Verify System Stability

Test with small batch first:
```bash
# Clean all recommendations
docker exec docker-backend-1 python manage.py shell -c "
from recommendations.models import Recommendation
Recommendation.objects.all().delete()
"

# Test with 20 articles
docker exec docker-backend-1 python manage.py process_articles --reprocess --limit 20 --verbose

# Run again to verify no duplicates created
docker exec docker-backend-1 python manage.py process_articles --reprocess --limit 20 --verbose

# Check for duplicates
docker exec docker-backend-1 python manage.py shell -c "
from recommendations.models import Recommendation
from django.db.models import Count

duplicates = Recommendation.objects.values(
    'business_id', 'object_id', 'action_type'
).annotate(count=Count('id')).filter(count__gt=1)

print(f'Duplicates found: {len(duplicates)}')
"
```

### 2. Full Reprocessing (Production)

Once verified stable:
```bash
# Backup current recommendations (optional)
docker exec docker-backend-1 python manage.py dumpdata recommendations.Recommendation > backup_recommendations_$(date +%Y%m%d).json

# Clear all existing recommendations
docker exec docker-backend-1 python manage.py shell -c "
from recommendations.models import Recommendation
count = Recommendation.objects.count()
print(f'Deleting {count} existing recommendations...')
Recommendation.objects.all().delete()
print('✓ Done')
"

# Reprocess all articles with verbose output
docker exec docker-backend-1 python manage.py process_articles --reprocess --verbose

# Alternative: Process in batches (for monitoring)
docker exec docker-backend-1 python manage.py process_articles --reprocess --limit 100 --verbose
docker exec docker-backend-1 python manage.py process_articles --reprocess --limit 200 --verbose
docker exec docker-backend-1 python manage.py process_articles --reprocess --limit 300 --verbose
docker exec docker-backend-1 python manage.py process_articles --reprocess --verbose
```

### 3. Validation

After reprocessing:
```bash
# Check statistics
docker exec docker-backend-1 python manage.py shell -c "
from recommendations.models import Recommendation
from news.models import NewsArticle
from django.db.models import Count

print('=== REPROCESSING RESULTS ===\n')
print(f'Total articles: {NewsArticle.objects.count()}')
print(f'Processed articles: {NewsArticle.objects.filter(features_extracted=True).count()}')
print(f'Suitable articles: {NewsArticle.objects.filter(business_suitability_score__gte=0.3).count()}')
print(f'Total recommendations: {Recommendation.objects.count()}')

print('\n=== BY PRIORITY ===')
for priority in ['urgent', 'high', 'medium', 'low']:
    count = Recommendation.objects.filter(priority=priority).count()
    print(f'{priority.upper()}: {count}')

print('\n=== BY BUSINESS ===')
businesses = Recommendation.objects.values('business__name').annotate(
    count=Count('id')
).order_by('-count')
for biz in businesses:
    print(f'{biz[\"business__name\"]}: {biz[\"count\"]}')

print('\n=== DUPLICATE CHECK ===')
duplicates = Recommendation.objects.values(
    'business_id', 'object_id', 'action_type'
).annotate(count=Count('id')).filter(count__gt=1)
print(f'Duplicate groups: {len(duplicates)}')
if duplicates:
    print('⚠️  WARNING: Duplicates found!')
else:
    print('✓ No duplicates')
"
```

## Expected Results

Based on previous testing with 100 articles:

- **Total articles**: ~699
- **Suitable articles**: ~200-250 (30-40%)
- **Recommendations generated**: ~100-200
- **Processing time**: ~4-7 minutes (0.38s per article)
- **Duplicates**: 0

**Priority Distribution**:
- URGENT: 30-40%
- HIGH: 40-50%
- MEDIUM: 10-20%
- LOW: 0-5%

**Category Distribution**:
- Marketing: 30-35%
- Inventory: 30-35%
- Staffing: 25-30%
- Operations: 5-10%

## Acceptance Criteria

- [ ] All 699 articles processed successfully
- [ ] 0 processing errors
- [ ] 0 duplicate recommendations
- [ ] Recommendations distributed across all business types
- [ ] All detected event types represented (sports_match, concert, festival, etc.)
- [ ] Priority distribution looks reasonable (30-40% urgent/high)
- [ ] Processing completes in reasonable time (<10 minutes)

## Rollback Plan

If issues occur:
```bash
# Restore from backup
docker exec docker-backend-1 python manage.py loaddata backup_recommendations_YYYYMMDD.json

# Or regenerate from scratch
docker exec docker-backend-1 python manage.py process_articles --reprocess --verbose
```

## Notes

- **Deduplication**: System now automatically deletes existing recommendations before regenerating
- **Safety**: Can be run multiple times without creating duplicates
- **Performance**: Processes ~0.38 seconds per article
- **Filtering**: ~65% of articles filtered out (politics, international, low quality)

## Related Tasks

- task-9.4: Generic Business Recommendations from News Features
- task-4: Integrate real news data with ML recommendation pipeline

## Testing Log

### Test Run 1 (Small Batch)
```
Date: YYYY-MM-DD
Articles: 20
Results: TBD
Duplicates: TBD
Status: TBD
```

### Full Reprocessing
```
Date: YYYY-MM-DD
Articles: 699
Results: TBD
Duplicates: TBD
Status: TBD
```

---

**Created**: 2025-10-15
**Status**: To Do (pending stability verification)
**Priority**: Medium (important for production, but not urgent)
