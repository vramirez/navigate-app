"""
Quick seed script for broadcastability taxonomy
Run with: docker exec docker-backend-1 python manage.py shell < seed_broadcastability.py
"""

from event_taxonomy.models import SportType, CompetitionLevel, HypeIndicator, BroadcastabilityConfig

print("\n=== Seeding Broadcastability Taxonomy ===\n")

# Seed Sport Types
print("Seeding Sport Types...")
sports = [
    {'code': 'soccer', 'name_es': 'Fútbol', 'name_en': 'Soccer', 'latin_america_appeal': 0.95, 'keywords': ['fútbol', 'futbol', 'soccer', 'partido', 'selección'], 'display_order': 1},
    {'code': 'combat_sports', 'name_es': 'Deportes de Combate', 'name_en': 'Combat Sports', 'latin_america_appeal': 0.87, 'keywords': ['boxeo', 'mma', 'ufc', 'pelea'], 'display_order': 2},
    {'code': 'baseball', 'name_es': 'Béisbol', 'name_en': 'Baseball', 'latin_america_appeal': 0.85, 'keywords': ['béisbol', 'beisbol', 'baseball', 'mlb'], 'display_order': 3},
    {'code': 'cycling', 'name_es': 'Ciclismo', 'name_en': 'Cycling', 'latin_america_appeal': 0.82, 'keywords': ['ciclismo', 'tour de francia', 'giro', 'vuelta', 'egan bernal'], 'display_order': 4},
]
for sport_data in sports:
    sport, created = SportType.objects.get_or_create(code=sport_data['code'], defaults=sport_data)
    print(f"{'✓ Created' if created else '- Exists'}: {sport.name_es}")

# Seed Competition Levels
print("\nSeeding Competition Levels...")
soccer = SportType.objects.get(code='soccer')
cycling = SportType.objects.get(code='cycling')

competitions = [
    {'code': 'world_cup_final', 'name_es': 'Final Copa Mundial', 'name_en': 'World Cup Final', 'sport_type': soccer, 'broadcast_multiplier': 3.0, 'keywords': ['final', 'copa mundial']},
    {'code': 'world_cup_match', 'name_es': 'Partido Copa Mundial', 'name_en': 'World Cup Match', 'sport_type': soccer, 'broadcast_multiplier': 2.8, 'keywords': ['mundial', 'world cup']},
    {'code': 'tour_de_france', 'name_es': 'Tour de Francia', 'name_en': 'Tour de France', 'sport_type': cycling, 'broadcast_multiplier': 2.5, 'keywords': ['tour de francia', 'tour']},
]
for comp_data in competitions:
    comp, created = CompetitionLevel.objects.get_or_create(code=comp_data['code'], defaults=comp_data)
    print(f"{'✓ Created' if created else '- Exists'}: {comp.name_es}")

# Seed Hype Indicators
print("\nSeeding Hype Indicators...")
indicators = [
    {'pattern': r'final|semifinal', 'description': 'Finals', 'hype_boost': 0.30, 'category': 'finals', 'language': 'es'},
    {'pattern': r'clásico|derbi', 'description': 'Classic rivalry', 'hype_boost': 0.20, 'category': 'rivalry', 'language': 'es'},
    {'pattern': r'selección colombia', 'description': 'Colombian team', 'hype_boost': 0.25, 'category': 'colombian', 'language': 'es'},
]
for indicator_data in indicators:
    indicator, created = HypeIndicator.objects.get_or_create(pattern=indicator_data['pattern'], category=indicator_data['category'], defaults=indicator_data)
    print(f"{'✓ Created' if created else '- Exists'}: {indicator.pattern}")

# Seed Config
print("\nSeeding Broadcastability Config...")
config, created = BroadcastabilityConfig.objects.get_or_create(pk=1, defaults={'min_broadcastability_score': 0.55})
print(f"{'✓ Created' if created else '- Exists'}: BroadcastabilityConfig")

print("\n✓ Seeding complete!")
print(f"  - Sport Types: {SportType.objects.count()}")
print(f"  - Competition Levels: {CompetitionLevel.objects.count()}")
print(f"  - Hype Indicators: {HypeIndicator.objects.count()}")
