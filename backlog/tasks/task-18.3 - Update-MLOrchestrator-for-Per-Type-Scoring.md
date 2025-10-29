---
id: task-18.3
title: 'Update MLOrchestrator.process_article for Per-Type Scoring'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - backend
  - ml-engine
dependencies: [task-18.1, task-18.2]
parent: task-18
priority: high
estimated_hours: 4
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace Step 4 (Business Matching) in MLOrchestrator.process_article() with new per-type scoring logic. Calculate and store ArticleBusinessTypeRelevance records for each BusinessType.
<!-- SECTION:DESCRIPTION:END -->

## File & Location

**File**: `backend/ml_engine/services/ml_pipeline.py`
**Method**: `MLOrchestrator.process_article()`
**Lines**: 1054-1086 (replace Steps 4-5)

## Implementation

**Replace existing Step 4**:
```python
# Step 4: Calculate relevance for each business type
from businesses.models import BusinessType
from news.models import ArticleBusinessTypeRelevance

# Delete old scores (for reprocessing)
ArticleBusinessTypeRelevance.objects.filter(article=article).delete()

business_types = BusinessType.objects.filter(is_active=True)
type_scores = {}

for biz_type in business_types:
    # Check suitability threshold
    if article.business_suitability_score < biz_type.min_suitability_threshold:
        continue
    
    # Calculate relevance
    result = self.business_matcher.calculate_relevance_for_type(article, biz_type)
    
    # Store in database
    ArticleBusinessTypeRelevance.objects.create(
        article=article,
        business_type=biz_type,
        relevance_score=result['relevance_score'],
        suitability_component=result['suitability_component'],
        keyword_component=result['keyword_component'],
        event_scale_component=result['event_scale_component'],
        neighborhood_component=result['neighborhood_component'],
        matching_keywords=result['matching_keywords']
    )
    
    type_scores[biz_type.code] = result['relevance_score']

# Step 5: Generate recommendations for matching businesses
matching_businesses = []

for biz_type_code, relevance in type_scores.items():
    biz_type = BusinessType.objects.get(code=biz_type_code)
    
    # Only if relevance >= threshold
    if relevance < biz_type.min_relevance_threshold:
        continue
    
    # Find businesses of this type
    businesses = Business.objects.filter(
        business_type=biz_type,
        is_active=True
    )
    
    for business in businesses:
        # Geographic filter
        if not self.geo_matcher.is_relevant(article, business):
            continue
        
        matching_businesses.append((business, relevance))

# Step 6: Generate recommendations (existing logic continues...)
recommendations_created = 0
for business, relevance in matching_businesses:
    recs = self.rec_generator.generate(article, business, relevance)
    if save:
        for rec in recs:
            rec.save()
            recommendations_created += 1
```

**Update return dict** (line ~1088):
```python
return {
    'success': True,
    'processed': True,
    'features_extracted': True,
    'suitability_score': article.business_suitability_score,
    'type_scores': type_scores,  # NEW
    'matching_businesses': len(matching_businesses),
    'recommendations_created': recommendations_created
}
```

## Testing

Test with one article:
```bash
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import NewsArticle, ArticleBusinessTypeRelevance
from ml_engine.services.ml_pipeline import MLOrchestrator

article = NewsArticle.objects.first()
orchestrator = MLOrchestrator()

result = orchestrator.process_article(article, save=True)
print('Result:', result)

# Check scores created
scores = ArticleBusinessTypeRelevance.objects.filter(article=article)
print(f'Scores created: {scores.count()}')
for s in scores:
    print(f'  {s.business_type.code}: {s.relevance_score:.2f}')
"
```

## Acceptance Criteria

- [ ] ArticleBusinessTypeRelevance records created (up to 4 per article)
- [ ] Respects min_suitability_threshold per type
- [ ] Recommendations generated for matching businesses
- [ ] Return dict includes type_scores
- [ ] No errors when processing articles
- [ ] Old business_relevance_score NOT set

## Notes

- Requires task-18.1 (field removal) and task-18.2 (new method) complete first
- After this task, can run process_articles --reprocess
