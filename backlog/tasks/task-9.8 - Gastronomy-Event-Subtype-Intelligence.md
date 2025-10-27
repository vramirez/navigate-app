---
id: task-9.8
title: Gastronomy Event Subtype Intelligence
status: In Progress
assignee:
  - '@claude'
created_date: '2025-10-27 15:08'
updated_date: '2025-10-27 15:48'
labels:
  - ml-engine
  - feature
  - database
  - gastronomy
dependencies: []
parent_task_id: task-9
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Split generic food_event into 6 distinct subtypes (food_festival, wine_event, chef_competition, restaurant_opening, culinary_workshop, gastronomy_award) with different relevance scores. Add cuisine type extraction (Italian, Japanese, Colombian, etc.)
<!-- SECTION:DESCRIPTION:END -->

## Progress Log

### 2025-10-27 - Session 1 (30% Complete)

**Completed**:
- ✅ Created CuisineType model (event_taxonomy/models.py:563-615)
- ✅ Added cuisine_types JSONField to NewsArticle (news/models.py:748-754)
- ✅ Created migrations (0004_add_cuisine_type, 0013_add_cuisine_types_field)
- ✅ Applied migrations successfully
- ✅ Registered CuisineType in Django admin (event_taxonomy/admin.py:226-242)

**Pending**:
- ❌ Create 6 food event subtypes (food_festival, wine_event, chef_competition, restaurant_opening, culinary_workshop, gastronomy_award)
- ❌ Add 30+ ExtractionPattern entries for each food subtype
- ❌ Update LLM prompt in llm_extractor.py to extract food_subtype + cuisine_types
- ❌ Update ML pipeline to handle food subtype scoring with different relevance scores
- ❌ Create seed script (scripts/seed_gastronomy_taxonomy.py) with:
  - 6 food event subtypes
  - 15 cuisine types (Italian, Japanese, Mexican, Colombian, French, Chinese, Peruvian, Argentine, Spanish, Thai, Indian, Fusion, Mediterranean, American, Venezuelan)
  - 30+ extraction patterns for food subtypes
- ❌ Test with sample food event articles

**Estimated Time Remaining**: 2-3 hours

**Files Modified**:
- backend/event_taxonomy/models.py (+53 lines)
- backend/news/models.py (+8 lines)
- backend/event_taxonomy/admin.py (+17 lines)

## Acceptance Criteria

- [ ] 6 food event subtypes created in EventSubtype model with appropriate base scores:
  - food_festival (0.95 appeal - mass crowds)
  - wine_event (0.70 appeal - niche)
  - chef_competition (0.60 appeal - industry interest)
  - restaurant_opening (0.75 appeal - competitive intel)
  - culinary_workshop (0.55 appeal - learning/community)
  - gastronomy_award (0.65 appeal - prestige)
- [ ] 30+ ExtractionPattern entries created (5+ patterns per subtype)
- [ ] CuisineType model populated with 15 cuisine types
- [ ] LLM prompt extracts food_subtype and cuisine_types fields
- [ ] ML pipeline uses dynamic food subtype scoring
- [ ] Category mapping updated to use database-driven food subtypes
- [ ] Seed script created and documented
- [ ] Tested with food festival, wine event, and restaurant opening articles
- [ ] Food events show proper subtype in Django admin
- [ ] Restaurants receive targeted recommendations based on cuisine type
