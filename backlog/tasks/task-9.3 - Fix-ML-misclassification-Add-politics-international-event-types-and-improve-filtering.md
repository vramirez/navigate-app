---
id: task-9.3
title: >-
  Fix ML misclassification: Add politics/international event types and improve
  filtering
status: Review
assignee:
  - '@claude'
created_date: '2025-10-13 21:57'
labels:
  - phase-3
  - ml-engine
  - backend
dependencies: []
parent_task_id: task-9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve ML pipeline to correctly classify and filter political/international news articles that are irrelevant to hospitality businesses
<!-- SECTION:DESCRIPTION:END -->

## Problem Analysis

Found article ID 309 with severe misclassification:
- **Article**: "Donald Trump confirma que Estados Unidos lanzó otro bombardeo..."
- **Source**: El Tiempo - Gastronomía (RSS feed misconfiguration)
- **Original Classification**: "cultural" with 0.75 suitability, 1.00 relevance
- **Issues**:
  1. International conflict article classified as cultural/food
  2. Paywall content (cookie wall) not detected
  3. No keywords extracted
  4. No geographic data
  5. High relevance despite being completely irrelevant to pub owners

## Implementation Plan

### Phase 1: Quick Wins ✅
1. Add politics/international/conflict/crime event types to feature_extractor.py
2. Update PreFilter LOW_RELEVANCE categories
3. Enhance negative keywords and penalties
4. Add paywall/cookie wall detection
5. Tighten geographic filter default behavior

### Phase 2: Section Validation (Optional)
6. Add RSS section validation to prevent mis-sectioned articles

## Changes Made

### 1. Feature Extractor ([feature_extractor.py:78-96](backend/ml_engine/services/feature_extractor.py#L78-L96))
Added 4 new low-relevance event types:
- **politics**: pol[ií]tica, gobierno, congreso, elecciones, etc.
- **international**: internacional, estados unidos, europa, diplomacia, etc.
- **conflict**: bombardeo, ataque, guerra, militar, misil, etc.
- **crime**: homicidio, asesinato, robo, narcotr[aá]fico, etc.

### 2. PreFilter Scoring ([ml_pipeline.py:43-48](backend/ml_engine/services/ml_pipeline.py#L43-L48))
Updated LOW_RELEVANCE_CATEGORIES:
```python
'politics': 0.15,       # Was not defined
'international': 0.10,  # Was not defined
'conflict': 0.05,       # NEW - very low relevance
'crime': 0.10,          # NEW - low relevance
```

### 3. Negative Keywords ([ml_pipeline.py:56-62](backend/ml_engine/services/ml_pipeline.py#L56-L62))
- Added: bombardeo, ataque, guerra, conflicto armado, narcotr[aá]fico, violencia, v[ií]ctima, secuestro
- **Increased penalty**: -0.2 → -0.5 per keyword (2.5x stronger)

### 4. Paywall Detection ([ml_pipeline.py:64-72](backend/ml_engine/services/ml_pipeline.py#L64-L72))
Added PAYWALL_PATTERNS to detect:
- Cookie consent walls
- Login/subscription walls
- "Inicia sesión", "Ya tienes una cuenta", "Datos de navegación"
- **Effect**: Immediate rejection (score = 0.0)

### 5. Content Quality Validation ([ml_pipeline.py:87-104](backend/ml_engine/services/ml_pipeline.py#L87-L104))
- Detects paywall content → immediate rejection
- Detects no keywords + short content → -0.3 penalty (not immediate rejection)
- Logs warnings for transparency

### 6. Geographic Filter Strictness ([ml_pipeline.py:194-205](backend/ml_engine/services/ml_pipeline.py#L194-L205))
Changed default from `return True` to stricter logic:
- Articles without city data: Only allow if massive scale + high-relevance event type
- Articles with non-matching city: Reject by default
- **Effect**: Filters out international news without local relevance

## Test Results

### Article 309 (Trump Bombardment) - BAD ARTICLE
**Before**:
- Event: cultural, Suitability: 0.75, Relevance: 1.00
- Would be shown to users ❌

**After**:
- Event: conflict, Suitability: 0.00, Relevance: N/A
- Immediately rejected due to paywall + conflict type ✅

### Article 300 (Hilton Gastronomy) - GOOD ARTICLE
**Before**: Event: food_event, Suitability: 1.00, Relevance: 0.65
**After**: Event: food_event, Suitability: 0.75, Relevance: TBD
- Minor penalty for no keywords but still kept ✅

### Article 698 (Copa América) - GOOD SPORTS
**Before**: Event: sports_match, Suitability: 1.00, Relevance: 1.00
**After**: Event: sports_match, Suitability: 1.00, Relevance: TBD
- Maintained perfect score ✅

## Acceptance Criteria

- [x] Politics/international/conflict event types correctly detected
- [x] Low relevance scores assigned to political/conflict news (<0.15)
- [x] Paywall content immediately rejected (score = 0.0)
- [x] Negative keywords apply stronger penalty (-0.5)
- [x] Geographic filter rejects articles without city data (unless massive)
- [x] Article 309 correctly rejected (suitability = 0.0)
- [x] Food/sports articles maintain high scores
- [ ] Section validation prevents mis-sectioned RSS articles (Optional - Phase 2)

## Next Steps (Optional)

1. **Add Section Validation**: Modify content_processor.py to reject articles where RSS section doesn't match source's expected section
2. **Re-process All Articles**: Run ML pipeline on existing articles to update scores
3. **Monitor False Positives**: Track if legitimate articles are being filtered

## Files Modified

- `backend/ml_engine/services/feature_extractor.py` - Added 4 new event types
- `backend/ml_engine/services/ml_pipeline.py` - Enhanced PreFilter, added paywall detection, stricter geographic filtering

## Technical Notes

- Paywall detection is crucial - many articles have cookie walls instead of content
- No keywords + short content gets penalty but not rejection (ML may not have run)
- Geographic filter now defaults to False (stricter) instead of True (permissive)
- Negative keyword penalty increased 2.5x for stronger filtering
