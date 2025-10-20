# Testing ML Extraction Improvements

## Overview

This document provides instructions for testing the enhanced ML feature extraction system that targets ~70% completeness.

## What Changed

### 1. Date/Time Extraction (`feature_extractor.py:282-402`)
- **New:** `extract_event_time()` - Extracts times from Spanish text
- **Enhanced:** `extract_event_date()` - Now uses 3 strategies:
  1. spaCy DATE entities (highest priority)
  2. 15+ comprehensive regex patterns
  3. dateparser library (fallback)
- **Patterns added:**
  - Relative dates: "mañana", "pasado mañana", "este sábado"
  - Weekday + date: "sábado 15 de marzo"
  - Numeric formats: "15/03/2025", "2025-03-15"
  - Time extraction: "a las 8 pm", "20:00 horas"

### 2. Duration Extraction (`feature_extractor.py:421-453`)
- **New:** `extract_duration()` - Parses Spanish duration expressions
- Supports: hours, days, weeks, "todo el día", "fin de semana"
- Auto-calculates `event_end_datetime` from start + duration

### 3. Event Type Classification (`feature_extractor.py:187-244`)
- **Fixed:** Now uses hardcoded `EVENT_TYPE_PATTERNS` as fallback
- Previously only used database patterns (could be empty)
- Better coverage for: sports, concerts, festivals, conferences, etc.

### 4. NLP Features (`feature_extractor.py:153-202`, `ml_pipeline.py:838-839`)
- **Now saving:** `extracted_keywords` (top 15 via spaCy)
- **Now saving:** `entities` (named entities: locations, organizations, people)
- These were extracted but never saved before

## Testing Methods

### Method 1: Reprocess All Articles (Recommended)

This will reprocess all existing articles with the new extraction logic:

```bash
# 1. Start the application
cd /home/vramirez/projects/navigate-app
./scripts/start.sh

# 2. Wait for services to be ready, then run reprocessing
docker exec navigate-backend python manage.py process_articles --reprocess

# 3. Monitor progress
# The command will output progress as it processes each article
# Expected time: ~10-30 seconds per article depending on length
```

### Method 2: Reprocess Specific Articles

Test with specific article IDs:

```bash
# Reprocess single article
docker exec navigate-backend python manage.py shell -c "
from news.models import NewsArticle
from ml_engine.services.ml_pipeline import MLOrchestrator

article = NewsArticle.objects.get(id=YOUR_ARTICLE_ID)
orchestrator = MLOrchestrator()
result = orchestrator.process_article(article, save=True)
print(f'Success: {result}')
"
```

### Method 3: Test with Django Shell (Interactive)

```bash
docker exec -it navigate-backend python manage.py shell
```

```python
from news.models import NewsArticle
from ml_engine.services.feature_extractor import FeatureExtractor
from news.utils import calculate_feature_completeness

# Get an article
article = NewsArticle.objects.first()

# Extract features
extractor = FeatureExtractor()
features = extractor.extract_all(article.content, article.title)

# Print results
print(f"\nExtracted Features:")
print(f"Event Type: {features['event_type']}")
print(f"Event Subtype: {features['event_subtype']}")
print(f"Event Date: {features['event_date']}")
print(f"Event End: {features['event_end_datetime']}")
print(f"Duration: {features['event_duration_hours']} hours")
print(f"City: {features['city']}")
print(f"Venue: {features['venue']}")
print(f"Keywords: {features['keywords']}")
print(f"Entities: {len(features['entities'])} entities")

# Update article
article.event_start_datetime = features['event_date']
article.event_end_datetime = features['event_end_datetime']
article.event_duration_hours = features['event_duration_hours']
article.event_type_detected = features['event_type'] or ''
article.event_subtype = features['event_subtype'] or ''
article.extracted_keywords = features['keywords']
article.entities = features['entities']
article.save()

# Check completeness
completeness = calculate_feature_completeness(article)
print(f"\nCompleteness Score: {completeness:.2%}")
```

### Method 4: Test Date Extraction Specifically

```bash
docker exec -it navigate-backend python manage.py shell
```

```python
from ml_engine.services.feature_extractor import FeatureExtractor

extractor = FeatureExtractor()

# Test various date formats
test_texts = [
    "El concierto será el sábado 15 de marzo a las 8 pm",
    "El evento es mañana a las 20:00 horas",
    "El partido es el próximo domingo 21 de abril",
    "Del 15 al 20 de marzo se realizará el festival",
    "Evento: 15/03/2025 a las 19:00",
]

for text in test_texts:
    date = extractor.extract_event_date(text)
    time = extractor.extract_event_time(text)
    print(f"\nText: {text}")
    print(f"Extracted Date: {date}")
    print(f"Extracted Time: {time}")
```

## Expected Results

### Before Changes
- Average completeness: ~50%
- Common missing fields:
  - `event_start_datetime` (missing ~50% of time)
  - `event_type_detected` (missing ~30% of time)
  - `event_subtype` (missing ~60% of time)
  - `extracted_keywords` (always missing - not saved)
  - `entities` (always missing - not saved)
  - `event_duration_hours` (always missing - not extracted)

### After Changes
- Target completeness: ~70%
- Improvements:
  - `event_start_datetime` should extract ~70-80% of time
  - `event_type_detected` should extract ~80-90% of time
  - `event_subtype` should extract ~50-60% of time
  - `extracted_keywords` should ALWAYS be populated
  - `entities` should ALWAYS be populated
  - `event_duration_hours` should extract ~30-40% of time

## Verification Checklist

After reprocessing, verify:

1. **Completeness Score Improved**
   ```bash
   docker exec navigate-backend python manage.py shell -c "
   from news.models import NewsArticle
   from news.utils import calculate_feature_completeness
   import statistics

   articles = NewsArticle.objects.filter(features_extracted=True)[:50]
   scores = [calculate_feature_completeness(a) for a in articles]
   avg = statistics.mean(scores)
   print(f'Average completeness: {avg:.2%}')
   print(f'Min: {min(scores):.2%}, Max: {max(scores):.2%}')
   "
   ```

2. **Date Extraction Working**
   ```bash
   docker exec navigate-backend python manage.py shell -c "
   from news.models import NewsArticle

   total = NewsArticle.objects.filter(features_extracted=True).count()
   with_dates = NewsArticle.objects.filter(
       features_extracted=True,
       event_start_datetime__isnull=False
   ).count()

   print(f'Articles with dates: {with_dates}/{total} ({with_dates/total*100:.1f}%)')
   "
   ```

3. **Event Types Detected**
   ```bash
   docker exec navigate-backend python manage.py shell -c "
   from news.models import NewsArticle

   total = NewsArticle.objects.filter(features_extracted=True).count()
   with_types = NewsArticle.objects.filter(
       features_extracted=True
   ).exclude(event_type_detected='').count()

   print(f'Articles with event type: {with_types}/{total} ({with_types/total*100:.1f}%)')
   "
   ```

4. **Keywords Saved**
   ```bash
   docker exec navigate-backend python manage.py shell -c "
   from news.models import NewsArticle

   total = NewsArticle.objects.filter(features_extracted=True).count()
   with_keywords = NewsArticle.objects.filter(
       features_extracted=True,
       extracted_keywords__len__gt=0
   ).count()

   print(f'Articles with keywords: {with_keywords}/{total} ({with_keywords/total*100:.1f}%)')
   "
   ```

5. **Check Frontend ArticleDebugPanel**
   - Navigate to any article detail page
   - The completeness score should be higher
   - More fields should show as populated (green)

## Troubleshooting

### Issue: Low improvement in completeness

**Possible causes:**
1. Database extraction patterns are empty or inactive
2. Articles don't contain clear date/event information
3. spaCy model not installed: `python -m spacy download es_core_news_md`

**Check:**
```bash
docker exec navigate-backend python manage.py shell -c "
from event_taxonomy.models import ExtractionPattern
print(f'Active patterns: {ExtractionPattern.objects.filter(is_active=True).count()}')
"
```

### Issue: Dates still not extracting

**Debug:**
```python
from ml_engine.services.feature_extractor import FeatureExtractor
import logging
logging.basicConfig(level=logging.DEBUG)

extractor = FeatureExtractor()
text = "YOUR ARTICLE TEXT HERE"
date = extractor.extract_event_date(text)
print(f"Extracted: {date}")

# Check what spaCy found
dates = extractor.nlp.extract_dates(text)
print(f"spaCy found: {dates}")
```

### Issue: Event types not detecting with hardcoded patterns

**Verify patterns are being used:**
```python
from ml_engine.services.feature_extractor import FeatureExtractor

extractor = FeatureExtractor()
print(f"Hardcoded patterns available: {list(extractor.EVENT_TYPE_PATTERNS.keys())}")

# Test specific text
text = "Partido de fútbol entre Medellín y Cali"
event_type, subtype = extractor.extract_event_type(text)
print(f"Detected: {event_type} / {subtype}")
```

## Performance

- **Processing time:** ~10-30 seconds per article (depends on length)
- **No additional API costs:** All improvements are free (regex + spaCy)
- **Memory usage:** Minimal increase (~50MB for spaCy model)
- **Database impact:** Same as before (no schema changes needed)

## Next Steps

1. **Immediate:** Run reprocessing and verify improvements
2. **Monitor:** Track completeness scores over next week
3. **Optional:** If 70% target not met, consider LLM integration (see `LLM_EXTRACTION_PROMPT.md`)
4. **Optional:** Add more extraction patterns to database for specific event types
5. **Future:** Implement article quality scoring to prioritize high-quality sources
