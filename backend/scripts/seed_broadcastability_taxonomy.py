#!/usr/bin/env python
"""
Seed script for Broadcastability Taxonomy (task-9.7)

Seeds database with:
- 14 sport types with Latin America appeal ratings
- 30+ competition levels with broadcast multipliers
- 30+ hype indicator patterns

Run: python manage.py shell < scripts/seed_broadcastability_taxonomy.py
Or: docker exec docker-backend-1 python manage.py shell < scripts/seed_broadcastability_taxonomy.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from event_taxonomy.models import SportType, CompetitionLevel, HypeIndicator, BroadcastabilityConfig


def seed_sport_types():
    """Seed 14 sport types with Latin America appeal ratings"""
    print("\n=== Seeding Sport Types ===")

    sports = [
        {
            'code': 'soccer',
            'name_es': 'Fútbol',
            'name_en': 'Soccer',
            'latin_america_appeal': 0.95,
            'description': 'Rey del deporte en Latinoamérica. Mundial, Copa América, Libertadores atraen audiencias masivas.',
            'keywords': ['fútbol', 'futbol', 'soccer', 'partido', 'selección', 'mundial', 'copa', 'gol', 'liga', 'clásico'],
            'display_order': 1
        },
        {
            'code': 'combat_sports',
            'name_es': 'Deportes de Combate',
            'name_en': 'Combat Sports',
            'latin_america_appeal': 0.87,
            'description': 'Boxeo y MMA/UFC. Tradición de boxeo en México, Colombia, Argentina. UFC en crecimiento.',
            'keywords': ['boxeo', 'mma', 'ufc', 'pelea', 'combate', 'nocaut', 'knock out', 'octágono', 'rounds', 'título'],
            'display_order': 2
        },
        {
            'code': 'baseball',
            'name_es': 'Béisbol',
            'name_en': 'Baseball',
            'latin_america_appeal': 0.85,
            'description': 'Dominante en el Caribe (República Dominicana, Venezuela, Cuba, Puerto Rico). MLB tiene muchas estrellas latinas.',
            'keywords': ['béisbol', 'beisbol', 'baseball', 'jonrón', 'home run', 'innings', 'grandes ligas', 'mlb', 'serie caribeña'],
            'display_order': 3
        },
        {
            'code': 'cycling',
            'name_es': 'Ciclismo',
            'name_en': 'Cycling',
            'latin_america_appeal': 0.82,
            'description': 'Colombia es potencia ciclística. Egan Bernal, Nairo Quintana, Rigoberto Urán son ídolos nacionales.',
            'keywords': ['ciclismo', 'tour de francia', 'giro', 'vuelta', 'etapa', 'montaña', 'egan bernal', 'nairo quintana', 'rigoberto urán'],
            'display_order': 4
        },
        {
            'code': 'basketball',
            'name_es': 'Baloncesto',
            'name_en': 'Basketball',
            'latin_america_appeal': 0.72,
            'description': 'NBA muy popular en áreas urbanas. FIBA Américas tiene buen seguimiento.',
            'keywords': ['baloncesto', 'básquetbol', 'basketball', 'nba', 'canasta', 'triple', 'playoffs', 'final'],
            'display_order': 5
        },
        {
            'code': 'formula_1',
            'name_es': 'Fórmula 1',
            'name_en': 'Formula 1',
            'latin_america_appeal': 0.70,
            'description': 'Fuerte seguimiento, especialmente con Checo Pérez (México). Herencia brasileña (Senna).',
            'keywords': ['fórmula 1', 'formula 1', 'f1', 'gran premio', 'carrera', 'checo pérez', 'sergio pérez', 'ferrari', 'red bull'],
            'display_order': 6
        },
        {
            'code': 'tennis',
            'name_es': 'Tenis',
            'name_en': 'Tennis',
            'latin_america_appeal': 0.65,
            'description': 'Grand Slams atraen espectadores. Jugadores latinoamericanos ocasionalmente en rankings.',
            'keywords': ['tenis', 'tennis', 'grand slam', 'wimbledon', 'roland garros', 'us open', 'abierto'],
            'display_order': 7
        },
        {
            'code': 'volleyball',
            'name_es': 'Voleibol',
            'name_en': 'Volleyball',
            'latin_america_appeal': 0.62,
            'description': 'Popular especialmente en Brasil (playa e indoor). Olímpicos atraen gran audiencia.',
            'keywords': ['voleibol', 'voley', 'vóley', 'volleyball', 'sets', 'saque', 'remate', 'playa'],
            'display_order': 8
        },
        {
            'code': 'american_football',
            'name_es': 'Fútbol Americano',
            'name_en': 'American Football',
            'latin_america_appeal': 0.52,
            'description': 'NFL creciendo en México. Super Bowl es evento de visión. No tradicional pero aumentando.',
            'keywords': ['fútbol americano', 'futbol americano', 'nfl', 'super bowl', 'touchdown', 'quarterback', 'patriots'],
            'display_order': 9
        },
        {
            'code': 'motorsports',
            'name_es': 'Otros Deportes Motoriz',
            'name_en': 'Other Motorsports',
            'latin_america_appeal': 0.45,
            'description': 'NASCAR, MotoGP, Rally tienen seguidores nicho. No tan grande como F1.',
            'keywords': ['motociclismo', 'motogp', 'rally', 'dakar', 'nascar', 'carreras', 'motos'],
            'display_order': 10
        },
        {
            'code': 'rugby',
            'name_es': 'Rugby',
            'name_en': 'Rugby',
            'latin_america_appeal': 0.38,
            'description': 'Fuerte solo en Argentina (Los Pumas). Mundial atrae interés mínimo.',
            'keywords': ['rugby', 'los pumas', 'mundial de rugby', 'try', 'melé', 'argentina', 'all blacks'],
            'display_order': 11
        },
        {
            'code': 'golf',
            'name_es': 'Golf',
            'name_en': 'Golf',
            'latin_america_appeal': 0.32,
            'description': 'Percepción de deporte elitista. Masters/majors tienen alguna audiencia.',
            'keywords': ['golf', 'masters', 'pga', 'hoyo', 'torneo', 'augusta', 'tiger woods'],
            'display_order': 12
        },
        {
            'code': 'ice_hockey',
            'name_es': 'Hockey sobre Hielo',
            'name_en': 'Ice Hockey',
            'latin_america_appeal': 0.15,
            'description': 'Seguimiento muy limitado. Desconexión climática/cultural.',
            'keywords': ['hockey sobre hielo', 'nhl', 'stanley cup', 'hockey'],
            'display_order': 13
        },
        {
            'code': 'winter_sports',
            'name_es': 'Deportes de Invierno',
            'name_en': 'Winter Sports',
            'latin_america_appeal': 0.10,
            'description': 'Sin tradición de deportes de invierno. Olímpicos de invierno mínimo interés.',
            'keywords': ['esquí', 'ski', 'patinaje sobre hielo', 'snowboard', 'juegos olímpicos de invierno'],
            'display_order': 14
        },
    ]

    created_count = 0
    for sport_data in sports:
        sport, created = SportType.objects.get_or_create(
            code=sport_data['code'],
            defaults=sport_data
        )
        if created:
            print(f"✓ Created: {sport.name_es} (appeal: {sport.latin_america_appeal})")
            created_count += 1
        else:
            print(f"- Already exists: {sport.name_es}")

    print(f"\nCreated {created_count}/{len(sports)} sport types")


def seed_competition_levels():
    """Seed 30+ competition levels with broadcast multipliers"""
    print("\n=== Seeding Competition Levels ===")

    # Get sport types
    soccer = SportType.objects.get(code='soccer')
    cycling = SportType.objects.get(code='cycling')
    combat = SportType.objects.get(code='combat_sports')
    baseball = SportType.objects.get(code='baseball')
    basketball = SportType.objects.get(code='basketball')
    formula1 = SportType.objects.get(code='formula_1')

    competitions = [
        # Soccer (10 levels)
        {'code': 'world_cup_final', 'name_es': 'Final Copa Mundial', 'name_en': 'World Cup Final', 'sport_type': soccer, 'broadcast_multiplier': 3.0, 'typical_attendance_min': 80000, 'keywords': ['final', 'copa mundial', 'final del mundo'], 'display_order': 1},
        {'code': 'world_cup_match', 'name_es': 'Partido Copa Mundial', 'name_en': 'World Cup Match', 'sport_type': soccer, 'broadcast_multiplier': 2.8, 'typical_attendance_min': 50000, 'keywords': ['mundial', 'world cup', 'qatar', 'copa del mundo'], 'display_order': 2},
        {'code': 'copa_america_final', 'name_es': 'Final Copa América', 'name_en': 'Copa América Final', 'sport_type': soccer, 'broadcast_multiplier': 2.6, 'typical_attendance_min': 70000, 'keywords': ['copa américa', 'final', 'conmebol'], 'display_order': 3},
        {'code': 'libertadores_final', 'name_es': 'Final Copa Libertadores', 'name_en': 'Libertadores Final', 'sport_type': soccer, 'broadcast_multiplier': 2.5, 'typical_attendance_min': 60000, 'keywords': ['libertadores', 'final', 'conmebol', 'copa libertadores'], 'display_order': 4},
        {'code': 'champions_league_final', 'name_es': 'Final Champions League', 'name_en': 'Champions League Final', 'sport_type': soccer, 'broadcast_multiplier': 2.3, 'typical_attendance_min': 70000, 'keywords': ['champions', 'liga de campeones', 'final', 'uefa'], 'display_order': 5},
        {'code': 'world_cup_qualifier', 'name_es': 'Eliminatorias Mundial', 'name_en': 'World Cup Qualifier', 'sport_type': soccer, 'broadcast_multiplier': 2.0, 'typical_attendance_min': 40000, 'keywords': ['eliminatorias', 'clasificar', 'selección', 'mundial'], 'display_order': 6},
        {'code': 'classic_derby', 'name_es': 'Clásico/Derbi', 'name_en': 'Classic/Derby', 'sport_type': soccer, 'broadcast_multiplier': 1.7, 'typical_attendance_min': 50000, 'keywords': ['clásico', 'derbi', 'derby', 'rival'], 'display_order': 7},
        {'code': 'primera_division_top', 'name_es': 'Primera División Top', 'name_en': 'Top Division Match', 'sport_type': soccer, 'broadcast_multiplier': 1.5, 'typical_attendance_min': 30000, 'keywords': ['primera división', 'liga', 'jornada'], 'display_order': 8},
        {'code': 'primera_division', 'name_es': 'Primera División Regular', 'name_en': 'First Division', 'sport_type': soccer, 'broadcast_multiplier': 1.0, 'typical_attendance_min': 15000, 'keywords': ['partido', 'liga', 'torneo'], 'display_order': 9},
        {'code': 'segunda_division', 'name_es': 'Segunda División', 'name_en': 'Second Division', 'sport_type': soccer, 'broadcast_multiplier': 0.4, 'typical_attendance_min': 3000, 'keywords': ['segunda división', 'ascenso'], 'display_order': 10},

        # Cycling (5 levels)
        {'code': 'tour_de_france', 'name_es': 'Tour de Francia', 'name_en': 'Tour de France', 'sport_type': cycling, 'broadcast_multiplier': 2.5, 'typical_attendance_min': 0, 'keywords': ['tour de francia', 'tour', 'etapa', 'maillot amarillo'], 'display_order': 1},
        {'code': 'giro_italia', 'name_es': 'Giro de Italia', 'name_en': 'Giro d\'Italia', 'sport_type': cycling, 'broadcast_multiplier': 2.3, 'typical_attendance_min': 0, 'keywords': ['giro de italia', 'giro', 'maglia rosa'], 'display_order': 2},
        {'code': 'vuelta_espana', 'name_es': 'Vuelta a España', 'name_en': 'Vuelta a España', 'sport_type': cycling, 'broadcast_multiplier': 2.3, 'typical_attendance_min': 0, 'keywords': ['vuelta a españa', 'vuelta', 'jersey rojo'], 'display_order': 3},
        {'code': 'cycling_world_champ', 'name_es': 'Campeonato Mundial Ciclismo', 'name_en': 'Cycling World Championship', 'sport_type': cycling, 'broadcast_multiplier': 2.1, 'typical_attendance_min': 0, 'keywords': ['mundial de ciclismo', 'campeonato mundial', 'arcoíris'], 'display_order': 4},
        {'code': 'cycling_olympics', 'name_es': 'Ciclismo Olímpico', 'name_en': 'Olympic Cycling', 'sport_type': cycling, 'broadcast_multiplier': 2.4, 'typical_attendance_min': 0, 'keywords': ['olimpiadas', 'juegos olímpicos', 'ciclismo'], 'display_order': 5},

        # Combat Sports (5 levels)
        {'code': 'boxing_world_title_multi', 'name_es': 'Título Mundial Boxeo (Múltiples Cinturones)', 'name_en': 'Boxing World Title (Multiple Belts)', 'sport_type': combat, 'broadcast_multiplier': 2.8, 'typical_attendance_min': 20000, 'keywords': ['pelea', 'título mundial', 'unificación', 'canelo', 'campeonato'], 'display_order': 1},
        {'code': 'boxing_world_title', 'name_es': 'Título Mundial Boxeo', 'name_en': 'Boxing World Title', 'sport_type': combat, 'broadcast_multiplier': 2.5, 'typical_attendance_min': 15000, 'keywords': ['título', 'campeonato', 'wbc', 'wba', 'ibf'], 'display_order': 2},
        {'code': 'ufc_championship', 'name_es': 'Campeonato UFC', 'name_en': 'UFC Championship', 'sport_type': combat, 'broadcast_multiplier': 2.3, 'typical_attendance_min': 15000, 'keywords': ['ufc', 'título', 'championship', 'octágono'], 'display_order': 3},
        {'code': 'boxing_regional', 'name_es': 'Título Regional Boxeo', 'name_en': 'Regional Boxing Title', 'sport_type': combat, 'broadcast_multiplier': 1.2, 'typical_attendance_min': 5000, 'keywords': ['regional', 'eliminatoria'], 'display_order': 4},
        {'code': 'olympic_boxing', 'name_es': 'Boxeo Olímpico', 'name_en': 'Olympic Boxing', 'sport_type': combat, 'broadcast_multiplier': 2.3, 'typical_attendance_min': 10000, 'keywords': ['olimpiadas', 'juegos olímpicos', 'boxeo'], 'display_order': 5},

        # Baseball (4 levels)
        {'code': 'world_series', 'name_es': 'Serie Mundial', 'name_en': 'World Series', 'sport_type': baseball, 'broadcast_multiplier': 2.6, 'typical_attendance_min': 40000, 'keywords': ['serie mundial', 'world series', 'mlb'], 'display_order': 1},
        {'code': 'mlb_playoffs', 'name_es': 'Playoffs MLB', 'name_en': 'MLB Playoffs', 'sport_type': baseball, 'broadcast_multiplier': 2.0, 'typical_attendance_min': 35000, 'keywords': ['playoffs', 'postemporada', 'mlb'], 'display_order': 2},
        {'code': 'caribbean_series', 'name_es': 'Serie del Caribe', 'name_en': 'Caribbean Series', 'sport_type': baseball, 'broadcast_multiplier': 2.2, 'typical_attendance_min': 20000, 'keywords': ['serie del caribe', 'caribeña'], 'display_order': 3},
        {'code': 'mlb_regular', 'name_es': 'Temporada Regular MLB', 'name_en': 'MLB Regular Season', 'sport_type': baseball, 'broadcast_multiplier': 0.8, 'typical_attendance_min': 25000, 'keywords': ['mlb', 'grandes ligas', 'temporada'], 'display_order': 4},

        # Basketball (3 levels)
        {'code': 'nba_finals', 'name_es': 'Finales NBA', 'name_en': 'NBA Finals', 'sport_type': basketball, 'broadcast_multiplier': 2.4, 'typical_attendance_min': 18000, 'keywords': ['finales nba', 'nba finals', 'campeonato'], 'display_order': 1},
        {'code': 'nba_playoffs', 'name_es': 'Playoffs NBA', 'name_en': 'NBA Playoffs', 'sport_type': basketball, 'broadcast_multiplier': 1.8, 'typical_attendance_min': 18000, 'keywords': ['playoffs nba', 'postemporada'], 'display_order': 2},
        {'code': 'olympic_basketball', 'name_es': 'Baloncesto Olímpico', 'name_en': 'Olympic Basketball', 'sport_type': basketball, 'broadcast_multiplier': 2.2, 'typical_attendance_min': 15000, 'keywords': ['olimpiadas', 'juegos olímpicos', 'baloncesto'], 'display_order': 3},

        # Formula 1 (3 levels)
        {'code': 'f1_race', 'name_es': 'Gran Premio F1', 'name_en': 'F1 Grand Prix', 'sport_type': formula1, 'broadcast_multiplier': 2.0, 'typical_attendance_min': 100000, 'keywords': ['fórmula 1', 'f1', 'gran premio', 'carrera'], 'display_order': 1},
        {'code': 'f1_mexico', 'name_es': 'Gran Premio de México', 'name_en': 'Mexico Grand Prix', 'sport_type': formula1, 'broadcast_multiplier': 2.5, 'typical_attendance_min': 140000, 'keywords': ['gran premio de méxico', 'méxico', 'checo pérez'], 'display_order': 2},
        {'code': 'f1_championship', 'name_es': 'Campeonato F1 (Final)', 'name_en': 'F1 Championship (Final)', 'sport_type': formula1, 'broadcast_multiplier': 2.3, 'typical_attendance_min': 100000, 'keywords': ['campeonato', 'título', 'champion'], 'display_order': 3},
    ]

    created_count = 0
    for comp_data in competitions:
        comp, created = CompetitionLevel.objects.get_or_create(
            code=comp_data['code'],
            defaults=comp_data
        )
        if created:
            print(f"✓ Created: {comp.name_es} ({comp.broadcast_multiplier}x)")
            created_count += 1
        else:
            print(f"- Already exists: {comp.name_es}")

    print(f"\nCreated {created_count}/{len(competitions)} competition levels")


def seed_hype_indicators():
    """Seed 30+ hype indicator patterns"""
    print("\n=== Seeding Hype Indicators ===")

    indicators = [
        # Finals/Championships (6 patterns)
        {'pattern': r'final|semifinal|cuartos de final', 'description': 'Finals/semifinals language', 'hype_boost': 0.30, 'category': 'finals', 'language': 'es'},
        {'pattern': r'campeonato mundial|copa del mundo', 'description': 'World championship', 'hype_boost': 0.30, 'category': 'finals', 'language': 'es'},
        {'pattern': r'título|corona|campeón', 'description': 'Title/champion keywords', 'hype_boost': 0.25, 'category': 'finals', 'language': 'es'},
        {'pattern': r'eliminatorias|clasificar', 'description': 'Qualifiers/classification', 'hype_boost': 0.20, 'category': 'stakes', 'language': 'es'},
        {'pattern': r'final', 'description': 'Finals', 'hype_boost': 0.30, 'category': 'finals', 'language': 'en'},
        {'pattern': r'championship|title fight', 'description': 'Championship/title', 'hype_boost': 0.25, 'category': 'finals', 'language': 'en'},

        # Historic (5 patterns)
        {'pattern': r'históric|épic|legendari|memorable', 'description': 'Historic event markers', 'hype_boost': 0.25, 'category': 'historic', 'language': 'es'},
        {'pattern': r'por primera vez|récord|historia', 'description': 'First time/record/history', 'hype_boost': 0.20, 'category': 'historic', 'language': 'es'},
        {'pattern': r'hazaña|proeza|gesta', 'description': 'Achievement/feat', 'hype_boost': 0.20, 'category': 'historic', 'language': 'es'},
        {'pattern': r'historic|legendary|epic', 'description': 'Historic markers', 'hype_boost': 0.25, 'category': 'historic', 'language': 'en'},
        {'pattern': r'first time|record|milestone', 'description': 'Historic milestones', 'hype_boost': 0.20, 'category': 'historic', 'language': 'en'},

        # Rivalry (4 patterns)
        {'pattern': r'clásico|derbi|derby|rival', 'description': 'Classic rivalry matches', 'hype_boost': 0.20, 'category': 'rivalry', 'language': 'es'},
        {'pattern': r'venganza|revancha', 'description': 'Revenge/rematch', 'hype_boost': 0.15, 'category': 'rivalry', 'language': 'es'},
        {'pattern': r'classic|derby|rival', 'description': 'Classic rivalry', 'hype_boost': 0.20, 'category': 'rivalry', 'language': 'en'},
        {'pattern': r'revenge|rematch', 'description': 'Revenge match', 'hype_boost': 0.15, 'category': 'rivalry', 'language': 'en'},

        # Stakes (5 patterns)
        {'pattern': r'define|decisiv|crucial', 'description': 'Defining/decisive/crucial', 'hype_boost': 0.15, 'category': 'stakes', 'language': 'es'},
        {'pattern': r'vida o muerte|todo o nada', 'description': 'Do or die stakes', 'hype_boost': 0.20, 'category': 'stakes', 'language': 'es'},
        {'pattern': r'último|definitivo', 'description': 'Final/definitive', 'hype_boost': 0.10, 'category': 'stakes', 'language': 'es'},
        {'pattern': r'decisive|crucial|defining', 'description': 'High-stakes language', 'hype_boost': 0.15, 'category': 'stakes', 'language': 'en'},
        {'pattern': r'do or die|all or nothing', 'description': 'Maximum stakes', 'hype_boost': 0.20, 'category': 'stakes', 'language': 'en'},

        # Scale (4 patterns)
        {'pattern': r'multitudinari|masiv|miles de|millones de', 'description': 'Massive scale indicators', 'hype_boost': 0.20, 'category': 'scale', 'language': 'es'},
        {'pattern': r'estadio lleno|sold out|agotado', 'description': 'Sold out/packed', 'hype_boost': 0.15, 'category': 'scale', 'language': 'es'},
        {'pattern': r'massive|thousands|millions', 'description': 'Massive scale', 'hype_boost': 0.20, 'category': 'scale', 'language': 'en'},
        {'pattern': r'sold out|packed|full stadium', 'description': 'Sold out stadium', 'hype_boost': 0.15, 'category': 'scale', 'language': 'en'},

        # Star Power (6 patterns)
        {'pattern': r'favorito|estrella|crack|figura|ídolo', 'description': 'Star athlete language', 'hype_boost': 0.10, 'category': 'star_power', 'language': 'es'},
        {'pattern': r'messi|ronaldo|neymar', 'description': 'Soccer superstars', 'hype_boost': 0.15, 'category': 'star_power', 'language': 'es'},
        {'pattern': r'canelo|pacquiao', 'description': 'Boxing stars', 'hype_boost': 0.10, 'category': 'star_power', 'language': 'es'},
        {'pattern': r'favorite|star|superstar', 'description': 'Star athletes', 'hype_boost': 0.10, 'category': 'star_power', 'language': 'en'},
        {'pattern': r'lebron|jordan|curry', 'description': 'Basketball legends', 'hype_boost': 0.10, 'category': 'star_power', 'language': 'en'},
        {'pattern': r'hamilton|verstappen', 'description': 'F1 stars', 'hype_boost': 0.10, 'category': 'star_power', 'language': 'en'},

        # Colombian Involvement (5 patterns)
        {'pattern': r'selección colombia|colombia vs|colombia contra', 'description': 'Colombian national team', 'hype_boost': 0.25, 'category': 'colombian', 'language': 'es'},
        {'pattern': r'egan bernal|nairo quintana|rigoberto urán', 'description': 'Colombian cycling stars', 'hype_boost': 0.20, 'category': 'colombian', 'language': 'es'},
        {'pattern': r'james rodríguez|falcao|cuadrado', 'description': 'Colombian soccer stars', 'hype_boost': 0.15, 'category': 'colombian', 'language': 'es'},
        {'pattern': r'colombiano participa|representante colombiano', 'description': 'Colombian participation', 'hype_boost': 0.15, 'category': 'colombian', 'language': 'es'},
        {'pattern': r'colombia|colombian', 'description': 'Colombia general', 'hype_boost': 0.10, 'category': 'colombian', 'language': 'en'},
    ]

    created_count = 0
    for indicator_data in indicators:
        indicator, created = HypeIndicator.objects.get_or_create(
            pattern=indicator_data['pattern'],
            category=indicator_data['category'],
            defaults=indicator_data
        )
        if created:
            print(f"✓ Created: [{indicator.category}] {indicator.pattern[:40]}... (+{indicator.hype_boost})")
            created_count += 1
        else:
            print(f"- Already exists: [{indicator.category}] {indicator.pattern[:40]}...")

    print(f"\nCreated {created_count}/{len(indicators)} hype indicators")


def seed_broadcastability_config():
    """Seed singleton BroadcastabilityConfig"""
    print("\n=== Seeding Broadcastability Config ===")

    config, created = BroadcastabilityConfig.objects.get_or_create(
        pk=1,
        defaults={
            'sport_appeal_weight': 0.35,
            'competition_level_weight': 0.30,
            'hype_indicators_weight': 0.20,
            'attendance_weight': 0.15,
            'min_broadcastability_score': 0.55,
            'attendance_small': 5000,
            'attendance_medium': 20000,
            'attendance_large': 50000,
            'requires_tv_screens': True,
        }
    )

    if created:
        print("✓ Created BroadcastabilityConfig (singleton)")
    else:
        print("- BroadcastabilityConfig already exists")


def main():
    print("\n" + "="*60)
    print("  BROADCASTABILITY TAXONOMY SEED SCRIPT (task-9.7)")
    print("="*60)

    seed_sport_types()
    seed_competition_levels()
    seed_hype_indicators()
    seed_broadcastability_config()

    print("\n" + "="*60)
    print("  ✓ SEEDING COMPLETE!")
    print("="*60)
    print("\nSummary:")
    print(f"  - Sport Types: {SportType.objects.count()}")
    print(f"  - Competition Levels: {CompetitionLevel.objects.count()}")
    print(f"  - Hype Indicators: {HypeIndicator.objects.count()}")
    print(f"  - Config: {BroadcastabilityConfig.objects.count()}")
    print("\nYou can now manage these via Django admin at:")
    print("  http://localhost:8000/admin/event_taxonomy/")


if __name__ == '__main__':
    main()
