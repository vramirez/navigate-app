from django.contrib import admin
from .models import Business, BusinessKeywords, BusinessTypeKeyword, AdminUser

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'business_type', 'city', 'owner', 'is_active', 'created_at'
    ]
    list_filter = ['business_type', 'city', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('owner', 'name', 'business_type', 'city', 'description')
        }),
        ('Contacto', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Configuración del Negocio', {
            'fields': (
                'target_audience', 'operating_hours_start', 'operating_hours_end',
                'capacity', 'staff_count'
            )
        }),
        ('Preferencias', {
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