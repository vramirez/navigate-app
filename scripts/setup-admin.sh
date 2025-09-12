#!/bin/bash

# NaviGate Admin Setup Script
# This script creates admin user, runs migrations, and sets up sample data

set -e

echo "🔧 Setting up NaviGate Admin and Sample Data..."
echo "=============================================="

# Check if containers are running
if ! docker compose -f docker/docker-compose.dev.yml ps | grep -q "Up"; then
    echo "❌ Error: Containers are not running. Please run ./start-server.sh first."
    exit 1
fi

echo "📦 Running database migrations..."
docker compose -f docker/docker-compose.dev.yml exec backend python manage.py migrate

echo "🗂️  Collecting static files..."
docker compose -f docker/docker-compose.dev.yml exec backend python manage.py collectstatic --noinput

echo "👤 Creating admin superuser..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from businesses.models import Business, AdminUser

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
        
        # Add some keywords for the business
        from businesses.models import BusinessKeywords
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
            ('alcohol', 0.5, True)  # Negative keyword
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

print("\n🎯 Setup completed successfully!")
print("=================================")
print("Admin Access:")
print("  URL: http://localhost:8000/admin")
print("  Username: admin")
print("  Password: admin123")
print("")
print("Business Owner Access:")
print("  URL: http://localhost:3001")
print("  Username: pub_owner")
print("  Password: pub123")
print("  Business: Irish Pub Medellín (Pub/Bar in Medellín)")
EOF

echo ""
echo "📊 Loading sample news sources..."
docker compose -f docker/docker-compose.dev.yml exec -T backend python manage.py shell << 'EOF'
from news.models import NewsSource

# Colombian news sources
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

print("✅ News sources setup completed")
EOF

echo ""
echo "🎉 All setup completed!"
echo "======================"
echo ""
echo "Ready to test! Follow these steps:"
echo ""
echo "1️⃣  ADMIN TESTING:"
echo "   • Go to http://localhost:8000/admin"
echo "   • Login with admin/admin123"
echo "   • Explore: Businesses, News Sources, etc."
echo ""
echo "2️⃣  CLIENT TESTING:"
echo "   • Go to http://localhost:3001"
echo "   • Use any email/password to 'login' (mock auth)"
echo "   • Navigate through Dashboard, Recommendations, etc."
echo ""
echo "3️⃣  NEXT STEPS:"
echo "   • Run ./create-mock-data.sh to add sample news and recommendations"
echo "   • Test the language switcher (🇨🇴 Spanish ↔ 🇺🇸 English)"
echo "   • Check mobile responsiveness"