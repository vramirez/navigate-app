#!/usr/bin/env python
"""
Test script for NewsArticleSerializer (task-18.7)
Tests user_relevance and type_scores fields
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from news.models import NewsArticle, ArticleBusinessTypeRelevance
from businesses.models import Business, BusinessType


def test_news_article_serializer():
    """Test NewsArticleSerializer with per-type relevance fields"""

    print("=" * 60)
    print("Testing NewsArticleSerializer (task-18.7)")
    print("=" * 60)

    # Setup
    client = APIClient()

    # Get a user with a business
    business = Business.objects.select_related('owner', 'business_type').first()
    if not business:
        print("\n⚠ No business found - creating test data skipped")
        return

    user = business.owner
    business_type = business.business_type

    print(f"\nTest user: {user.username}")
    print(f"Business: {business.name}")
    print(f"Business type: {business_type.code}")

    # Authenticate
    client.force_authenticate(user=user)

    # Test 1: Get articles without include_type_scores
    print("\n1. Testing GET /api/news/articles/ (without include_type_scores)")
    response = client.get('/api/news/articles/')
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        response_data = response.json()
        if 'results' in response_data:
            articles = response_data['results']
        else:
            articles = response_data

        print(f"   Articles found: {len(articles)}")

        if len(articles) > 0:
            article = articles[0]
            print(f"\n   First article: {article['title'][:50]}...")

            # Check user_relevance field
            if 'user_relevance' in article:
                print(f"   ✓ user_relevance present: {article['user_relevance']}")
            else:
                print("   ⚠ user_relevance missing")

            # Check type_scores is NOT present (not requested)
            if 'type_scores' not in article or article['type_scores'] is None:
                print("   ✓ type_scores correctly excluded (not requested)")
            else:
                print(f"   ⚠ type_scores present when not requested: {article['type_scores']}")

    # Test 2: Get articles WITH include_type_scores
    print("\n2. Testing GET /api/news/articles/?include_type_scores=true")
    response = client.get('/api/news/articles/?include_type_scores=true')
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        response_data = response.json()
        if 'results' in response_data:
            articles = response_data['results']
        else:
            articles = response_data

        print(f"   Articles found: {len(articles)}")

        if len(articles) > 0:
            article = articles[0]
            print(f"\n   First article: {article['title'][:50]}...")

            # Check user_relevance
            if 'user_relevance' in article:
                print(f"   ✓ user_relevance: {article['user_relevance']}")

            # Check type_scores IS present
            if 'type_scores' in article and article['type_scores']:
                print(f"   ✓ type_scores present")
                type_scores = article['type_scores']
                print(f"   Business types with scores: {list(type_scores.keys())}")

                # Check structure of first type score
                if type_scores:
                    first_type = list(type_scores.keys())[0]
                    first_score = type_scores[first_type]
                    print(f"\n   Sample type score ({first_type}):")
                    print(f"     - relevance_score: {first_score.get('relevance_score')}")
                    print(f"     - suitability: {first_score.get('suitability')}")
                    print(f"     - keyword: {first_score.get('keyword')}")
                    print(f"     - event_scale: {first_score.get('event_scale')}")
                    print(f"     - neighborhood: {first_score.get('neighborhood')}")
                    print(f"     - matching_keywords: {first_score.get('matching_keywords', [])}")

                    # Verify structure
                    required_keys = ['relevance_score', 'suitability', 'keyword', 'event_scale', 'neighborhood', 'matching_keywords']
                    if all(k in first_score for k in required_keys):
                        print("   ✓ All required fields present in type_scores")
                    else:
                        missing = [k for k in required_keys if k not in first_score]
                        print(f"   ⚠ Missing fields: {missing}")
            else:
                print("   ⚠ type_scores missing when requested")

    # Test 3: Get specific article with business_type filter
    print("\n3. Testing GET /api/news/articles/?business_type={code}")
    response = client.get(f'/api/news/articles/?business_type={business_type.code}')
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        response_data = response.json()
        if 'results' in response_data:
            articles = response_data['results']
            count = response_data.get('count', len(articles))
        else:
            articles = response_data
            count = len(articles)

        print(f"   Filtered articles for {business_type.code}: {count}")

        if len(articles) > 0:
            article = articles[0]
            if 'user_relevance' in article and article['user_relevance']:
                print(f"   ✓ user_relevance for {business_type.code}: {article['user_relevance']}")
            else:
                print(f"   ⚠ user_relevance missing or null")

    # Test 4: Verify database has ArticleBusinessTypeRelevance records
    print("\n4. Checking database ArticleBusinessTypeRelevance records")
    total_records = ArticleBusinessTypeRelevance.objects.count()
    print(f"   Total ArticleBusinessTypeRelevance records: {total_records}")

    if total_records > 0:
        # Get a sample
        sample = ArticleBusinessTypeRelevance.objects.select_related('article', 'business_type').first()
        print(f"   Sample record:")
        print(f"     Article: {sample.article.title[:40]}...")
        print(f"     Type: {sample.business_type.code}")
        print(f"     Score: {sample.relevance_score}")
        print(f"     Components: suitability={sample.suitability_component}, keyword={sample.keyword_component}")

    print("\n" + "=" * 60)
    print("✓ NewsArticleSerializer tests complete!")
    print("=" * 60)


if __name__ == '__main__':
    test_news_article_serializer()
