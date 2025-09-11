from django.contrib import admin
from .models import Recommendation, RecommendationFeedback, RecommendationTemplate

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'business', 'title', 'category', 'priority', 
        'confidence_score', 'is_viewed', 'is_accepted', 'created_at'
    ]
    list_filter = [
        'category', 'priority', 'action_type', 
        'is_viewed', 'is_accepted', 'is_implemented', 'created_at'
    ]
    search_fields = ['title', 'description', 'business__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Recomendación', {
            'fields': ('business', 'title', 'description', 'category', 'action_type')
        }),
        ('Evaluación ML', {
            'fields': ('confidence_score', 'impact_score', 'effort_score', 'priority')
        }),
        ('Implementación', {
            'fields': (
                'recommended_start_date', 'recommended_end_date',
                'estimated_duration_hours', 'resources_needed', 'expected_outcomes'
            )
        }),
        ('Interacción del Usuario', {
            'fields': (
                'is_viewed', 'is_accepted', 'is_implemented',
                'user_feedback', 'user_rating'
            )
        }),
        ('Contexto', {
            'fields': ('reasoning', 'content_type', 'object_id')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'expires_at')
        }),
    )

@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'recommendation', 'user', 'feedback_type', 'rating', 'created_at'
    ]
    list_filter = ['feedback_type', 'rating', 'created_at']
    search_fields = ['recommendation__title', 'user__username', 'comments']
    readonly_fields = ['created_at']

@admin.register(RecommendationTemplate)
class RecommendationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'action_type', 'default_priority', 'is_active'
    ]
    list_filter = ['category', 'action_type', 'default_priority', 'is_active']
    search_fields = ['name', 'title_template', 'description_template']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'action_type', 'is_active')
        }),
        ('Plantillas', {
            'fields': ('title_template', 'description_template', 'reasoning_template')
        }),
        ('Configuración Predeterminada', {
            'fields': ('default_priority', 'default_effort_score')
        }),
        ('Condiciones de Aplicación', {
            'fields': ('applicable_business_types', 'required_keywords')
        }),
    )