#!/usr/bin/env python3
"""
Find real upcoming event articles and test improved extraction
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import NewsArticle
from news.utils import calculate_feature_completeness
from ml_engine.services.feature_extractor import FeatureExtractor
from datetime import datetime

def main():
    print("="*80)
    print("REAL UPCOMING EVENT ARTICLES - EXTRACTION TEST")
    print("="*80)
    print()

    # Find articles that mention future event keywords
    future_keywords = [
        'próximo', 'este sábado', 'este domingo', 'este viernes',
        'mañana', 'festival', 'concierto', 'partido',
        'este fin de semana', 'la próxima semana'
    ]

    print("Searching for upcoming event articles...")

    # Get recent articles with good business suitability
    candidates = NewsArticle.objects.filter(
        business_suitability_score__gte=0.7,
        features_extracted=True
    ).order_by('-id')[:200]

    print(f"Checking {len(candidates)} recent articles...")
    print()

    upcoming_events = []

    for article in candidates:
        content_lower = (article.title + ' ' + article.content).lower()

        # Check if mentions future keywords
        if any(kw in content_lower for kw in future_keywords):
            completeness = calculate_feature_completeness(article)

            # Only include if completeness could be improved
            if completeness < 0.8:
                upcoming_events.append({
                    'article': article,
                    'current_completeness': completeness,
                    'title': article.title
                })

    if not upcoming_events:
        print("No upcoming event articles found with <80% completeness")
        return

    # Sort by lowest completeness first
    upcoming_events.sort(key=lambda x: x['current_completeness'])

    print(f"Found {len(upcoming_events)} upcoming event articles")
    print("Testing top 5 with lowest completeness...")
    print()

    extractor = FeatureExtractor()
    results = []

    for i, item in enumerate(upcoming_events[:5], 1):
        article = item['article']
        old_completeness = item['current_completeness']

        print(f"[{i}/5] Article #{article.id}")
        print(f"  Title: {article.title[:70]}...")
        print(f"  Current completeness: {old_completeness:.1%}")

        # Store current values
        old_values = {
            'event_date': article.event_start_datetime,
            'city': article.primary_city,
            'venue': article.venue_name,
            'attendance': article.expected_attendance,
        }

        # Re-extract with improved code
        features = extractor.extract_all(article.content, article.title)

        # Update article object (in-memory only)
        article.event_type_detected = features.get('event_type', '')
        article.event_subtype = features.get('event_subtype', '')
        article.primary_city = features.get('city', '')
        article.neighborhood = features.get('neighborhood', '')
        article.venue_name = features.get('venue', '')
        article.event_start_datetime = features.get('event_date')
        article.event_end_datetime = features.get('event_end_datetime')
        article.event_duration_hours = features.get('event_duration_hours')
        article.expected_attendance = features.get('attendance')
        article.event_scale = features.get('scale', '')
        article.colombian_involvement = features.get('colombian_involvement', False)
        article.extracted_keywords = features.get('keywords', [])
        article.entities = features.get('entities', [])

        # Calculate new completeness
        new_completeness = calculate_feature_completeness(article)
        improvement = new_completeness - old_completeness

        print(f"  NEW completeness: {new_completeness:.1%} ({improvement:+.1%})")

        # Show what was gained
        if improvement > 0:
            gained = []
            new_values = {
                'event_date': article.event_start_datetime,
                'city': article.primary_city,
                'venue': article.venue_name,
                'attendance': article.expected_attendance,
            }

            for key, new_val in new_values.items():
                old_val = old_values[key]
                if new_val and new_val not in [None, '', [], 0.0] and old_val in [None, '', [], 0.0]:
                    val_str = str(new_val)[:50]
                    gained.append(f"{key}={val_str}")

            if gained:
                print(f"  Gained: {', '.join(gained)}")

        results.append({
            'article_id': article.id,
            'title': article.title,
            'old_completeness': old_completeness,
            'new_completeness': new_completeness,
            'improvement': improvement,
        })

        print()

        # Rollback changes
        article.refresh_from_db()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)

    if results:
        avg_old = sum(r['old_completeness'] for r in results) / len(results)
        avg_new = sum(r['new_completeness'] for r in results) / len(results)
        avg_improvement = avg_new - avg_old

        print(f"\nTested {len(results)} real upcoming event articles")
        print(f"Average OLD completeness: {avg_old:.1%}")
        print(f"Average NEW completeness: {avg_new:.1%}")
        print(f"Average improvement:      {avg_improvement:+.1%}")

        if avg_improvement > 0.05:
            print(f"\n✅ REAL IMPROVEMENT: +{avg_improvement:.1%}")
            print("   Improved patterns are working on real articles!")
            print("\n   Next step: Reprocess all articles with improved code")
        elif avg_improvement > 0:
            print(f"\n🟡 SMALL IMPROVEMENT: +{avg_improvement:.1%}")
            print("   Some improvement, but may need more patterns")
        else:
            print(f"\n⚠️  NO IMPROVEMENT: {avg_improvement:+.1%}")
            print("   These articles may lack extractable event information")

if __name__ == '__main__':
    main()
