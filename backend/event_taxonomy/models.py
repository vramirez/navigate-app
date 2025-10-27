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


class SportType(models.Model):
    """
    Sport types with Latin America appeal ratings for broadcastability scoring

    Stores sport-specific parameters to intelligently calculate whether an
    international sports event is likely to draw pub/bar crowds in Latin America.

    Examples:
    - Soccer: 0.95 appeal (very high - World Cup, Copa América draw massive crowds)
    - Cycling: 0.82 appeal (high - Colombian cyclists dominate European tours)
    - Skiing: 0.10 appeal (very low - no cultural relevance)
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Identificador del deporte (ej: soccer, cycling, combat_sports)'
    )
    name_es = models.CharField(
        max_length=100,
        verbose_name='Nombre (Español)',
        help_text='Nombre en español (ej: Fútbol, Ciclismo)'
    )
    name_en = models.CharField(
        max_length=100,
        verbose_name='Nombre (Inglés)',
        help_text='Nombre en inglés (ej: Soccer, Cycling)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción del deporte y su relevancia en Latinoamérica'
    )
    latin_america_appeal = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Atractivo en Latinoamérica',
        help_text='Puntuación 0.0-1.0: qué tanto atrae audiencias en bares/pubs (0.95=fútbol, 0.10=esquí)'
    )
    keywords = models.JSONField(
        default=list,
        verbose_name='Palabras clave',
        help_text='Lista de keywords en español para detección: ["fútbol", "partido", "gol"]'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se usará en cálculo de broadcastability'
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Deporte'
        verbose_name_plural = 'Tipos de Deportes'
        ordering = ['-latin_america_appeal', 'display_order']

    def __str__(self):
        return f"{self.name_es} ({self.code}) - Appeal: {self.latin_america_appeal}"


class CompetitionLevel(models.Model):
    """
    Competition tiers and their broadcast appeal multipliers

    Different competition levels have vastly different broadcast appeal:
    - World Cup Final: 3.0x multiplier (massive global event)
    - Segunda División match: 0.4x multiplier (local interest only)

    This allows intelligent inference: "World Cup" in article → high broadcastability
    even if article doesn't explicitly say "será transmitido en TV"
    """

    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código',
        help_text='Identificador de la competición (ej: world_cup_final, tour_de_france)'
    )
    name_es = models.CharField(
        max_length=150,
        verbose_name='Nombre (Español)',
        help_text='Nombre de la competición (ej: Copa Mundial, Tour de Francia)'
    )
    name_en = models.CharField(
        max_length=150,
        verbose_name='Nombre (Inglés)',
        help_text='Nombre en inglés (ej: World Cup, Tour de France)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    sport_type = models.ForeignKey(
        SportType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='competition_levels',
        verbose_name='Tipo de deporte',
        help_text='Deporte al que pertenece (null = aplica a todos)'
    )
    broadcast_multiplier = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(3.0)],
        verbose_name='Multiplicador de transmisión',
        help_text='0.1-3.0: impacto en broadcastability (3.0=Mundial, 1.0=liga regular, 0.4=segunda división)'
    )
    typical_attendance_min = models.IntegerField(
        default=0,
        verbose_name='Asistencia típica mínima',
        help_text='Asistencia típica del evento (para validación)'
    )
    keywords = models.JSONField(
        default=list,
        verbose_name='Palabras clave',
        help_text='Patrones de detección: ["copa mundial", "final", "clasificatorias"]'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nivel de Competición'
        verbose_name_plural = 'Niveles de Competición'
        ordering = ['-broadcast_multiplier', 'display_order']

    def __str__(self):
        sport_str = f" ({self.sport_type.code})" if self.sport_type else ""
        return f"{self.name_es}{sport_str} - {self.broadcast_multiplier}x"


class HypeIndicator(models.Model):
    """
    Text patterns that signal high-impact, must-watch events

    Detects language indicating event magnitude/excitement:
    - "final", "semifinal" → Championship stakes
    - "histórico", "épico" → Historic significance
    - "clásico", "derbi" → Rivalry matches
    - "Egan Bernal", "Nairo Quintana" → Colombian star athletes

    Each match adds to the article's hype_score (0.0-1.0)
    """

    CATEGORY_CHOICES = [
        ('finals', 'Finals/Championships'),
        ('historic', 'Historic Significance'),
        ('rivalry', 'Rivalries/Derbies'),
        ('stakes', 'High Stakes'),
        ('scale', 'Massive Scale'),
        ('star_power', 'Star Athletes'),
        ('colombian', 'Colombian Involvement'),
    ]

    pattern = models.CharField(
        max_length=500,
        verbose_name='Patrón regex',
        help_text='Expresión regular (ej: r"final|semifinal", r"egan bernal|nairo quintana")'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción del patrón (ej: "Detecta lenguaje de finales")'
    )
    hype_boost = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(0.5)],
        verbose_name='Impulso de hype',
        help_text='0.0-0.5: cuánto aumenta el hype_score al coincidir'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría',
        help_text='Tipo de indicador de hype'
    )
    language = models.CharField(
        max_length=2,
        default='es',
        verbose_name='Idioma',
        help_text='Idioma del patrón (es=español, en=inglés)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Indicador de Hype'
        verbose_name_plural = 'Indicadores de Hype'
        ordering = ['-hype_boost', 'category']

    def __str__(self):
        return f"[{self.category}] {self.pattern[:40]} (+{self.hype_boost})"


class BroadcastabilityConfig(models.Model):
    """
    Global configuration for broadcastability scoring (Singleton)

    Defines weights for each component and thresholds for classification.
    Only one row should exist in this table.

    Formula:
    broadcastability = (
        sport_appeal × sport_appeal_weight +
        competition_level × competition_level_weight +
        hype_indicators × hype_indicators_weight +
        attendance × attendance_weight
    )
    """

    # Component weights (must sum to 1.0)
    sport_appeal_weight = models.FloatField(
        default=0.35,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Peso: Atractivo del deporte',
        help_text='Peso del componente sport_appeal (0.0-1.0, default 0.35 = 35%)'
    )
    competition_level_weight = models.FloatField(
        default=0.30,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Peso: Nivel de competición',
        help_text='Peso del componente competition_level (0.0-1.0, default 0.30 = 30%)'
    )
    hype_indicators_weight = models.FloatField(
        default=0.20,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Peso: Indicadores de hype',
        help_text='Peso del componente hype_indicators (0.0-1.0, default 0.20 = 20%)'
    )
    attendance_weight = models.FloatField(
        default=0.15,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Peso: Asistencia',
        help_text='Peso del componente attendance (0.0-1.0, default 0.15 = 15%)'
    )

    # Thresholds
    min_broadcastability_score = models.FloatField(
        default=0.55,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='Puntuación mínima de broadcastability',
        help_text='Score >= este valor se marca como broadcastable (default 0.55)'
    )

    # Attendance scaling thresholds
    attendance_small = models.IntegerField(
        default=5000,
        verbose_name='Umbral de asistencia: Pequeño',
        help_text='< este valor = asistencia muy baja'
    )
    attendance_medium = models.IntegerField(
        default=20000,
        verbose_name='Umbral de asistencia: Mediano',
        help_text='< este valor = asistencia mediana'
    )
    attendance_large = models.IntegerField(
        default=50000,
        verbose_name='Umbral de asistencia: Grande',
        help_text='< este valor = asistencia grande, >= este valor = masiva'
    )

    # Business requirements
    requires_tv_screens = models.BooleanField(
        default=True,
        verbose_name='Requiere pantallas de TV',
        help_text='Si True, eventos broadcastables solo relevantes para negocios con has_tv_screens=True'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Broadcastability'
        verbose_name_plural = 'Configuración de Broadcastability'

    def __str__(self):
        return f"Broadcastability Config (min_score: {self.min_broadcastability_score})"

    def clean(self):
        """Validate that weights sum to approximately 1.0"""
        from django.core.exceptions import ValidationError
        total_weight = (
            self.sport_appeal_weight +
            self.competition_level_weight +
            self.hype_indicators_weight +
            self.attendance_weight
        )
        if not (0.99 <= total_weight <= 1.01):
            raise ValidationError(
                f'Los pesos deben sumar 1.0 (actual: {total_weight:.2f})'
            )

    def save(self, *args, **kwargs):
        """Enforce singleton pattern"""
        if not self.pk and BroadcastabilityConfig.objects.exists():
            raise ValueError('Solo puede existir una instancia de BroadcastabilityConfig')
        return super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create singleton instance"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'sport_appeal_weight': 0.35,
                'competition_level_weight': 0.30,
                'hype_indicators_weight': 0.20,
                'attendance_weight': 0.15,
                'min_broadcastability_score': 0.55,
            }
        )
        return obj


class CuisineType(models.Model):
    """
    Cuisine types for food event classification (task-9.8)

    Allows targeted recommendations based on cuisine type.
    Examples: Italian restaurant gets notified about Italian food festivals.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Identificador del tipo de cocina (ej: italian, japanese, colombian)'
    )
    name_es = models.CharField(
        max_length=100,
        verbose_name='Nombre (Español)',
        help_text='Nombre en español (ej: Italiana, Japonesa)'
    )
    name_en = models.CharField(
        max_length=100,
        verbose_name='Nombre (Inglés)',
        help_text='Nombre en inglés (ej: Italian, Japanese)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción del tipo de cocina'
    )
    keywords = models.JSONField(
        default=list,
        verbose_name='Palabras clave',
        help_text='Keywords para detección: ["italiano", "pasta", "pizza", "risotto"]'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se usará en extracción'
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Cocina'
        verbose_name_plural = 'Tipos de Cocina'
        ordering = ['display_order', 'name_es']

    def __str__(self):
        return f"{self.name_es} ({self.code})"
