#!/bin/bash

# NaviGate First-Time Setup Script
# This script performs a complete reset and setup of the NaviGate application
# Can be run multiple times safely - it resets everything each time

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for mock data flag
MOCK_DATA=false
if [[ "$1" == "--mock" ]]; then
    MOCK_DATA=true
fi

echo -e "${BLUE}🚀 NaviGate First-Time Setup${NC}"
echo "================================="
if [[ "$MOCK_DATA" == "true" ]]; then
    echo -e "${YELLOW}🎭 Mock data mode enabled${NC}"
fi
echo ""

# Function for colored output
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker first."
fi

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
    log_error "docker compose is not installed."
fi

echo -e "${YELLOW}⚠️  WARNING: This will completely reset the NaviGate application!${NC}"
echo "   • All containers will be stopped and removed"
echo "   • All data will be deleted (database, volumes)"  
echo "   • All migrations will be regenerated"
echo "   • Everything will be rebuilt from scratch"
echo ""
echo -e "${BLUE}Do you want to continue? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
log_info "Starting complete reset and setup..."

# Phase 1: Complete Reset
log_info "Phase 1: Resetting environment..."

# Stop and remove all containers, networks, volumes
log_info "Stopping and removing all containers..."
docker compose -f docker/docker-compose.dev.yml down --remove-orphans --volumes || true

# Remove any orphaned containers
log_info "Cleaning up any orphaned containers..."
docker container prune -f || true
docker volume prune -f || true
docker network prune -f || true

# Clean up database file if it exists
if [[ -f backend/db.sqlite3 ]]; then
    log_info "Removing existing database..."
    rm -f backend/db.sqlite3
fi

# Remove existing migrations from custom apps
log_info "Removing existing migrations..."
find backend/ -path "*/migrations/*.py" -not -name "__init__.py" -delete || true
find backend/ -path "*/migrations/__pycache__" -type d -exec rm -rf {} + || true

log_success "Environment reset complete"

# Phase 2: Build and Start Services
log_info "Phase 2: Building and starting services..."

# Build and start all services
log_info "Building Docker containers..."
docker compose -f docker/docker-compose.dev.yml build

log_info "Starting services..."
docker compose -f docker/docker-compose.dev.yml up -d

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
sleep 10

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local has_health_endpoint=${3:-false}
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if [ "$has_health_endpoint" = "true" ] && curl -f -s "http://localhost:$port/health/" > /dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        elif nc -z localhost $port > /dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Wait for services
wait_for_service "Backend API" 8000 true
wait_for_service "Frontend" 3001 false

# Phase 3: Generate Migrations and Setup Database
log_info "Phase 3: Setting up database schema..."

# Create migrations for all custom apps
log_info "Generating migrations for custom apps..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py makemigrations businesses
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py makemigrations news  
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py makemigrations recommendations
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py makemigrations ml_engine

# Run all migrations
log_info "Running all migrations..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py migrate

# Collect static files
log_info "Collecting static files..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py collectstatic --noinput

log_success "Database schema created successfully"

# Phase 4: Create Users and Basic Configuration
log_info "Phase 4: Creating users and basic configuration..."

log_info "Creating admin superuser and basic configuration..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from businesses.models import Business, AdminUser
from news.models import NewsSource

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@navigate.com',
        password='admin123'
    )
    print("✅ Admin superuser created:")
    print("   Username: admin")
    print("   Password: admin123")
    
    # Create admin profile
    AdminUser.objects.create(
        user=admin_user,
        can_manage_news_sources=True,
        can_create_businesses=True,
        city_access='medellin,bogota,cartagena,barranquilla'
    )
    print("✅ Admin profile created with full permissions")
else:
    print("ℹ️  Admin superuser already exists")

# Create Colombian news sources
news_sources = [
    {
        'name': 'El Tiempo',
        'source_type': 'newspaper',
        'city': 'nacional',
        'website_url': 'https://www.eltiempo.com',
        'rss_url': 'https://www.eltiempo.com/rss.xml',
        'reliability_score': 0.9
    },
    {
        'name': 'El Espectador',
        'source_type': 'newspaper', 
        'city': 'nacional',
        'website_url': 'https://www.elespectador.com',
        'rss_url': 'https://www.elespectador.com/rss.xml',
        'reliability_score': 0.85
    },
    {
        'name': 'El Colombiano',
        'source_type': 'newspaper',
        'city': 'medellin',
        'website_url': 'https://www.elcolombiano.com',
        'reliability_score': 0.8
    },
    {
        'name': 'Caracol Radio',
        'source_type': 'online',
        'city': 'nacional',
        'website_url': 'https://caracol.com.co',
        'reliability_score': 0.75
    },
    {
        'name': 'El Heraldo',
        'source_type': 'newspaper',
        'city': 'barranquilla',
        'website_url': 'https://www.elheraldo.co',
        'reliability_score': 0.8
    },
    {
        'name': 'El Universal',
        'source_type': 'newspaper',
        'city': 'cartagena',
        'website_url': 'https://www.eluniversal.com.co',
        'reliability_score': 0.75
    }
]

for source_data in news_sources:
    source, created = NewsSource.objects.get_or_create(
        name=source_data['name'],
        defaults=source_data
    )
    if created:
        print(f"✅ Created news source: {source.name}")
    else:
        print(f"ℹ️  News source already exists: {source.name}")

print("✅ Basic configuration completed")
EOF

log_success "Users and basic configuration created"

# Phase 5: Optional Mock Data
if [[ "$MOCK_DATA" == "true" ]]; then
    log_info "Phase 5: Creating mock data..."
    
    log_info "Creating sample business and mock data..."
    docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from businesses.models import Business, BusinessKeywords
from news.models import NewsSource, NewsArticle
from recommendations.models import Recommendation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

# Create a business owner user
if not User.objects.filter(username='pub_owner').exists():
    pub_owner = User.objects.create_user(
        username='pub_owner',
        email='owner@irishpub.com',
        password='pub123',
        first_name='Carlos',
        last_name='Mendoza'
    )
    print("✅ Business owner user created:")
    print("   Username: pub_owner")
    print("   Password: pub123")
    
    # Create the business
    if not Business.objects.filter(name='Irish Pub Medellín').exists():
        business = Business.objects.create(
            owner=pub_owner,
            name='Irish Pub Medellín',
            business_type='pub',
            city='medellin',
            description='Auténtico pub irlandés en el corazón de El Poblado. Especialistas en cervezas artesanales y comida irlandesa tradicional.',
            address='Carrera 35 #8A-97, El Poblado, Medellín',
            phone='+57 4 444-5555',
            email='info@irishpubmed.com',
            website='https://irishpubmedellin.com',
            target_audience='Jóvenes profesionales, expatriados, amantes de la cerveza artesanal',
            capacity=120,
            staff_count=8,
            email_notifications=True,
            recommendation_frequency='daily'
        )
        print("✅ Sample business created: Irish Pub Medellín")
        
        # Add business keywords
        keywords_data = [
            ('fútbol', 1.5, False),
            ('cerveza', 2.0, False),
            ('música', 1.2, False),
            ('partido', 1.8, False),
            ('Copa América', 2.0, False),
            ('Colombia', 1.5, False),
            ('Brasil', 1.3, False),
            ('celebración', 1.4, False),
            ('bar', 1.0, False),
            ('alcohol', 0.5, True)
        ]
        
        for keyword, weight, is_negative in keywords_data:
            BusinessKeywords.objects.create(
                business=business,
                keyword=keyword,
                weight=weight,
                is_negative=is_negative
            )
        print("✅ Business keywords created")
    else:
        print("ℹ️  Sample business already exists")
else:
    print("ℹ️  Business owner user already exists")

# Create sample news articles
el_tiempo = NewsSource.objects.filter(name='El Tiempo').first()
if el_tiempo:
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
    
    # Create sample recommendations
    pub = Business.objects.filter(name='Irish Pub Medellín').first()
    marathon_article = NewsArticle.objects.filter(title__icontains='Maratón').first()
    soccer_article = NewsArticle.objects.filter(title__icontains='Copa América').first()
    
    if pub and marathon_article:
        rec_data = {
            'business': pub,
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
            'expected_outcomes': 'Incremento estimado de ventas del 180-220% durante el fin de semana del evento.',
            'content_type': ContentType.objects.get_for_model(marathon_article),
            'object_id': marathon_article.id
        }
        
        rec, created = Recommendation.objects.get_or_create(
            business=pub,
            title=rec_data['title'],
            defaults=rec_data
        )
        if created:
            print(f"✅ Created recommendation: {rec.title}")
    
    if pub and soccer_article:
        rec_data = {
            'business': pub,
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
            'expected_outcomes': 'Incremento proyectado de ventas del 400-600%. Posibilidad de récord histórico de ventas en un solo día.',
            'content_type': ContentType.objects.get_for_model(soccer_article),
            'object_id': soccer_article.id
        }
        
        rec, created = Recommendation.objects.get_or_create(
            business=pub,
            title=rec_data['title'],
            defaults=rec_data
        )
        if created:
            print(f"✅ Created recommendation: {rec.title}")
    
    print("✅ Mock data created successfully")
else:
    print("❌ Could not create mock data - news source not found")
EOF
    
    log_success "Mock data created successfully"
fi

# Phase 6: Final Verification and Instructions
log_info "Phase 6: Final verification..."

# Verify services are still running
if ! curl -f -s "http://localhost:8000/health/" > /dev/null 2>&1; then
    log_error "Backend API is not responding"
fi

if ! nc -z localhost 3001 > /dev/null 2>&1; then
    log_error "Frontend is not responding"
fi

log_success "All services are running correctly"

echo ""
echo -e "${GREEN}🎉 NaviGate First-Time Setup Completed Successfully!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}🔐 Login Information:${NC}"
echo ""
echo -e "${GREEN}📱 ADMIN ACCESS (Django Admin Panel):${NC}"
echo "   • URL: http://localhost:8000/admin"
echo "   • Username: admin"
echo "   • Password: admin123"
echo "   • Manage: News sources, businesses, recommendations"
echo ""
echo -e "${GREEN}👤 CLIENT ACCESS (React Frontend):${NC}"
echo "   • URL: http://localhost:3001"
if [[ "$MOCK_DATA" == "true" ]]; then
    echo "   • Business Login: pub_owner / pub123"
    echo "   • Business: Irish Pub Medellín (with sample data)"
else
    echo "   • Use any email/password (mock authentication)"
    echo "   • Note: No sample data created"
fi
echo ""
echo -e "${BLUE}🎯 Next Steps:${NC}"
if [[ "$MOCK_DATA" == "true" ]]; then
    echo "   ✅ Everything is ready! Start testing:"
    echo "     • Try the admin panel to explore data"
    echo "     • Test the client app with sample business"
    echo "     • Check recommendations and news articles"
    echo "     • Test language switching (🇨🇴 Spanish ↔ 🇺🇸 English)"
else
    echo "   1. Create a business in the admin panel"
    echo "   2. Add some news sources if needed"
    echo "   3. Or run with --mock flag for instant demo data:"
    echo "      ./scripts/first-time-setup.sh --mock"
fi
echo ""
echo -e "${BLUE}🛠️  Other Available Scripts:${NC}"
echo "   • ./scripts/start-server.sh - Start services (after first setup)"
echo "   • ./scripts/stop-server.sh - Stop all services"  
echo "   • ./scripts/first-time-setup.sh --mock - Reset with demo data"
echo ""
echo -e "${YELLOW}💡 Tip: You can run this script anytime to completely reset everything!${NC}"