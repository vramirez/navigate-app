# Generated seed data migration for event_taxonomy
from django.db import migrations


def seed_event_data(apps, schema_editor):
    """Seed initial event types, subtypes, and extraction patterns"""
    EventType = apps.get_model('event_taxonomy', 'EventType')
    EventSubtype = apps.get_model('event_taxonomy', 'EventSubtype')
    ExtractionPattern = apps.get_model('event_taxonomy', 'ExtractionPattern')
    
    # Event types with their metadata
    event_types_data = [
        {
            'code': 'sports_match',
            'name_es': 'Partido Deportivo',
            'name_en': 'Sports Match',
            'description': 'Competitive sports events (soccer, basketball, volleyball, tennis, etc.)',
            'relevance_category': 'high',
            'icon': 'trophy',
            'display_order': 1,
        },
        {
            'code': 'concert',
            'name_es': 'Concierto',
            'name_en': 'Concert',
            'description': 'Live musical performances and shows',
            'relevance_category': 'high',
            'icon': 'music',
            'display_order': 2,
        },
        {
            'code': 'festival',
            'name_es': 'Festival',
            'name_en': 'Festival',
            'description': 'Cultural, food, music, and entertainment festivals',
            'relevance_category': 'high',
            'icon': 'calendar-star',
            'display_order': 3,
        },
        {
            'code': 'marathon',
            'name_es': 'Maratón/Carrera',
            'name_en': 'Marathon/Race',
            'description': 'Running, cycling, triathlon, and athletic race events',
            'relevance_category': 'high',
            'icon': 'person-running',
            'display_order': 4,
        },
        {
            'code': 'conference',
            'name_es': 'Conferencia/Congreso',
            'name_en': 'Conference',
            'description': 'Business, academic, and professional conferences',
            'relevance_category': 'medium',
            'icon': 'users',
            'display_order': 5,
        },
        {
            'code': 'exposition',
            'name_es': 'Exposición',
            'name_en': 'Exhibition',
            'description': 'Art, photography, and technology exhibitions',
            'relevance_category': 'medium',
            'icon': 'palette',
            'display_order': 6,
        },
        {
            'code': 'food_event',
            'name_es': 'Evento Gastronómico',
            'name_en': 'Food Event',
            'description': 'Tastings, culinary competitions, cooking workshops',
            'relevance_category': 'high',
            'icon': 'utensils',
            'display_order': 7,
        },
        {
            'code': 'cultural',
            'name_es': 'Evento Cultural',
            'name_en': 'Cultural Event',
            'description': 'Theater, dance, opera, cinema, performing arts',
            'relevance_category': 'medium',
            'icon': 'masks-theater',
            'display_order': 8,
        },
        {
            'code': 'nightlife',
            'name_es': 'Vida Nocturna',
            'name_en': 'Nightlife',
            'description': 'Parties, nightclubs, bar events, nighttime entertainment',
            'relevance_category': 'high',
            'icon': 'moon-stars',
            'display_order': 9,
        },
        {
            'code': 'politics',
            'name_es': 'Política',
            'name_en': 'Politics',
            'description': 'Political and governmental events (low business relevance)',
            'relevance_category': 'low',
            'icon': 'landmark',
            'display_order': 10,
        },
        {
            'code': 'international',
            'name_es': 'Internacional',
            'name_en': 'International',
            'description': 'General international news (low business relevance)',
            'relevance_category': 'low',
            'icon': 'globe',
            'display_order': 11,
        },
        {
            'code': 'conflict',
            'name_es': 'Conflicto/Guerra',
            'name_en': 'Conflict/War',
            'description': 'Armed conflicts and military operations (low business relevance)',
            'relevance_category': 'low',
            'icon': 'shield-exclamation',
            'display_order': 12,
        },
        {
            'code': 'crime',
            'name_es': 'Crimen',
            'name_en': 'Crime',
            'description': 'Crime and security news (low business relevance)',
            'relevance_category': 'low',
            'icon': 'triangle-exclamation',
            'display_order': 13,
        },
    ]
    
    # Create event types
    event_types = {}
    for et_data in event_types_data:
        et = EventType.objects.create(**et_data)
        event_types[et.code] = et
    
    # Subtypes data (code, parent_code, name_es, name_en, description)
    subtypes_data = [
        # Sports subtypes
        ('colombian_soccer', 'sports_match', 'Fútbol Colombiano', 'Colombian Soccer', 'Colombian national team or Colombian club teams'),
        ('international_soccer', 'sports_match', 'Fútbol Internacional', 'International Soccer', 'International matches without Colombian participation'),
        ('basketball', 'sports_match', 'Baloncesto', 'Basketball', 'Basketball games and tournaments'),
        ('volleyball', 'sports_match', 'Voleibol', 'Volleyball', 'Volleyball matches and events'),
        ('tennis', 'sports_match', 'Tenis', 'Tennis', 'Tennis tournaments and matches'),
        ('cycling', 'sports_match', 'Ciclismo', 'Cycling', 'Cycling races and competitions'),
        
        # Concert subtypes
        ('rock_concert', 'concert', 'Concierto de Rock', 'Rock Concert', 'Rock, metal, and punk concerts'),
        ('pop_concert', 'concert', 'Concierto Pop', 'Pop Concert', 'Pop music concerts'),
        ('classical_concert', 'concert', 'Concierto Clásico', 'Classical Concert', 'Classical music, orchestras, symphonies'),
        ('reggaeton_concert', 'concert', 'Concierto de Reggaeton', 'Reggaeton Concert', 'Urban music and reggaeton concerts'),
        ('electronic_concert', 'concert', 'Concierto Electrónico', 'Electronic Concert', 'DJ, electronic music, techno events'),
        ('salsa_concert', 'concert', 'Concierto de Salsa', 'Salsa Concert', 'Salsa and tropical music concerts'),
        ('vallenato_concert', 'concert', 'Concierto de Vallenato', 'Vallenato Concert', 'Vallenato and traditional Colombian music'),
        
        # Festival subtypes
        ('food_festival', 'festival', 'Festival Gastronómico', 'Food Festival', 'Food and gastronomy festivals'),
        ('music_festival', 'festival', 'Festival Musical', 'Music Festival', 'Multi-genre music festivals'),
        ('cultural_festival', 'festival', 'Festival Cultural', 'Cultural Festival', 'Cultural and traditional festivals'),
        ('film_festival', 'festival', 'Festival de Cine', 'Film Festival', 'Film festivals and cinema showcases'),
        ('arts_festival', 'festival', 'Festival de Artes', 'Arts Festival', 'Visual and performing arts festivals'),
        ('beer_festival', 'festival', 'Festival de Cerveza', 'Beer Festival', 'Beer festivals and oktoberfest events'),
        
        # Marathon subtypes
        ('running_race', 'marathon', 'Carrera de Running', 'Running Race', 'Marathons and running races'),
        ('cycling_race', 'marathon', 'Carrera de Ciclismo', 'Cycling Race', 'Mountain biking and road cycling races'),
        ('triathlon', 'marathon', 'Triatlón', 'Triathlon', 'Triathlons and multi-sport events'),
        
        # Conference subtypes
        ('business_conference', 'conference', 'Conferencia de Negocios', 'Business Conference', 'Business events and networking'),
        ('tech_conference', 'conference', 'Conferencia de Tecnología', 'Tech Conference', 'Technology and innovation events'),
        ('academic_conference', 'conference', 'Conferencia Académica', 'Academic Conference', 'Academic seminars and congresses'),
        
        # Exposition subtypes
        ('art_exhibition', 'exposition', 'Exhibición de Arte', 'Art Exhibition', 'Art exhibitions and galleries'),
        ('photo_exhibition', 'exposition', 'Exhibición Fotográfica', 'Photo Exhibition', 'Photography exhibitions'),
        ('tech_expo', 'exposition', 'Expo de Tecnología', 'Tech Expo', 'Technology fairs and expos'),
        
        # Food event subtypes
        ('tasting_event', 'food_event', 'Degustación', 'Tasting Event', 'Food and beverage tastings'),
        ('cooking_competition', 'food_event', 'Competencia Culinaria', 'Cooking Competition', 'Cooking and chef competitions'),
        ('cooking_workshop', 'food_event', 'Taller de Cocina', 'Cooking Workshop', 'Cooking classes and workshops'),
        
        # Cultural subtypes
        ('theater', 'cultural', 'Teatro', 'Theater', 'Theater plays and performances'),
        ('dance', 'cultural', 'Danza', 'Dance', 'Dance shows and ballet'),
        ('opera', 'cultural', 'Ópera', 'Opera', 'Opera performances'),
        ('cinema', 'cultural', 'Cine', 'Cinema', 'Movie premieres and screenings'),
        
        # Nightlife subtypes
        ('club_party', 'nightlife', 'Fiesta en Discoteca', 'Club Party', 'Nightclub and club parties'),
        ('bar_event', 'nightlife', 'Evento en Bar', 'Bar Event', 'Bar and pub events'),
    ]
    
    # Create subtypes
    subtypes = {}
    for st_code, et_code, name_es, name_en, description in subtypes_data:
        st = EventSubtype.objects.create(
            code=st_code,
            event_type=event_types[et_code],
            name_es=name_es,
            name_en=name_en,
            description=description,
        )
        subtypes[st_code] = st
    
    # Patterns data: (target, type_code, subtype_code, pattern, description, weight)
    # NOTE: patterns are in SPANISH because they search Spanish article text
    patterns_data = [
        # Sports match TYPE patterns
        ('type', 'sports_match', None, r'partido\s+de\s+f[uú]tbol', 'Soccer match', 1.5),
        ('type', 'sports_match', None, r'partido.*contra', 'Match against', 1.2),
        ('type', 'sports_match', None, r'vs\.?', 'Versus', 1.0),
        ('type', 'sports_match', None, r'enfrentar[áa]', 'Will face/faces', 1.2),
        ('type', 'sports_match', None, r'liga\s+de\s+f[uú]tbol', 'Soccer league', 1.3),
        ('type', 'sports_match', None, r'campeonato', 'Championship', 1.1),
        ('type', 'sports_match', None, r'final\s+de', 'Final of', 1.4),
        
        # Colombian soccer SUBTYPE patterns
        ('subtype', 'sports_match', 'colombian_soccer', r'selección\s+colombia', 'Colombian national team', 2.0),
        ('subtype', 'sports_match', 'colombian_soccer', r'colombia\s+(vs|contra)', 'Colombia vs', 2.0),
        ('subtype', 'sports_match', 'colombian_soccer', r'tricolor', 'Tricolor (national team nickname)', 1.5),
        ('subtype', 'sports_match', 'colombian_soccer', r'james\s+rodr[ií]guez', 'James Rodriguez (player)', 1.3),
        ('subtype', 'sports_match', 'colombian_soccer', r'luis\s+d[ií]az', 'Luis Diaz (player)', 1.3),
        ('subtype', 'sports_match', 'colombian_soccer', r'radamel\s+falcao', 'Radamel Falcao (player)', 1.3),
        
        # International soccer SUBTYPE patterns
        ('subtype', 'sports_match', 'international_soccer', r'champions\s+league', 'Champions League', 1.5),
        ('subtype', 'sports_match', 'international_soccer', r'premier\s+league', 'Premier League', 1.3),
        ('subtype', 'sports_match', 'international_soccer', r'la\s+liga', 'La Liga', 1.3),
        ('subtype', 'sports_match', 'international_soccer', r'serie\s+a', 'Serie A', 1.2),
        ('subtype', 'sports_match', 'international_soccer', r'real\s+madrid|barcelona|manchester', 'Top European clubs', 1.1),
        
        # Basketball SUBTYPE patterns
        ('subtype', 'sports_match', 'basketball', r'baloncesto', 'Basketball', 2.0),
        ('subtype', 'sports_match', 'basketball', r'nba', 'NBA', 1.8),
        ('subtype', 'sports_match', 'basketball', r'básquet', 'Basketball (alternative spelling)', 1.5),
        
        # Concert TYPE patterns
        ('type', 'concert', None, r'concierto', 'Concert', 2.0),
        ('type', 'concert', None, r'show\s+musical', 'Musical show', 1.5),
        ('type', 'concert', None, r'presentaci[oó]n.*musical', 'Musical presentation', 1.3),
        ('type', 'concert', None, r'tocar[áa]', 'Will play/plays', 1.2),
        ('type', 'concert', None, r'artista', 'Artist', 1.0),
        ('type', 'concert', None, r'cantante', 'Singer', 1.1),
        ('type', 'concert', None, r'm[uú]sica\s+en\s+vivo', 'Live music', 1.4),
        
        # Rock concert SUBTYPE patterns
        ('subtype', 'concert', 'rock_concert', r'\brock\b', 'Rock', 2.0),
        ('subtype', 'concert', 'rock_concert', r'\bmetal\b', 'Metal', 1.8),
        ('subtype', 'concert', 'rock_concert', r'\bpunk\b', 'Punk', 1.5),
        ('subtype', 'concert', 'rock_concert', r'metallica|iron\s+maiden|ac/dc', 'Famous rock bands', 1.5),
        
        # Pop concert SUBTYPE patterns
        ('subtype', 'concert', 'pop_concert', r'\bpop\b', 'Pop', 2.0),
        ('subtype', 'concert', 'pop_concert', r'm[uú]sica\s+popular', 'Popular music', 1.3),
        ('subtype', 'concert', 'pop_concert', r'shakira|maluma|karol\s+g', 'Latin pop artists', 1.5),
        
        # Reggaeton concert SUBTYPE patterns
        ('subtype', 'concert', 'reggaeton_concert', r'reggaeton|reguetón', 'Reggaeton', 2.0),
        ('subtype', 'concert', 'reggaeton_concert', r'm[uú]sica\s+urbana', 'Urban music', 1.5),
        ('subtype', 'concert', 'reggaeton_concert', r'daddy\s+yankee|bad\s+bunny|j\s+balvin', 'Urban artists', 1.5),
        
        # Classical concert SUBTYPE patterns
        ('subtype', 'concert', 'classical_concert', r'cl[aá]sica', 'Classical', 2.0),
        ('subtype', 'concert', 'classical_concert', r'orquesta', 'Orchestra', 1.8),
        ('subtype', 'concert', 'classical_concert', r'sinfon[ií]a', 'Symphony', 1.7),
        
        # Festival TYPE patterns
        ('type', 'festival', None, r'festival', 'Festival', 2.0),
        ('type', 'festival', None, r'feria', 'Fair', 1.5),
        ('type', 'festival', None, r'festividad', 'Festivity', 1.3),
        ('type', 'festival', None, r'celebraci[oó]n', 'Celebration', 1.1),
        ('type', 'festival', None, r'carnaval', 'Carnival', 1.5),
        
        # Food festival SUBTYPE patterns
        ('subtype', 'festival', 'food_festival', r'festival.*gastron[oó]mic', 'Gastronomic festival', 2.0),
        ('subtype', 'festival', 'food_festival', r'festival.*comida', 'Food festival', 2.0),
        ('subtype', 'festival', 'food_festival', r'feria.*gastron[oó]mica', 'Gastronomic fair', 1.8),
        
        # Film festival SUBTYPE patterns
        ('subtype', 'festival', 'film_festival', r'festival.*cine', 'Film festival', 2.0),
        ('subtype', 'festival', 'film_festival', r'muestra.*cinematogr[aá]fica', 'Cinema showcase', 1.8),
        ('subtype', 'festival', 'film_festival', r'festival.*cortometrajes', 'Short film festival', 1.7),
        
        # Music festival SUBTYPE patterns
        ('subtype', 'festival', 'music_festival', r'festival.*m[uú]sica', 'Music festival', 2.0),
        ('subtype', 'festival', 'music_festival', r'fest.*rock|rock.*fest', 'Rock festival', 1.8),
        ('subtype', 'festival', 'music_festival', r'stereo\s+picnic|festival\s+estereo', 'Colombian music festivals', 1.9),
        
        # Marathon TYPE patterns
        ('type', 'marathon', None, r'marat[oó]n', 'Marathon', 2.0),
        ('type', 'marathon', None, r'carrera\s+atl[eé]tica', 'Athletic race', 1.8),
        ('type', 'marathon', None, r'\d+k\b|10k|21k|42k', 'Race distance (kilometers)', 1.5),
        ('type', 'marathon', None, r'media\s+marat[oó]n', 'Half marathon', 1.7),
        ('type', 'marathon', None, r'corredores', 'Runners', 1.2),
        
        # Conference TYPE patterns
        ('type', 'conference', None, r'conferencia', 'Conference', 1.8),
        ('type', 'conference', None, r'congreso', 'Congress', 1.7),
        ('type', 'conference', None, r'simposio', 'Symposium', 1.5),
        ('type', 'conference', None, r'seminario', 'Seminar', 1.4),
        ('type', 'conference', None, r'taller', 'Workshop', 1.2),
        
        # Food event TYPE patterns
        ('type', 'food_event', None, r'gastron[oó]mico', 'Gastronomic', 1.8),
        ('type', 'food_event', None, r'culinario', 'Culinary', 1.7),
        ('type', 'food_event', None, r'\bchef\b', 'Chef', 1.3),
        ('type', 'food_event', None, r'degustaci[oó]n', 'Tasting', 1.6),
        
        # Cultural TYPE patterns
        ('type', 'cultural', None, r'cultural', 'Cultural', 1.5),
        ('type', 'cultural', None, r'\bteatro\b', 'Theater', 1.7),
        ('type', 'cultural', None, r'\bdanza\b', 'Dance', 1.6),
        ('type', 'cultural', None, r'[oó]pera', 'Opera', 1.8),
        ('type', 'cultural', None, r'ballet', 'Ballet', 1.7),
        ('type', 'cultural', None, r'obra\s+de\s+teatro', 'Theater play', 1.8),
        
        # Nightlife TYPE patterns
        ('type', 'nightlife', None, r'fiesta', 'Party', 1.5),
        ('type', 'nightlife', None, r'rumba', 'Party (Colombian slang)', 1.7),
        ('type', 'nightlife', None, r'discoteca', 'Nightclub', 1.8),
        ('type', 'nightlife', None, r'club\s+nocturno', 'Night club', 1.7),
        
        # Low-relevance types (politics, conflict, crime) - minimal patterns
        ('type', 'politics', None, r'pol[ií]tica|gobierno|congreso', 'Politics/government', 1.0),
        ('type', 'conflict', None, r'bombardeo|guerra|militar', 'Conflict/war', 1.0),
        ('type', 'crime', None, r'homicidio|crimen|robo', 'Crime', 1.0),
    ]
    
    # Create patterns
    for target, type_code, subtype_code, pattern, description, weight in patterns_data:
        ExtractionPattern.objects.create(
            target=target,
            event_type=event_types[type_code],
            event_subtype=subtypes.get(subtype_code) if subtype_code else None,
            pattern=pattern,
            description=description,
            weight=weight,
        )


def reverse_seed(apps, schema_editor):
    """Delete all seeded data"""
    EventType = apps.get_model('event_taxonomy', 'EventType')
    EventSubtype = apps.get_model('event_taxonomy', 'EventSubtype')
    ExtractionPattern = apps.get_model('event_taxonomy', 'ExtractionPattern')
    
    ExtractionPattern.objects.all().delete()
    EventSubtype.objects.all().delete()
    EventType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('event_taxonomy', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_event_data, reverse_seed),
    ]
