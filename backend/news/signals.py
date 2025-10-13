"""
Django signals for automatic ML processing of news articles

This module handles post-save signals to trigger asynchronous ML processing
when new articles are created by the crawler.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewsArticle

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NewsArticle)
def trigger_ml_processing(sender, instance, created, **kwargs):
    """
    Automatically trigger ML processing when a new article is saved

    This signal handler:
    1. Only processes NEW articles (created=True)
    2. Skips already processed articles
    3. Queues async Celery task with 5 second delay
    4. Batches multiple articles for efficiency

    Args:
        sender: NewsArticle model class
        instance: The actual article instance being saved
        created: True if this is a new article, False if update
        **kwargs: Additional signal arguments
    """
    # Import here to avoid circular imports
    from ml_engine.tasks import process_article_async

    # Only process NEW articles (not updates)
    if not created:
        return

    # Skip if already processed (safety check)
    if instance.features_extracted:
        logger.debug(f"Article {instance.id} already processed, skipping ML trigger")
        return

    # Skip if there's no content to process
    if not instance.content or len(instance.content) < 50:
        logger.warning(
            f"Article {instance.id} has insufficient content ({len(instance.content)} chars), "
            f"skipping ML processing"
        )
        return

    try:
        # Queue Celery task with small delay for batching
        # The countdown allows the crawler to save multiple articles before processing
        task = process_article_async.apply_async(
            args=[instance.id],
            countdown=5  # Wait 5 seconds before processing
        )

        logger.info(
            f"Queued ML processing for article {instance.id}: {instance.title[:50]}... "
            f"(Task ID: {task.id})"
        )

    except Exception as e:
        # Log error but don't break the save operation
        logger.error(
            f"Failed to queue ML processing for article {instance.id}: {str(e)}. "
            f"Article saved but will need manual processing."
        )


@receiver(post_save, sender=NewsArticle)
def log_article_creation(sender, instance, created, **kwargs):
    """
    Log when new articles are created for monitoring

    Args:
        sender: NewsArticle model class
        instance: The actual article instance being saved
        created: True if this is a new article, False if update
        **kwargs: Additional signal arguments
    """
    if created:
        logger.info(
            f"New article created: [{instance.source.name}] {instance.title[:60]}... "
            f"(ID: {instance.id}, Published: {instance.published_date.strftime('%Y-%m-%d')})"
        )
