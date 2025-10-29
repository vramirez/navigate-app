from django.contrib import admin
from django.db.models import Count
from .models import Business, BusinessKeywords, BusinessType, BusinessTypeKeyword, AdminUser

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'business_type', 'city', 'neighborhood',
        'owner', 'is_active', 'created_at'
    ]
    list_filter = ['business_type', 'city', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'owner__username', 'neighborhood']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['owner']

    fieldsets = (
        ('Información Básica', {
            'fields': ('owner', 'name', 'business_type', 'description')
        }),
        ('Ubicación', {
            'fields': (
                'city', 'address', 'neighborhood',
                'latitude', 'longitude',
                'geographic_radius_km'
            )
        }),
        ('Preferencias Geográficas', {
            'fields': (
                'include_citywide_events',
                'include_national_events',
                'has_tv_screens'
            )
        }),
        ('Detalles del Negocio', {
            'fields': (
                'target_audience', 'capacity', 'staff_count',
                'operating_hours_start', 'operating_hours_end'
            )
        }),
        ('Contacto', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Notificaciones', {
            'fields': ('email_notifications', 'recommendation_frequency')
        }),
        ('Estado', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

class BusinessKeywordsInline(admin.TabularInline):
    model = BusinessKeywords
    extra = 1

@admin.register(BusinessKeywords)
class BusinessKeywordsAdmin(admin.ModelAdmin):
    list_display = ['business', 'keyword', 'weight', 'is_negative', 'created_at']
    list_filter = ['is_negative', 'weight', 'created_at']
    search_fields = ['keyword', 'business__name']

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
    list_display = ['keyword', 'business_type', 'category', 'weight', 'is_active', 'created_at']
    list_filter = ['business_type', 'category', 'is_active', 'weight']
    search_fields = ['keyword', 'category']
    list_editable = ['weight', 'is_active']
    ordering = ['business_type', 'category', 'keyword']

    fieldsets = (
        ('Palabra Clave', {
            'fields': ('business_type', 'keyword', 'category')
        }),
        ('Configuración', {
            'fields': ('weight', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

    actions = ['activate_keywords', 'deactivate_keywords']

    def activate_keywords(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} palabras clave activadas.')
    activate_keywords.short_description = 'Activar palabras clave seleccionadas'

    def deactivate_keywords(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} palabras clave desactivadas.')
    deactivate_keywords.short_description = 'Desactivar palabras clave seleccionadas'

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'can_manage_news_sources', 'can_create_businesses', 'created_at'
    ]
    list_filter = ['can_manage_news_sources', 'can_create_businesses', 'created_at']
    search_fields = ['user__username', 'city_access']