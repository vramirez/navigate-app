from django.contrib import admin
from .models import (
    EventType,
    EventSubtype,
    ExtractionPattern,
    SportType,
    CompetitionLevel,
    HypeIndicator,
    BroadcastabilityConfig,
    CuisineType
)


class ExtractionPatternInline(admin.TabularInline):
    """Inline for managing extraction patterns within EventType or EventSubtype"""
    model = ExtractionPattern
    extra = 1
    fields = ['pattern', 'description', 'weight', 'is_active']
    verbose_name = 'Extraction Pattern'
    verbose_name_plural = 'Extraction Patterns'


class EventSubtypeInline(admin.TabularInline):
    """Inline for managing subtypes within EventType"""
    model = EventSubtype
    extra = 0
    fields = ['code', 'name_es', 'name_en', 'is_active', 'display_order']
    show_change_link = True
    verbose_name = 'Event Subtype'
    verbose_name_plural = 'Event Subtypes'


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_es', 'name_en', 'relevance_category', 'is_active', 'display_order', 'pattern_count', 'subtype_count']
    list_filter = ['relevance_category', 'is_active']
    search_fields = ['code', 'name_es', 'name_en', 'description']
    ordering = ['display_order', 'name_es']
    inlines = [EventSubtypeInline, ExtractionPatternInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (('code', 'is_active'), ('name_es', 'name_en'), 'description')
        }),
        ('Classification', {
            'fields': (('relevance_category', 'icon'), 'display_order')
        }),
    )
    
    def pattern_count(self, obj):
        """Count of extraction patterns for this type"""
        return obj.patterns.count()
    pattern_count.short_description = 'Patterns'
    
    def subtype_count(self, obj):
        """Count of subtypes for this type"""
        return obj.subtypes.count()
    subtype_count.short_description = 'Subtypes'


@admin.register(EventSubtype)
class EventSubtypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'event_type', 'name_es', 'name_en', 'is_active', 'display_order', 'pattern_count']
    list_filter = ['event_type', 'is_active']
    search_fields = ['code', 'name_es', 'name_en', 'description']
    ordering = ['event_type', 'display_order', 'name_es']
    inlines = [ExtractionPatternInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (('event_type', 'code'), ('name_es', 'name_en'), 'description')
        }),
        ('Display', {
            'fields': (('is_active', 'display_order'),)
        }),
    )
    
    def pattern_count(self, obj):
        """Count of extraction patterns for this subtype"""
        return obj.patterns.count()
    pattern_count.short_description = 'Patterns'


@admin.register(ExtractionPattern)
class ExtractionPatternAdmin(admin.ModelAdmin):
    list_display = ['id', 'target', 'event_type', 'event_subtype', 'pattern_preview', 'weight', 'is_active']
    list_filter = ['target', 'is_active', 'event_type']
    search_fields = ['pattern', 'description']
    ordering = ['event_type', 'event_subtype', '-weight']
    
    fieldsets = (
        ('Target', {
            'fields': (('target', 'is_active'), ('event_type', 'event_subtype'))
        }),
        ('Pattern', {
            'fields': (('pattern', 'weight'), 'description')
        }),
    )
    
    def pattern_preview(self, obj):
        """Show first 50 chars of pattern"""
        return obj.pattern[:50] + '...' if len(obj.pattern) > 50 else obj.pattern
    pattern_preview.short_description = 'Pattern'
    
    def save_model(self, request, obj, form, change):
        """Validate before saving"""
        obj.clean()
        super().save_model(request, obj, form, change)


# Broadcastability Models Admin (task-9.7)

class CompetitionLevelInline(admin.TabularInline):
    """Inline for managing competition levels within SportType"""
    model = CompetitionLevel
    extra = 0
    fields = ['code', 'name_es', 'broadcast_multiplier', 'typical_attendance_min', 'is_active']
    show_change_link = True


@admin.register(SportType)
class SportTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_es', 'latin_america_appeal', 'is_active', 'display_order', 'competition_count']
    list_filter = ['is_active']
    search_fields = ['code', 'name_es', 'name_en', 'description']
    ordering = ['-latin_america_appeal', 'display_order']
    inlines = [CompetitionLevelInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (('code', 'is_active'), ('name_es', 'name_en'), 'description')
        }),
        ('Broadcastability', {
            'fields': (('latin_america_appeal', 'display_order'), 'keywords')
        }),
    )

    def competition_count(self, obj):
        """Count of competition levels for this sport"""
        return obj.competition_levels.count()
    competition_count.short_description = 'Competitions'


@admin.register(CompetitionLevel)
class CompetitionLevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'sport_type', 'name_es', 'broadcast_multiplier', 'typical_attendance_min', 'is_active', 'display_order']
    list_filter = ['sport_type', 'is_active']
    search_fields = ['code', 'name_es', 'name_en', 'description']
    ordering = ['-broadcast_multiplier', 'sport_type', 'display_order']

    fieldsets = (
        ('Basic Information', {
            'fields': (('sport_type', 'code'), ('name_es', 'name_en'), 'description')
        }),
        ('Broadcastability Parameters', {
            'fields': (('broadcast_multiplier', 'typical_attendance_min'), 'keywords')
        }),
        ('Display', {
            'fields': (('is_active', 'display_order'),)
        }),
    )


@admin.register(HypeIndicator)
class HypeIndicatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'pattern_preview', 'hype_boost', 'language', 'is_active']
    list_filter = ['category', 'language', 'is_active']
    search_fields = ['pattern', 'description']
    ordering = ['-hype_boost', 'category']

    fieldsets = (
        ('Pattern', {
            'fields': (('category', 'language', 'is_active'), 'pattern', 'description')
        }),
        ('Impact', {
            'fields': ('hype_boost',)
        }),
    )

    def pattern_preview(self, obj):
        """Show first 40 chars of pattern"""
        return obj.pattern[:40] + '...' if len(obj.pattern) > 40 else obj.pattern
    pattern_preview.short_description = 'Pattern'


@admin.register(BroadcastabilityConfig)
class BroadcastabilityConfigAdmin(admin.ModelAdmin):
    """Admin for singleton BroadcastabilityConfig"""

    def has_add_permission(self, request):
        """Only allow one instance"""
        return not BroadcastabilityConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of singleton"""
        return False

    fieldsets = (
        ('Component Weights (must sum to 1.0)', {
            'fields': (
                ('sport_appeal_weight', 'competition_level_weight'),
                ('hype_indicators_weight', 'attendance_weight')
            )
        }),
        ('Thresholds', {
            'fields': ('min_broadcastability_score',)
        }),
        ('Attendance Scaling', {
            'fields': (
                ('attendance_small', 'attendance_medium', 'attendance_large'),
            )
        }),
        ('Business Requirements', {
            'fields': ('requires_tv_screens',)
        }),
    )

    list_display = ['id', 'min_broadcastability_score', 'sport_appeal_weight', 'competition_level_weight', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Validate weights sum to 1.0"""
        obj.clean()
        super().save_model(request, obj, form, change)


# Gastronomy Models Admin (task-9.8)

@admin.register(CuisineType)
class CuisineTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_es', 'name_en', 'is_active', 'display_order']
    list_filter = ['is_active']
    search_fields = ['code', 'name_es', 'name_en', 'description']
    ordering = ['display_order', 'name_es']

    fieldsets = (
        ('Basic Information', {
            'fields': (('code', 'is_active'), ('name_es', 'name_en'), 'description')
        }),
        ('Detection', {
            'fields': (('display_order',), 'keywords')
        }),
    )
