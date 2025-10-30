---
id: task-18.12
title: 'Reprocess All Articles with Per-Type Scoring'
status: Done
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
completed_date: '2025-10-30'
labels:
  - backend
  - ml-engine
  - operations
dependencies: [task-18.3, task-18.11]
parent: task-18
priority: high
estimated_hours: 2
actual_hours: 0.5
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reprocess all existing articles to calculate and store ArticleBusinessTypeRelevance records. This populates the new per-type scoring system for all historical articles. Includes progress tracking and error handling for large batches.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

### Option 1: Extend Existing Management Command

**File**: `backend/news/management/commands/process_articles.py`

Update existing command to support reprocessing flag:

```python
from django.core.management.base import BaseCommand
from django.db.models import Q
from news.models import NewsArticle
from ml_engine.services.ml_pipeline import MLOrchestrator


class Command(BaseCommand):
    help = 'Process news articles through ML pipeline'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reprocess',
            action='store_true',
            help='Reprocess all articles (even those already processed)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of articles to process'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of articles to process before committing (default: 10)'
        )

    def handle(self, *args, **options):
        orchestrator = MLOrchestrator()

        # Build query
        if options['reprocess']:
            # Reprocess all articles with basic features
            queryset = NewsArticle.objects.filter(
                business_suitability_score__gte=0  # Has been through feature extraction
            )
            self.stdout.write(
                self.style.WARNING('REPROCESSING MODE: Processing all articles')
            )
        else:
            # Only process unprocessed articles
            queryset = NewsArticle.objects.filter(
                Q(business_suitability_score=-1.0) |  # Not processed
                Q(type_relevance_scores__isnull=True)  # No type scores yet
            ).distinct()

        if options['limit']:
            queryset = queryset[:options['limit']]

        total = queryset.count()
        self.stdout.write(f'Found {total} articles to process')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('No articles to process'))
            return

        # Process in batches
        batch_size = options['batch_size']
        processed = 0
        success = 0
        failed = 0
        errors = []

        for article in queryset.iterator(chunk_size=batch_size):
            try:
                result = orchestrator.process_article(article, save=True)

                if result['success']:
                    success += 1
                    type_count = len(result.get('type_scores', {}))
                    self.stdout.write(
                        f'[{processed + 1}/{total}] ✓ {article.id}: {article.title[:40]}... '
                        f'({type_count} type scores)'
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'[{processed + 1}/{total}] ✗ {article.id}: {article.title[:40]}... '
                            f'(processing incomplete)'
                        )
                    )

            except Exception as e:
                failed += 1
                error_msg = f'Article {article.id}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(
                    self.style.ERROR(
                        f'[{processed + 1}/{total}] ERROR {article.id}: {str(e)}'
                    )
                )

            processed += 1

            # Progress update every batch
            if processed % batch_size == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Progress: {processed}/{total} ({success} success, {failed} failed)'
                    )
                )

        # Final summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'COMPLETED: {processed} articles processed'))
        self.stdout.write(self.style.SUCCESS(f'  Success: {success}'))

        if failed > 0:
            self.stdout.write(self.style.WARNING(f'  Failed: {failed}'))

        if errors:
            self.stdout.write('\nERRORS:')
            for error in errors[:10]:  # Show first 10 errors
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            if len(errors) > 10:
                self.stdout.write(f'  ... and {len(errors) - 10} more errors')
```

### Option 2: Create Dedicated Reprocessing Script

**File**: `test/reprocess_articles.py` (NEW)

```python
#!/usr/bin/env python
"""
Reprocess all articles to generate ArticleBusinessTypeRelevance scores
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import NewsArticle
from ml_engine.services.ml_pipeline import MLOrchestrator


def main():
    orchestrator = MLOrchestrator()

    # Get all articles with suitability scores
    articles = NewsArticle.objects.filter(
        business_suitability_score__gte=0
    ).order_by('-published_date')

    total = articles.count()
    print(f'Reprocessing {total} articles...\n')

    success = 0
    failed = 0

    for i, article in enumerate(articles, 1):
        try:
            result = orchestrator.process_article(article, save=True)

            if result['success']:
                type_count = len(result.get('type_scores', {}))
                print(f'[{i}/{total}] ✓ {article.id}: {type_count} type scores created')
                success += 1
            else:
                print(f'[{i}/{total}] ✗ {article.id}: Processing incomplete')
                failed += 1

        except Exception as e:
            print(f'[{i}/{total}] ERROR {article.id}: {e}')
            failed += 1

        # Progress update
        if i % 10 == 0:
            print(f'\nProgress: {i}/{total} ({success} success, {failed} failed)\n')

    print('\n' + '=' * 60)
    print(f'COMPLETED: {total} articles processed')
    print(f'  Success: {success}')
    print(f'  Failed: {failed}')


if __name__ == '__main__':
    main()
```

## Testing

### Test 1: Dry Run (Small Batch)

```bash
# Process just 5 articles to test
docker exec docker-backend-1 python manage.py process_articles --reprocess --limit 5

# Verify type scores created
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import ArticleBusinessTypeRelevance

print(f'Total type scores: {ArticleBusinessTypeRelevance.objects.count()}')
print(f'Unique articles: {ArticleBusinessTypeRelevance.objects.values(\"article\").distinct().count()}')

# Show sample
sample = ArticleBusinessTypeRelevance.objects.select_related(
    'article', 'business_type'
)[:10]

for score in sample:
    print(f'{score.article.title[:40]}... -> {score.business_type.code}: {score.relevance_score:.2f}')
"
```

### Test 2: Full Reprocessing

```bash
# Reprocess all articles
docker exec docker-backend-1 python manage.py process_articles --reprocess

# This may take several minutes depending on article count
```

### Test 3: Verify Results

```bash
docker exec docker-backend-1 python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import NewsArticle, ArticleBusinessTypeRelevance
from businesses.models import BusinessType

total_articles = NewsArticle.objects.count()
total_scores = ArticleBusinessTypeRelevance.objects.count()

print(f'Total articles: {total_articles}')
print(f'Total type scores: {total_scores}')
print(f'Average scores per article: {total_scores / total_articles:.1f}')
print()

# Scores per business type
for bt in BusinessType.objects.all():
    count = ArticleBusinessTypeRelevance.objects.filter(business_type=bt).count()
    avg = ArticleBusinessTypeRelevance.objects.filter(
        business_type=bt
    ).aggregate(Avg('relevance_score'))['relevance_score__avg'] or 0

    print(f'{bt.code}: {count} scores, avg {avg:.2f}')
"
```

### Test 4: Verify Dashboard Works

```bash
# Test API with different business types
curl "http://localhost:8000/api/news/articles/?business_type=pub" | jq length
curl "http://localhost:8000/api/news/articles/?business_type=restaurant" | jq length
curl "http://localhost:8000/api/news/articles/?business_type=coffee_shop" | jq length
curl "http://localhost:8000/api/news/articles/?business_type=bookstore" | jq length
```

## Acceptance Criteria

- [ ] Command processes all articles with business_suitability_score >= 0
- [ ] ArticleBusinessTypeRelevance records created for each article
- [ ] Up to 4 type scores per article (one per business type if above threshold)
- [ ] Progress tracking shows articles processed
- [ ] Error handling prevents one failure from stopping batch
- [ ] --limit flag works for testing
- [ ] --batch-size flag controls commit frequency
- [ ] Final summary shows success/failure counts
- [ ] Existing type scores replaced (not duplicated)
- [ ] Dashboard shows articles after reprocessing
- [ ] No articles with user_relevance = -1.0 or 0.0

## Notes

- Requires task-18.3 (MLOrchestrator update) complete
- Requires task-18.11 (keyword seeding) for accurate matching
- Reprocessing is idempotent (safe to run multiple times)
- Large datasets: Consider running overnight
- Monitor database disk space (type scores add data)
- Future: Implement incremental processing (only articles without type scores)

## Progress Log

### 2025-10-30 - Implementation Complete

**Created Management Command**
- Created `backend/news/management/commands/process_articles.py`
- Implemented --reprocess flag to process all articles
- Implemented --limit flag for batch testing
- Implemented --batch-size flag for commit frequency
- Added progress tracking and error handling

**Test Run**
- Successfully tested with --limit 5 flag
- Verified ArticleBusinessTypeRelevance records created
- All 5 articles processed successfully

**Full Reprocessing**
- Ran `docker exec docker-backend-1 python manage.py process_articles --reprocess`
- Processed all 20 articles successfully (100% success rate)
- Created 32 ArticleBusinessTypeRelevance records
  - 8 articles created 4 type scores each (one per business type)
  - 12 articles created 0 type scores (below relevance threshold)
- Average scores per business type:
  - pub: 8 scores, avg 0.46
  - restaurant: 8 scores, avg 0.37
  - coffee_shop: 8 scores, avg 0.38
  - bookstore: 8 scores, avg 0.38

**API Verification**
- Tested API filtering by business_type parameter
- Results per business type (with min_relevance_threshold=0.5):
  - pub: 4 articles
  - restaurant: 1 article
  - coffee_shop: 1 article
  - bookstore: 1 article
- Per-type filtering working correctly

**Files Modified**
- Created: backend/news/management/__init__.py
- Created: backend/news/management/commands/__init__.py
- Created: backend/news/management/commands/process_articles.py

**Committed**
- Branch: task-18.12-reprocess-articles
- Commit: c0edd88
