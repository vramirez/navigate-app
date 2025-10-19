---
id: task-14
title: Remove Business Suitability Score from Frontend UI
status: Backlog
priority: low
assignee: @claude
labels: frontend, ux, cleanup
parent: task-9
created: 2025-10-19
milestone: Phase 3 - ML Engine Refinement
---

## Description

**Simplify user experience by removing the internal ML score (`business_suitability_score`) from frontend UI.**

Currently, business owners see TWO scores in the Article Detail page:
1. **business_suitability_score** - "Puntuación de idoneidad"
2. **business_relevance_score** - "Relevancia para negocios"

**Problem:**
- `business_suitability_score` is an **internal ML optimization** for early filtering
- Business owners don't need to see it - it's a technical detail
- Having two scores is confusing: "Which one should I pay attention to?"

**Solution:**
- Remove `business_suitability_score` from frontend UI entirely
- Keep it in backend for filtering logic
- Only show `business_relevance_score` to business owners
- Simplify labels: just call it "Relevancia" or "Puntuación de relevancia"

---

## User Impact

**Before (Confusing):**
```
Puntuación de idoneidad: 0.46
Relevancia para negocios: 0.99
```
User thinks: "Wait, which score matters? Why are they different?"

**After (Clear):**
```
Relevancia para tu negocio: 0.99
```
User thinks: "Okay, this article is highly relevant to me"

---

## Implementation Plan

### Step 1: Remove from Article Detail Page

**File:** `frontend/src/pages/ArticleDetail.jsx`

Remove this section:
```javascript
{article.business_suitability_score !== null && (
  <div className="stat-item">
    <span className="stat-label">{t('articleDetail.suitabilityScore')}</span>
    <span className="stat-value">{(article.business_suitability_score * 100).toFixed(0)}%</span>
  </div>
)}
```

Keep only:
```javascript
{article.business_relevance_score !== null && (
  <div className="stat-item">
    <span className="stat-label">{t('articleDetail.relevanceScore')}</span>
    <span className="stat-value">{(article.business_relevance_score * 100).toFixed(0)}%</span>
  </div>
)}
```

### Step 2: Update Translations

**Files:** `frontend/src/i18n/locales/es.json` and `en.json`

Remove:
```json
"suitabilityScore": "Puntuación de idoneidad"
```

Simplify:
```json
"relevanceScore": "Relevancia para tu negocio"
```

### Step 3: Clean Up Serializer (Optional)

**File:** `backend/news/serializers.py`

Consider removing `business_suitability_score` from `NewsArticleSerializer.fields` if it's not used anywhere else in the frontend.

**Keep it if:**
- Used for filtering in API queries
- Used for debugging/admin purposes
- Used in analytics

**Remove it if:**
- Only used for display purposes

---

## Acceptance Criteria

- [ ] Article Detail page shows only ONE score (business_relevance_score)
- [ ] Label is clear and user-friendly
- [ ] Translations updated in both English and Spanish
- [ ] No references to business_suitability_score in frontend code
- [ ] Backend still uses business_suitability_score for filtering logic

---

## Dependencies

- None (standalone cleanup task)

## Blockers

None

---

## Technical Notes

### Why Keep business_suitability_score in Backend?

**PreFilter uses it for early exit:**
```python
# Step 3: Early exit if not suitable
if article.business_suitability_score < 0.3:
    return {
        'success': True,
        'processed': False,
        'reason': f'Low suitability score: {article.business_suitability_score:.2f}',
        'features_extracted': True
    }
```

This optimization saves computation by skipping irrelevant articles before checking all businesses.

### Alternative: Admin-Only Display

Instead of completely removing, we could:
- Hide from business owner UI
- Show in Django Admin for debugging
- Show in analytics dashboard for system monitoring

---

## Related Tasks

- task-13: Geographic relevance detection (added these scores)
- task-12: Article Detail page (displays these scores)

---

## Progress Log

### 2025-10-19 - Task Created
- Identified during task-13 review
- User questioned: "does this prefilter matter for the client?"
- Answer: No, business owners only care about business_relevance_score
- Created as backlog task for future cleanup
- Status: Backlog (low priority UX improvement)
