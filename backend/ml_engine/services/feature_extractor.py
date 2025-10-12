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

        return {
            'event_type': self.extract_event_type(full_text),
            'city': self.extract_city(full_text),
            'neighborhood': self.extract_neighborhood(full_text),
            'venue': self.extract_venue(full_text),
            'event_date': self.extract_event_date(full_text),
            'attendance': self.extract_attendance(full_text),
            'scale': self.calculate_scale(full_text),
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
