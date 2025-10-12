from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Business(models.Model):
    BUSINESS_TYPES = [
        ('coffee_shop', 'Cafetería'),
        ('restaurant', 'Restaurante'),
        ('pub', 'Pub/Bar'),
        ('bookstore', 'Librería'),
    ]
    
    CITIES = [
        ('medellin', 'Medellín'),
        ('bogota', 'Bogotá'),
        ('cartagena', 'Cartagena'),
        ('barranquilla', 'Barranquilla'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=200, verbose_name='Nombre del negocio')
    business_type = models.CharField(
        max_length=50, 
        choices=BUSINESS_TYPES,
        verbose_name='Tipo de negocio'
    )
    city = models.CharField(
        max_length=50, 
        choices=CITIES,
        verbose_name='Ciudad'
    )
    address = models.TextField(blank=True, verbose_name='Dirección')

    # Geographic data for ML matching (task-4)
    neighborhood = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Barrio/Localidad',
        help_text='Barrio específico (El Poblado, Laureles, Chapinero, etc.)'
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Latitud',
        help_text='Coordenada geográfica para matching basado en distancia'
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Longitud',
        help_text='Coordenada geográfica para matching basado en distancia'
    )

    # Geographic matching preferences
    geographic_radius_km = models.FloatField(
        default=5.0,
        verbose_name='Radio geográfico (km)',
        help_text='Mostrar noticias dentro de este radio (kilómetros)'
    )
    include_citywide_events = models.BooleanField(
        default=True,
        verbose_name='Incluir eventos a nivel ciudad',
        help_text='Mostrar eventos grandes que afectan toda la ciudad'
    )
    include_national_events = models.BooleanField(
        default=False,
        verbose_name='Incluir eventos nacionales',
        help_text='Mostrar eventos masivos de nivel nacional (Copa América, etc.)'
    )

    description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Descripción del negocio'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, verbose_name='Email')
    website = models.URLField(blank=True, verbose_name='Sitio web')
    
    # Business preferences for recommendations
    target_audience = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='Público objetivo',
        help_text='Ej: Estudiantes universitarios, profesionales, familias'
    )
    operating_hours_start = models.TimeField(
        null=True, 
        blank=True,
        verbose_name='Hora de apertura'
    )
    operating_hours_end = models.TimeField(
        null=True, 
        blank=True,
        verbose_name='Hora de cierre'
    )
    capacity = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name='Capacidad máxima'
    )
    staff_count = models.PositiveIntegerField(
        default=1,
        verbose_name='Número de empleados'
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Recibir notificaciones por email'
    )
    recommendation_frequency = models.CharField(
        max_length=20,
        choices=[
            ('real_time', 'Tiempo real'),
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
        ],
        default='daily',
        verbose_name='Frecuencia de recomendaciones'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.get_city_display()}"
        
    def get_business_type_display_spanish(self):
        """Return business type in Spanish"""
        type_map = dict(self.BUSINESS_TYPES)
        return type_map.get(self.business_type, self.business_type)

class BusinessKeywords(models.Model):
    """Keywords that are relevant to a specific business for news filtering"""
    business = models.ForeignKey(
        Business, 
        on_delete=models.CASCADE,
        related_name='keywords'
    )
    keyword = models.CharField(max_length=100, verbose_name='Palabra clave')
    weight = models.FloatField(
        default=1.0,
        verbose_name='Peso',
        help_text='Importancia de esta palabra clave (0.1 - 2.0)'
    )
    is_negative = models.BooleanField(
        default=False,
        verbose_name='Es negativa',
        help_text='Excluir noticias que contengan esta palabra'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Palabra clave del negocio'
        verbose_name_plural = 'Palabras clave del negocio'
        unique_together = ['business', 'keyword']
        
    def __str__(self):
        negative = " (negativa)" if self.is_negative else ""
        return f"{self.business.name}: {self.keyword}{negative}"

class AdminUser(models.Model):
    """Extended admin user for managing news sources and customer accounts"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_manage_news_sources = models.BooleanField(default=False)
    can_create_businesses = models.BooleanField(default=True)
    city_access = models.CharField(
        max_length=200,
        blank=True,
        help_text='Ciudades que puede administrar (separadas por comas)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Usuario administrador'
        verbose_name_plural = 'Usuarios administradores'
        
    def __str__(self):
        return f"Admin: {self.user.username}"