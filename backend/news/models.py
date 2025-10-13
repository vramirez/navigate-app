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

    COUNTRIES = [
        ('CO', 'Colombia'),
        ('AD', 'Andorra'),
        ('AE', 'United Arab Emirates'),
        ('AF', 'Afghanistan'),
        ('AG', 'Antigua and Barbuda'),
        ('AI', 'Anguilla'),
        ('AL', 'Albania'),
        ('AM', 'Armenia'),
        ('AO', 'Angola'),
        ('AQ', 'Antarctica'),
        ('AR', 'Argentina'),
        ('AS', 'American Samoa'),
        ('AT', 'Austria'),
        ('AU', 'Australia'),
        ('AW', 'Aruba'),
        ('AX', 'Åland Islands'),
        ('AZ', 'Azerbaijan'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BB', 'Barbados'),
        ('BD', 'Bangladesh'),
        ('BE', 'Belgium'),
        ('BF', 'Burkina Faso'),
        ('BG', 'Bulgaria'),
        ('BH', 'Bahrain'),
        ('BI', 'Burundi'),
        ('BJ', 'Benin'),
        ('BL', 'Saint Barthélemy'),
        ('BM', 'Bermuda'),
        ('BN', 'Brunei Darussalam'),
        ('BO', 'Bolivia'),
        ('BQ', 'Bonaire, Sint Eustatius and Saba'),
        ('BR', 'Brazil'),
        ('BS', 'Bahamas'),
        ('BT', 'Bhutan'),
        ('BV', 'Bouvet Island'),
        ('BW', 'Botswana'),
        ('BY', 'Belarus'),
        ('BZ', 'Belize'),
        ('CA', 'Canada'),
        ('CC', 'Cocos (Keeling) Islands'),
        ('CD', 'Congo, The Democratic Republic of the'),
        ('CF', 'Central African Republic'),
        ('CG', 'Congo'),
        ('CH', 'Switzerland'),
        ('CI', 'Côte d\'Ivoire'),
        ('CK', 'Cook Islands'),
        ('CL', 'Chile'),
        ('CM', 'Cameroon'),
        ('CN', 'China'),
        ('CR', 'Costa Rica'),
        ('CU', 'Cuba'),
        ('CV', 'Cape Verde'),
        ('CW', 'Curaçao'),
        ('CX', 'Christmas Island'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DE', 'Germany'),
        ('DJ', 'Djibouti'),
        ('DK', 'Denmark'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('DZ', 'Algeria'),
        ('EC', 'Ecuador'),
        ('EE', 'Estonia'),
        ('EG', 'Egypt'),
        ('EH', 'Western Sahara'),
        ('ER', 'Eritrea'),
        ('ES', 'Spain'),
        ('ET', 'Ethiopia'),
        ('FI', 'Finland'),
        ('FJ', 'Fiji'),
        ('FK', 'Falkland Islands (Malvinas)'),
        ('FM', 'Micronesia, Federated States of'),
        ('FO', 'Faroe Islands'),
        ('FR', 'France'),
        ('GA', 'Gabon'),
        ('GB', 'United Kingdom'),
        ('GD', 'Grenada'),
        ('GE', 'Georgia'),
        ('GF', 'French Guiana'),
        ('GG', 'Guernsey'),
        ('GH', 'Ghana'),
        ('GI', 'Gibraltar'),
        ('GL', 'Greenland'),
        ('GM', 'Gambia'),
        ('GN', 'Guinea'),
        ('GP', 'Guadeloupe'),
        ('GQ', 'Equatorial Guinea'),
        ('GR', 'Greece'),
        ('GS', 'South Georgia and the South Sandwich Islands'),
        ('GT', 'Guatemala'),
        ('GU', 'Guam'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HK', 'Hong Kong'),
        ('HM', 'Heard Island and McDonald Islands'),
        ('HN', 'Honduras'),
        ('HR', 'Croatia'),
        ('HT', 'Haiti'),
        ('HU', 'Hungary'),
        ('ID', 'Indonesia'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IM', 'Isle of Man'),
        ('IN', 'India'),
        ('IO', 'British Indian Ocean Territory'),
        ('IQ', 'Iraq'),
        ('IR', 'Iran, Islamic Republic of'),
        ('IS', 'Iceland'),
        ('IT', 'Italy'),
        ('JE', 'Jersey'),
        ('JM', 'Jamaica'),
        ('JO', 'Jordan'),
        ('JP', 'Japan'),
        ('KE', 'Kenya'),
        ('KG', 'Kyrgyzstan'),
        ('KH', 'Cambodia'),
        ('KI', 'Kiribati'),
        ('KM', 'Comoros'),
        ('KN', 'Saint Kitts and Nevis'),
        ('KP', 'Korea, Democratic People\'s Republic of'),
        ('KR', 'Korea, Republic of'),
        ('KW', 'Kuwait'),
        ('KY', 'Cayman Islands'),
        ('KZ', 'Kazakhstan'),
        ('LA', 'Lao People\'s Democratic Republic'),
        ('LB', 'Lebanon'),
        ('LC', 'Saint Lucia'),
        ('LI', 'Liechtenstein'),
        ('LK', 'Sri Lanka'),
        ('LR', 'Liberia'),
        ('LS', 'Lesotho'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('LV', 'Latvia'),
        ('LY', 'Libya'),
        ('MA', 'Morocco'),
        ('MC', 'Monaco'),
        ('MD', 'Moldova, Republic of'),
        ('ME', 'Montenegro'),
        ('MF', 'Saint Martin (French part)'),
        ('MG', 'Madagascar'),
        ('MH', 'Marshall Islands'),
        ('MK', 'Macedonia, the former Yugoslav Republic of'),
        ('ML', 'Mali'),
        ('MM', 'Myanmar'),
        ('MN', 'Mongolia'),
        ('MO', 'Macao'),
        ('MP', 'Northern Mariana Islands'),
        ('MQ', 'Martinique'),
        ('MR', 'Mauritania'),
        ('MS', 'Montserrat'),
        ('MT', 'Malta'),
        ('MU', 'Mauritius'),
        ('MV', 'Maldives'),
        ('MW', 'Malawi'),
        ('MX', 'Mexico'),
        ('MY', 'Malaysia'),
        ('MZ', 'Mozambique'),
        ('NA', 'Namibia'),
        ('NC', 'New Caledonia'),
        ('NE', 'Niger'),
        ('NF', 'Norfolk Island'),
        ('NG', 'Nigeria'),
        ('NI', 'Nicaragua'),
        ('NL', 'Netherlands'),
        ('NO', 'Norway'),
        ('NP', 'Nepal'),
        ('NR', 'Nauru'),
        ('NU', 'Niue'),
        ('NZ', 'New Zealand'),
        ('OM', 'Oman'),
        ('PA', 'Panama'),
        ('PE', 'Peru'),
        ('PF', 'French Polynesia'),
        ('PG', 'Papua New Guinea'),
        ('PH', 'Philippines'),
        ('PK', 'Pakistan'),
        ('PL', 'Poland'),
        ('PM', 'Saint Pierre and Miquelon'),
        ('PN', 'Pitcairn'),
        ('PR', 'Puerto Rico'),
        ('PS', 'Palestine, State of'),
        ('PT', 'Portugal'),
        ('PW', 'Palau'),
        ('PY', 'Paraguay'),
        ('QA', 'Qatar'),
        ('RE', 'Réunion'),
        ('RO', 'Romania'),
        ('RS', 'Serbia'),
        ('RU', 'Russian Federation'),
        ('RW', 'Rwanda'),
        ('SA', 'Saudi Arabia'),
        ('SB', 'Solomon Islands'),
        ('SC', 'Seychelles'),
        ('SD', 'Sudan'),
        ('SE', 'Sweden'),
        ('SG', 'Singapore'),
        ('SH', 'Saint Helena, Ascension and Tristan da Cunha'),
        ('SI', 'Slovenia'),
        ('SJ', 'Svalbard and Jan Mayen'),
        ('SK', 'Slovakia'),
        ('SL', 'Sierra Leone'),
        ('SM', 'San Marino'),
        ('SN', 'Senegal'),
        ('SO', 'Somalia'),
        ('SR', 'Suriname'),
        ('SS', 'South Sudan'),
        ('ST', 'Sao Tome and Principe'),
        ('SV', 'El Salvador'),
        ('SX', 'Sint Maarten (Dutch part)'),
        ('SY', 'Syrian Arab Republic'),
        ('SZ', 'Swaziland'),
        ('TC', 'Turks and Caicos Islands'),
        ('TD', 'Chad'),
        ('TF', 'French Southern Territories'),
        ('TG', 'Togo'),
        ('TH', 'Thailand'),
        ('TJ', 'Tajikistan'),
        ('TK', 'Tokelau'),
        ('TL', 'Timor-Leste'),
        ('TM', 'Turkmenistan'),
        ('TN', 'Tunisia'),
        ('TO', 'Tonga'),
        ('TR', 'Turkey'),
        ('TT', 'Trinidad and Tobago'),
        ('TV', 'Tuvalu'),
        ('TW', 'Taiwan, Province of China'),
        ('TZ', 'Tanzania, United Republic of'),
        ('UA', 'Ukraine'),
        ('UG', 'Uganda'),
        ('UM', 'United States Minor Outlying Islands'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VA', 'Holy See (Vatican City State)'),
        ('VC', 'Saint Vincent and the Grenadines'),
        ('VE', 'Venezuela'),
        ('VG', 'Virgin Islands, British'),
        ('VI', 'Virgin Islands, U.S.'),
        ('VN', 'Viet Nam'),
        ('VU', 'Vanuatu'),
        ('WF', 'Wallis and Futuna'),
        ('WS', 'Samoa'),
        ('YE', 'Yemen'),
        ('YT', 'Mayotte'),
        ('ZA', 'South Africa'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe'),
    ]

    CRAWL_STATUS_CHOICES = [
        ('unknown', 'No probado'),
        ('rss_available', 'RSS disponible'),
        ('manual_crawlable', 'Crawling manual funciona'),
        ('spa_detected', 'SPA/JavaScript detectado'),
        ('uncrawlable', 'No se puede rastrear'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nombre del medio')
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        verbose_name='Tipo de fuente'
    )
    country = models.CharField(
        max_length=2,
        choices=COUNTRIES,
        default='CO',
        verbose_name='País'
    )
    website_url = models.URLField(blank=True, verbose_name='Sitio web')
    rss_url = models.URLField(blank=True, verbose_name='URL del RSS')
    api_endpoint = models.URLField(blank=True, verbose_name='Endpoint API')

    # Crawler configuration
    crawler_url = models.URLField(
        blank=True,
        verbose_name='URL para crawling',
        help_text='URL principal del sitio web para rastreo automático'
    )
    rss_discovered = models.BooleanField(
        default=False,
        verbose_name='RSS auto-descubierto'
    )
    discovered_rss_url = models.URLField(
        blank=True,
        verbose_name='URL RSS descubierta'
    )
    manual_crawl_enabled = models.BooleanField(
        default=False,
        verbose_name='Crawling manual habilitado',
        help_text='Para sitios sin RSS disponible'
    )
    crawl_sections = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Secciones detectadas',
        help_text='Secciones del sitio web descubiertas para crawling'
    )

    # Crawlability status and retry management
    crawl_status = models.CharField(
        max_length=20,
        choices=CRAWL_STATUS_CHOICES,
        default='unknown',
        verbose_name='Estado de rastreo',
        help_text='Indica si el sitio puede ser rastreado y cómo'
    )
    last_crawl_attempt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último intento de rastreo'
    )
    crawl_retry_after = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Reintentar después de',
        help_text='Fecha/hora cuando se puede intentar rastrear nuevamente'
    )
    failed_crawl_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Conteo de fallos consecutivos'
    )

    # Legacy scraping configuration (keep for backwards compatibility)
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
        ordering = ['country', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_country_display()})"

    def save(self, *args, **kwargs):
        if self.website_url and not self.crawler_url:
            self.crawler_url = self.website_url
        super().save(*args, **kwargs)

class CrawlHistory(models.Model):
    """Track crawling history for news sources"""
    STATUS_CHOICES = [
        ('success', 'Exitoso'),
        ('failed', 'Fallido'),
        ('partial', 'Parcial'),
    ]

    source = models.ForeignKey(
        NewsSource,
        on_delete=models.CASCADE,
        related_name='crawl_history',
        verbose_name='Fuente'
    )
    crawl_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de crawling'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Estado'
    )
    articles_found = models.PositiveIntegerField(
        default=0,
        verbose_name='Artículos encontrados'
    )
    articles_saved = models.PositiveIntegerField(
        default=0,
        verbose_name='Artículos guardados'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de error'
    )
    crawl_duration = models.DurationField(
        null=True,
        blank=True,
        verbose_name='Duración del crawling'
    )
    crawl_type = models.CharField(
        max_length=10,
        choices=[('rss', 'RSS'), ('manual', 'Manual')],
        default='rss',
        verbose_name='Tipo de crawling'
    )

    class Meta:
        verbose_name = 'Historial de crawling'
        verbose_name_plural = 'Historial de crawling'
        ordering = ['-crawl_date']

    def __str__(self):
        return f"{self.source.name} - {self.get_status_display()} ({self.crawl_date.strftime('%Y-%m-%d %H:%M')})"

class NewsArticle(models.Model):
    """Individual news articles from various sources"""
    # Legacy event types (kept for backwards compatibility)
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

    # Public categories (displayed to users)
    CATEGORY_CHOICES = [
        ('eventos', 'Eventos'),
        ('gastronomia', 'Gastronomía'),
        ('infraestructura', 'Infraestructura'),
        ('clima-alertas', 'Clima y Alertas'),
        ('turismo', 'Turismo'),
        ('economia', 'Economía'),
        ('regulaciones', 'Regulaciones'),
        ('educacion', 'Educación'),
        ('comunidad', 'Comunidad'),
        ('seguridad', 'Seguridad'),
    ]

    # Private subcategories (for ML classification)
    SUBCATEGORY_CHOICES = [
        # Eventos
        ('conciertos', 'Conciertos'),
        ('festivales', 'Festivales'),
        ('deportes', 'Deportes'),
        ('teatro-cultura', 'Teatro y Cultura'),
        ('ferias', 'Ferias'),
        # Gastronomía
        ('tendencias-gastronomicas', 'Tendencias Gastronómicas'),
        ('bebidas', 'Bebidas'),
        ('competencias-culinarias', 'Competencias Culinarias'),
        ('apertura-cierre', 'Apertura/Cierre'),
        ('productos-nuevos', 'Productos Nuevos'),
        # Infraestructura
        ('obras-viales', 'Obras Viales'),
        ('transporte-publico', 'Transporte Público'),
        ('desarrollo-urbano', 'Desarrollo Urbano'),
        ('servicios-publicos', 'Servicios Públicos'),
        # Clima y Alertas
        ('clima-extremo', 'Clima Extremo'),
        ('alertas-emergencia', 'Alertas de Emergencia'),
        ('desastres-naturales', 'Desastres Naturales'),
        # Turismo
        ('estadisticas-turismo', 'Estadísticas de Turismo'),
        ('feriados-puentes', 'Feriados y Puentes'),
        ('temporada-alta-baja', 'Temporada Alta/Baja'),
        ('turismo-internacional', 'Turismo Internacional'),
        # Economía
        ('tendencias-consumo', 'Tendencias de Consumo'),
        ('inflacion-precios', 'Inflación y Precios'),
        ('empleo', 'Empleo'),
        ('poder-adquisitivo', 'Poder Adquisitivo'),
        # Regulaciones
        ('leyes-nuevas', 'Leyes Nuevas'),
        ('permisos-licencias', 'Permisos y Licencias'),
        ('salud-publica', 'Salud Pública'),
        ('impuestos', 'Impuestos'),
        ('horarios-restricciones', 'Horarios y Restricciones'),
        # Educación
        ('universidades', 'Universidades'),
        ('colegios', 'Colegios'),
        ('inicio-fin-semestre', 'Inicio/Fin de Semestre'),
        # Comunidad
        ('eventos-barriales', 'Eventos Barriales'),
        ('mercados-ferias', 'Mercados y Ferias'),
        ('tendencias-sociales', 'Tendencias Sociales'),
        ('celebraciones-locales', 'Celebraciones Locales'),
        # Seguridad
        ('seguridad-publica', 'Seguridad Pública'),
        ('zonas-riesgo', 'Zonas de Riesgo'),
        ('operativos-policiales', 'Operativos Policiales'),
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
    crawl_section = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Sección de crawling',
        help_text='Sección específica del sitio web desde donde se extrajo el artículo'
    )
    
    # ML processing results
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        null=True,
        blank=True,
        verbose_name='Tipo de evento detectado (legacy)'
    )

    # New category system
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        verbose_name='Categoría pública',
        help_text='Categoría principal visible para el usuario'
    )
    subcategory = models.CharField(
        max_length=50,
        choices=SUBCATEGORY_CHOICES,
        null=True,
        blank=True,
        verbose_name='Subcategoría privada',
        help_text='Subcategoría detallada para clasificación ML'
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
        default=-1.0,
        verbose_name='Puntuación de relevancia comercial',
        help_text='-1.0 = no procesado, 0.0+ = procesado con score de relevancia'
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

    # ML Feature Extraction fields (Phase 3 - task-4)
    # Event type detection (detailed classification)
    event_type_detected = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo de evento detectado (ML)',
        help_text='sports_match, concert, festival, marathon, conference, etc.'
    )
    event_subtype = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Subtipo de evento',
        help_text='football match, rock concert, food festival, etc.'
    )

    # Geographic features
    primary_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ciudad principal',
        help_text='Ciudad donde ocurre el evento o noticia'
    )
    neighborhood = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Barrio/Localidad',
        help_text='Barrio específico (El Poblado, Laureles, etc.)'
    )
    venue_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre del lugar',
        help_text='Nombre del venue/estadio/teatro donde ocurre'
    )
    venue_address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Dirección del lugar'
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Latitud',
        help_text='Coordenada geográfica'
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Longitud',
        help_text='Coordenada geográfica'
    )

    # Temporal features
    event_start_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha/hora de inicio del evento',
        help_text='Fecha y hora específica de inicio'
    )
    event_end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha/hora de fin del evento',
        help_text='Fecha y hora específica de fin'
    )
    event_duration_hours = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Duración del evento (horas)'
    )

    # Scale features
    expected_attendance = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Asistencia esperada',
        help_text='Número estimado de asistentes'
    )
    event_scale = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('small', 'Pequeño (<500)'),
            ('medium', 'Mediano (500-5000)'),
            ('large', 'Grande (5000-50000)'),
            ('massive', 'Masivo (>50000)'),
        ],
        verbose_name='Escala del evento'
    )

    # Pre-filtering scores
    business_suitability_score = models.FloatField(
        default=0.0,
        verbose_name='Puntuación de idoneidad para negocios',
        help_text='0.0-1.0: Qué tan relevante es para CUALQUIER negocio de hostelería'
    )
    urgency_score = models.FloatField(
        default=0.0,
        verbose_name='Puntuación de urgencia',
        help_text='0.0-1.0: Qué tan urgente es actuar sobre esta noticia'
    )

    # Feature extraction metadata
    features_extracted = models.BooleanField(
        default=False,
        verbose_name='Features extraídas',
        help_text='Indica si las features ML ya fueron extraídas'
    )
    feature_extraction_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de extracción de features'
    )
    feature_extraction_confidence = models.FloatField(
        default=0.0,
        verbose_name='Confianza de extracción',
        help_text='0.0-1.0: Nivel de confianza en las features extraídas'
    )

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

    def save(self, *args, **kwargs):
        """Prevent modification of crawler-generated fields after creation"""
        # Fields that cannot be modified after creation (data integrity)
        protected_fields = [
            'source_id', 'title', 'content', 'url', 'author',
            'published_date', 'section', 'crawl_section'
        ]

        # If this is an update (not a new object)
        if self.pk:
            try:
                existing = NewsArticle.objects.get(pk=self.pk)

                # Check if any protected field was modified
                for field in protected_fields:
                    old_value = getattr(existing, field)
                    new_value = getattr(self, field)

                    # Restore original value if it was changed
                    if old_value != new_value:
                        setattr(self, field, old_value)

            except NewsArticle.DoesNotExist:
                pass  # New object, allow all fields

        super().save(*args, **kwargs)

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