---
id: task-13
title: Fix Geographic Relevance and Colombian Involvement Detection
status: To Do
priority: high
assignee: @claude
labels: ml-engine, bug-fix, feature
parent: task-9
created: 2025-10-18
milestone: Phase 3 - ML Engine Refinement
---

## Description

**Problem Identified:** Article 593 (film festival in Morelia, Mexico) scores 100% relevance for Colombian businesses despite event being in another country with 0 local impact.

**Root Causes:**
1. Feature extractor fails to detect international cities (only detects Colombian cities)
2. No `event_country` field - system can't distinguish Colombian vs international events
3. No `colombian_involvement` detection - can't identify remote events that generate local traffic (e.g., World Cup matches)
4. Geographic matcher allows articles with empty `primary_city` to pass through
5. Business model doesn't distinguish gathering places (pubs with TVs) from quiet establishments (bookstores)

**Business Impact:**
- Users see irrelevant international events in their dashboard
- Cannot differentiate between:
  - Local events (high relevance)
  - International events with Colombian participation (medium relevance for specific business types)
  - Completely irrelevant international events (zero relevance)

---

## User Requirements

### Requirement 1: Detect Event Country
System should identify WHERE an event physically occurs:
- Events in Colombia → high relevance
- Events outside Colombia → low/zero relevance by default

### Requirement 2: Detect Colombian Involvement
Some international events generate local traffic:
- **Sports**: World Cup match with Colombia playing → people go to pubs to watch
- **Culture**: Colombian artist at international event → some interest
- **Awards**: Oscar nomination of Colombian → media attention

### Requirement 3: Business-Type-Specific Relevance
International events with Colombian involvement should ONLY be relevant to specific business types:
- **Pubs/bars with TVs**: HIGH relevance for sports events (people watch matches)
- **Bookstores/quiet cafés**: LOW relevance for sports events
- **Cultural venues**: MEDIUM relevance for cultural events

---

## Implementation Plan

### Part 1: Database Schema Changes ✅ DONE

**backend/news/models.py**
```python
colombian_involvement = models.BooleanField(default=False)
event_country = models.CharField(max_length=100, blank=True)
```

**backend/businesses/models.py**
```python
has_tv_screens = models.BooleanField(default=False)
```

**Status:** Fields added, migration pending.

---

### Part 2: Feature Extractor Updates ⏳ TO DO

**File:** `backend/ml_engine/services/feature_extractor.py`

**Add international city detection:**
```python
INTERNATIONAL_CITIES = {
    'México': ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Morelia', 'Puebla'],
    'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza'],
    'Brasil': ['São Paulo', 'Río de Janeiro', 'Brasilia', 'Salvador'],
    'Estados Unidos': ['Nueva York', 'Los Ángeles', 'Miami', 'Houston'],
    'España': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla'],
    'Qatar': ['Doha'],
    'Rusia': ['Moscú'],
    # Add more as needed
}
```

**Add Colombian involvement detection:**
```python
def detect_colombian_involvement(self, text: str) -> bool:
    """
    Detect if event involves Colombia or Colombians

    Patterns:
    - Selección Colombia, Colombia vs X
    - Colombiano/a participa, compite, juega
    - Artista/director/atleta colombiano
    - Equipo colombiano
    """
    patterns = [
        r'selección\s+colombia',
        r'colombia\s+(vs|contra)\s+',
        r'colombiano[sa]?\s+(participa|compite|juega|dirige|actúa)',
        r'(artista|director|atleta|actor|actriz)\s+colombiano',
        r'equipo\s+colombiano',
        r'representante\s+de\s+colombia',
        r'colombia\s+en\s+(la\s+)?(copa|mundial|olimpiadas|festival)',
    ]

    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in patterns)
```

**Add country extraction:**
```python
def extract_event_country(self, text: str, primary_city: str) -> str:
    """
    Determine event country from text and extracted city

    Returns: 'Colombia', 'México', 'Argentina', etc. or ''
    """
    # Check if city is Colombian
    if primary_city in self.COLOMBIAN_CITIES:
        return 'Colombia'

    # Check if city is in international cities dict
    for country, cities in self.INTERNATIONAL_CITIES.items():
        if primary_city in cities:
            return country

    # Parse country from text patterns
    country_patterns = [
        r'en\s+(méxico|argentina|brasil|estados unidos|españa)',
        r'festival.*\((méxico|argentina|brasil)\)',
    ]

    for pattern in country_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).title()

    return ''  # Unknown
```

**Update extract_features() method:**
```python
def extract_features(self, article) -> Dict[str, Any]:
    # ... existing code ...

    # Extract country
    event_country = self.extract_event_country(text, primary_city)

    # Detect Colombian involvement
    colombian_involvement = self.detect_colombian_involvement(text)

    return {
        # ... existing fields ...
        'event_country': event_country,
        'colombian_involvement': colombian_involvement,
    }
```

---

### Part 3: Geographic Matcher Updates ⏳ TO DO

**File:** `backend/ml_engine/services/ml_pipeline.py`

**Update `GeographicMatcher.is_relevant()` method:**

```python
def is_relevant(self, article: NewsArticle, business: Business) -> bool:
    """
    Determine if article is geographically relevant to business

    New logic:
    1. Local events (same city in Colombia) → ALWAYS relevant
    2. National events (Colombia, different city) → relevant if business.include_national_events
    3. International events WITHOUT Colombian involvement → NOT relevant
    4. International events WITH Colombian involvement → relevant ONLY for gathering places
    """

    # Case 1: Local event (same city in Colombia)
    if article.event_country == 'Colombia' and article.primary_city:
        article_city = self._normalize_city(article.primary_city)
        business_city = self._normalize_city(business.get_city_display())

        if article_city == business_city:
            return True

        # Case 2: National event (different Colombian city)
        if business.include_national_events:
            if article.event_scale in ['massive', 'large']:
                return True

    # Case 3: International event WITHOUT Colombian involvement
    if article.event_country and article.event_country != 'Colombia':
        if not article.colombian_involvement:
            return False  # Not relevant at all

        # Case 4: International event WITH Colombian involvement
        # Only relevant for "gathering places" (pubs with TVs)
        if business.has_tv_screens:
            # Check if event type is "watchable"
            if article.event_type_detected in ['sports_match', 'tournament', 'awards', 'festival']:
                return True

    # Case 5: Unknown location - be conservative
    if not article.primary_city and not article.event_country:
        # Only show if it's a massive national event
        if article.event_scale == 'massive' and business.include_national_events:
            return True
        return False

    return False

def _normalize_city(self, city: str) -> str:
    """Normalize city name for comparison"""
    return city.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
```

---

### Part 4: PreFilter Suitability Calculation Updates ⏳ TO DO

**File:** `backend/ml_engine/services/ml_pipeline.py`

**Update `PreFilter.calculate_suitability()` to accept business parameter:**

```python
def calculate_suitability(self, article: NewsArticle, event_type: Optional[str] = None, business: Optional[Business] = None) -> float:
    """
    Calculate 0.0-1.0 score for business suitability

    Now considers:
    - Event type (existing)
    - Event location/country (NEW)
    - Colombian involvement (NEW)
    - Business characteristics (NEW)
    """

    text = f"{article.title} {article.content}".lower()

    # Existing paywall/quality checks
    if any(re.search(pattern, text) for pattern in self.PAYWALL_PATTERNS):
        return 0.0

    # Base score from event type (existing logic)
    score = 0.0
    if event_type:
        if event_type in self.HIGH_RELEVANCE_CATEGORIES:
            score = self.HIGH_RELEVANCE_CATEGORIES[event_type]
        elif event_type in self.MEDIUM_RELEVANCE_CATEGORIES:
            score = self.MEDIUM_RELEVANCE_CATEGORIES[event_type]
        elif event_type in self.LOW_RELEVANCE_CATEGORIES:
            score = self.LOW_RELEVANCE_CATEGORIES[event_type]

    # NEW: Penalize international events without Colombian involvement
    if article.event_country and article.event_country != 'Colombia':
        if not article.colombian_involvement:
            return 0.0  # Completely irrelevant

        # Has Colombian involvement but is international
        # Reduce score significantly
        score *= 0.4  # 60% penalty

        # Additional penalty if business doesn't have TVs (for sports events)
        if business:
            if event_type in ['sports_match', 'tournament'] and not business.has_tv_screens:
                return 0.0  # Sports event but no TVs = not relevant

    # NEW: Boost for Colombian involvement in sports
    if article.colombian_involvement and event_type in ['sports_match', 'tournament']:
        if business and business.has_tv_screens:
            score += 0.2  # Extra boost for pubs/bars with TVs

    # Existing hospitality keywords boost
    hospitality_matches = sum(1 for kw in self.HOSPITALITY_KEYWORDS if re.search(kw, text))
    score += min(0.3, hospitality_matches * 0.1)

    # Existing negative keywords penalty
    negative_matches = sum(1 for kw in self.NEGATIVE_KEYWORDS if re.search(kw, text))
    score -= negative_matches * 0.5

    return max(0.0, min(1.0, score))
```

**Update `MLPipeline.process_article()` to pass business to prefilter:**

```python
# OLD: article.business_suitability_score = self.prefilter.calculate_suitability(article, features['event_type'])

# NEW: Calculate suitability considering primary business (business_id=1 for demo)
from businesses.models import Business
primary_business = Business.objects.filter(id=1).first()
article.business_suitability_score = self.prefilter.calculate_suitability(
    article,
    features['event_type'],
    business=primary_business
)
```

---

### Part 5: Update Serializers ⏳ TO DO

**File:** `backend/news/serializers.py`

Add new fields to NewsArticleSerializer:
```python
fields = [
    # ... existing fields ...
    'colombian_involvement', 'event_country',
]
```

**File:** `backend/businesses/serializers.py`

Add new field to BusinessSerializer:
```python
fields = [
    # ... existing fields ...
    'has_tv_screens',
]
```

---

### Part 6: Django Migrations ⏳ TO DO

```bash
# Create migrations
python manage.py makemigrations news businesses

# Expected migrations:
# - news.0008_add_colombian_involvement_event_country
# - businesses.0003_add_has_tv_screens

# Apply migrations
python manage.py migrate

# Update existing business (set has_tv_screens=True for pubs)
python manage.py shell
>>> from businesses.models import Business
>>> Business.objects.filter(business_type='pub').update(has_tv_screens=True)
```

---

### Part 7: Reprocess Existing Articles ⏳ TO DO

```bash
# Reprocess articles to extract new fields
python manage.py process_articles --reprocess --limit 100

# Verify article 593 is now correctly scored
python manage.py shell
>>> from news.models import NewsArticle
>>> art = NewsArticle.objects.get(id=593)
>>> print(f"Country: {art.event_country}")
>>> print(f"Colombian involvement: {art.colombian_involvement}")
>>> print(f"Suitability: {art.business_suitability_score}")
# Expected: Country='México', colombian_involvement=True, suitability=0.3-0.4 (not 1.0)
```

---

## Acceptance Criteria

- [ ] 1. Article 593 (Mexican film festival) correctly identified as `event_country='México'`
- [ ] 2. Article 593 correctly identified as `colombian_involvement=True` (director colombiano)
- [ ] 3. Article 593 has `business_suitability_score < 0.5` (not 1.0)
- [ ] 4. Article 593 NOT shown in dashboard for bookstores
- [ ] 5. Article 593 shown with LOW relevance for pubs WITH TVs (cultural event, not sports)
- [ ] 6. World Cup match (hypothetical) with Colombia playing:
  - [ ] Correctly detected as international with Colombian involvement
  - [ ] HIGH relevance for pubs with TVs
  - [ ] ZERO relevance for bookstores
- [ ] 7. Local event (Medellín) correctly shows HIGH relevance for all Medellín businesses
- [ ] 8. International event WITHOUT Colombian involvement scores 0.0 and is filtered out
- [ ] 9. Migration runs successfully on production database
- [ ] 10. Reprocessing existing articles completes without errors

---

## Testing Plan

### Test Case 1: Article 593 (Mexican Film Festival)
**Input:** Film premiere in Morelia, Mexico with Colombian director
**Expected:**
- `event_country`: 'México'
- `colombian_involvement`: True
- `business_suitability_score`: 0.3-0.4 (cultural event, international)
- **Pub with TV:** Low/medium relevance (cultural, not sports)
- **Bookstore:** Zero relevance

### Test Case 2: World Cup Match - Colombia vs Brazil (Qatar)
**Input:** Sports match in Qatar, Colombia playing
**Expected:**
- `event_country`: 'Qatar'
- `colombian_involvement`: True
- `event_type_detected`: 'sports_match'
- `business_suitability_score`: 0.9 for pub with TV, 0.0 for bookstore
- **Pub with TV:** HIGH relevance (people come to watch)
- **Bookstore:** Zero relevance

### Test Case 3: Local Event - Marathon in Medellín
**Input:** Marathon in Medellín
**Expected:**
- `event_country`: 'Colombia'
- `primary_city`: 'Medellín'
- `business_suitability_score`: 0.8
- **All Medellín businesses:** HIGH relevance

### Test Case 4: Oscars (Los Angeles, no Colombian nominee)
**Input:** Oscar awards in LA, no Colombians
**Expected:**
- `event_country`: 'Estados Unidos'
- `colombian_involvement`: False
- `business_suitability_score`: 0.0
- **All businesses:** Zero relevance

---

## Dependencies

- task-4: ML feature extraction (foundation)
- task-9: Phase 3 ML engine (parent epic)

## Blockers

None

---

## Technical Notes

### City Detection Challenges
- Some cities have multiple names (e.g., "Ciudad de México" vs "CDMX")
- Accent handling required (Bogotá vs Bogota)
- Some articles mention multiple cities (extract primary venue city)

### Colombian Involvement Edge Cases
- Colombian living abroad vs Colombian national team
- Colombian company sponsoring vs Colombian participating
- Threshold: must be meaningful involvement, not just mention

### Business Type Mapping
Current types that should have `has_tv_screens=True` by default:
- `pub` → True
- `bar` → True
- `sports_bar` → True
- `restaurant` → Depends (some do, some don't)
- `coffee_shop` → Usually False
- `bookstore` → False

---

## Progress Log

### 2025-10-18 - Task Created
- Bug identified by user: Article 593 scored 100% despite being in Mexico
- Root causes analyzed: missing country detection, no Colombian involvement field
- User requirements gathered via interactive questions
- Models updated with new fields (colombian_involvement, event_country, has_tv_screens)
- Implementation plan drafted
- Status: Models ready, feature extractor updates needed

**Next Steps:**
1. Update FeatureExtractor with international city detection
2. Update GeographicMatcher with new relevance logic
3. Update PreFilter with country/involvement penalties
4. Create and apply migrations
5. Reprocess articles and verify article 593 scoring
