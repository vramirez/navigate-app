"""
Management command to process news articles through ML pipeline

Usage:
    python manage.py process_articles                    # Process all unprocessed
    python manage.py process_articles --reprocess         # Reprocess all articles
    python manage.py process_articles --city Medellín     # Process only Medellín articles
    python manage.py process_articles --limit 10          # Process max 10 articles
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import NewsArticle
from ml_engine.services.ml_pipeline import MLOrchestrator


class Command(BaseCommand):
    help = 'Process news articles through ML pipeline for feature extraction and recommendations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reprocess',
            action='store_true',
            help='Reprocess all articles (including already processed)',
        )
        parser.add_argument(
            '--min-suitability',
            type=float,
            default=0.3,
            help='Minimum suitability score to generate recommendations (default: 0.3)',
        )
        parser.add_argument(
            '--city',
            type=str,
            help='Filter by city (e.g., Medellín, Bogotá)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Process max N articles',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed processing information',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ML article processing...'))

        # Query articles
        articles = NewsArticle.objects.all().select_related('source')

        # Apply filters
        if not options['reprocess']:
            articles = articles.filter(features_extracted=False)
            self.stdout.write(f'Processing only unprocessed articles')
        else:
            self.stdout.write(f'Reprocessing all articles')

        if options['city']:
            # This will work after first processing sets primary_city
            articles = articles.filter(primary_city=options['city'])
            self.stdout.write(f"Filtering by city: {options['city']}")

        total_count = articles.count()

        if options['limit']:
            articles = articles[:options['limit']]
            self.stdout.write(f"Limited to {options['limit']} articles")

        self.stdout.write(f'Total articles to process: {articles.count()} of {total_count}')

        # Initialize orchestrator
        orchestrator = MLOrchestrator()

        # Process statistics
        stats = {
            'processed': 0,
            'suitable': 0,
            'not_suitable': 0,
            'recommendations_created': 0,
            'errors': 0
        }

        # Process each article
        start_time = timezone.now()

        for idx, article in enumerate(articles, 1):
            try:
                if options['verbose']:
                    self.stdout.write(f"\n[{idx}/{articles.count()}] Processing: {article.title[:60]}...")

                result = orchestrator.process_article(article, save=True)

                if result['success']:
                    stats['processed'] += 1

                    if result['processed']:
                        stats['suitable'] += 1
                        stats['recommendations_created'] += result['recommendations_created']

                        if options['verbose']:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  ✓ Suitability: {result['suitability_score']:.2f}, "
                                    f"Matches: {result['matching_businesses']}, "
                                    f"Recommendations: {result['recommendations_created']}"
                                )
                            )
                    else:
                        stats['not_suitable'] += 1
                        if options['verbose']:
                            self.stdout.write(
                                self.style.WARNING(f"  ⊘ {result.get('reason', 'Not suitable')}")
                            )
                else:
                    stats['errors'] += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error: {result.get('error', 'Unknown error')}")
                    )

                # Progress indicator (every 20 articles)
                if idx % 20 == 0 and not options['verbose']:
                    self.stdout.write(f"Processed {idx}/{articles.count()}...")

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\n\nProcessing interrupted by user'))
                break
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Unexpected error: {str(e)}")
                )

        # Calculate processing time
        duration = (timezone.now() - start_time).total_seconds()

        # Print final statistics
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('Processing Complete!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f"Total processed:          {stats['processed']}")
        self.stdout.write(f"Suitable for business:    {stats['suitable']}")
        self.stdout.write(f"Not suitable:             {stats['not_suitable']}")
        self.stdout.write(f"Recommendations created:  {stats['recommendations_created']}")
        self.stdout.write(f"Errors:                   {stats['errors']}")
        self.stdout.write(f"Processing time:          {duration:.1f} seconds")

        if stats['processed'] > 0:
            avg_time = duration / stats['processed']
            self.stdout.write(f"Average per article:      {avg_time:.2f} seconds")

        self.stdout.write(self.style.SUCCESS('='*70))

        # Success message with actionable next steps
        if stats['recommendations_created'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Generated {stats['recommendations_created']} recommendations!"
                )
            )
            self.stdout.write("\nNext steps:")
            self.stdout.write("  1. View recommendations in Django Admin")
            self.stdout.write("  2. Check Dashboard at http://localhost:3000")
            self.stdout.write("  3. Test API: /api/recommendations/")
