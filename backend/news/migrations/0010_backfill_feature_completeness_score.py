# Generated manually on 2025-10-19

from django.db import migrations


def backfill_completeness_scores(apps, schema_editor):
    """Calculate and save feature_completeness_score for all existing articles"""
    NewsArticle = apps.get_model('news', 'NewsArticle')
    
    # Import calculation function
    from news.utils import calculate_feature_completeness
    
    articles = NewsArticle.objects.all()
    total = articles.count()
    updated = 0
    
    print(f"\nBackfilling feature_completeness_score for {total} articles...")
    
    for article in articles:
        try:
            article.feature_completeness_score = calculate_feature_completeness(article)
            article.save(update_fields=['feature_completeness_score'])
            updated += 1
            
            if updated % 100 == 0:
                print(f"Processed {updated}/{total} articles...")
        except Exception as e:
            print(f"Error processing article {article.id}: {e}")
            continue
    
    print(f"✓ Successfully updated {updated} articles")


def reverse_backfill(apps, schema_editor):
    """Reset all completeness scores to 0.0"""
    NewsArticle = apps.get_model('news', 'NewsArticle')
    NewsArticle.objects.all().update(feature_completeness_score=0.0)


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_add_feature_completeness_score'),
    ]

    operations = [
        migrations.RunPython(backfill_completeness_scores, reverse_backfill),
    ]
