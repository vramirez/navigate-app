from django.contrib import admin
from .models import NewsSource, NewsArticle, SocialMediaPost, ManualNewsEntry

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'source_type', 'city', 'is_active', 
        'reliability_score', 'last_fetched'
    ]
    list_filter = ['source_type', 'city', 'is_active', 'created_at']
    search_fields = ['name', 'website_url']
    readonly_fields = ['last_fetched', 'created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'source_type', 'city', 'website_url')
        }),
        ('Configuración de Datos', {
            'fields': ('rss_url', 'api_endpoint', 'scraping_enabled', 'css_selectors')
        }),
        ('Estado y Métricas', {
            'fields': (
                'is_active', 'reliability_score', 'fetch_frequency_hours',
                'last_fetched', 'created_at'
            )
        }),
    )

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'source', 'published_date', 'event_type', 
        'business_relevance_score', 'is_processed'
    ]
    list_filter = [
        'source', 'event_type', 'is_processed', 
        'published_date', 'business_relevance_score'
    ]
    search_fields = ['title', 'content', 'author']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Artículo', {
            'fields': ('source', 'title', 'content', 'url', 'author', 'published_date', 'section')
        }),
        ('Procesamiento ML', {
            'fields': (
                'event_type', 'event_date', 'event_location',
                'business_relevance_score', 'sentiment_score',
                'extracted_keywords', 'entities'
            )
        }),
        ('Estado', {
            'fields': ('is_processed', 'processing_error', 'created_at', 'updated_at')
        }),
    )

@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = [
        'platform', 'account_name', 'posted_date', 
        'business_relevance_score', 'is_processed'
    ]
    list_filter = ['platform', 'is_processed', 'posted_date']
    search_fields = ['account_name', 'text_content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'posted_date'

@admin.register(ManualNewsEntry)
class ManualNewsEntryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'entered_by', 'event_type', 'event_date', 'created_at'
    ]
    list_filter = ['event_type', 'event_date', 'created_at']
    search_fields = ['title', 'content', 'location']
    readonly_fields = ['created_at']