"""
Celery tasks for asynchronous ML processing

This module defines background tasks for processing news articles through the ML pipeline.
Articles are processed asynchronously after being saved by the crawler.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    soft_time_limit=120,  # 2 minute timeout per article
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def process_article_async(self, article_id: int) -> dict:
    """
    Process a news article through the ML pipeline asynchronously

    This task is triggered automatically when a new news article is saved.
    It performs feature extraction, business matching, and recommendation generation.

    Args:
        article_id: Primary key of the NewsArticle to process

    Returns:
        Dictionary with processing results

    Raises:
        Retries automatically on failure (up to 3 times)
    """
    from news.models import NewsArticle
    from .services.ml_pipeline import MLOrchestrator

    try:
        # Fetch article
        try:
            article = NewsArticle.objects.get(id=article_id)
        except NewsArticle.DoesNotExist:
            logger.error(f"Article {article_id} not found, cannot process")
            return {
                'success': False,
                'error': 'Article not found',
                'article_id': article_id
            }

        # Skip if already processed
        if article.features_extracted:
            logger.info(f"Article {article_id} already processed, skipping")
            return {
                'success': True,
                'skipped': True,
                'reason': 'Already processed',
                'article_id': article_id
            }

        logger.info(f"Starting ML processing for article {article_id}: {article.title[:50]}...")

        # Process through ML pipeline
        orchestrator = MLOrchestrator()
        result = orchestrator.process_article(article, save=True)

        # Log result
        if result['success']:
            if result.get('processed'):
                logger.info(
                    f"✓ Article {article_id} processed successfully: "
                    f"Suitability={result['suitability_score']:.2f}, "
                    f"Businesses={result['matching_businesses']}, "
                    f"Recommendations={result['recommendations_created']}"
                )
            else:
                logger.info(
                    f"⊘ Article {article_id} not suitable for business: "
                    f"{result.get('reason', 'Unknown reason')}"
                )
        else:
            logger.error(
                f"✗ Article {article_id} processing failed: "
                f"{result.get('error', 'Unknown error')}"
            )

        return {
            **result,
            'article_id': article_id,
            'article_title': article.title[:100],
            'processed_at': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing article {article_id}: {str(e)}")

        # Update article with error
        try:
            article = NewsArticle.objects.get(id=article_id)
            article.processing_error = f"Celery task error: {str(e)}"
            article.save()
        except Exception as save_error:
            logger.error(f"Failed to save error to article {article_id}: {save_error}")

        # Re-raise to trigger Celery retry
        raise


@shared_task
def process_articles_bulk(article_ids: list) -> dict:
    """
    Process multiple articles in bulk

    Args:
        article_ids: List of article IDs to process

    Returns:
        Dictionary with bulk processing statistics
    """
    logger.info(f"Starting bulk processing of {len(article_ids)} articles")

    results = {
        'total': len(article_ids),
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }

    for article_id in article_ids:
        try:
            result = process_article_async.apply_async(args=[article_id])
            results['successful'] += 1
        except Exception as e:
            logger.error(f"Failed to queue article {article_id}: {e}")
            results['failed'] += 1
            results['errors'].append(f"Article {article_id}: {str(e)}")

    logger.info(
        f"Bulk processing queued: {results['successful']} successful, "
        f"{results['failed']} failed"
    )

    return results


@shared_task
def cleanup_old_processing_errors(days: int = 7) -> dict:
    """
    Clean up old processing errors to allow retry

    Args:
        days: Clear errors older than this many days

    Returns:
        Dictionary with cleanup statistics
    """
    from news.models import NewsArticle
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    # Find articles with old errors that haven't been processed
    articles = NewsArticle.objects.filter(
        features_extracted=False,
        processing_error__isnull=False,
        updated_at__lt=cutoff_date
    )

    count = articles.count()
    article_ids = list(articles.values_list('id', flat=True))

    # Clear errors
    articles.update(processing_error='')

    logger.info(f"Cleared processing errors for {count} articles older than {days} days")

    # Queue for reprocessing
    if article_ids:
        process_articles_bulk.apply_async(args=[article_ids])
        logger.info(f"Queued {count} articles for reprocessing")

    return {
        'cleared': count,
        'queued': len(article_ids)
    }
