#!/bin/bash

# NaviGate Mock Data Creation Script
# This script creates sample news articles and recommendations for demo

set -e

echo "📰 Creating Mock News and Recommendations..."
echo "==========================================="

# Check if containers are running
if ! docker compose -f docker/docker-compose.dev.yml ps | grep -q "Up"; then
    echo "❌ Error: Containers are not running. Please run ./start-server.sh first."
    exit 1
fi

echo "📰 Creating sample news articles..."
docker compose -f docker/docker-compose.dev.yml exec backend python manage.py shell << 'EOF'
from news.models import NewsSource, NewsArticle
from businesses.models import Business
from recommendations.models import Recommendation, RecommendationTemplate
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
import json

# Get news source
el_tiempo = NewsSource.objects.filter(name='El Tiempo').first()
if not el_tiempo:
    print("❌ News source 'El Tiempo' not found. Run setup-admin.sh first.")
    exit()

# Sample news articles for the 6 mock scenarios
news_articles_data = [
    {
        'title': 'Medellín se prepara para el Maratón Internacional 2025 con más de 15,000 participantes',
        'content': '''La capital antioqueña se alista para recibir el próximo 15 de octubre el Maratón Internacional de Medellín 2025, uno de los eventos deportivos más importantes del país. Se esperan más de 15,000 corredores nacionales e internacionales.

El evento incluirá tres modalidades: maratón completo (42K), media maratón (21K) y carrera recreativa (10K). La largada será desde el Estadio Atanasio Girardot a las 6:00 AM y el recorrido pasará por las principales avenidas de El Poblado, Envigado y Sabaneta.

"Esperamos un gran impacto económico en la ciudad, especialmente en el sector hotelero y gastronómico", afirmó el alcalde de Medellín. Los restaurantes y cafeterías de la zona esperan incrementar sus ventas en un 200% durante el fin de semana del evento.

Las autoridades recomiendan a los establecimientos comerciales prepararse con inventario adicional, especialmente bebidas isotónicas, agua, frutas y comida rápida para los participantes y espectadores.''',
        'url': 'https://www.eltiempo.com/deportes/maraton-medellin-2025',
        'published_date': timezone.now() + timedelta(days=30),
        'section': 'Deportes',
        'event_type': 'sports',
        'event_date': timezone.now() + timedelta(days=30),
        'event_location': 'Medellín, El Poblado',
        'business_relevance_score': 0.95,
        'extracted_keywords': ['maratón', 'deportes', 'corredores', 'Medellín', 'El Poblado', 'restaurantes', 'cafeterías', 'bebidas', 'comida'],
        'sentiment_score': 0.8,
        'is_processed': True
    },
    {
        'title': 'Festival Gastronómico Internacional llega a Bogotá con 200 restaurantes participantes',
        'content': '''Del 20 al 25 de noviembre, la Zona Rosa de Bogotá será el epicentro del Festival Gastronómico Internacional, el evento culinario más grande del país con la participación de 200 restaurantes.

El festival incluirá cenas especiales, talleres de cocina, degustaciones y competencias entre chefs. Se esperan más de 50,000 visitantes durante los cinco días del evento, lo que representa una oportunidad única para los establecimientos gastronómicos de la capital.

"Los restaurantes participantes podrán mostrar sus especialidades a un público muy amplio", explicó la directora del evento. Se estima que las ventas de los restaurantes de la zona aumenten entre 150% y 300% durante el festival.

Los organizadores recomiendan a los establecimientos preparar menús especiales, contratar personal adicional y aumentar significativamente su inventario de ingredientes frescos y bebidas.''',
        'url': 'https://www.eltiempo.com/gastronomia/festival-bogota-2025',
        'published_date': timezone.now() + timedelta(days=45),
        'section': 'Gastronomía',
        'event_type': 'gastronomy',
        'event_date': timezone.now() + timedelta(days=45),
        'event_location': 'Bogotá, Zona Rosa',
        'business_relevance_score': 0.98,
        'extracted_keywords': ['festival', 'gastronomía', 'restaurantes', 'Bogotá', 'chefs', 'cocina', 'menús', 'ingredientes'],
        'sentiment_score': 0.9,
        'is_processed': True
    },
    {
        'title': 'Colombia clasifica a la final de la Copa América: el partido decisivo contra Brasil',
        'content': '''La Selección Colombia logró clasificar a la final de la Copa América 2025 y enfrentará a Brasil el próximo 10 de diciembre en el Estadio Metropolitano de Barranquilla, en lo que promete ser el partido del siglo.

Las autoridades esperan que más de 50,000 hinchas llenen el estadio, mientras que millones de colombianos seguirán el partido desde bares, restaurantes y espacios públicos en todo el país.

"Este es el momento que todos esperábamos. Colombia tiene la oportunidad histórica de ganar su primera Copa América en casa", declaró el técnico de la selección.

Los bares y restaurantes de Barranquilla, y especialmente los de otras ciudades, se preparan para recibir multitudes. Se recomienda a los establecimientos preparar promociones especiales, aumentar el stock de cerveza y bebidas, y considerar la instalación de pantallas adicionales.

El partido comenzará a las 8:00 PM hora colombiana y se espera que la celebración se extienda hasta altas horas de la madrugada.''',
        'url': 'https://www.eltiempo.com/deportes/copa-america-colombia-brasil',
        'published_date': timezone.now() + timedelta(days=60),
        'section': 'Deportes',
        'event_type': 'sports',
        'event_date': timezone.now() + timedelta(days=60),
        'event_location': 'Barranquilla, Nacional',
        'business_relevance_score': 0.92,
        'extracted_keywords': ['fútbol', 'Copa América', 'Colombia', 'Brasil', 'final', 'bares', 'restaurantes', 'cerveza', 'celebración'],
        'sentiment_score': 0.95,
        'is_processed': True
    }
]

for article_data in news_articles_data:
    article, created = NewsArticle.objects.get_or_create(
        url=article_data['url'],
        defaults={**article_data, 'source': el_tiempo}
    )
    if created:
        print(f"✅ Created news article: {article.title[:50]}...")
    else:
        print(f"ℹ️  News article already exists: {article.title[:50]}...")

print("✅ Sample news articles created")
EOF

echo "💡 Creating sample recommendations..."
docker compose -f docker/docker-compose.dev.yml exec backend python manage.py shell << 'EOF'
from recommendations.models import Recommendation
from businesses.models import Business
from news.models import NewsArticle
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
import json

# Get the business
pub = Business.objects.filter(name='Irish Pub Medellín').first()
if not pub:
    print("❌ Business 'Irish Pub Medellín' not found.")
    exit()

# Get news articles
marathon_article = NewsArticle.objects.filter(title__icontains='Maratón').first()
soccer_article = NewsArticle.objects.filter(title__icontains='Copa América').first()

recommendations_data = []

if marathon_article:
    recommendations_data.append({
        'business': pub,
        'content_object': marathon_article,
        'title': 'Estrategia de Inventario para Evento Deportivo (ALTA)',
        'description': '''El Maratón Internacional de Medellín 2025 traerá más de 15,000 corredores y miles de espectadores al área de El Poblado. 

ACCIONES RECOMENDADAS:
• Aumentar inventario de bebidas isotónicas en 200%
• Incrementar stock de agua embotellada en 300%  
• Preparar menú especial con opciones saludables y energéticas
• Considerar desayunos especiales para corredores (5:00-7:00 AM)
• Aumentar stock de cervezas para la celebración post-evento

TIMING: El evento es el 15 de octubre. Implementar cambios 1 semana antes.''',
        'category': 'inventory',
        'action_type': 'increase_inventory',
        'priority': 'high',
        'confidence_score': 0.92,
        'impact_score': 0.85,
        'effort_score': 0.4,
        'recommended_start_date': timezone.now() + timedelta(days=23),
        'recommended_end_date': timezone.now() + timedelta(days=32),
        'estimated_duration_hours': 8,
        'reasoning': 'Evento deportivo masivo en zona cercana al negocio. Histórico incremento de ventas del 150-200% en eventos similares.',
        'resources_needed': ['Personal adicional para compras', 'Espacio extra de almacenamiento', 'Presupuesto adicional para inventario'],
        'expected_outcomes': 'Incremento estimado de ventas del 180-220% durante el fin de semana del evento.'
    })

if soccer_article:
    recommendations_data.append({
        'business': pub,
        'content_object': soccer_article,
        'title': 'Campaña Especial Copa América: Colombia vs Brasil (URGENTE)',
        'description': '''¡OPORTUNIDAD HISTÓRICA! Final de Copa América Colombia vs Brasil - El partido más importante en años.

ACCIONES INMEDIATAS REQUERIDAS:
• Crear promoción especial "Final Copa América" 
• Aumentar stock de cerveza en 400% (especialmente marcas nacionales)
• Instalar pantallas adicionales para mayor capacidad
• Preparar decoración temática Colombia
• Menú especial con comida típica colombiana
• Contratar personal adicional para el día del partido

PROMOCIÓN SUGERIDA: "2x1 en cervezas nacionales durante el partido"
HORARIO EXTENDIDO: Abrir desde las 6:00 PM hasta 2:00 AM

TIMING CRÍTICO: Partido el 10 de diciembre a las 8:00 PM. ¡Implementar YA!''',
        'category': 'marketing',
        'action_type': 'create_promotion',
        'priority': 'urgent',
        'confidence_score': 0.98,
        'impact_score': 0.95,
        'effort_score': 0.6,
        'recommended_start_date': timezone.now() + timedelta(days=1),
        'recommended_end_date': timezone.now() + timedelta(days=62),
        'estimated_duration_hours': 20,
        'reasoning': 'Final histórica de Copa América en Colombia. Los pubs/bares experimentan incrementos de 300-500% en ventas durante finales de fútbol.',
        'resources_needed': ['Pantallas adicionales', 'Personal extra', 'Decoración temática', 'Stock masivo de cerveza', 'Marketing/publicidad'],
        'expected_outcomes': 'Incremento proyectado de ventas del 400-600%. Posibilidad de récord histórico de ventas en un solo día.'
    })

# Add a third recommendation for staffing
recommendations_data.append({
    'business': pub,
    'content_object': marathon_article if marathon_article else None,
    'title': 'Contratación Personal Temporal para Eventos (MEDIA)',
    'description': '''Con los próximos eventos deportivos y festivales, se recomienda fortalecer el equipo de trabajo temporalmente.

NECESIDADES IDENTIFICADAS:
• 2 meseros adicionales para fines de semana de eventos
• 1 bartender extra para horarios pico
• 1 persona de seguridad/control de acceso
• Personal de limpieza adicional

PERFIL REQUERIDO:
• Experiencia mínima 6 meses en sector gastronómico
• Disponibilidad fines de semana
• Manejo básico de inglés (clientela internacional)

PROCESO SUGERIDO:
1. Publicar vacantes esta semana
2. Entrevistas la próxima semana  
3. Inducción 1 semana antes del primer evento

COSTO ESTIMADO: $2,400,000 COP/mes por todo el personal adicional''',
    'category': 'staffing',
    'action_type': 'hire_staff',
    'priority': 'medium',
    'confidence_score': 0.78,
    'impact_score': 0.70,
    'effort_score': 0.7,
    'recommended_start_date': timezone.now() + timedelta(days=7),
    'recommended_end_date': timezone.now() + timedelta(days=21),
    'estimated_duration_hours': 15,
    'reasoning': 'Eventos masivos requieren personal adicional para mantener calidad del servicio y maximizar ingresos.',
    'resources_needed': ['Presupuesto para salarios', 'Tiempo para reclutamiento', 'Uniformes adicionales'],
    'expected_outcomes': 'Mejora en calidad del servicio, mayor capacidad de atención, reducción de tiempos de espera.'
})

# Create recommendations
for rec_data in recommendations_data:
    content_object = rec_data.pop('content_object', None)
    
    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        rec_data['content_type'] = content_type
        rec_data['object_id'] = content_object.id
    
    rec, created = Recommendation.objects.get_or_create(
        business=rec_data['business'],
        title=rec_data['title'],
        defaults=rec_data
    )
    
    if created:
        print(f"✅ Created recommendation: {rec.title}")
    else:
        print(f"ℹ️  Recommendation already exists: {rec.title}")

print("✅ Sample recommendations created")
print(f"📊 Total recommendations for {pub.name}: {pub.recommendations.count()}")
EOF

echo ""
echo "🎉 Mock Data Creation Completed!"
echo "==============================="
echo ""
echo "✅ Created:"
echo "   • Sample news articles (3)"
echo "   • Business recommendations (3)"
echo "   • Linked recommendations to news sources"
echo ""
echo "🎯 Ready to test the complete flow:"
echo ""
echo "1️⃣  ADMIN VIEW (Django Admin):"
echo "   • URL: http://localhost:8000/admin"
echo "   • Username: admin / Password: admin123"
echo "   • Check: News Articles, Recommendations, Businesses"
echo ""
echo "2️⃣  CLIENT VIEW (React App):"
echo "   • URL: http://localhost:3001"
echo "   • Use any email/password (mock auth)"
echo "   • Dashboard shows statistics"
echo "   • Navigate through all sections"
echo ""
echo "📱 Test Features:"
echo "   • Language switching (Spanish ↔ English)"
echo "   • Mobile responsive design"
echo "   • PWA functionality"
echo "   • Navigation between pages"