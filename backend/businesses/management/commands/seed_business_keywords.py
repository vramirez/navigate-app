"""
Management command to seed BusinessTypeKeyword table with initial keywords.
Task-18.11: Create Seed Command for Business Type Keywords
"""
from django.core.management.base import BaseCommand
from businesses.models import BusinessType, BusinessTypeKeyword


class Command(BaseCommand):
    help = 'Seed BusinessTypeKeyword table with initial keywords for all business types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing keywords before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = BusinessTypeKeyword.objects.all().count()
            BusinessTypeKeyword.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing keywords'))

        # Define keywords for each business type
        # Format: (keyword, weight, category)
        keywords_data = {
            'pub': [
                # Beverages
                ('cerveza', 0.20, 'bebidas'),
                ('cervezas', 0.20, 'bebidas'),
                ('beer', 0.20, 'bebidas'),
                ('artesanal', 0.15, 'bebidas'),
                ('craft', 0.15, 'bebidas'),
                ('bar', 0.25, 'establecimiento'),
                ('pub', 0.25, 'establecimiento'),
                ('taberna', 0.20, 'establecimiento'),
                ('brewery', 0.20, 'establecimiento'),
                ('cervecería', 0.20, 'establecimiento'),

                # Events
                ('música en vivo', 0.20, 'eventos'),
                ('live music', 0.20, 'eventos'),
                ('concierto', 0.15, 'eventos'),
                ('DJ', 0.15, 'eventos'),
                ('fiesta', 0.15, 'eventos'),
                ('karaoke', 0.15, 'eventos'),
                ('trivia', 0.15, 'eventos'),

                # Sports
                ('fútbol', 0.20, 'deportes'),
                ('partido', 0.20, 'deportes'),
                ('deportes', 0.15, 'deportes'),
                ('sports', 0.15, 'deportes'),
                ('champions', 0.15, 'deportes'),
                ('mundial', 0.20, 'deportes'),

                # Time/social
                ('happy hour', 0.15, 'social'),
                ('promoción', 0.10, 'social'),
                ('descuento', 0.10, 'social'),
                ('reunión', 0.10, 'social'),
            ],

            'restaurant': [
                # Food types
                ('restaurante', 0.25, 'establecimiento'),
                ('restaurant', 0.25, 'establecimiento'),
                ('comida', 0.20, 'comida'),
                ('gastronomía', 0.20, 'comida'),
                ('gastronomy', 0.20, 'comida'),
                ('plato', 0.15, 'comida'),
                ('menú', 0.15, 'comida'),
                ('chef', 0.15, 'comida'),

                # Cuisine types
                ('italiana', 0.15, 'cocina'),
                ('mexicana', 0.15, 'cocina'),
                ('japonesa', 0.15, 'cocina'),
                ('mediterránea', 0.15, 'cocina'),
                ('fusion', 0.15, 'cocina'),
                ('colombiana', 0.15, 'cocina'),

                # Events
                ('degustación', 0.15, 'eventos'),
                ('tasting', 0.15, 'eventos'),
                ('festival gastronómico', 0.20, 'eventos'),
                ('food festival', 0.20, 'eventos'),
                ('cena', 0.15, 'eventos'),
                ('almuerzo', 0.10, 'eventos'),

                # Quality
                ('michelin', 0.20, 'calidad'),
                ('gourmet', 0.15, 'calidad'),
                ('orgánico', 0.10, 'calidad'),
                ('local', 0.10, 'calidad'),
            ],

            'coffee_shop': [
                # Core products
                ('café', 0.25, 'bebidas'),
                ('coffee', 0.25, 'bebidas'),
                ('cafetería', 0.25, 'establecimiento'),
                ('coffee shop', 0.25, 'establecimiento'),
                ('espresso', 0.20, 'bebidas'),
                ('cappuccino', 0.15, 'bebidas'),
                ('latte', 0.15, 'bebidas'),

                # Related products
                ('pastelería', 0.15, 'comida'),
                ('pastry', 0.15, 'comida'),
                ('panadería', 0.15, 'comida'),
                ('bakery', 0.15, 'comida'),
                ('postre', 0.10, 'comida'),
                ('dessert', 0.10, 'comida'),

                # Coffee culture
                ('barista', 0.15, 'cultura'),
                ('tostado', 0.10, 'cultura'),
                ('roasting', 0.10, 'cultura'),
                ('origen', 0.10, 'cultura'),
                ('specialty', 0.15, 'cultura'),
                ('especialidad', 0.15, 'cultura'),

                # Events
                ('cafetero', 0.15, 'eventos'),
                ('coffee tasting', 0.15, 'eventos'),
                ('latte art', 0.10, 'eventos'),

                # Ambiance
                ('coworking', 0.10, 'ambiente'),
                ('wifi', 0.05, 'ambiente'),
                ('lectura', 0.10, 'ambiente'),
                ('reunión', 0.10, 'ambiente'),
            ],

            'bookstore': [
                # Core business
                ('librería', 0.25, 'establecimiento'),
                ('bookstore', 0.25, 'establecimiento'),
                ('libro', 0.25, 'productos'),
                ('books', 0.25, 'productos'),
                ('editorial', 0.15, 'productos'),
                ('publisher', 0.15, 'productos'),

                # Events
                ('presentación', 0.20, 'eventos'),
                ('book launch', 0.20, 'eventos'),
                ('autor', 0.20, 'eventos'),
                ('author', 0.20, 'eventos'),
                ('firma', 0.15, 'eventos'),
                ('signing', 0.15, 'eventos'),
                ('lectura', 0.15, 'eventos'),
                ('reading', 0.15, 'eventos'),
                ('club de lectura', 0.15, 'eventos'),
                ('book club', 0.15, 'eventos'),

                # Genres
                ('novela', 0.15, 'géneros'),
                ('novel', 0.15, 'géneros'),
                ('poesía', 0.15, 'géneros'),
                ('poetry', 0.15, 'géneros'),
                ('ensayo', 0.10, 'géneros'),
                ('literatura', 0.20, 'géneros'),
                ('literature', 0.20, 'géneros'),

                # Cultural
                ('cultural', 0.15, 'cultura'),
                ('literario', 0.20, 'cultura'),
                ('literary', 0.20, 'cultura'),
                ('feria del libro', 0.20, 'eventos'),
                ('book fair', 0.20, 'eventos'),
            ]
        }

        created_count = 0
        updated_count = 0

        for business_type_code, keywords in keywords_data.items():
            try:
                business_type = BusinessType.objects.get(code=business_type_code)
            except BusinessType.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'BusinessType "{business_type_code}" not found. Skipping.')
                )
                continue

            for keyword, weight, category in keywords:
                obj, created = BusinessTypeKeyword.objects.update_or_create(
                    business_type=business_type,
                    keyword=keyword,
                    defaults={
                        'weight': weight,
                        'category': category,
                        'is_active': True
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Processed {len(keywords)} keywords for {business_type.display_name}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal: {created_count} created, {updated_count} updated'
            )
        )
