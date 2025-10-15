---
id: task-9.4
title: Generic Business Recommendations from News Features
status: Review
assignee:
  - '@claude'
created_date: '2025-10-15 15:40'
labels:
  - phase-3
  - ml-engine
  - recommendations
dependencies: []
parent_task_id: task-9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement comprehensive recommendation generation based on article features (event type, scale, date, location) and business features (type, city, capacity). Generate generic actionable recommendations without specific quantities.
<!-- SECTION:DESCRIPTION:END -->

## Progress Log

### 2025-10-15

**Implementation Complete**

Successfully implemented comprehensive generic recommendation system based on article and business features.

#### Changes Made

1. **Expanded Template System** ([ml_pipeline.py:280-634](backend/ml_engine/services/ml_pipeline.py#L280-L634))
   - Added 9 event types: sports_match, concert, marathon, festival, food_event, cultural, nightlife, conference, exposition
   - Each template includes:
     - `business_types`: List of compatible business types
     - `priority_by_scale`: Dynamic priority based on event scale
     - `days_threshold`: Time window for recommendation relevance
     - `estimated_hours`: Effort estimation
   - Total: ~30 unique recommendation templates

2. **Enhanced Recommendation Generator** ([ml_pipeline.py:636-755](backend/ml_engine/services/ml_pipeline.py#L636-L755))
   - Business-type matching: Only generates recommendations for compatible business types
   - Time-based filtering: Skips recommendations outside time thresholds
   - Dynamic priority adjustment: Increases urgency for imminent events (≤2 days)
   - Enhanced reasoning: Includes event details, location, timing, and scale
   - Smart scoring:
     - Impact score: Combines relevance (70%) + scale bonus (5-30%) + timing bonus (10%)
     - Effort score: Normalized from hours (0-1 range)

3. **Generic Recommendations**
   All recommendations are generic and actionable without specific quantities:
   - ✅ "Aumentar inventario de bebidas" (not "buy 200L beer")
   - ✅ "Considerar contratar personal adicional" (not "hire 5 waiters")
   - ✅ "Crear promoción especial" (not "20% discount")
   - ✅ "Extender horario de atención" (not specific hours)

4. **Business-Type Matching Matrix**
   - **Pub/Bar**: sports_match, concert, festival, nightlife, marathon
   - **Restaurant**: sports_match, concert, marathon, festival, food_event, cultural, conference, exposition
   - **Coffee Shop**: sports_match, concert, marathon, festival, food_event, cultural, conference, exposition
   - **Bookstore**: festival, cultural, exposition

#### Key Features

**Dynamic Priority Based on Scale:**
- Massive events → urgent/high priority
- Large events → high/medium priority
- Medium events → medium priority
- Small events → low priority

**Time-Based Urgency:**
- Events within 2 days → priority upgraded (medium→high, high→urgent)
- Events beyond threshold → filtered out (e.g., don't recommend 30 days in advance for 7-day actions)

**Enhanced Reasoning Format:**
```
Recomendación generada por evento: sports_match
Título: Copa América Final: Colombia vs Argentina...
Lugar: Estadio El Campín
Ubicación: Bogotá
Fecha: 20/10/2025 (5 días)
Asistencia esperada: 45,000 personas
Escala del evento: massive
```

#### Testing

Created demonstration script: [test/demo_recommendations.py](test/demo_recommendations.py)
- Shows 5 sample articles with different event types
- Demonstrates matching with 4 business types
- Validates filtering and priority logic
- Output: 9 recommendations generated from 7 matches

**Test Results:**
- ✅ Business-type matching works correctly
- ✅ Geographic filtering works (city-level)
- ✅ Time-based filtering works (days_threshold)
- ✅ Dynamic priority adjustment works
- ✅ Generic recommendations generated successfully

#### Files Modified

1. [backend/ml_engine/services/ml_pipeline.py](backend/ml_engine/services/ml_pipeline.py)
   - Lines 277-634: Expanded TEMPLATES dictionary
   - Lines 636-755: Enhanced generate() method

2. [test/demo_recommendations.py](test/demo_recommendations.py)
   - New file: Demonstration script (200 lines)

#### Next Steps for Production

1. **Start Docker services**: `./scripts/start-server.sh`
2. **Run ML processing**: `docker exec navigate-django python manage.py process_articles --verbose`
3. **Verify recommendations**: Check Django Admin or API endpoints
4. **Frontend integration**: Display recommendations in dashboard

#### Technical Notes

- System uses rules-based matching (no ML training needed for MVP)
- All recommendations are generated at article processing time
- Recommendations include timing metadata (recommended_start_date, recommended_end_date)
- System can handle future enhancements:
  - Add more event types easily
  - Adjust priorities per business feedback
  - Add more business-specific templates
  - Future: Add ML-based scoring based on historical performance

**Status**: ✅ Ready for testing with real article data
