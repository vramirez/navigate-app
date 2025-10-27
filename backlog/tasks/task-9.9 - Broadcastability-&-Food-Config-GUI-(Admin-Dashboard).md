---
id: task-9.9
title: Broadcastability & Food Config GUI (Admin Dashboard)
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-27 15:09'
labels:
  - frontend
  - admin
  - configuration
dependencies: []
parent_task_id: task-9
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build web admin dashboard for managing broadcastability configuration (sports, competition levels, hype patterns, weights/thresholds) and food event taxonomy (subtypes, cuisine types, patterns). Includes real-time preview feature.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

### Frontend Pages (React)

**Route**: `/admin/ml-config/`

1. **BroadcastabilityConfig.jsx**: Manage sports, competitions, hype patterns
   - Sport types table (CRUD): code, name, appeal rating, keywords, active status
   - Competition levels table (CRUD): code, name, sport, multiplier, keywords
   - Hype indicators table (CRUD): pattern, category, boost, language
   - System weights panel: 4 sliders (sport 35%, competition 30%, hype 20%, attendance 15%)
   - Min threshold slider (0.55 default)

2. **FoodEventsConfig.jsx**: Manage food taxonomy
   - Food subtypes table (CRUD): code, name, base appeal score, keywords
   - Cuisine types table (CRUD): code, name, keywords, active status
   - Extraction patterns table (CRUD): pattern, subtype, confidence

3. **SystemHealth.jsx**: Metrics dashboard
   - Detection rate charts (sport types, food subtypes)
   - Top 10 detected sports/competitions
   - Broadcastability score distribution histogram
   - Recent articles processed (last 50)

4. **PreviewTest.jsx**: Real-time preview tool
   - Text area: "Paste article text here"
   - Calculate button
   - Results panel: extracted features, broadcastability score, components breakdown
   - Visual score meter (0-100%)

### Backend API

**New ViewSets** (`backend/ml_engine/viewsets.py`):
- `SportTypeViewSet` (list, retrieve, create, update, destroy)
- `CompetitionLevelViewSet`
- `HypeIndicatorViewSet`
- `BroadcastabilityConfigViewSet` (retrieve, update only - singleton)
- `CuisineTypeViewSet`
- `FoodSubtypeViewSet`
- `ExtractionPatternViewSet`

**Preview Endpoint** (`POST /api/ml-config/preview/`):
- Accepts article text
- Returns extracted features + broadcastability calculation
- Does NOT save to database

### Files to Create/Modify

**Frontend**:
- `frontend/src/pages/admin/MLConfig/BroadcastabilityConfig.jsx`
- `frontend/src/pages/admin/MLConfig/FoodEventsConfig.jsx`
- `frontend/src/pages/admin/MLConfig/SystemHealth.jsx`
- `frontend/src/pages/admin/MLConfig/PreviewTest.jsx`
- `frontend/src/services/mlConfigApi.js` (API client)
- `frontend/src/App.jsx` (add routes)

**Backend**:
- `backend/ml_engine/viewsets.py` (new file)
- `backend/ml_engine/urls.py` (new routes)
- `backend/config/urls.py` (include ml_engine.urls)

## Acceptance Criteria

### Broadcastability Configuration Page
- [ ] Sport types table displays all sports with appeal ratings
- [ ] Can add new sport type with name, appeal (0-1 slider), keywords (comma-separated)
- [ ] Can edit existing sport type inline
- [ ] Can delete sport type (with confirmation if has competitions)
- [ ] Competition levels table shows sport filter dropdown
- [ ] Can add new competition with sport, multiplier (0.1-3.0 slider), keywords
- [ ] Can edit existing competition inline
- [ ] Can delete competition (with confirmation)
- [ ] Hype indicators table shows category filter (finals, historic, rivalry, etc.)
- [ ] Can add new hype pattern with regex, boost (0-0.5 slider), category, language
- [ ] Can edit/delete hype indicators
- [ ] System weights panel shows 4 sliders that sum to 100%
- [ ] Weight sliders auto-adjust to maintain 100% total
- [ ] Min threshold slider updates BroadcastabilityConfig (0.0-1.0)
- [ ] All changes save to database immediately (optimistic UI updates)

### Food Events Configuration Page
- [ ] Food subtypes table displays 6 subtypes with base appeal scores
- [ ] Can add new food subtype with code, name, appeal, keywords
- [ ] Can edit/delete food subtypes
- [ ] Cuisine types table shows 15+ cuisines with keywords
- [ ] Can add new cuisine type with code, names (ES/EN), keywords
- [ ] Can toggle cuisine active status
- [ ] Extraction patterns table shows subtype filter
- [ ] Can add patterns for each food subtype
- [ ] All CRUD operations work with validation

### System Health Dashboard
- [ ] Detection rate chart shows sport types detected in last 100 articles
- [ ] Top 10 sports chart shows most common detections
- [ ] Top 10 competitions chart shows tournament frequency
- [ ] Broadcastability score histogram (0-1.0 buckets)
- [ ] Recent articles table shows last 50 processed with scores
- [ ] Click article opens detail modal with full breakdown
- [ ] Charts update in real-time (or refresh button)
- [ ] Export data to CSV button works

### Preview Test Tool
- [ ] Text area accepts article text (min 100 chars)
- [ ] Calculate button disabled until text entered
- [ ] Loading spinner shows during calculation
- [ ] Results panel shows extracted fields: event_type, event_country, sport_type, competition_level
- [ ] Broadcastability components breakdown: sport_appeal (value + detected sport), competition_level (value + detected tier), hype_score (value + matched patterns), attendance_score (value)
- [ ] Final broadcastability score displayed with visual meter
- [ ] Is Broadcastable flag shown (green/red badge)
- [ ] Would show to TV pub indicator (if score >= threshold)
- [ ] Can test multiple articles without page refresh
- [ ] Error handling for API failures

### Backend API Requirements
- [ ] GET /api/ml-config/sport-types/ returns all sport types
- [ ] POST /api/ml-config/sport-types/ creates new sport (validates appeal 0-1)
- [ ] PUT /api/ml-config/sport-types/:id/ updates sport
- [ ] DELETE /api/ml-config/sport-types/:id/ removes sport
- [ ] Similar endpoints for competition-levels, hype-indicators, cuisine-types
- [ ] GET /api/ml-config/broadcastability-config/ returns singleton config
- [ ] PUT /api/ml-config/broadcastability-config/ updates weights/threshold (validates sum=1.0)
- [ ] POST /api/ml-config/preview/ accepts {text} returns {features, broadcastability, components}
- [ ] Preview endpoint does NOT save article to database
- [ ] All endpoints require authentication (staff only)

### UI/UX Requirements
- [ ] Responsive design (works on desktop/tablet)
- [ ] Consistent styling with existing admin pages
- [ ] Form validation with clear error messages
- [ ] Optimistic UI updates (immediate feedback)
- [ ] Confirmation modals for destructive actions
- [ ] Keyboard shortcuts (Ctrl+S to save, Esc to cancel)
- [ ] Loading states for all async operations
- [ ] Success/error toast notifications

### Testing
- [ ] Manual testing of all CRUD operations
- [ ] Preview tool tested with 5 sample articles (World Cup, Tour de France, Champions League, Food Festival, Wine Event)
- [ ] Weight slider validation (always sums to 100%)
- [ ] Database constraints enforced (unique codes, valid ranges)
- [ ] Error handling for malformed data

## Estimated Time

**Total**: 4-5 hours

**Breakdown**:
- Backend API (ViewSets, serializers, URLs): 1.5 hours
- Frontend CRUD pages (Broadcastability + Food): 2 hours
- System Health dashboard: 1 hour
- Preview test tool: 1 hour
- Testing + refinement: 30 minutes
