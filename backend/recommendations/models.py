from django.db import models
from django.contrib.auth.models import User
from businesses.models import Business
from news.models import NewsArticle, SocialMediaPost, ManualNewsEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Recommendation(models.Model):
    """Business recommendations generated from news and social media analysis"""
    PRIORITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'), 
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    CATEGORIES = [
        ('inventory', 'Inventario'),
        ('staffing', 'Personal'),
        ('marketing', 'Marketing'),
        ('pricing', 'Precios'),
        ('operations', 'Operaciones'),
        ('partnerships', 'Alianzas'),
        ('events', 'Eventos'),
        ('seasonal', 'Estacional'),
    ]
    
    ACTION_TYPES = [
        ('increase_inventory', 'Aumentar inventario'),
        ('hire_staff', 'Contratar personal'),
        ('create_promotion', 'Crear promoción'),
        ('adjust_hours', 'Ajustar horarios'),
        ('contact_supplier', 'Contactar proveedor'),
        ('plan_event', 'Planificar evento'),
        ('social_campaign', 'Campaña en redes sociales'),
        ('partner_collaboration', 'Colaboración con socios'),
        ('price_adjustment', 'Ajuste de precios'),
        ('menu_modification', 'Modificar menú/ofertas'),
    ]
    
    business = models.ForeignKey(
        Business, 
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Source of the recommendation (news, social media, manual)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Recommendation details
    title = models.CharField(max_length=300, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        verbose_name='Categoría'
    )
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        verbose_name='Tipo de acción'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        verbose_name='Prioridad'
    )
    
    # ML confidence and scoring
    confidence_score = models.FloatField(
        verbose_name='Puntuación de confianza',
        help_text='0.0 - 1.0, generado por ML'
    )
    impact_score = models.FloatField(
        verbose_name='Puntuación de impacto',
        help_text='0.0 - 1.0, impacto potencial en el negocio'
    )
    effort_score = models.FloatField(
        default=0.5,
        verbose_name='Puntuación de esfuerzo',
        help_text='0.0 - 1.0, esfuerzo requerido para implementar'
    )
    
    # Timing and implementation
    recommended_start_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Fecha recomendada de inicio'
    )
    recommended_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha recomendada de fin'
    )
    estimated_duration_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duración estimada (horas)'
    )
    
    # Additional context and resources
    reasoning = models.TextField(
        blank=True,
        verbose_name='Razonamiento',
        help_text='Por qué se genera esta recomendación'
    )
    resources_needed = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Recursos necesarios',
        help_text='Lista de recursos, personal, materiales, etc.'
    )
    expected_outcomes = models.TextField(
        blank=True,
        verbose_name='Resultados esperados'
    )
    
    # User interaction
    is_viewed = models.BooleanField(default=False, verbose_name='Visto')
    is_accepted = models.BooleanField(default=False, verbose_name='Aceptado')
    is_implemented = models.BooleanField(default=False, verbose_name='Implementado')
    user_feedback = models.TextField(
        blank=True,
        verbose_name='Comentarios del usuario'
    )
    user_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Calificación del usuario (1-5)'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira el'
    )
    
    class Meta:
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'
        ordering = ['-priority', '-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['business', 'priority']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['is_viewed', 'is_accepted']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.business.name}: {self.title}"
        
    def get_priority_weight(self):
        """Return numeric weight for priority ordering"""
        weights = {
            'urgent': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
        }
        return weights.get(self.priority, 1)
    
    def calculate_final_score(self):
        """Calculate final recommendation score based on multiple factors"""
        priority_weight = self.get_priority_weight()
        return (
            (self.confidence_score * 0.4) +
            (self.impact_score * 0.3) +
            ((1 - self.effort_score) * 0.2) +  # Lower effort = higher score
            (priority_weight / 4 * 0.1)
        )

class RecommendationFeedback(models.Model):
    """Track user feedback on recommendations for ML improvement"""
    FEEDBACK_TYPES = [
        ('helpful', 'Útil'),
        ('not_helpful', 'No útil'),
        ('implemented', 'Implementado'),
        ('not_relevant', 'No relevante'),
        ('too_late', 'Muy tarde'),
        ('too_early', 'Muy temprano'),
    ]
    
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        verbose_name='Tipo de comentario'
    )
    rating = models.PositiveIntegerField(
        verbose_name='Calificación (1-5)',
        help_text='1 = Muy malo, 5 = Excelente'
    )
    comments = models.TextField(
        blank=True,
        verbose_name='Comentarios adicionales'
    )
    
    # Implementation details if applicable
    implemented_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de implementación'
    )
    implementation_notes = models.TextField(
        blank=True,
        verbose_name='Notas de implementación'
    )
    actual_outcomes = models.TextField(
        blank=True,
        verbose_name='Resultados reales'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comentario sobre recomendación'
        verbose_name_plural = 'Comentarios sobre recomendaciones'
        unique_together = ['recommendation', 'user']
        
    def __str__(self):
        return f"{self.recommendation.title}: {self.feedback_type}"

class RecommendationTemplate(models.Model):
    """Templates for generating consistent recommendations"""
    name = models.CharField(max_length=200, verbose_name='Nombre')
    category = models.CharField(
        max_length=20,
        choices=Recommendation.CATEGORIES,
        verbose_name='Categoría'
    )
    action_type = models.CharField(
        max_length=30,
        choices=Recommendation.ACTION_TYPES,
        verbose_name='Tipo de acción'
    )
    
    # Template content
    title_template = models.CharField(
        max_length=300,
        verbose_name='Plantilla de título',
        help_text='Use {variables} para datos dinámicos'
    )
    description_template = models.TextField(
        verbose_name='Plantilla de descripción'
    )
    reasoning_template = models.TextField(
        blank=True,
        verbose_name='Plantilla de razonamiento'
    )
    
    # Default values
    default_priority = models.CharField(
        max_length=10,
        choices=Recommendation.PRIORITY_LEVELS,
        default='medium',
        verbose_name='Prioridad por defecto'
    )
    default_effort_score = models.FloatField(
        default=0.5,
        verbose_name='Puntuación de esfuerzo por defecto'
    )
    
    # Conditions for when to use this template
    applicable_business_types = models.JSONField(
        default=list,
        verbose_name='Tipos de negocio aplicables'
    )
    required_keywords = models.JSONField(
        default=list,
        verbose_name='Palabras clave requeridas'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plantilla de recomendación'
        verbose_name_plural = 'Plantillas de recomendaciones'
        
    def __str__(self):
        return f"{self.name} ({self.category})"