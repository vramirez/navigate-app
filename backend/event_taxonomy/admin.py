from django.contrib import admin
from .models import EventType, EventSubtype, ExtractionPattern


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
