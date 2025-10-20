# Generated manually on 2025-10-19
# Seeds comprehensive keyword list for business type matching

from django.db import migrations


def seed_keywords(apps, schema_editor):
    """Seed 83 keywords across 4 business types with categories and weights"""
    BusinessTypeKeyword = apps.get_model('businesses', 'BusinessTypeKeyword')

    keywords_data = [
        # PUB/BAR (23 keywords)
        # Bebidas (7)
        ('pub', 'cerveza', 'bebidas', 0.20),
        ('pub', 'whisky', 'bebidas', 0.15),
        ('pub', 'ron', 'bebidas', 0.15),
        ('pub', 'cocktail', 'bebidas', 0.15),
        ('pub', 'trago', 'bebidas', 0.15),
        ('pub', 'licor', 'bebidas', 0.15),
        ('pub', 'bebida', 'bebidas', 0.10),
        # Deportes (8)
        ('pub', 'fútbol', 'deportes', 0.20),
        ('pub', 'partido', 'deportes', 0.20),
        ('pub', 'deportes', 'deportes', 0.15),
        ('pub', 'champions', 'deportes', 0.15),
        ('pub', 'liga', 'deportes', 0.15),
        ('pub', 'selección', 'deportes', 0.15),
        ('pub', 'gol', 'deportes', 0.10),
        ('pub', 'mundial', 'deportes', 0.15),
        # Entretenimiento (5)
        ('pub', 'música', 'entretenimiento', 0.15),
        ('pub', 'concierto', 'entretenimiento', 0.15),
        ('pub', 'banda', 'entretenimiento', 0.10),
        ('pub', 'DJ', 'entretenimiento', 0.10),
        ('pub', 'karaoke', 'entretenimiento', 0.10),
        # Social (3)
        ('pub', 'amigos', 'social', 0.10),
        ('pub', 'celebración', 'social', 0.10),
        ('pub', 'fiesta', 'social', 0.10),

        # RESTAURANT (22 keywords)
        # Comida (6)
        ('restaurant', 'comida', 'comida', 0.20),
        ('restaurant', 'gastronomía', 'comida', 0.20),
        ('restaurant', 'restaurante', 'comida', 0.20),
        ('restaurant', 'chef', 'comida', 0.15),
        ('restaurant', 'cocina', 'comida', 0.15),
        ('restaurant', 'menú', 'comida', 0.10),
        # Cocinas (5)
        ('restaurant', 'colombiana', 'cocinas', 0.15),
        ('restaurant', 'italiana', 'cocinas', 0.15),
        ('restaurant', 'mexicana', 'cocinas', 0.15),
        ('restaurant', 'asiática', 'cocinas', 0.15),
        ('restaurant', 'internacional', 'cocinas', 0.10),
        # Momentos (4)
        ('restaurant', 'cena', 'momentos', 0.15),
        ('restaurant', 'almuerzo', 'momentos', 0.15),
        ('restaurant', 'degustación', 'momentos', 0.15),
        ('restaurant', 'maridaje', 'momentos', 0.15),
        # Calidad (4)
        ('restaurant', 'gourmet', 'calidad', 0.15),
        ('restaurant', 'premium', 'calidad', 0.15),
        ('restaurant', 'artesanal', 'calidad', 0.10),
        ('restaurant', 'orgánico', 'calidad', 0.10),
        # Eventos (3)
        ('restaurant', 'festival gastronómico', 'eventos', 0.15),
        ('restaurant', 'feria', 'eventos', 0.10),
        ('restaurant', 'food truck', 'eventos', 0.10),

        # COFFEE_SHOP (20 keywords)
        # Bebidas (7)
        ('coffee_shop', 'café', 'bebidas', 0.20),
        ('coffee_shop', 'cappuccino', 'bebidas', 0.15),
        ('coffee_shop', 'espresso', 'bebidas', 0.15),
        ('coffee_shop', 'latte', 'bebidas', 0.15),
        ('coffee_shop', 'té', 'bebidas', 0.10),
        ('coffee_shop', 'jugo', 'bebidas', 0.10),
        ('coffee_shop', 'chocolate', 'bebidas', 0.10),
        # Comida (6)
        ('coffee_shop', 'brunch', 'comida', 0.20),
        ('coffee_shop', 'desayuno', 'comida', 0.20),
        ('coffee_shop', 'pastelería', 'comida', 0.15),
        ('coffee_shop', 'postre', 'comida', 0.15),
        ('coffee_shop', 'croissant', 'comida', 0.10),
        ('coffee_shop', 'pan', 'comida', 0.10),
        # Ambiente (4)
        ('coffee_shop', 'tertulia', 'ambiente', 0.10),
        ('coffee_shop', 'lectura', 'ambiente', 0.10),
        ('coffee_shop', 'wifi', 'ambiente', 0.05),
        ('coffee_shop', 'coworking', 'ambiente', 0.10),
        # Calidad (3)
        ('coffee_shop', 'artesanal', 'calidad', 0.15),
        ('coffee_shop', 'specialty', 'calidad', 0.15),
        ('coffee_shop', 'barista', 'calidad', 0.10),

        # BOOKSTORE (18 keywords)
        # Libros (5)
        ('bookstore', 'libro', 'libros', 0.20),
        ('bookstore', 'librería', 'libros', 0.20),
        ('bookstore', 'literatura', 'libros', 0.15),
        ('bookstore', 'autor', 'libros', 0.15),
        ('bookstore', 'escritor', 'libros', 0.15),
        # Eventos (5)
        ('bookstore', 'feria del libro', 'eventos', 0.20),
        ('bookstore', 'presentación', 'eventos', 0.15),
        ('bookstore', 'firma', 'eventos', 0.15),
        ('bookstore', 'charla', 'eventos', 0.10),
        ('bookstore', 'taller', 'eventos', 0.10),
        # Géneros (5)
        ('bookstore', 'novela', 'géneros', 0.15),
        ('bookstore', 'poesía', 'géneros', 0.15),
        ('bookstore', 'ensayo', 'géneros', 0.10),
        ('bookstore', 'cómic', 'géneros', 0.10),
        ('bookstore', 'infantil', 'géneros', 0.10),
        # Actividades (3)
        ('bookstore', 'lectura', 'actividades', 0.15),
        ('bookstore', 'club de lectura', 'actividades', 0.15),
        ('bookstore', 'tertulia literaria', 'actividades', 0.10),
    ]

    print(f"\n Seeding {len(keywords_data)} business type keywords...")

    for business_type, keyword, category, weight in keywords_data:
        BusinessTypeKeyword.objects.create(
            business_type=business_type,
            keyword=keyword,
            category=category,
            weight=weight,
            is_active=True
        )

    print(f"✓ Successfully seeded {len(keywords_data)} keywords")
    print(f"  - Pub/Bar: 23 keywords")
    print(f"  - Restaurant: 22 keywords")
    print(f"  - Coffee Shop: 20 keywords")
    print(f"  - Bookstore: 18 keywords")


def reverse_seed(apps, schema_editor):
    """Remove all seeded keywords"""
    BusinessTypeKeyword = apps.get_model('businesses', 'BusinessTypeKeyword')
    deleted_count = BusinessTypeKeyword.objects.all().delete()[0]
    print(f"Deleted {deleted_count} business type keywords")


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0004_add_businesstypekeyword'),
    ]

    operations = [
        migrations.RunPython(seed_keywords, reverse_seed),
    ]
