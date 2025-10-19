"""
Feature Extractor Service

Extracts structured features from news articles:
- Event type classification
- Geographic data (city, neighborhood, venue)
- Temporal data (dates, times)
- Scale/attendance estimation
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
import dateparser

from .nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract structured features from news article text"""

    # Colombian cities (priority list)
    COLOMBIAN_CITIES = [
        'Medellín', 'Bogotá', 'Cali', 'Cartagena', 'Barranquilla',
        'Bucaramanga', 'Pereira', 'Manizales', 'Cúcuta', 'Ibagué',
        'Santa Marta', 'Pasto', 'Villavicencio', 'Montería', 'Valledupar'
    ]

    # International cities by country (for event_country detection)
    INTERNATIONAL_CITIES = {
        'México': ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Morelia', 'Puebla', 'Cancún', 'Tijuana'],
        'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata'],
        'Brasil': ['São Paulo', 'Río de Janeiro', 'Brasilia', 'Salvador', 'Belo Horizonte'],
        'Estados Unidos': ['Nueva York', 'Los Ángeles', 'Miami', 'Houston', 'Chicago', 'Las Vegas'],
        'España': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao'],
        'Chile': ['Santiago', 'Valparaíso', 'Concepción'],
        'Perú': ['Lima', 'Cuzco', 'Arequipa'],
        'Ecuador': ['Quito', 'Guayaquil', 'Cuenca'],
        'Qatar': ['Doha'],
        'Rusia': ['Moscú', 'San Petersburgo'],
        'Francia': ['París', 'Lyon', 'Marsella'],
        'Inglaterra': ['Londres', 'Manchester', 'Liverpool'],
    }

    # Medellín neighborhoods
    MEDELLIN_NEIGHBORHOODS = [
        'El Poblado', 'Laureles', 'Envigado', 'Belén', 'Estadio',
        'La Candelaria', 'Sabaneta', 'Itagüí', 'Bello', 'Robledo'
    ]

    # Event type patterns
    EVENT_TYPE_PATTERNS = {
        'sports_match': [
            r'partido\s+de\s+f[uú]tbol', r'partido.*contra', r'vs\.?', r'enfrentar[áa]',
            r'liga\s+de\s+f[uú]tbol', r'campeonato', r'clasificar', r'final\s+de'
        ],
        'marathon': [
            r'marat[oó]n', r'carrera\s+atl[eé]tica', r'\d+k\b', r'10k', r'21k', r'42k',
            r'media\s+marat[oó]n', r'carrera\s+recreativa', r'corredores'
        ],
        'concert': [
            r'concierto', r'show\s+musical', r'presentaci[oó]n.*musical',
            r'tocar[aá]', r'artista', r'cantante', r'm[uú]sica\s+en\s+vivo'
        ],
        'festival': [
            r'festival', r'feria', r'festividad', r'celebraci[oó]n',
            r'fest\b', r'carnaval'
        ],
        'conference': [
            r'conferencia', r'congreso', r'simposio', r'seminario',
            r'taller', r'charla', r'foro', r'encuentro\s+empresarial'
        ],
        'exposition': [
            r'exposici[oó]n', r'muestra', r'exhibici[oó]n', r'galer[ií]a',
            r'arte\s+contempor[aá]neo', r'museo'
        ],
        'food_event': [
            r'gastron[oó]mico', r'culinario', r'chef', r'degustaci[oó]n',
            r'comida', r'festival\s+de\s+comida', r'cocina'
        ],
        'cultural': [
            r'cultural', r'teatro', r'danza', r'[oó]pera', r'ballet',
            r'obra\s+de\s+teatro', r'obra\s+teatral'
        ],
        'nightlife': [
            r'fiesta', r'rumba', r'discoteca', r'club\s+nocturno',
            r'vida\s+nocturna', r'bar\s+', r'pub\s+'
        ],
        # Low-relevance event types (should be filtered by PreFilter)
        'politics': [
            r'pol[ií]tica', r'gobierno', r'congreso', r'senado', r'c[aá]mara',
            r'legislaci[oó]n', r'proyecto\s+de\s+ley', r'ministro', r'presidente',
            r'alcalde', r'gobernador', r'elecciones', r'votaci[oó]n', r'partido\s+pol[ií]tico'
        ],
        'international': [
            r'internacional', r'extranjero', r'exterior', r'mundial',
            r'estados\s+unidos', r'europa', r'asia', r'áfrica',
            r'otan', r'onu', r'diplomacia', r'embajada', r'pa[ií]ses'
        ],
        'conflict': [
            r'bombardeo', r'ataque', r'guerra', r'militar', r'ej[eé]rcito',
            r'conflicto\s+armado', r'operaci[oó]n\s+militar', r'ofensiva',
            r'tropas', r'misil', r'drone', r'combate'
        ],
        'crime': [
            r'homicidio', r'asesinato', r'crimen', r'delincuencia',
            r'robo', r'atraco', r'hurto', r'secuestro', r'narcotr[aá]fico'
        ]
    }

    # Attendance patterns
    ATTENDANCE_PATTERNS = [
        r'(\d+[,.]?\d*)\s*mil\s+(?:personas|asistentes|espectadores|hinchas)',
        r'm[aá]s\s+de\s+(\d+[,.]?\d*)',
        r'hasta\s+(\d+[,.]?\d*)',
        r'(\d+[,.]?\d*)\s+(?:personas|asistentes|espectadores)',
    ]

    def __init__(self):
        self.nlp = NLPProcessor()
        # Pattern caching to avoid DB queries on every extraction
        self._pattern_cache = None
        self._cache_timestamp = None
        self.CACHE_DURATION = 300  # 5 minutes

    def _load_patterns_cached(self):
        """Load extraction patterns from database with 5-minute cache"""
        from django.utils import timezone

        now = timezone.now()

        # Check if cache is valid
        if (self._pattern_cache is None or
            self._cache_timestamp is None or
            (now - self._cache_timestamp).seconds > self.CACHE_DURATION):

            # Reload from database
            from event_taxonomy.models import ExtractionPattern

            self._pattern_cache = list(
                ExtractionPattern.objects.filter(is_active=True)
                .select_related('event_type', 'event_subtype')
            )
            self._cache_timestamp = now
            logger.info(f"Loaded {len(self._pattern_cache)} extraction patterns from database")

        return self._pattern_cache

    def extract_all(self, article_text: str, article_title: str = "") -> Dict[str, Any]:
        """
        Extract all features from article

        Args:
            article_text: Full article content
            article_title: Article title

        Returns:
            Dictionary with all extracted features
        """
        full_text = f"{article_title} {article_text}"

        # Extract basic features
        event_type, event_subtype = self.extract_event_type(full_text)
        city = self.extract_city(full_text)

        # Extract geographic and involvement features
        event_country = self.extract_event_country(full_text, city)
        colombian_involvement = self.detect_colombian_involvement(full_text)

        # Extract temporal features
        event_start = self.extract_event_date(full_text)
        duration_hours = self.extract_duration(full_text)

        # Calculate end datetime if we have both start and duration
        event_end = None
        if event_start and duration_hours:
            event_end = event_start + timedelta(hours=duration_hours)

        # Extract NLP features (keywords and entities)
        keywords = self.nlp.get_keywords(full_text, top_n=15)
        entities = self.nlp.extract_entities(full_text)

        return {
            'event_type': event_type,
            'event_subtype': event_subtype,
            'city': city,
            'neighborhood': self.extract_neighborhood(full_text),
            'venue': self.extract_venue(full_text),
            'event_date': event_start,
            'event_end_datetime': event_end,
            'event_duration_hours': duration_hours,
            'attendance': self.extract_attendance(full_text),
            'scale': self.calculate_scale(full_text),
            'event_country': event_country,
            'colombian_involvement': colombian_involvement,
            'keywords': keywords,
            'entities': entities,
        }

    def extract_event_type(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Classify event type AND subtype using database patterns with hardcoded fallback

        Args:
            text: Article title + content

        Returns:
            Tuple of (event_type_code, event_subtype_code)
            Example: ('sports_match', 'colombian_soccer') or ('concert', None)
        """
        text_lower = text.lower()

        # Load patterns from database (cached)
        patterns = self._load_patterns_cached()

        # Score event types from database
        type_scores = {}
        for pattern_obj in patterns:
            if pattern_obj.target == 'type':
                matches = len(re.findall(pattern_obj.pattern, text_lower))
                if matches > 0:
                    event_type_code = pattern_obj.event_type.code
                    score = matches * pattern_obj.weight
                    type_scores[event_type_code] = type_scores.get(event_type_code, 0) + score

        # FALLBACK: Use hardcoded EVENT_TYPE_PATTERNS if no database matches
        if not type_scores:
            for event_type, patterns_list in self.EVENT_TYPE_PATTERNS.items():
                for pattern in patterns_list:
                    matches = len(re.findall(pattern, text_lower))
                    if matches > 0:
                        # Default weight of 1.0 for hardcoded patterns
                        type_scores[event_type] = type_scores.get(event_type, 0) + matches

        # Get best type
        best_type = max(type_scores, key=type_scores.get) if type_scores else None

        # If no type detected, return early
        if not best_type:
            return (None, None)

        # Score subtypes for the best type (only from database - hardcoded patterns don't have subtypes)
        subtype_scores = {}
        for pattern_obj in patterns:
            if (pattern_obj.target == 'subtype' and
                pattern_obj.event_type and
                pattern_obj.event_type.code == best_type):
                matches = len(re.findall(pattern_obj.pattern, text_lower))
                if matches > 0:
                    subtype_code = pattern_obj.event_subtype.code
                    score = matches * pattern_obj.weight
                    subtype_scores[subtype_code] = subtype_scores.get(subtype_code, 0) + score

        # Get best subtype (may be None - that's okay)
        best_subtype = max(subtype_scores, key=subtype_scores.get) if subtype_scores else None

        return (best_type, best_subtype)

    def extract_city(self, text: str) -> Optional[str]:
        """Extract primary city from text"""
        locations = self.nlp.extract_locations(text)

        # Check for Colombian cities in extracted locations
        for loc in locations:
            for city in self.COLOMBIAN_CITIES:
                if city.lower() in loc.lower():
                    return city

        # Fallback: search directly in text
        for city in self.COLOMBIAN_CITIES:
            if city.lower() in text.lower():
                return city

        return None

    def extract_neighborhood(self, text: str) -> Optional[str]:
        """Extract neighborhood (currently only Medellín)"""
        for neighborhood in self.MEDELLIN_NEIGHBORHOODS:
            if neighborhood.lower() in text.lower():
                return neighborhood
        return None

    def extract_venue(self, text: str) -> Optional[str]:
        """
        Extract venue name using organizations and noun chunks
        """
        # Get organizations (stadiums, theaters are usually ORG entities)
        orgs = self.nlp.extract_organizations(text)

        # Filter for venue-like names
        venue_keywords = ['estadio', 'teatro', 'centro', 'auditorio', 'coliseo', 'arena', 'parque']
        for org in orgs:
            if any(keyword in org.lower() for keyword in venue_keywords):
                return org

        # Fallback: look for patterns like "en el Estadio X"
        venue_pattern = r'en\s+el\s+((?:Estadio|Teatro|Centro|Auditorio|Coliseo|Arena|Parque)\s+[A-ZÁ-Ú][a-zá-ú\s]+)'
        match = re.search(venue_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    def extract_event_time(self, text: str) -> Optional[str]:
        """
        Extract event time from text

        Returns:
            Time string in HH:MM format or None
        """
        # Time patterns (Spanish)
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(?:horas?|hrs?|h)?',  # 20:00, 8:30 h
            r'(\d{1,2})\s*(?:pm|p\.m\.|de\s+la\s+tarde|de\s+la\s+noche)',  # 8 pm, 8 de la tarde
            r'(\d{1,2})\s*(?:am|a\.m\.|de\s+la\s+mañana)',  # 9 am, 9 de la mañana
            r'a\s+las\s+(\d{1,2}):?(\d{2})?',  # a las 20:00, a las 8
        ]

        text_lower = text.lower()

        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0

                # Handle PM/AM notation
                if 'pm' in match.group(0) or 'tarde' in match.group(0) or 'noche' in match.group(0):
                    if hour < 12:
                        hour += 12
                elif 'am' in match.group(0) or 'mañana' in match.group(0):
                    if hour == 12:
                        hour = 0

                return f"{hour:02d}:{minute:02d}"

        return None

    def extract_event_date(self, text: str) -> Optional[datetime]:
        """
        Extract event date using multiple strategies:
        1. spaCy DATE entities (highest priority)
        2. Comprehensive Spanish regex patterns
        3. dateparser library (fallback)

        Returns:
            datetime object with extracted date (and time if found)
        """
        now = timezone.now()

        # Strategy 1: Use spaCy DATE entities first
        date_entities = self.nlp.extract_dates(text)
        if date_entities:
            for date_str in date_entities:
                parsed = dateparser.parse(date_str, languages=['es'], settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': now
                })
                if parsed and parsed > now - timedelta(days=30):  # Ignore dates more than 30 days in past
                    # Try to extract time and combine
                    time_str = self.extract_event_time(text)
                    if time_str:
                        hour, minute = map(int, time_str.split(':'))
                        parsed = parsed.replace(hour=hour, minute=minute)
                    return parsed

        # Strategy 2: Comprehensive Spanish date regex patterns
        date_patterns = [
            # Weekday + date: "sábado 15 de marzo", "viernes 20 de abril de 2025"
            r'(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\s+(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?)',

            # Standard: "el próximo 15 de marzo", "el 15 de marzo de 2025"
            r'el\s+pr[oó]ximo\s+(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?)',
            r'el\s+(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?)',

            # Ranges: "del 15 al 20 de marzo", "entre el 15 y 20 de marzo"
            r'del\s+(\d{1,2})\s+al\s+\d{1,2}\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?',
            r'entre\s+el\s+(\d{1,2})\s+y\s+\d{1,2}\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?',

            # Numeric: "15/03/2025", "15-03-2025", "2025-03-15"
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',

            # Month first: "marzo 15", "abril 15 de 2025"
            r'(\w+)\s+(\d{1,2})(?:\s+de\s+(\d{4}))?',

            # Relative: "mañana", "pasado mañana", "este fin de semana"
            r'(ma[ñn]ana)',
            r'(pasado\s+ma[ñn]ana)',
            r'(este\s+(?:fin\s+de\s+semana|s[aá]bado|domingo|lunes|martes|mi[eé]rcoles|jueves|viernes))',
            r'(pr[oó]ximo\s+(?:fin\s+de\s+semana|s[aá]bado|domingo|lunes|martes|mi[eé]rcoles|jueves|viernes))',

            # Starting from: "a partir del 15 de marzo"
            r'a\s+partir\s+del?\s+(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?)',
        ]

        text_lower = text.lower()

        for pattern in date_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                date_str = match.group(0)

                # Strategy 3: Parse with dateparser
                parsed = dateparser.parse(date_str, languages=['es'], settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': now,
                    'PREFER_DAY_OF_MONTH': 'first'
                })

                if parsed:
                    # Ignore dates more than 30 days in past (unless clearly historical)
                    if parsed < now - timedelta(days=30):
                        continue

                    # Try to extract and combine time
                    time_str = self.extract_event_time(text)
                    if time_str:
                        hour, minute = map(int, time_str.split(':'))
                        parsed = parsed.replace(hour=hour, minute=minute)

                    return parsed

        return None

    def extract_attendance(self, text: str) -> Optional[int]:
        """Extract expected attendance number"""
        for pattern in self.ATTENDANCE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number_str = match.group(1).replace('.', '').replace(',', '')
                try:
                    number = float(number_str)
                    # If pattern mentions "mil" (thousand), multiply
                    if 'mil' in match.group(0).lower():
                        number *= 1000
                    return int(number)
                except ValueError:
                    continue

        return None

    def extract_duration(self, text: str) -> Optional[float]:
        """
        Extract event duration in hours

        Returns:
            Duration in hours as float, or None
        """
        text_lower = text.lower()

        # Duration patterns
        duration_patterns = [
            (r'(\d+)\s*horas?', 1.0),  # "3 horas"
            (r'(\d+)\s*d[ií]as?', 24.0),  # "2 días"
            (r'todo\s+el\s+d[ií]a', None, 12.0),  # "todo el día" = 12 hours
            (r'toda\s+la\s+noche', None, 8.0),  # "toda la noche" = 8 hours
            (r'fin\s+de\s+semana', None, 48.0),  # "fin de semana" = 48 hours
            (r'una\s+semana', None, 168.0),  # "una semana" = 168 hours
            (r'(\d+)\s*semanas?', 168.0),  # "2 semanas"
            (r'(\d+)\s*minutos?', 1.0/60.0),  # "30 minutos"
        ]

        for pattern_info in duration_patterns:
            if len(pattern_info) == 2:
                pattern, multiplier = pattern_info
                match = re.search(pattern, text_lower)
                if match and match.group(1):
                    return float(match.group(1)) * multiplier
            else:
                pattern, _, fixed_value = pattern_info
                if re.search(pattern, text_lower):
                    return fixed_value

        return None

    def calculate_scale(self, text: str) -> Optional[str]:
        """Calculate event scale based on attendance and keywords"""
        attendance = self.extract_attendance(text)

        if attendance:
            if attendance < 500:
                return 'small'
            elif attendance < 5000:
                return 'medium'
            elif attendance < 50000:
                return 'large'
            else:
                return 'massive'

        # Fallback: keyword-based detection
        text_lower = text.lower()
        if any(word in text_lower for word in ['masivo', 'multitudinario', 'miles de personas']):
            return 'massive'
        elif any(word in text_lower for word in ['gran', 'importante', 'nacional']):
            return 'large'

        return 'medium'  # Default

    def detect_colombian_involvement(self, text: str) -> bool:
        """
        Detect if event involves Colombia or Colombians

        Returns True if:
        - Colombian national team/selection participates
        - Colombian artist/athlete/director participates
        - Event directly affects Colombia

        Args:
            text: Article title + content

        Returns:
            Boolean indicating Colombian involvement
        """
        patterns = [
            r'selección\s+colombia',
            r'colombia\s+(vs|contra)\s+',
            r'colombiano[sa]?\s+(participa|compite|juega|dirige|actúa|presenta)',
            r'(artista|director|atleta|actor|actriz)\s+colombiano',
            r'equipo\s+colombiano',
            r'representante\s+de\s+colombia',
            r'colombia\s+en\s+(la\s+)?(copa|mundial|olimpiadas|festival|ceremonia)',
            r'(jugador|jugadora)\s+colombiano',
            r'seleccionado\s+colombiano',
        ]

        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in patterns)

    def extract_event_country(self, text: str, primary_city: str) -> str:
        """
        Determine event country from text and extracted city

        Priority:
        1. Check if primary_city is Colombian
        2. Check if primary_city is in INTERNATIONAL_CITIES
        3. Parse country mentions from text patterns

        Args:
            text: Article title + content
            primary_city: Extracted city name

        Returns:
            Country name ('Colombia', 'México', etc.) or empty string
        """
        # Check if city is Colombian
        if primary_city and primary_city in self.COLOMBIAN_CITIES:
            return 'Colombia'

        # Check if city is in international cities dict
        for country, cities in self.INTERNATIONAL_CITIES.items():
            if primary_city and primary_city in cities:
                return country

        # Parse country from text patterns
        text_lower = text.lower()

        # Pattern: "en México", "en Argentina", etc.
        country_patterns = {
            r'\ben\s+m[eé]xico\b': 'México',
            r'\ben\s+argentina\b': 'Argentina',
            r'\ben\s+brasil\b': 'Brasil',
            r'\ben\s+(los\s+)?estados\s+unidos\b': 'Estados Unidos',
            r'\ben\s+espa[ñn]a\b': 'España',
            r'\ben\s+chile\b': 'Chile',
            r'\ben\s+per[uú]\b': 'Perú',
            r'\ben\s+ecuador\b': 'Ecuador',
            r'\ben\s+qatar\b': 'Qatar',
            r'\ben\s+rusia\b': 'Rusia',
            r'\ben\s+francia\b': 'Francia',
            r'\ben\s+inglaterra\b': 'Inglaterra',
        }

        for pattern, country in country_patterns.items():
            if re.search(pattern, text_lower):
                return country

        # Pattern: "festival de Morelia", "copa de Rusia", etc.
        if 'morelia' in text_lower or 'guadalajara' in text_lower:
            return 'México'
        if 'buenos aires' in text_lower or 'río de la plata' in text_lower:
            return 'Argentina'
        if 'doha' in text_lower or 'qatar' in text_lower:
            return 'Qatar'
        if 'moscú' in text_lower or 'rusia' in text_lower:
            return 'Rusia'

        return ''  # Unknown/not detected
