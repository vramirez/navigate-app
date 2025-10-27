from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import NewsSource, NewsArticle, SocialMediaPost, ManualNewsEntry, CrawlHistory
from .services.crawler_orchestrator import CrawlerOrchestratorService

# Configure admin site headers
admin.site.site_header = "NaviGate Admin"
admin.site.site_title = "NaviGate Admin Portal"
admin.site.index_title = "Welcome to NaviGate Administration"

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'source_type', 'country', 'crawl_status_display', 'retry_after_display',
        'is_active', 'last_fetched', 'crawler_actions'
    ]
    list_filter = ['source_type', 'country', 'is_active', 'crawl_status', 'rss_discovered', 'manual_crawl_enabled', 'created_at']
    search_fields = ['name', 'website_url', 'crawler_url']
    readonly_fields = [
        'last_fetched', 'created_at', 'rss_discovered', 'discovered_rss_url',
        'crawl_sections', 'manual_crawl_enabled', 'crawl_status', 'last_crawl_attempt',
        'crawl_retry_after', 'failed_crawl_count'
    ]
    actions = ['setup_sources', 'crawl_sources', 'discover_rss_feeds', 'reset_crawl_status_action']

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'source_type', 'country', 'website_url')
        }),
        ('Configuración de Crawler', {
            'fields': (
                'crawler_url', 'rss_discovered', 'discovered_rss_url',
                'manual_crawl_enabled', 'crawl_sections'
            ),
            'description': 'Los campos auto-descubiertos (RSS, secciones, estado manual) son de solo lectura y se actualizan automáticamente.'
        }),
        ('Estado de Rastreo', {
            'fields': (
                'crawl_status', 'last_crawl_attempt', 'crawl_retry_after', 'failed_crawl_count'
            ),
            'description': 'Estado de rastreabilidad del sitio y gestión de reintentos'
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
            path('<int:source_id>/reset-status/', self.reset_status_view, name='news_source_reset_status'),
            path('bulk-crawl/', self.bulk_crawl_view, name='news_source_bulk_crawl'),
        ]
        return custom_urls + urls

    def crawl_status_display(self, obj):
        """Display crawl status with colored indicators"""
        status_colors = {
            'rss_available': 'green',
            'manual_crawlable': 'blue',
            'spa_detected': 'orange',
            'uncrawlable': 'red',
            'unknown': 'gray',
        }

        status_icons = {
            'rss_available': '🟢',
            'manual_crawlable': '🔵',
            'spa_detected': '🟠',
            'uncrawlable': '🔴',
            'unknown': '⚪',
        }

        color = status_colors.get(obj.crawl_status, 'gray')
        icon = status_icons.get(obj.crawl_status, '⚪')

        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, icon, obj.get_crawl_status_display()
        )

    crawl_status_display.short_description = 'Estado de Rastreo'

    def retry_after_display(self, obj):
        """Display retry after datetime or 'Available now'"""
        from django.utils import timezone

        if not obj.crawl_retry_after:
            return format_html('<span style="color: green;">Disponible</span>')

        if obj.crawl_retry_after > timezone.now():
            return format_html(
                '<span style="color: orange;">{}</span>',
                obj.crawl_retry_after.strftime('%Y-%m-%d %H:%M')
            )
        else:
            return format_html('<span style="color: green;">Disponible ahora</span>')

    retry_after_display.short_description = 'Reintentar Después'

    def crawler_actions(self, obj):
        """Display action buttons for crawler operations"""
        from django.utils import timezone
        actions = []

        # Check if blocked
        is_blocked = (
            obj.crawl_retry_after and
            obj.crawl_retry_after > timezone.now() and
            obj.crawl_status in ['uncrawlable', 'spa_detected']
        )

        if is_blocked:
            # Show blocked message and reset button
            retry_time = obj.crawl_retry_after.strftime('%Y-%m-%d %H:%M')
            actions.append(
                f'<span style="color: orange;">🔒 Bloqueado hasta {retry_time}</span> '
                f'<a href="{obj.id}/reset-status/" class="button">Reiniciar Estado</a>'
            )
        else:
            # Normal actions
            if obj.crawler_url and not (obj.rss_discovered or obj.manual_crawl_enabled):
                actions.append(f'<a href="{obj.id}/setup/" class="button">Configurar</a>')

            if not obj.rss_discovered and obj.crawler_url:
                actions.append(f'<a href="{obj.id}/discover-rss/" class="button">Descubrir RSS</a>')

            if not obj.manual_crawl_enabled and obj.crawler_url:
                actions.append(f'<a href="{obj.id}/analyze-structure/" class="button">Analizar Sitio</a>')

            if obj.rss_discovered or obj.manual_crawl_enabled:
                actions.append(f'<a href="{obj.id}/crawl/" class="button default">Obtener Ahora</a>')

            # Add reset button for SPA/uncrawlable (even after block expires)
            if obj.crawl_status in ['spa_detected', 'uncrawlable']:
                actions.append(f'<a href="{obj.id}/reset-status/" class="button">Reiniciar Estado</a>')

        return format_html(' '.join(actions))

    crawler_actions.short_description = 'Acciones'

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

        self.message_user(request, f'Se configuraron exitosamente {setup_count} fuentes')

    setup_sources.short_description = "Configurar fuentes seleccionadas (descubrir RSS y analizar estructura)"

    def crawl_sources(self, request, queryset):
        """Crawl selected sources"""
        orchestrator = CrawlerOrchestratorService()
        crawl_count = 0

        for source in queryset:
            result = orchestrator.crawl_source(source.id)
            if result['success']:
                crawl_count += 1

        self.message_user(request, f'Se obtuvieron exitosamente {crawl_count} fuentes')

    crawl_sources.short_description = "Obtener contenido de fuentes seleccionadas"

    def discover_rss_feeds(self, request, queryset):
        """Discover RSS feeds for selected sources"""
        orchestrator = CrawlerOrchestratorService()
        discovery_count = 0

        for source in queryset:
            if source.crawler_url:
                result = orchestrator.discover_rss_for_source(source.id)
                if result['success']:
                    discovery_count += 1

        self.message_user(request, f'Se descubrieron feeds RSS para {discovery_count} fuentes')

    discover_rss_feeds.short_description = "Descubrir feeds RSS para fuentes seleccionadas"

    def reset_crawl_status_action(self, request, queryset):
        """Reset crawl status for selected sources"""
        orchestrator = CrawlerOrchestratorService()
        reset_count = 0

        for source in queryset:
            result = orchestrator.reset_crawl_status(source.id)
            if result['success']:
                reset_count += 1

        self.message_user(request, f'Se reinició el estado de rastreo para {reset_count} fuentes')

    reset_crawl_status_action.short_description = "Reiniciar estado de rastreo (permite reintentar inmediatamente)"

    # Custom Views
    def discover_rss_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.discover_rss_for_source(source_id)

        if result['success']:
            messages.success(request, f'Descubrimiento RSS completado para {source.name}')
        else:
            error_msg = result.get('error', 'No se encontraron feeds RSS en este sitio')
            messages.error(request, f'Descubrimiento RSS falló para {source.name}: {error_msg}')

        return redirect('admin:news_newssource_changelist')

    def analyze_structure_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.analyze_site_structure(source_id)

        if result['success']:
            messages.success(request, f'Análisis de estructura completado para {source.name}')
        else:
            error_msg = result.get('error', 'No se pudo analizar la estructura del sitio')
            messages.error(request, f'Análisis de estructura falló para {source.name}: {error_msg}')

        return redirect('admin:news_newssource_changelist')

    def crawl_source_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        force_manual = request.GET.get('force_manual', '').lower() == 'true'
        result = orchestrator.crawl_source(source_id, force_manual=force_manual)

        if result['success']:
            messages.success(request, f'Obtención completada para {source.name}: {result["articles_saved"]} artículos guardados')
        else:
            # Get detailed error message
            error_msg = result.get('error')
            if not error_msg and result.get('errors'):
                error_msg = '; '.join(result['errors'][:3])  # Show first 3 errors
            if not error_msg:
                error_msg = "No se pudo obtener contenido de esta fuente"

            messages.error(request, f'Obtención falló para {source.name}: {error_msg}')

        return redirect('admin:news_newssource_changelist')

    def setup_source_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.setup_news_source(source)

        if result['success']:
            messages.success(request, f'Configuración completada para {source.name}')
        else:
            # Get detailed error message
            error_msg = None
            if result.get('errors'):
                error_msg = '; '.join(result['errors'][:3])
            if not error_msg:
                error_msg = "No se pudo configurar la fuente automáticamente"

            messages.error(request, f'Configuración falló para {source.name}: {error_msg}')

        return redirect('admin:news_newssource_changelist')

    def reset_status_view(self, request, source_id):
        source = get_object_or_404(NewsSource, id=source_id)
        orchestrator = CrawlerOrchestratorService()

        result = orchestrator.reset_crawl_status(source_id)

        if result['success']:
            messages.success(request, f'Estado reiniciado para {source.name}: {result["message"]}')
        else:
            messages.error(request, f'Error al reiniciar estado: {result.get("error")}')

        return redirect('admin:news_newssource_changelist')

    def bulk_crawl_view(self, request):
        orchestrator = CrawlerOrchestratorService()
        country_code = request.GET.get('country')

        result = orchestrator.bulk_crawl(country_code=country_code)

        if result['success']:
            messages.success(request, f'Obtención masiva completada: {result["successful_crawls"]} fuentes obtenidas exitosamente')
        else:
            messages.error(request, 'Obtención masiva falló')

        return redirect('admin:news_newssource_changelist')

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'source', 'published_date', 'crawl_section', 'event_type',
        'business_relevance_score'
    ]
    list_filter = [
        'source', 'event_type', 'crawl_section',
        'published_date', 'business_relevance_score'
    ]
    search_fields = ['title', 'content', 'author', 'crawl_section']
    readonly_fields = [
        'source', 'title', 'content', 'first_paragraph', 'url', 'author', 'published_date',
        'section', 'crawl_section', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'published_date'

    fieldsets = (
        ('Artículo (Datos del Crawler - Solo Lectura)', {
            'fields': ('source', 'title', 'content', 'first_paragraph', 'url', 'author', 'published_date', 'section', 'crawl_section'),
            'description': 'Estos campos son generados automáticamente por el crawler y no pueden ser modificados.'
        }),
        ('Procesamiento ML (Editable)', {
            'fields': (
                'event_type', 'event_date', 'event_location',
                'business_relevance_score', 'sentiment_score',
                'extracted_keywords', 'entities'
            )
        }),
        ('Estado', {
            'fields': ('processing_error', 'created_at', 'updated_at')
        }),
    )

@admin.register(CrawlHistory)
class CrawlHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'source_display', 'crawl_date', 'status', 'crawl_type',
        'articles_found', 'articles_saved', 'crawl_duration_display'
    ]
    list_filter = ['status', 'crawl_type', 'crawl_date', 'source']
    search_fields = ['source__name', 'error_message']
    readonly_fields = [
        'source_display', 'crawl_date', 'status', 'crawl_type',
        'articles_found', 'articles_saved', 'error_message', 'crawl_duration'
    ]
    date_hierarchy = 'crawl_date'

    def source_display(self, obj):
        """Display source name or 'Deleted Source' if null"""
        if obj.source:
            return obj.source.name
        return format_html('<em style="color: gray;">Fuente eliminada</em>')

    source_display.short_description = 'Fuente'

    def has_add_permission(self, request):
        """Prevent manual creation of crawl history"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of crawl history for audit trail"""
        return False

    def crawl_duration_display(self, obj):
        if obj.crawl_duration:
            return f"{obj.crawl_duration.total_seconds():.1f}s"
        return "-"

    crawl_duration_display.short_description = 'Duration'

    fieldsets = (
        ('Información del Crawl (Solo Lectura - Registro de Auditoría)', {
            'fields': ('source_display', 'crawl_date', 'status', 'crawl_type'),
            'description': 'Este es un registro de auditoría automático. No se puede modificar ni eliminar. Las fuentes eliminadas se muestran como "Fuente eliminada".'
        }),
        ('Resultados', {
            'fields': ('articles_found', 'articles_saved', 'crawl_duration')
        }),
        ('Detalles de Error', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = [
        'platform', 'account_name', 'posted_date',
        'business_relevance_score'
    ]
    list_filter = ['platform', 'posted_date']
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