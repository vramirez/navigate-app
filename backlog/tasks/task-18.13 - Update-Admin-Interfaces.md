---
id: task-18.13
title: 'Update Admin Interfaces for Business Types'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - backend
  - admin
dependencies: []
parent: task-18
priority: medium
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update Django admin interfaces to support new BusinessType and ArticleBusinessTypeRelevance models. Add inline editing for BusinessTypeKeyword. Improve article admin to show type scores. Make it easy to manage business type configuration without code changes.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `backend/businesses/admin.py`

### Add BusinessType Admin

```python
from django.contrib import admin
from django.db.models import Count
from .models import (
    Business, BusinessKeywords, AdminUser,
    BusinessType, BusinessTypeKeyword
)


class BusinessTypeKeywordInline(admin.TabularInline):
    """Inline editor for business type keywords"""
    model = BusinessTypeKeyword
    extra = 3
    fields = ('keyword', 'weight', 'category', 'is_active')
    ordering = ('category', 'keyword')


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    """Admin interface for BusinessType"""

    list_display = [
        'code', 'display_name', 'display_name_es', 'icon',
        'min_relevance_threshold', 'min_suitability_threshold',
        'business_count', 'keyword_count', 'is_active'
    ]

    list_filter = ['is_active', 'created_at']

    search_fields = ['code', 'display_name', 'display_name_es', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'display_name', 'display_name_es', 'description', 'icon')
        }),
        ('Relevance Calculation Weights', {
            'fields': (
                'suitability_weight', 'keyword_weight',
                'event_scale_weight', 'neighborhood_weight'
            ),
            'description': 'Weights for calculating relevance score (should sum to ~1.0)'
        }),
        ('Thresholds', {
            'fields': ('min_relevance_threshold', 'min_suitability_threshold'),
            'description': 'Minimum scores required for articles to be shown'
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )

    inlines = [BusinessTypeKeywordInline]

    readonly_fields = []

    def get_queryset(self, request):
        """Annotate with counts"""
        qs = super().get_queryset(request)
        return qs.annotate(
            _business_count=Count('businesses', distinct=True),
            _keyword_count=Count('keywords', distinct=True)
        )

    def business_count(self, obj):
        """Number of businesses of this type"""
        return obj._business_count
    business_count.short_description = 'Businesses'
    business_count.admin_order_field = '_business_count'

    def keyword_count(self, obj):
        """Number of keywords for this type"""
        return obj._keyword_count
    keyword_count.short_description = 'Keywords'
    keyword_count.admin_order_field = '_keyword_count'


@admin.register(BusinessTypeKeyword)
class BusinessTypeKeywordAdmin(admin.ModelAdmin):
    """Admin interface for BusinessTypeKeyword"""

    list_display = [
        'keyword', 'business_type', 'weight', 'category', 'is_active'
    ]

    list_filter = ['business_type', 'category', 'is_active']

    search_fields = ['keyword', 'category']

    list_editable = ['weight', 'is_active']

    ordering = ['business_type', 'category', 'keyword']


# Update existing Business admin
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Admin interface for Business"""

    list_display = [
        'name', 'business_type', 'city', 'neighborhood',
        'owner', 'is_active', 'created_at'
    ]

    list_filter = ['business_type', 'city', 'is_active', 'created_at']

    search_fields = ['name', 'description', 'neighborhood']

    raw_id_fields = ['owner']

    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'business_type', 'description')
        }),
        ('Location', {
            'fields': (
                'city', 'address', 'neighborhood',
                'latitude', 'longitude',
                'geographic_radius_km'
            )
        }),
        ('Geographic Preferences', {
            'fields': (
                'include_citywide_events',
                'include_national_events',
                'has_tv_screens'
            )
        }),
        ('Business Details', {
            'fields': (
                'target_audience', 'capacity', 'staff_count',
                'operating_hours_start', 'operating_hours_end'
            )
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'recommendation_frequency')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
```

**File**: `backend/news/admin.py`

### Update NewsArticle Admin

```python
from django.contrib import admin
from django.db.models import Count, Avg
from django.utils.html import format_html
from .models import (
    NewsSource, NewsArticle, CrawlHistory,
    ArticleBusinessTypeRelevance
)


class ArticleBusinessTypeRelevanceInline(admin.TabularInline):
    """Inline viewer for article type relevance scores"""
    model = ArticleBusinessTypeRelevance
    extra = 0
    can_delete = False
    readonly_fields = [
        'business_type', 'relevance_score',
        'suitability_component', 'keyword_component',
        'event_scale_component', 'neighborhood_component',
        'matching_keywords'
    ]
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """Admin interface for NewsArticle"""

    list_display = [
        'short_title', 'news_source', 'published_date',
        'suitability_score_badge', 'type_scores_badge',
        'is_event', 'city', 'processing_status'
    ]

    list_filter = [
        'processing_status', 'is_event', 'city',
        'news_source', 'event_scale', 'published_date'
    ]

    search_fields = ['title', 'content', 'summary', 'neighborhood']

    readonly_fields = [
        'created_at', 'updated_at', 'processing_status',
        'business_suitability_score', 'error_message',
        'type_scores_summary'
    ]

    inlines = [ArticleBusinessTypeRelevanceInline]

    fieldsets = (
        ('Article Information', {
            'fields': ('news_source', 'title', 'url', 'image_url', 'published_date')
        }),
        ('Content', {
            'fields': ('summary', 'content')
        }),
        ('Event Information', {
            'fields': (
                'is_event', 'event_title', 'event_description',
                'event_start_datetime', 'event_end_datetime',
                'event_location', 'event_scale'
            )
        }),
        ('Geographic Information', {
            'fields': ('city', 'neighborhood', 'latitude', 'longitude')
        }),
        ('ML Scores', {
            'fields': (
                'business_suitability_score',
                'type_scores_summary'
            ),
            'description': 'Calculated by ML pipeline'
        }),
        ('Processing', {
            'fields': ('processing_status', 'error_message', 'created_at', 'updated_at')
        })
    )

    def get_queryset(self, request):
        """Annotate with type score stats"""
        qs = super().get_queryset(request)
        return qs.annotate(
            _type_score_count=Count('type_relevance_scores', distinct=True),
            _avg_type_score=Avg('type_relevance_scores__relevance_score')
        )

    def short_title(self, obj):
        """Truncated title"""
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    short_title.short_description = 'Title'

    def suitability_score_badge(self, obj):
        """Color-coded suitability score badge"""
        score = obj.business_suitability_score

        if score < 0:
            color = 'gray'
            text = 'Not processed'
        elif score < 0.3:
            color = 'red'
            text = f'{score:.2f}'
        elif score < 0.5:
            color = 'orange'
            text = f'{score:.2f}'
        elif score < 0.7:
            color = 'yellow'
            text = f'{score:.2f}'
        else:
            color = 'green'
            text = f'{score:.2f}'

        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, text
        )
    suitability_score_badge.short_description = 'Suitability'

    def type_scores_badge(self, obj):
        """Badge showing number of type scores and average"""
        count = obj._type_score_count
        avg = obj._avg_type_score or 0

        if count == 0:
            return format_html(
                '<span style="background: gray; color: white; padding: 3px 8px; border-radius: 3px;">No scores</span>'
            )

        if avg < 0.5:
            color = 'orange'
        elif avg < 0.7:
            color = 'yellow'
        else:
            color = 'green'

        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} types (avg: {:.2f})</span>',
            color, count, avg
        )
    type_scores_badge.short_description = 'Type Scores'

    def type_scores_summary(self, obj):
        """Summary of all type scores"""
        scores = obj.type_relevance_scores.select_related('business_type').all()

        if not scores:
            return 'No type scores calculated yet'

        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr><th>Type</th><th>Score</th><th>Keywords</th></tr>'

        for score in scores:
            html += f'<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td><strong>{score.business_type.display_name}</strong></td>'
            html += f'<td>{score.relevance_score:.2f}</td>'
            html += f'<td>{", ".join(score.matching_keywords[:5])}</td>'
            html += '</tr>'

        html += '</table>'
        return format_html(html)
    type_scores_summary.short_description = 'Type Scores Summary'


@admin.register(ArticleBusinessTypeRelevance)
class ArticleBusinessTypeRelevanceAdmin(admin.ModelAdmin):
    """Admin interface for ArticleBusinessTypeRelevance"""

    list_display = [
        'article_title', 'business_type', 'relevance_score',
        'keyword_component', 'event_scale_component', 'created_at'
    ]

    list_filter = ['business_type', 'created_at']

    search_fields = ['article__title']

    readonly_fields = [
        'article', 'business_type', 'relevance_score',
        'suitability_component', 'keyword_component',
        'event_scale_component', 'neighborhood_component',
        'matching_keywords', 'created_at'
    ]

    def article_title(self, obj):
        """Article title"""
        return obj.article.title[:60] + '...' if len(obj.article.title) > 60 else obj.article.title
    article_title.short_description = 'Article'

    def has_add_permission(self, request):
        """Prevent manual creation (auto-generated by ML)"""
        return False
```

## Testing

### Test 1: Access Admin Interfaces

1. Navigate to http://localhost:8000/admin/
2. Verify sections:
   - Businesses > Business Types
   - Businesses > Business Type Keywords
   - News > Article Business Type Relevance

### Test 2: Edit Business Type

1. Go to Business Types list
2. Click on "Pub/Bar"
3. Verify:
   - All fields editable
   - Keywords inline editor works
   - Weight validation (sum should be ~1.0)
4. Add a new keyword: "happy hour", weight 0.15, category "social"
5. Save and verify keyword appears

### Test 3: View Article Type Scores

1. Go to News > Articles
2. Click on any article
3. Verify:
   - Type scores inline shows all types
   - Summary section displays nicely
   - Scores color-coded in list view

### Test 4: Bulk Edit Keywords

1. Go to Business Type Keywords
2. Filter by business type "pub"
3. Use inline editing to change weights
4. Save and verify changes

## Acceptance Criteria

- [ ] BusinessType admin registered and accessible
- [ ] BusinessType list shows counts (businesses, keywords)
- [ ] BusinessType form has organized fieldsets
- [ ] BusinessTypeKeyword inline editing works
- [ ] BusinessTypeKeyword admin allows bulk editing
- [ ] Business admin updated with business_type FK
- [ ] NewsArticle admin shows type scores inline
- [ ] NewsArticle list has suitability_score_badge
- [ ] NewsArticle list has type_scores_badge
- [ ] ArticleBusinessTypeRelevance admin read-only (auto-generated)
- [ ] All admins have appropriate filters
- [ ] Search fields work correctly

## Notes

- Make configuration changes easy for non-technical users
- Color-coded badges improve readability
- Inline editors reduce clicks
- Read-only fields prevent accidental modifications of ML-generated data
- Future: Add actions for bulk reprocessing articles
