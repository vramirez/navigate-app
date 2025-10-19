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
from typing import Dict, Any, Optional, List
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
        event_type = self.extract_event_type(full_text)
        city = self.extract_city(full_text)

        # Extract geographic and involvement features
        event_country = self.extract_event_country(full_text, city)
        colombian_involvement = self.detect_colombian_involvement(full_text)

        return {
            'event_type': event_type,
            'city': city,
            'neighborhood': self.extract_neighborhood(full_text),
            'venue': self.extract_venue(full_text),
            'event_date': self.extract_event_date(full_text),
            'attendance': self.extract_attendance(full_text),
            'scale': self.calculate_scale(full_text),
            'event_country': event_country,
            'colombian_involvement': colombian_involvement,
        }

    def extract_event_type(self, text: str) -> Optional[str]:
        """
        Classify event type based on pattern matching

        Returns:
            Event type string or None
        """
        text_lower = text.lower()

        # Count matches for each event type
        scores = {}
        for event_type, patterns in self.EVENT_TYPE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            if score > 0:
                scores[event_type] = score

        # Return type with highest score
        if scores:
            return max(scores, key=scores.get)

        return None

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

    def extract_event_date(self, text: str) -> Optional[datetime]:
        """
        Extract event date using dateparser (Spanish-aware)
        """
        # Common Spanish date patterns
        date_patterns = [
            r'el\s+pr[oó]ximo\s+(\d+\s+de\s+\w+)',
            r'el\s+(\d+\s+de\s+\w+)',
            r'del\s+(\d+)\s+al\s+(\d+)\s+de\s+(\w+)',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(0)
                parsed = dateparser.parse(date_str, languages=['es'], settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': timezone.now()
                })
                if parsed:
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
