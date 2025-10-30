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
