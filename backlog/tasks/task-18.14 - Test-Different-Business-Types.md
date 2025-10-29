---
id: task-18.14
title: 'Test System with Different Business Types'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - testing
  - qa
dependencies: [task-18.10, task-18.12]
parent: task-18
priority: high
estimated_hours: 3
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
End-to-end testing of the per-business-type relevance system. Create test users for each business type, verify they see different articles, validate relevance scores are appropriate, and ensure filtering works correctly. Documents expected behavior for future regression testing.
<!-- SECTION:DESCRIPTION:END -->

## Test Setup

### Create Test Accounts

**Script**: `test/create_test_users.py`

```python
#!/usr/bin/env python
"""
Create test users for each business type
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from django.contrib.auth.models import User
from businesses.models import Business, BusinessType


def create_test_user(username, business_name, business_type_code):
    """Create user with business of specified type"""

    # Create or get user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@test.com',
            'first_name': username.capitalize(),
            'last_name': 'Test'
        }
    )

    if created:
        user.set_password('test123')
        user.save()
        print(f'Created user: {username}')
    else:
        print(f'User exists: {username}')

    # Get business type
    business_type = BusinessType.objects.get(code=business_type_code)

    # Create or update business
    business, created = Business.objects.update_or_create(
        owner=user,
        defaults={
            'name': business_name,
            'business_type': business_type,
            'city': 'medellin',
            'neighborhood': 'El Poblado',
            'is_active': True
        }
    )

    if created:
        print(f'  Created business: {business_name} ({business_type_code})')
    else:
        print(f'  Updated business: {business_name} ({business_type_code})')

    return user, business


def main():
    print('Creating test users...\n')

    test_accounts = [
        ('pubowner', 'Test Pub El Poblado', 'pub'),
        ('restaurantowner', 'Test Restaurant Gourmet', 'restaurant'),
        ('coffeeowner', 'Test Coffee Shop Artisan', 'coffee_shop'),
        ('bookowner', 'Test Bookstore Literary', 'bookstore'),
    ]

    for username, business_name, business_type_code in test_accounts:
        create_test_user(username, business_name, business_type_code)
        print()

    print('=' * 60)
    print('Test accounts created!')
    print('\nLogin credentials:')
    for username, _, _ in test_accounts:
        print(f'  Username: {username}, Password: test123')


if __name__ == '__main__':
    main()
```

Run:
```bash
docker exec docker-backend-1 python test/create_test_users.py
```

## Test Cases

### Test 1: Login and Profile Verification

**For each test user:**

1. Login via frontend: http://localhost:3001/login
   - Username: `pubowner` / Password: `test123`
   - Username: `restaurantowner` / Password: `test123`
   - Username: `coffeeowner` / Password: `test123`
   - Username: `bookowner` / Password: `test123`

2. Verify dashboard header shows:
   - Correct business name
   - Correct business type icon
   - Correct business type display name

3. Open browser console and check:
```javascript
// Should show current user's business type
const auth = window.__authContext;
console.log('Business Type:', auth.businessTypeCode);
console.log('Business:', auth.business);
```

**Expected Results:**
- Each user sees their own business info
- businessTypeCode matches their business type

---

### Test 2: Article Filtering by Business Type

**Test Script**: `test/test_article_filtering.py`

```python
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from businesses.models import BusinessType


def test_user_articles(username):
    """Test article filtering for a user"""
    user = User.objects.get(username=username)
    business = user.businesses.first()
    business_type = business.business_type

    client = APIClient()
    client.force_authenticate(user=user)

    # Fetch articles
    response = client.get(f'/api/news/articles/?business_type={business_type.code}')
    articles = response.json()

    print(f'\n{username} ({business_type.code}):')
    print(f'  Articles: {len(articles)}')

    if articles:
        print(f'  Top 3 by relevance:')
        for article in articles[:3]:
            print(f'    - [{article["user_relevance"]:.2f}] {article["title"][:50]}...')

    return len(articles)


def main():
    print('Testing article filtering by business type...')

    test_users = ['pubowner', 'restaurantowner', 'coffeeowner', 'bookowner']
    results = {}

    for username in test_users:
        count = test_user_articles(username)
        results[username] = count

    print('\n' + '=' * 60)
    print('Summary:')
    for username, count in results.items():
        print(f'  {username}: {count} articles')

    # Verify different results
    if len(set(results.values())) > 1:
        print('\n✓ Different business types see different articles')
    else:
        print('\n✗ WARNING: All business types see same articles')


if __name__ == '__main__':
    main()
```

Run:
```bash
docker exec docker-backend-1 python test/test_article_filtering.py
```

**Expected Results:**
- Different business types see different article counts
- Relevance scores vary by business type
- Articles relevant to each type appear first

---

### Test 3: Relevance Score Validation

**Test Script**: `test/test_relevance_scores.py`

```python
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import NewsArticle, ArticleBusinessTypeRelevance
from businesses.models import BusinessType


def test_article_scores():
    """Test that articles have appropriate scores per type"""

    # Get a sample article
    article = NewsArticle.objects.filter(
        type_relevance_scores__isnull=False
    ).first()

    print(f'Article: {article.title}\n')

    # Get scores for each type
    for bt in BusinessType.objects.filter(is_active=True):
        try:
            score = ArticleBusinessTypeRelevance.objects.get(
                article=article,
                business_type=bt
            )

            print(f'{bt.code}:')
            print(f'  Relevance: {score.relevance_score:.2f}')
            print(f'  Components:')
            print(f'    Suitability: {score.suitability_component:.2f}')
            print(f'    Keyword: {score.keyword_component:.2f}')
            print(f'    Event Scale: {score.event_scale_component:.2f}')
            print(f'  Keywords: {", ".join(score.matching_keywords[:5])}')
            print()

        except ArticleBusinessTypeRelevance.DoesNotExist:
            print(f'{bt.code}: No score (below threshold)\n')


def test_score_distribution():
    """Test overall score distribution"""

    print('\n' + '=' * 60)
    print('Score Distribution by Business Type:\n')

    for bt in BusinessType.objects.filter(is_active=True):
        scores = ArticleBusinessTypeRelevance.objects.filter(
            business_type=bt
        ).values_list('relevance_score', flat=True)

        if scores:
            avg = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)

            print(f'{bt.code}:')
            print(f'  Articles: {len(scores)}')
            print(f'  Avg: {avg:.2f}')
            print(f'  Range: {min_score:.2f} - {max_score:.2f}')
            print()


if __name__ == '__main__':
    test_article_scores()
    test_score_distribution()
```

Run:
```bash
docker exec docker-backend-1 python test/test_relevance_scores.py
```

**Expected Results:**
- Same article has different scores for different types
- Scores reflect keyword matches (higher keyword match = higher score)
- Component breakdown shows where score comes from
- Distribution shows variety (not all 0.0 or all 1.0)

---

### Test 4: Frontend Filter Controls

**Manual Test:**

1. Login as `pubowner`
2. On dashboard:
   - Note number of articles displayed
   - Change "Minimum Relevance" to 0.7 (High)
   - Verify article count decreases
   - Verify remaining articles all have score >= 0.7
   - Change to 0.3 (Low)
   - Verify article count increases

3. Test event date filter:
   - Uncheck "Only show events from last 7 days or upcoming"
   - Verify older articles appear
   - Re-check filter
   - Verify only recent/upcoming events shown

**Expected Results:**
- Filter controls work instantly
- Article count updates correctly
- Scores match filter threshold
- Date filter respects 7-day window

---

### Test 5: Cross-Type Comparison

**Test Script**: `test/compare_business_types.py`

```python
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'navigate.settings')
django.setup()

from news.models import NewsArticle, ArticleBusinessTypeRelevance
from businesses.models import BusinessType


def find_distinctive_articles():
    """Find articles highly relevant to one type but not others"""

    print('Articles with distinctive relevance patterns:\n')

    # Get articles with scores
    articles = NewsArticle.objects.filter(
        type_relevance_scores__isnull=False
    ).distinct()[:20]

    for article in articles:
        scores = {}
        for bt in BusinessType.objects.filter(is_active=True):
            try:
                score_obj = ArticleBusinessTypeRelevance.objects.get(
                    article=article,
                    business_type=bt
                )
                scores[bt.code] = score_obj.relevance_score
            except ArticleBusinessTypeRelevance.DoesNotExist:
                scores[bt.code] = 0.0

        # Check if there's significant variation
        max_score = max(scores.values())
        min_score = min(scores.values())

        if max_score - min_score > 0.3:  # Significant difference
            print(f'{article.title[:60]}...')
            for code, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                print(f'  {code}: {score:.2f}')
            print()


if __name__ == '__main__':
    find_distinctive_articles()
```

Run:
```bash
docker exec docker-backend-1 python test/compare_business_types.py
```

**Expected Results:**
- Articles about beer/sports score high for pubs, low for bookstores
- Articles about books/authors score high for bookstores, low for pubs
- Articles about coffee score high for coffee shops
- System effectively differentiates relevance by type

---

## Acceptance Criteria

- [ ] Test users created for all 4 business types
- [ ] Each user can login and see their business type
- [ ] Different business types see different article counts
- [ ] Relevance scores vary appropriately by business type
- [ ] Filter controls work correctly
- [ ] Articles show user_relevance scores
- [ ] Event date filter respects 7-day window
- [ ] Score components sum to total relevance
- [ ] Keywords matched appropriately per type
- [ ] System shows meaningful differences between types
- [ ] No errors in console or logs
- [ ] Performance acceptable (page load < 2 seconds)

## Notes

- Keep test accounts for future regression testing
- Document any unexpected behavior for investigation
- Test scripts can be run regularly to verify system health
- Consider adding automated integration tests based on these
