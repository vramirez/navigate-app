from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils.html import format_html
from .models import NewsSource, NewsArticle, SocialMediaPost, ManualNewsEntry, CrawlHistory
from .services.crawler_orchestrator import CrawlerOrchestratorService

# Configure admin site headers
admin.site.site_header = "NaviGate Admin"
admin.site.site_title = "NaviGate Admin Portal"
admin.site.index_title = "Welcome to NaviGate Administration"

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'source_type', 'country', 'crawler_status_display', 'is_active',
        'reliability_score', 'last_fetched', 'crawler_actions'
    ]
    list_filter = ['source_type', 'country', 'is_active', 'rss_discovered', 'manual_crawl_enabled', 'created_at']
    search_fields = ['name', 'website_url', 'crawler_url']
    readonly_fields = ['last_fetched', 'created_at', 'rss_discovered', 'discovered_rss_url']
    actions = ['setup_sources', 'crawl_sources', 'discover_rss_feeds']

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'source_type', 'country', 'website_url')
        }),
        ('Configuración de Crawler', {
            'fields': (
                'crawler_url', 'rss_discovered', 'discovered_rss_url',
                'manual_crawl_enabled', 'crawl_sections'
            ),
            'description': 'Configuración para el sistema de crawling automático'
        }),
        ('Configuración Legacy de Datos', {
            'fields': ('rss_url', 'api_endpoint', 'scraping_enabled', 'css_selectors'),
            'classes': ('collapse',),
            'description': 'Configuración heredada del sistema anterior'
        }),
        ('Estado y Métricas', {
            'fields': (
                'is_active', 'reliability_score', 'fetch_frequency_hours',
                'last_fetched', 'created_at'
            )
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:source_id>/discover-rss/', self.discover_rss_view, name='news_source_discover_rss'),
            path('<int:source_id>/analyze-structure/', self.analyze_structure_view, name='news_source_analyze_structure'),
            path('<int:source_id>/crawl/', self.crawl_source_view, name='news_source_crawl'),
            path('<int:source_id>/setup/', self.setup_source_view, name='news_source_setup'),
            path('bulk-crawl/', self.bulk_crawl_view, name='news_source_bulk_crawl'),
        ]
        return custom_urls + urls

    def crawler_status_display(self, obj):
        """Display crawler status with colored indicators"""
        status_parts = []

        if obj.rss_discovered and obj.discovered_rss_url:
            status_parts.append('<span style="color: green;">📡 RSS</span>')

        if obj.manual_crawl_enabled and obj.crawl_sections:
            sections_count = len(obj.crawl_sections) if obj.crawl_sections else 0
            status_parts.append(f'<span style="color: blue;">🕷️ Manual ({sections_count})</span>')

        if not status_parts:
            if obj.crawler_url:
                status_parts.append('<span style="color: orange;">⚙️ Needs Setup</span>')
            else:
                status_parts.append('<span style="color: red;">❌ Not Configured</span>')

        return format_html(' | '.join(status_parts))

    crawler_status_display.short_description = 'Crawler Status'

    def crawler_actions(self, obj):
        """Display action buttons for crawler operations"""
        actions = []

        if obj.crawler_url and not (obj.rss_discovered or obj.manual_crawl_enabled):
            actions.append(f'<a href="{obj.id}/setup/" class="button">Setup</a>')

        if not obj.rss_discovered and obj.crawler_url:
            actions.append(f'<a href="{obj.id}/discover-rss/" class="button">Discover RSS</a>')

        if not obj.manual_crawl_enabled and obj.crawler_url:
            actions.append(f'<a href="{obj.id}/analyze-structure/" class="button">Analyze Site</a>')

        if obj.rss_discovered or obj.manual_crawl_enabled:
            actions.append(f'<a href="{obj.id}/crawl/" class="button default">Crawl Now</a>')

        return format_html(' '.join(actions))

    crawler_actions.short_description = 'Actions'

    # Admin Actions
    def setup_sources(self, request, queryset):
        """Setup selected sources by discovering RSS and analyzing structure"""
        orchestrator = CrawlerOrchestratorService()
        setup_count = 0

        for source in queryset:
            if source.crawler_url:
                result = orchestrator.setup_news_source(source)
                if result['success']:
                    setup_count += 1

        self.message_user(request, f'Successfully set up {setup_count} sources')

    setup_sources.short_description = "Setup selected sources (discover RSS & analyze structure)"

    def crawl_sources(self, request, queryset):
        """Crawl selected sources"""
        orchestrator = CrawlerOrchestratorService()
        crawl_count = 0

        for source in queryset:
            result = orchestrator.crawl_source(source.id)
            if result['success']:
                crawl_count += 1

        self.message_user(request, f'Successfully crawled {crawl_count} sources')

    crawl_sources.short_description = "Crawl selected sources"

    def discover_rss_feeds(self, request, queryset):
        """Discover RSS feeds for selected sources"""
        orchestrator = CrawlerOrchestratorService()
        discovery_count = 0

        for source in queryset:
            if source.crawler_url:
                result = orchestrator.discover_rss_for_source(source.id)
                if result['success']:
                    discovery_count += 1

        self.message_user(request, f'Discovered RSS feeds for {discovery_count} sources')

    discover_rss_feeds.short_description = "Discover RSS feeds for selected sources"

    # Custom Views
    def discover_rss_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.discover_rss_for_source(source_id)

        if result['success']:
            messages.success(request, f'RSS discovery completed for {source.name}')
        else:
            messages.error(request, f'RSS discovery failed: {result.get("error", "Unknown error")}')

        return JsonResponse(result)

    def analyze_structure_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.analyze_site_structure(source_id)

        if result['success']:
            messages.success(request, f'Site structure analysis completed for {source.name}')
        else:
            messages.error(request, f'Structure analysis failed: {result.get("error", "Unknown error")}')

        return JsonResponse(result)

    def crawl_source_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        force_manual = request.GET.get('force_manual', '').lower() == 'true'
        result = orchestrator.crawl_source(source_id, force_manual=force_manual)

        if result['success']:
            messages.success(request, f'Crawl completed for {source.name}: {result["articles_saved"]} articles saved')
        else:
            messages.error(request, f'Crawl failed: {result.get("error", "Unknown error")}')

        return JsonResponse(result)

    def setup_source_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.setup_news_source(source)

        if result['success']:
            messages.success(request, f'Setup completed for {source.name}')
        else:
            messages.error(request, f'Setup failed: {result.get("error", "Unknown error")}')

        return JsonResponse(result)

    def bulk_crawl_view(self, request):
        orchestrator = CrawlerOrchestratorService()
        country_code = request.GET.get('country')

        result = orchestrator.bulk_crawl(country_code=country_code)

        if result['success']:
            messages.success(request, f'Bulk crawl completed: {result["successful_crawls"]} sources crawled successfully')
        else:
            messages.error(request, 'Bulk crawl failed')

        return JsonResponse(result)

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'source', 'published_date', 'crawl_section', 'event_type',
        'business_relevance_score', 'is_processed'
    ]
    list_filter = [
        'source', 'event_type', 'is_processed', 'crawl_section',
        'published_date', 'business_relevance_score'
    ]
    search_fields = ['title', 'content', 'author', 'crawl_section']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_date'

    fieldsets = (
        ('Artículo', {
            'fields': ('source', 'title', 'content', 'url', 'author', 'published_date', 'section', 'crawl_section')
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

@admin.register(CrawlHistory)
class CrawlHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'source', 'crawl_date', 'status', 'crawl_type',
        'articles_found', 'articles_saved', 'crawl_duration_display'
    ]
    list_filter = ['status', 'crawl_type', 'crawl_date', 'source']
    search_fields = ['source__name', 'error_message']
    readonly_fields = ['crawl_date', 'crawl_duration']
    date_hierarchy = 'crawl_date'

    def crawl_duration_display(self, obj):
        if obj.crawl_duration:
            return f"{obj.crawl_duration.total_seconds():.1f}s"
        return "-"

    crawl_duration_display.short_description = 'Duration'

    fieldsets = (
        ('Crawl Information', {
            'fields': ('source', 'crawl_date', 'status', 'crawl_type')
        }),
        ('Results', {
            'fields': ('articles_found', 'articles_saved', 'crawl_duration')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
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