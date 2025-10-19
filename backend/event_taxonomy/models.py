"""
Event Taxonomy Models

Manages event types, subtypes, and extraction patterns for ML classification.
Allows dynamic configuration of event categories without code changes.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class EventType(models.Model):
    """
    Main event categories (sports_match, concert, festival, etc.)

    Examples:
    - sports_match: General sports events
    - concert: Musical performances
    - festival: Cultural/music/food festivals
    """

    RELEVANCE_CHOICES = [
        ('high', 'High Relevance'),
        ('medium', 'Medium Relevance'),
        ('low', 'Low Relevance'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Identificador único (ej: sports_match, concert, festival)'
    )
    name_es = models.CharField(
        max_length=100,
        verbose_name='Nombre (Español)',
        help_text='Nombre en español (ej: Partido deportivo)'
    )
    name_en = models.CharField(
        max_length=100,
        verbose_name='Nombre (Inglés)',
        help_text='Nombre en inglés (ej: Sports match)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del tipo de evento'
    )
    relevance_category = models.CharField(
        max_length=10,
        choices=RELEVANCE_CHOICES,
        default='medium',
        verbose_name='Categoría de relevancia',
        help_text='Nivel de relevancia para negocios de hospitalidad'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Icono',
        help_text='Nombre del icono (ej: trophy, music, fork-knife)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se detectará en nuevos artículos'
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name='Orden de visualización',
        help_text='Orden para mostrar en listas (menor primero)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'
        ordering = ['display_order', 'name_es']

    def __str__(self):
        return f"{self.name_es} ({self.code})"


class EventSubtype(models.Model):
    """
    Specific event subtypes (colombian_soccer, rock_concert, food_festival, etc.)

    Examples:
    - colombian_soccer (sports_match): Colombian national team soccer
    - rock_concert (concert): Rock music concert
    - food_festival (festival): Culinary/gastronomy festival
    """

    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE,
        related_name='subtypes',
        verbose_name='Tipo de evento padre'
    )
    code = models.CharField(
        max_length=100,
        verbose_name='Código',
        help_text='Identificador del subtipo (ej: colombian_soccer, rock_concert)'
    )
    name_es = models.CharField(
        max_length=150,
        verbose_name='Nombre (Español)',
        help_text='Nombre en español (ej: Fútbol colombiano)'
    )
    name_en = models.CharField(
        max_length=150,
        verbose_name='Nombre (Inglés)',
        help_text='Nombre en inglés (ej: Colombian soccer)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del subtipo'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se detectará en nuevos artículos'
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subtipo de Evento'
        verbose_name_plural = 'Subtipos de Eventos'
        ordering = ['event_type', 'display_order', 'name_es']
        unique_together = ['event_type', 'code']

    def __str__(self):
        return f"{self.event_type.code}/{self.code} - {self.name_es}"


class ExtractionPattern(models.Model):
    """
    Regex patterns for ML extraction of event types and subtypes

    Each pattern is a regular expression tested against article text.
    Matches are scored and the highest-scoring type/subtype is selected.
    """

    PATTERN_TARGET_CHOICES = [
        ('type', 'Event Type'),
        ('subtype', 'Event Subtype'),
    ]

    target = models.CharField(
        max_length=10,
        choices=PATTERN_TARGET_CHOICES,
        verbose_name='Objetivo del patrón',
        help_text='¿Este patrón detecta un tipo o un subtipo?'
    )

    # Foreign keys - one must be set based on target
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patterns',
        verbose_name='Tipo de evento',
        help_text='Tipo de evento (requerido si target=type o target=subtype)'
    )
    event_subtype = models.ForeignKey(
        EventSubtype,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patterns',
        verbose_name='Subtipo de evento',
        help_text='Subtipo de evento (requerido solo si target=subtype)'
    )

    pattern = models.CharField(
        max_length=500,
        verbose_name='Patrón regex',
        help_text='Expresión regular en Python (ej: r"concierto", r"selección\\\\s+colombia")'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción legible del patrón (ej: "detecta partidos de fútbol")'
    )
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        verbose_name='Peso',
        help_text='Importancia del patrón (0.1-10.0, default 1.0)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se usará en la extracción'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patrón de Extracción'
        verbose_name_plural = 'Patrones de Extracción'
        ordering = ['-weight', 'id']

    def __str__(self):
        if self.target == 'type':
            return f"Type: {self.event_type.code if self.event_type else '?'} - {self.pattern[:50]}"
        else:
            return f"Subtype: {self.event_subtype.code if self.event_subtype else '?'} - {self.pattern[:50]}"

    def clean(self):
        """Validate that correct foreign keys are set based on target"""
        from django.core.exceptions import ValidationError

        if self.target == 'type':
            if not self.event_type:
                raise ValidationError('event_type is required when target is "type"')
            self.event_subtype = None  # Clear subtype if set

        elif self.target == 'subtype':
            if not self.event_subtype:
                raise ValidationError('event_subtype is required when target is "subtype"')
            if not self.event_type:
                # Auto-set event_type from subtype
                self.event_type = self.event_subtype.event_type
