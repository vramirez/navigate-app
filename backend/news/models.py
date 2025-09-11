from django.db import models
from django.contrib.auth.models import User
import json

class NewsSource(models.Model):
    """Newspaper and media source management"""
    SOURCE_TYPES = [
        ('newspaper', 'Periódico'),
        ('online', 'Medio digital'),
        ('social_media', 'Redes sociales'),
        ('rss', 'Feed RSS'),
        ('manual', 'Entrada manual'),
    ]
    
    CITIES = [
        ('nacional', 'Nacional'),
        ('medellin', 'Medellín'),
        ('bogota', 'Bogotá'),
        ('cartagena', 'Cartagena'),
        ('barranquilla', 'Barranquilla'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre del medio')
    source_type = models.CharField(
        max_length=20, 
        choices=SOURCE_TYPES,
        verbose_name='Tipo de fuente'
    )
    city = models.CharField(
        max_length=50, 
        choices=CITIES,
        verbose_name='Ciudad/Cobertura'
    )
    website_url = models.URLField(blank=True, verbose_name='Sitio web')
    rss_url = models.URLField(blank=True, verbose_name='URL del RSS')
    api_endpoint = models.URLField(blank=True, verbose_name='Endpoint API')
    
    # Scraping configuration
    scraping_enabled = models.BooleanField(default=False, verbose_name='Scraping habilitado')
    css_selectors = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Selectores CSS',
        help_text='JSON con selectores para título, contenido, fecha, etc.'
    )
    
    # Status and metadata
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    reliability_score = models.FloatField(
        default=1.0, 
        verbose_name='Puntuación de confiabilidad'
    )
    fetch_frequency_hours = models.PositiveIntegerField(
        default=6,
        verbose_name='Frecuencia de actualización (horas)'
    )
    last_fetched = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fuente de noticias'
        verbose_name_plural = 'Fuentes de noticias'
        ordering = ['city', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.get_city_display()})"

class NewsArticle(models.Model):
    """Individual news articles from various sources"""
    EVENT_TYPES = [
        ('sports', 'Deportes'),
        ('cultural', 'Cultural'),
        ('gastronomy', 'Gastronomía'),
        ('education', 'Educación'),
        ('business', 'Negocios'),
        ('entertainment', 'Entretenimiento'),
        ('tourism', 'Turismo'),
        ('construction', 'Construcción'),
        ('transportation', 'Transporte'),
        ('weather', 'Clima'),
        ('government', 'Gobierno'),
        ('other', 'Otro'),
    ]
    
    source = models.ForeignKey(
        NewsSource, 
        on_delete=models.CASCADE,
        related_name='articles'
    )
    title = models.CharField(max_length=300, verbose_name='Título')
    content = models.TextField(verbose_name='Contenido')
    url = models.URLField(unique=True, verbose_name='URL original')
    
    # Article metadata
    author = models.CharField(max_length=200, blank=True, verbose_name='Autor')
    published_date = models.DateTimeField(verbose_name='Fecha de publicación')
    section = models.CharField(max_length=100, blank=True, verbose_name='Sección')
    
    # ML processing results
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        null=True,
        blank=True,
        verbose_name='Tipo de evento detectado'
    )
    event_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha del evento detectada'
    )
    event_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ubicación del evento'
    )
    business_relevance_score = models.FloatField(
        default=0.0,
        verbose_name='Puntuación de relevancia comercial'
    )
    
    # Keywords and entities extracted
    extracted_keywords = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Palabras clave extraídas'
    )
    entities = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Entidades detectadas'
    )
    sentiment_score = models.FloatField(
        default=0.0,
        verbose_name='Puntuación de sentimiento (-1 a 1)'
    )
    
    # Processing status
    is_processed = models.BooleanField(default=False, verbose_name='Procesado por ML')
    processing_error = models.TextField(blank=True, verbose_name='Error de procesamiento')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Artículo de noticias'
        verbose_name_plural = 'Artículos de noticias'
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['published_date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['business_relevance_score']),
            models.Index(fields=['is_processed']),
        ]
        
    def __str__(self):
        return f"{self.title} - {self.source.name}"
        
    def get_keywords_list(self):
        """Return keywords as a list"""
        if isinstance(self.extracted_keywords, str):
            try:
                return json.loads(self.extracted_keywords)
            except json.JSONDecodeError:
                return []
        return self.extracted_keywords or []

class SocialMediaPost(models.Model):
    """Social media posts from various platforms"""
    PLATFORMS = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
    ]
    
    platform = models.CharField(
        max_length=20, 
        choices=PLATFORMS,
        verbose_name='Plataforma'
    )
    post_id = models.CharField(
        max_length=200, 
        unique=True,
        verbose_name='ID de la publicación'
    )
    account_name = models.CharField(max_length=100, verbose_name='Cuenta')
    account_url = models.URLField(blank=True, verbose_name='URL de la cuenta')
    
    # Post content
    text_content = models.TextField(verbose_name='Contenido de texto')
    media_urls = models.JSONField(
        default=list,
        blank=True,
        verbose_name='URLs de medios'
    )
    post_url = models.URLField(verbose_name='URL de la publicación')
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0, verbose_name='Likes')
    shares_count = models.PositiveIntegerField(default=0, verbose_name='Compartidos')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='Comentarios')
    
    # Location and timing
    location = models.CharField(max_length=200, blank=True, verbose_name='Ubicación')
    posted_date = models.DateTimeField(verbose_name='Fecha de publicación')
    
    # ML processing results
    business_relevance_score = models.FloatField(
        default=0.0,
        verbose_name='Puntuación de relevancia comercial'
    )
    extracted_keywords = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Palabras clave extraídas'
    )
    sentiment_score = models.FloatField(
        default=0.0,
        verbose_name='Puntuación de sentimiento'
    )
    
    # Processing status
    is_processed = models.BooleanField(default=False, verbose_name='Procesado')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Publicación en redes sociales'
        verbose_name_plural = 'Publicaciones en redes sociales'
        ordering = ['-posted_date']
        
    def __str__(self):
        return f"{self.platform}: {self.account_name} - {self.text_content[:50]}..."

class ManualNewsEntry(models.Model):
    """Manually entered news by admin users"""
    entered_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Ingresado por'
    )
    title = models.CharField(max_length=300, verbose_name='Título')
    content = models.TextField(verbose_name='Contenido')
    event_type = models.CharField(
        max_length=20,
        choices=NewsArticle.EVENT_TYPES,
        verbose_name='Tipo de evento'
    )
    event_date = models.DateTimeField(verbose_name='Fecha del evento')
    location = models.CharField(max_length=200, verbose_name='Ubicación')
    source_notes = models.TextField(
        blank=True,
        verbose_name='Notas sobre la fuente'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Noticia manual'
        verbose_name_plural = 'Noticias manuales'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Manual: {self.title}"