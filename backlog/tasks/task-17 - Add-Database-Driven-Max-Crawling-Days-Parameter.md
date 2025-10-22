---
id: task-17
title: Add database-driven max crawling days parameter with web dashboard management
status: Backlog
assignee: []
reporter: '@victor'
created_date: '2025-10-22'
labels:
  - backend
  - frontend
  - crawler
  - configuration
priority: medium
dependencies: []
parent: task-8
milestone: Phase 2 - Crawler Enhancements
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add configurable max crawling days parameter stored in database, allowing runtime configuration through web dashboard. This prevents excessive retrieval of old articles and allows per-source customization with global defaults.
<!-- SECTION:DESCRIPTION:END -->

## Business Value

- **Efficiency**: Avoid crawling months/years of old articles unnecessarily
- **Resource Management**: Reduce processing time and storage for irrelevant old content
- **Flexibility**: Different sources may need different time windows (news vs evergreen content)
- **User Control**: Configurable through web UI without code deployment

## Current Behavior

- Crawler retrieves all available articles from RSS feeds without date limits
- No mechanism to stop based on article age
- Can result in processing hundreds of old, irrelevant articles

## Desired Behavior

- System-level default: 30 days (stored in database)
- Source-level override: Optional per-source configuration
- Crawling stops when:
  - No more articles available, OR
  - Article published_date exceeds max_crawling_days threshold
- Configurable through web dashboard

## Implementation Plan

### 1. Database Schema Changes

**A. Create SystemSetting Model**

```python
# backend/core/models.py (or new settings app)

class SystemSetting(models.Model):
    """System-wide configuration settings stored in database"""

    key = models.CharField(
        max_length=100,
        unique=True,
        help_text='Setting key (e.g., MAX_CRAWLING_DAYS_DEFAULT)'
    )
    value = models.JSONField(
        help_text='Setting value (supports int, str, bool, list, dict)'
    )
    description = models.TextField(
        blank=True,
        help_text='Human-readable description of this setting'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get_value(cls, key, default=None):
        """Get setting value with fallback"""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value, description='', user='system'):
        """Set or update setting value"""
        obj, created = cls.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'description': description,
                'updated_by': user
            }
        )
        return obj
```

**B. Add max_crawling_days to NewsSource**

```python
# backend/news/models.py

class NewsSource(models.Model):
    # ... existing fields ...

    max_crawling_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Max Crawling Days',
        help_text='How far back to retrieve articles. Leave empty to use system default (30 days).'
    )
```

**C. Migrations**

```bash
# Create SystemSetting model
python manage.py makemigrations core --name create_system_setting

# Add max_crawling_days to NewsSource
python manage.py makemigrations news --name add_max_crawling_days

# Apply migrations
python manage.py migrate

# Seed default value
python manage.py shell
>>> from core.models import SystemSetting
>>> SystemSetting.set_value('MAX_CRAWLING_DAYS_DEFAULT', 30,
...     'Default number of days to look back when crawling news sources')
```

### 2. Backend API Updates

**A. System Settings API**

```python
# backend/core/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

class SystemSettingViewSet(viewsets.ModelViewSet):
    """API for managing system settings"""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAdminUser]  # Admin only
```

**B. Update NewsSource Serializer**

```python
# backend/news/serializers.py

class NewsSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSource
        fields = [
            # ... existing fields ...
            'max_crawling_days',
        ]
```

### 3. Crawler Logic Updates

**A. Helper Function**

```python
# backend/news/utils.py

from datetime import timedelta
from django.utils import timezone
from core.models import SystemSetting

def get_max_crawling_days(source):
    """
    Get max crawling days for a source

    Resolution order:
    1. source.max_crawling_days (if set)
    2. SystemSetting MAX_CRAWLING_DAYS_DEFAULT
    3. Hard-coded fallback: 30
    """
    if source.max_crawling_days is not None:
        return source.max_crawling_days

    system_default = SystemSetting.get_value('MAX_CRAWLING_DAYS_DEFAULT', 30)
    return system_default

def is_article_too_old(article_date, source):
    """Check if article exceeds max crawling days threshold"""
    max_days = get_max_crawling_days(source)
    threshold = timezone.now() - timedelta(days=max_days)
    return article_date < threshold
```

**B. Update RSS Crawler**

```python
# backend/news/services/rss_crawler.py

def crawl_rss_feed(source, feed_url):
    # ... existing code ...

    for entry in feed.entries:
        # Parse published date
        published_date = parse_rss_date(entry.published)

        # Check if article is too old
        if is_article_too_old(published_date, source):
            logger.info(f"Stopping crawl for {source.name}: article from {published_date} exceeds max_crawling_days")
            break  # Stop processing older articles

        # ... continue processing ...
```

**C. Update Manual Crawler**

```python
# backend/news/services/manual_crawler.py

def crawl_manual_article(source, url):
    # ... existing code ...

    # After extracting article
    if article.published_date and is_article_too_old(article.published_date, source):
        logger.warning(f"Article from {article.published_date} exceeds max_crawling_days for {source.name}")
        return None  # Skip this article

    # ... continue processing ...
```

### 4. Web Dashboard UI

**A. System Settings Page (Admin Only)**

```jsx
// frontend/src/pages/admin/SystemSettings.jsx

import React from 'react';
import { useQuery, useMutation } from 'react-query';
import { getSystemSettings, updateSystemSetting } from '@/services/settingsApi';

export default function SystemSettings() {
  const { data: settings } = useQuery('systemSettings', getSystemSettings);

  const updateMutation = useMutation(updateSystemSetting, {
    onSuccess: () => {
      // Refetch settings
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">System Settings</h1>

      <div className="space-y-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium mb-2">
            Max Crawling Days (Default)
          </label>
          <input
            type="number"
            min="1"
            max="365"
            value={settings?.MAX_CRAWLING_DAYS_DEFAULT}
            onChange={(e) => updateMutation.mutate({
              key: 'MAX_CRAWLING_DAYS_DEFAULT',
              value: parseInt(e.target.value)
            })}
            className="border rounded px-3 py-2"
          />
          <p className="text-sm text-gray-600 mt-1">
            Default number of days to look back when crawling news sources
          </p>
        </div>
      </div>
    </div>
  );
}
```

**B. Update NewsSource Form**

```jsx
// frontend/src/components/NewsSourceForm.jsx

<div className="mb-4">
  <label className="block text-sm font-medium mb-2">
    Max Crawling Days
  </label>
  <input
    type="number"
    name="max_crawling_days"
    min="1"
    max="365"
    value={formData.max_crawling_days || ''}
    onChange={handleChange}
    placeholder="Leave empty for system default"
    className="border rounded px-3 py-2 w-full"
  />
  <p className="text-sm text-gray-600 mt-1">
    How far back to retrieve articles. Leave empty to use system default (currently 30 days).
  </p>
</div>
```

### 5. Django Admin Updates

```python
# backend/core/admin.py

from django.contrib import admin
from .models import SystemSetting

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description', 'updated_at', 'updated_by')
    search_fields = ('key', 'description')
    readonly_fields = ('updated_at',)

# backend/news/admin.py

class NewsSourceAdmin(admin.ModelAdmin):
    fieldsets = [
        # ... existing fieldsets ...
        ('Crawling Configuration', {
            'fields': ('max_crawling_days',)
        })
    ]
```

## Acceptance Criteria

- [ ] SystemSetting model created with migration
- [ ] max_crawling_days field added to NewsSource model
- [ ] Default value of 30 days seeded in database
- [ ] System settings API endpoint (admin only)
- [ ] Web dashboard page for system settings
- [ ] NewsSource form includes max_crawling_days field
- [ ] Crawler respects max_crawling_days parameter
- [ ] Crawling stops when article exceeds threshold
- [ ] Fallback logic works: source → system default → hard-coded 30
- [ ] Django admin shows both tables
- [ ] Documentation updated in README
- [ ] Logging when crawl stops due to date threshold

## Testing Plan

1. **Unit Tests**:
   - Test `get_max_crawling_days()` with various scenarios
   - Test `is_article_too_old()` with different dates
   - Test fallback logic (source → system → default)

2. **Integration Tests**:
   - Create source with custom max_crawling_days=7
   - Crawl RSS feed with mix of old/new articles
   - Verify only articles from last 7 days processed
   - Test with source.max_crawling_days=None (uses system default)

3. **Manual Tests**:
   - Set system default to 15 days via web UI
   - Create source without custom value → verify uses 15
   - Create source with custom value 60 → verify uses 60
   - Monitor crawler logs for "exceeds max_crawling_days" messages

## Technical Notes

- Use database storage for runtime configuration flexibility
- SystemSetting table can be extended for other config needs
- Consider adding validation: max_crawling_days must be positive
- RSS feeds are ordered newest-first, so breaking early is safe
- Manual crawling may process articles individually, check before processing

## Related Tasks

- Depends on: task-8 (Phase 2: Advanced News Crawler System)
- Related: Future task for automated crawl scheduling

## Future Enhancements

- Add audit log for system setting changes
- UI indicator showing how many articles were skipped due to age
- Per-source crawl frequency configuration
- Email alerts when crawl hits date threshold repeatedly
