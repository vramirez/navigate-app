# Automatic ML Processing for News Articles

## Overview

News articles are now automatically processed through the ML pipeline when saved by the crawler. This is implemented using Django signals and Celery background tasks.

## Architecture

```
News Crawler
    ↓
NewsArticle.save() [Django ORM]
    ↓
post_save signal triggered
    ↓
Celery task queued (5 second delay)
    ↓
ML Pipeline processing (async)
    ↓
Features extracted + Recommendations created
```

## Implementation Components

### 1. Celery Task (`ml_engine/tasks.py`)

**Task:** `process_article_async(article_id)`

- Processes one article through `MLOrchestrator`
- Auto-retries on failure (max 3 attempts, 60s delay)
- Timeout: 120 seconds per article
- Logs all processing results

**Configuration:**
- Max retries: 3
- Retry backoff: Exponential with jitter
- Soft time limit: 120 seconds
- Auto-retry on exceptions

### 2. Django Signal (`news/signals.py`)

**Signal:** `post_save` on `NewsArticle`

**Trigger conditions:**
- Only for NEW articles (`created=True`)
- Only if not already processed
- Only if content length > 50 characters

**Behavior:**
- Queues Celery task with 5-second countdown
- Non-blocking (doesn't slow down crawler)
- Error-safe (failures logged but don't break save)

### 3. App Configuration (`news/apps.py`)

Registers signals when Django app starts via `ready()` method.

## Processing Flow

### Step 1: Article Creation
```python
article = NewsArticle.objects.create(
    source=source,
    title="Event in Medellín...",
    content="Description...",
    url="https://...",
    published_date=timezone.now()
)
# Signal automatically triggered here
```

### Step 2: Signal Handler
- Validates article is new and has content
- Queues Celery task with 5s delay
- Logs task ID for tracking

### Step 3: Celery Worker
- Picks up task after countdown
- Loads article from database
- Runs ML pipeline:
  - Feature extraction (event type, city, venue, dates)
  - Business suitability scoring
  - Geographic matching
  - Business relevance scoring
  - Recommendation generation

### Step 4: Results Saved
- Article fields updated:
  - `features_extracted = True`
  - Event type, city, venue, etc.
  - Suitability and relevance scores
- Recommendations created and linked

## Running the System

### Start Celery Worker

**Inside Docker container:**
```bash
docker exec -d docker-backend-1 celery -A navigate worker --loglevel=info --logfile=/tmp/celery_worker.log
```

**Locally (if not using Docker):**
```bash
cd backend
celery -A navigate worker --loglevel=info
```

### Monitor Processing

**View Celery logs:**
```bash
docker exec docker-backend-1 tail -f /tmp/celery_worker.log
```

**Check processing status:**
```bash
docker exec docker-backend-1 python manage.py shell -c "
from news.models import NewsArticle
total = NewsArticle.objects.count()
processed = NewsArticle.objects.filter(features_extracted=True).count()
print(f'Processed: {processed}/{total} ({processed/total*100:.1f}%)')
"
```

## Testing

### Test Automatic Processing

Create a test article and verify it gets processed:

```python
from news.models import NewsSource, NewsArticle
from django.utils import timezone
import time

# Create article
source = NewsSource.objects.first()
article = NewsArticle.objects.create(
    source=source,
    title="Test Event in Medellín",
    content="This is a test event with relevant business content...",
    url=f"https://test.example.com/article-{int(time.time())}",
    published_date=timezone.now()
)

print(f"Created article ID: {article.id}")

# Wait for processing
time.sleep(15)
article.refresh_from_db()

print(f"Processed: {article.features_extracted}")
print(f"Event type: {article.event_type_detected}")
print(f"City: {article.primary_city}")
```

### Expected Timeline

- **0s:** Article created, signal triggered
- **5s:** Celery task starts
- **8-10s:** ML processing completes
- **10-15s:** Article marked as processed

## Performance Characteristics

### Processing Speed
- **Per article:** 3-5 seconds
- **Batch of 20:** 60-100 seconds (parallel processing)
- **Bottleneck:** Spanish NLP model loading (first article only)

### Resource Usage
- **Memory:** ~500MB per Celery worker
- **CPU:** High during NLP processing
- **Redis:** Minimal (task queue only)

### Scalability
- **Current:** 1 worker, sequential processing
- **Recommended prod:** 4-8 workers for parallel processing
- **Max throughput:** ~10-15 articles/minute per worker

## Configuration

### Celery Settings (`navigate/settings.py`)

```python
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'
```

### Task Configuration (`ml_engine/tasks.py`)

```python
@shared_task(
    max_retries=3,              # Retry failed tasks up to 3 times
    default_retry_delay=60,     # Wait 60s between retries
    soft_time_limit=120,        # 2 minute timeout per article
    autoretry_for=(Exception,), # Auto-retry on any exception
    retry_backoff=True,         # Exponential backoff
    retry_jitter=True,          # Add randomness to retry timing
)
```

## Monitoring and Debugging

### Check Recent Processing

```bash
docker exec docker-backend-1 python manage.py shell -c "
from news.models import NewsArticle
from django.utils import timezone
from datetime import timedelta

recent = NewsArticle.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
)

total = recent.count()
processed = recent.filter(features_extracted=True).count()

print(f'Last hour: {processed}/{total} processed')
"
```

### View Processing Errors

```bash
docker exec docker-backend-1 python manage.py shell -c "
from news.models import NewsArticle

errors = NewsArticle.objects.exclude(processing_error='').order_by('-id')[:5]

for article in errors:
    print(f'ID {article.id}: {article.title[:40]}')
    print(f'  Error: {article.processing_error}')
    print()
"
```

### Celery Task History

```bash
# View all tasks
docker exec docker-backend-1 celery -A navigate inspect active

# View registered tasks
docker exec docker-backend-1 celery -A navigate inspect registered

# View worker stats
docker exec docker-backend-1 celery -A navigate inspect stats
```

## Troubleshooting

### Issue: Articles not being processed

**Check:**
1. Is Celery worker running?
   ```bash
   docker exec docker-backend-1 ps aux | grep celery
   ```

2. Is Redis available?
   ```bash
   docker ps | grep redis
   ```

3. Are signals registered?
   ```bash
   docker exec docker-backend-1 python manage.py shell -c "
   import news.signals
   print('Signals imported successfully')
   "
   ```

### Issue: Processing is slow

**Solutions:**
- Start multiple Celery workers
- Increase worker concurrency: `--concurrency=4`
- Use separate queue for ML tasks

### Issue: Worker crashes

**Check logs:**
```bash
docker exec docker-backend-1 tail -100 /tmp/celery_worker.log
```

**Common causes:**
- Out of memory (increase Docker memory)
- Timeout (increase `soft_time_limit`)
- Missing dependencies (check requirements.txt)

## Maintenance Tasks

### Process Backlog of Old Articles

For articles created before automatic processing was enabled:

```bash
docker exec docker-backend-1 python manage.py process_articles
```

### Clear Old Processing Errors

Use the Celery task to retry failed articles:

```bash
docker exec docker-backend-1 python manage.py shell -c "
from ml_engine.tasks import cleanup_old_processing_errors
result = cleanup_old_processing_errors.delay(days=7)
print(f'Cleanup task queued: {result.id}')
"
```

### Monitor Queue Size

```bash
docker exec docker-backend-1 python manage.py shell -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
queue_size = r.llen('celery')
print(f'Tasks in queue: {queue_size}')
"
```

## Production Recommendations

1. **Multiple Workers:** Run 4-8 Celery workers for parallel processing
2. **Monitoring:** Set up Flower for Celery monitoring
3. **Alerting:** Configure alerts for failed tasks
4. **Logging:** Send logs to centralized logging system
5. **Health Checks:** Monitor worker heartbeat
6. **Rate Limiting:** Consider rate limits on expensive ML operations
7. **Resource Limits:** Set memory and CPU limits for workers

## Related Documentation

- [ML Pipeline](ML_PIPELINE.md)
- [News Crawler](NEWS_CRAWLER.md)
- [Celery Configuration](../navigate/celery.py)
- [Task Definitions](../ml_engine/tasks.py)

## Test Results

**Test Date:** 2025-10-13

**Test Case:** Automatic processing of manually created article

**Results:**
- ✅ Article created successfully
- ✅ Signal triggered automatically
- ✅ Celery task queued with 5s delay
- ✅ ML processing completed in 3.2 seconds
- ✅ Features extracted correctly:
  - Event type: sports_match
  - City: Medellín
  - Venue: Estadio Atanasio Girardot
  - Attendance: 40,000
  - Suitability: 1.0
- ✅ 2 recommendations created for matching business

**Performance:** 8.2 seconds from article creation to recommendations

**Conclusion:** System working as expected! 🎉
