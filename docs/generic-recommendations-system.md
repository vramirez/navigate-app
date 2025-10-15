# Generic Business Recommendations System

**Date**: 2025-10-15
**Status**: ✅ Implemented
**Task**: task-9.4

## Overview

NaviGate's recommendation system generates generic, actionable business recommendations based on news article features and business characteristics. The system matches events to businesses intelligently and provides recommendations without requiring detailed business inventory or operational data.

## Key Design Principles

### 1. Generic Recommendations (No Specific Quantities)

The system provides actionable guidance without requiring detailed business data:

❌ **Avoid**: "Comprar 200 litros adicionales de cerveza"
✅ **Instead**: "Aumentar inventario de bebidas para el evento"

❌ **Avoid**: "Contratar 5 meseros adicionales"
✅ **Instead**: "Considerar contratar personal adicional"

❌ **Avoid**: "Ofrecer 20% de descuento"
✅ **Instead**: "Crear promoción especial para el evento"

### 2. Business-Type Aware Matching

Each event type is mapped to compatible business types:

| Event Type | Compatible Businesses |
|-----------|----------------------|
| Sports Match | Pub, Restaurant, Coffee Shop |
| Concert | Pub, Restaurant, Coffee Shop |
| Marathon | Coffee Shop, Restaurant, Pub |
| Festival | All types |
| Food Event | Restaurant, Coffee Shop, Pub |
| Cultural | Coffee Shop, Restaurant, Bookstore |
| Nightlife | Pub, Restaurant |
| Conference | Coffee Shop, Restaurant |
| Exposition | Coffee Shop, Restaurant, Bookstore |

### 3. Dynamic Priority Based on Event Scale

```
Massive (>50K attendance)  → Urgent/High priority
Large (5K-50K attendance)  → High/Medium priority
Medium (500-5K attendance) → Medium priority
Small (<500 attendance)    → Low priority
```

### 4. Time-Based Urgency

- **≤2 days**: Priority upgrade (medium→high, high→urgent)
- **>threshold**: Filtered out (e.g., don't recommend inventory 30 days in advance)

## Article Features Used

The system analyzes these features from crawled news articles:

### Event Classification
- `event_type_detected`: sports_match, concert, festival, marathon, etc.
- `event_subtype`: football match, rock concert, food festival

### Geographic Data
- `primary_city`: Medellín, Bogotá, Cartagena, Barranquilla
- `neighborhood`: El Poblado, Chapinero, etc.
- `venue_name`: Estadio Atanasio Girardot, Teatro Colón, etc.
- `latitude`, `longitude`: Coordinates for distance calculations

### Temporal Data
- `event_start_datetime`: When the event occurs
- `event_end_datetime`: When it ends
- `event_duration_hours`: Duration
- Days until event (calculated)

### Scale Data
- `expected_attendance`: Estimated number of attendees
- `event_scale`: small, medium, large, massive

### Relevance Scores
- `business_suitability_score`: 0.0-1.0 (how relevant for ANY business)
- `business_relevance_score`: 0.0-1.0 (max relevance across businesses)

## Business Features Used

The system considers these business characteristics:

### Identity
- `business_type`: coffee_shop, restaurant, pub, bookstore
- `city`: Medellín, Bogotá, Cartagena, Barranquilla
- `neighborhood`: Specific neighborhood

### Preferences
- `geographic_radius_km`: Distance threshold (default 5km)
- `include_citywide_events`: Show city-wide events (default true)
- `include_national_events`: Show national events (default false)

### Capacity (Optional, for future use)
- `capacity`: Maximum customers
- `staff_count`: Current staff size

### Keywords
- Custom business keywords with weights
- Used for relevance scoring

## Recommendation Template Structure

Each recommendation template includes:

```python
{
    'title': 'Aumentar inventario de bebidas para {event_name}',
    'description': 'Evento deportivo generará alta demanda...',
    'action_type': 'increase_inventory',
    'category': 'inventory',
    'priority_by_scale': {
        'massive': 'urgent',
        'large': 'urgent',
        'medium': 'high',
        'small': 'medium'
    },
    'estimated_hours': 6,
    'days_threshold': 7,  # Only recommend if event within 7 days
}
```

## Recommendation Categories

### Inventory
- Increase beverage stock
- Prepare for high demand
- Stock healthy options (marathons)
- Seasonal inventory adjustments

### Staffing
- Hire temporary staff
- Adjust shift schedules
- Consider security reinforcement

### Marketing
- Create event-specific promotions
- Pre/post event campaigns
- Social media campaigns
- Cross-promotions with event

### Operations
- Adjust operating hours
- Extend closing time
- Early opening (marathons)
- Menu modifications

### Partnerships
- Event participation
- Vendor collaborations
- Sponsorship opportunities

## Example: Sports Match Recommendation Flow

**Article**: Copa América Final - Colombia vs Argentina
**Features**:
- Event Type: sports_match
- City: Bogotá
- Venue: Estadio El Campín
- Date: 5 days away
- Attendance: 45,000
- Scale: massive

**Business**: Irish Pub (Bogotá)
**Match**: ✅ Compatible (pub + sports_match + same city)

**Recommendations Generated**:

1. **Aumentar inventario de bebidas** (🔴 URGENT)
   - Category: inventory
   - Effort: ~6 hours
   - Days threshold: 7 days
   - Priority: URGENT (massive + ≤7 days)

2. **Campaña de marketing para Copa América** (🟡 HIGH)
   - Category: marketing
   - Effort: ~12 hours
   - Days threshold: 14 days
   - Priority: HIGH (massive scale)

3. **Contratar personal adicional** (🟡 HIGH)
   - Category: staffing
   - Effort: ~8 hours
   - Days threshold: 10 days
   - Priority: HIGH (massive scale)

**Reasoning Provided**:
```
Recomendación generada por evento: sports_match
Título: Copa América Final: Colombia vs Argentina...
Lugar: Estadio El Campín
Ubicación: Bogotá
Fecha: 20/10/2025 (5 días)
Asistencia esperada: 45,000 personas
Escala del evento: massive
```

## Implementation Details

### Files Modified

1. **[backend/ml_engine/services/ml_pipeline.py](../backend/ml_engine/services/ml_pipeline.py)**
   - Lines 280-634: TEMPLATES dictionary (9 event types, ~30 templates)
   - Lines 636-755: Enhanced `generate()` method

### Key Functions

**`RecommendationGenerator.generate(article, business, relevance_score)`**
- Checks business-type compatibility
- Filters by time threshold
- Calculates dynamic priority
- Builds enhanced reasoning
- Returns list of Recommendation objects

**Priority Calculation**:
```python
# Base priority from scale
priority = priority_by_scale[event_scale]

# Upgrade if event is imminent
if days_until_event <= 2:
    if priority == 'high':
        priority = 'urgent'
    elif priority == 'medium':
        priority = 'high'
```

**Impact Score Calculation**:
```python
impact_score = relevance_score * 0.7  # Base (70%)
impact_score += scale_bonus  # 0.05 to 0.30
if days_until_event <= 7:
    impact_score += 0.1  # Timing bonus
impact_score = min(1.0, impact_score)
```

## Testing

### Demo Script

Run: `python3 test/demo_recommendations.py`

Shows 5 sample articles generating recommendations for 4 businesses.

**Results**:
- 5 articles analyzed
- 4 businesses evaluated
- 7 matches found
- 9 recommendations generated

### Manual Testing (with Docker)

1. Start services: `./scripts/start-server.sh`
2. Process articles: `docker exec navigate-django python manage.py process_articles --verbose`
3. Check results: Django Admin or API (`/api/recommendations/`)

## Future Enhancements

### Phase 4 (Production Ready)
- [ ] ML-based priority scoring using historical performance
- [ ] User feedback loop (track which recommendations were useful)
- [ ] A/B testing of recommendation templates
- [ ] Personalized recommendations based on business profile

### Phase 5 (Advanced Features)
- [ ] Quantity recommendations (requires capacity data)
- [ ] ROI estimation per recommendation
- [ ] Multi-location business support
- [ ] Competitor intelligence recommendations
- [ ] Supply chain optimization

## Benefits

### For Business Owners
✅ Actionable recommendations without complex setup
✅ Relevant events based on business type and location
✅ Time-aware urgency (don't miss opportunities)
✅ Generic enough to apply to any business size

### For System
✅ No ML training required (rules-based)
✅ Easy to add new event types
✅ Easy to adjust priorities
✅ Scales to thousands of businesses

### For Future ML
✅ Structured data for training
✅ Feedback loop ready (user ratings)
✅ Clear baseline for improvement
✅ Template system can coexist with ML models

## Related Documentation

- [Phase 3 Task: task-9](../backlog/tasks/task-9%20-%20Phase-3-Frontend-Integration-ML-Enhancement.md)
- [ML Pipeline](../backend/ml_engine/services/ml_pipeline.py)
- [Feature Extraction](../backend/ml_engine/services/feature_extractor.py)
- [News Sources](news-sources-food-events.md)

---

**Last Updated**: 2025-10-15
**Author**: Claude (task-9.4)
**Status**: ✅ Ready for production testing
