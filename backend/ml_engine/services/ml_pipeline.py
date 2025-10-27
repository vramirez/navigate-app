"""
ML Pipeline - Complete integration of all ML services

This file combines prefilter, geographic matcher, business matcher,
and recommendation generator into one cohesive pipeline.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from news.models import NewsArticle
from businesses.models import Business
from recommendations.models import Recommendation
from .nlp_processor import NLPProcessor
from .feature_extractor import FeatureExtractor
from .llm_extractor import LLMExtractor
from .broadcastability_calculator import BroadcastabilityCalculator

logger = logging.getLogger(__name__)


class PreFilter:
    """Pre-filtering to determine business suitability of articles"""

    HIGH_RELEVANCE_CATEGORIES = {
        'food_event': 0.95,
        'festival': 0.90,
        'concert': 0.85,
        'sports_match': 0.85,
        'nightlife': 0.90,
        'cultural': 0.75,
        'marathon': 0.80,
    }

    MEDIUM_RELEVANCE_CATEGORIES = {
        'conference': 0.60,
        'exposition': 0.55,
    }

    LOW_RELEVANCE_CATEGORIES = {
        'politics': 0.15,
        'international': 0.10,
        'conflict': 0.05,
        'crime': 0.10,
    }

    HOSPITALITY_KEYWORDS = [
        'restaurante', r'caf[eé]', 'bar', 'pub', 'cerveza',
        'comida', r'gastronom[ií]a', 'reservas', 'mesa',
        r'm[uú]sica\s+en\s+vivo', r'happy\s+hour', 'brunch'
    ]

    NEGATIVE_KEYWORDS = [
        'asesinato', 'homicidio', 'accidente', 'muerto',
        'robo', 'atraco', 'incendio', 'tragedia',
        r'corrupci[oó]n', r'esc[aá]ndalo',
        'bombardeo', 'ataque', 'guerra', r'conflicto\s+armado',
        r'narcotr[aá]fico', 'violencia', r'v[ií]ctima', 'secuestro'
    ]

    # Paywall/cookie wall detection patterns
    PAYWALL_PATTERNS = [
        r'cookies?\s+propias\s+y\s+de\s+terceros',
        r'inicia\s+sesi[oó]n',
        r'ya\s+tienes\s+una\s+cuenta',
        r'suscr[ií]bete',
        r'contenido\s+exclusivo',
        r'datos\s+de\s+navegaci[oó]n',
    ]

    def calculate_suitability(self, article: NewsArticle, event_type: Optional[str] = None, business: Optional[Business] = None) -> float:
        """
        Calculate 0.0-1.0 score for business suitability

        Now considers:
        - Event type (existing)
        - Event location/country (NEW)
        - Colombian involvement (NEW)
        - Business characteristics (NEW)

        Args:
            article: NewsArticle object
            event_type: Detected event type
            business: Business object (optional, for business-specific scoring)

        Returns:
            float between 0.0 and 1.0
        """
        text = f"{article.title} {article.content}".lower()

        # Content quality checks - detect paywalls and bad content
        paywall_detected = any(re.search(pattern, text) for pattern in self.PAYWALL_PATTERNS)
        no_keywords = not article.extracted_keywords or len(article.extracted_keywords) == 0
        short_content = len(article.content) < 200

        # Reject if content is behind paywall (cookie wall, login wall, etc.)
        if paywall_detected:
            logger.warning(f"Paywall detected for article {article.id}, rejecting")
            return 0.0

        # Warn but don't reject if no keywords (ML may not have run yet)
        if no_keywords and short_content:
            logger.warning(f"Low quality content for article {article.id}: "
                          f"no_keywords={no_keywords}, content_length={len(article.content)}")
            # Don't immediately reject - give a penalty instead
            score_penalty = 0.3
        else:
            score_penalty = 0.0

        score = 0.0

        # Base score from event type
        if event_type:
            if event_type in self.HIGH_RELEVANCE_CATEGORIES:
                score = self.HIGH_RELEVANCE_CATEGORIES[event_type]
            elif event_type in self.MEDIUM_RELEVANCE_CATEGORIES:
                score = self.MEDIUM_RELEVANCE_CATEGORIES[event_type]
            elif event_type in self.LOW_RELEVANCE_CATEGORIES:
                score = self.LOW_RELEVANCE_CATEGORIES[event_type]
            else:
                score = 0.4  # Unknown event type gets medium-low score

        # NEW: Penalize international events without Colombian involvement
        # BUT check broadcastability first (task-9.7)
        if article.event_country and article.event_country != 'Colombia':
            if not article.colombian_involvement:
                # Check if it's a broadcastable TV event before rejecting
                if article.is_broadcastable and business and business.has_tv_screens:
                    # High broadcast appeal + business has TVs = RELEVANT
                    base_score = article.broadcastability_score * 0.75
                    logger.info(
                        f"International broadcastable event: {article.title[:50]}... "
                        f"Score: {base_score:.2f} (broadcastability: {article.broadcastability_score:.2f})"
                    )
                    return base_score
                else:
                    return 0.0  # Not broadcastable or no TV screens

            # Has Colombian involvement but is international
            # Reduce score significantly
            score *= 0.4  # 60% penalty

            # Additional penalty if business doesn't have TVs (for sports events)
            if business:
                if event_type in ['sports_match', 'tournament'] and not business.has_tv_screens:
                    return 0.0  # Sports event but no TVs = not relevant

        # NEW: Boost for Colombian involvement in sports
        if article.colombian_involvement and event_type in ['sports_match', 'tournament']:
            if business and business.has_tv_screens:
                score += 0.2  # Extra boost for pubs/bars with TVs

        # Boost for hospitality keywords
        hospitality_matches = sum(1 for kw in self.HOSPITALITY_KEYWORDS
                                   if re.search(kw, text))
        score += min(0.3, hospitality_matches * 0.1)

        # Penalize negative keywords (stronger penalty to filter out bad news)
        negative_matches = sum(1 for kw in self.NEGATIVE_KEYWORDS
                                if re.search(kw, text))
        score -= negative_matches * 0.5

        # Apply content quality penalty
        score -= score_penalty

        # Clip to 0.0-1.0
        return max(0.0, min(1.0, score))


class GeographicMatcher:
    """Match articles to businesses based on geographic proximity"""

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points in kilometers using Haversine formula

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c  # Radius of earth in kilometers

        return km

    def is_relevant(self, article: NewsArticle, business: Business) -> bool:
        """
        Determine if article is geographically relevant to business

        New logic:
        1. Local events (same city in Colombia) → ALWAYS relevant
        2. National events (Colombia, different city) → relevant if business.include_national_events
        3. International events WITHOUT Colombian involvement → NOT relevant
        4. International events WITH Colombian involvement → relevant ONLY for gathering places
        5. Unknown location → conservative, only massive events

        Args:
            article: NewsArticle with extracted geographic features
            business: Business object

        Returns:
            True if relevant, False otherwise
        """
        # Case 1: Local event (same city in Colombia)
        if article.event_country == 'Colombia' and article.primary_city:
            article_city = self._normalize_city(article.primary_city)
            business_city = self._normalize_city(business.get_city_display())

            if article_city == business_city:
                # Same city = always relevant
                return True

            # Case 2: National event (different Colombian city)
            if business.include_national_events:
                if article.event_scale in ['massive', 'large']:
                    return True

        # Case 3: International event WITHOUT Colombian involvement
        if article.event_country and article.event_country != 'Colombia':
            if not article.colombian_involvement:
                return False  # Not relevant at all

            # Case 4: International event WITH Colombian involvement
            # Only relevant for "gathering places" (pubs with TVs)
            if business.has_tv_screens:
                # Check if event type is "watchable"
                if article.event_type_detected in ['sports_match', 'tournament', 'awards', 'festival']:
                    return True

            # International events are not relevant otherwise
            return False

        # Case 5: Unknown location - be conservative
        if not article.primary_city and not article.event_country:
            # Only show if it's a massive national event
            if article.event_scale == 'massive' and business.include_national_events:
                return True
            return False

        return False

    def _normalize_city(self, city: str) -> str:
        """Normalize city name for comparison"""
        return city.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')


class BusinessMatcher:
    """Match articles to businesses based on keywords and relevance"""

    def calculate_relevance(self, article: NewsArticle, business: Business) -> float:
        """
        Calculate relevance score 0.0-1.0 for article-business pair

        Args:
            article: NewsArticle object
            business: Business object

        Returns:
            float between 0.0 and 1.0
        """
        # Base score from business_suitability (if article is suitable for any business)
        score = article.business_suitability_score * 0.3  # Start with 30% of suitability

        text = f"{article.title} {article.content}".lower()

        # Check business-specific custom keywords
        keywords = business.keywords.filter(is_negative=False)
        for kw_obj in keywords:
            if kw_obj.keyword.lower() in text:
                score += kw_obj.weight * 0.2

        # Business type matching - now using database keywords
        from businesses.models import BusinessTypeKeyword
        type_keywords = BusinessTypeKeyword.objects.filter(
            business_type=business.business_type,
            is_active=True
        )

        for kw_obj in type_keywords:
            if kw_obj.keyword.lower() in text:
                score += kw_obj.weight

        # Event scale bonus (bigger events = more relevant)
        if article.event_scale == 'massive':
            score += 0.2
        elif article.event_scale == 'large':
            score += 0.15
        elif article.event_scale == 'medium':
            score += 0.05

        # Proximity bonus (from neighborhood match)
        if (article.neighborhood and business.neighborhood and
                article.neighborhood.lower() == business.neighborhood.lower()):
            score += 0.3

        return min(1.0, score)


class RecommendationGenerator:
    """Generate actionable recommendations from articles"""

    TEMPLATES = {
        'sports_match': {
            'business_types': ['pub', 'restaurant', 'coffee_shop'],
            'templates': [
                {
                    'title': 'Aumentar inventario de bebidas para {event_name}',
                    'description': 'Evento deportivo generará alta demanda de bebidas. Contactar proveedores con anticipación.',
                    'action_type': 'increase_inventory',
                    'category': 'inventory',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'urgent',
                        'medium': 'high',
                        'small': 'medium'
                    },
                    'estimated_hours': 6,
                    'days_threshold': 7,
                },
                {
                    'title': 'Campaña de marketing para {event_name}',
                    'description': 'Crear promoción especial para el evento deportivo. Considerar descuentos o paquetes especiales.',
                    'action_type': 'create_promotion',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 12,
                    'days_threshold': 14,
                },
                {
                    'title': 'Contratar personal adicional para día del evento',
                    'description': 'Volumen de clientes será excepcional. Considerar contratar staff temporal o ajustar turnos.',
                    'action_type': 'hire_staff',
                    'category': 'staffing',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 8,
                    'days_threshold': 10,
                }
            ]
        },
        'concert': {
            'business_types': ['pub', 'restaurant', 'coffee_shop'],
            'templates': [
                {
                    'title': 'Promoción pre y post concierto',
                    'description': 'Ofrecer descuentos antes/después del concierto. Muchos asistentes buscarán dónde cenar/beber.',
                    'action_type': 'create_promotion',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 8,
                    'days_threshold': 14,
                },
                {
                    'title': 'Extender horario de atención',
                    'description': 'Considerar abrir más tarde el día del concierto. Afluencia esperada después del evento.',
                    'action_type': 'adjust_hours',
                    'category': 'operations',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'medium',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 2,
                    'days_threshold': 7,
                },
                {
                    'title': 'Aumentar inventario de bebidas y snacks',
                    'description': 'Conciertos generan alta demanda. Preparar stock adicional de productos populares.',
                    'action_type': 'increase_inventory',
                    'category': 'inventory',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 4,
                    'days_threshold': 5,
                }
            ]
        },
        'marathon': {
            'business_types': ['coffee_shop', 'restaurant', 'pub'],
            'templates': [
                {
                    'title': 'Aumentar stock de bebidas saludables',
                    'description': 'Maratón generará alta demanda de hidratación. Considerar bebidas isotónicas, agua, jugos naturales.',
                    'action_type': 'increase_inventory',
                    'category': 'inventory',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 4,
                    'days_threshold': 5,
                },
                {
                    'title': 'Menú especial para corredores',
                    'description': 'Ofrecer opciones saludables y energéticas. Desayunos tempranos, almuerzos ligeros.',
                    'action_type': 'menu_modification',
                    'category': 'operations',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'medium',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 8,
                    'days_threshold': 7,
                },
                {
                    'title': 'Considerar apertura temprana',
                    'description': 'Maratones suelen iniciar temprano. Evaluar abrir más temprano para capturar tráfico.',
                    'action_type': 'adjust_hours',
                    'category': 'operations',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'medium',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 2,
                    'days_threshold': 5,
                }
            ]
        },
        'festival': {
            'business_types': ['pub', 'restaurant', 'coffee_shop', 'bookstore'],
            'templates': [
                {
                    'title': 'Preparar inventario para festival',
                    'description': 'Festival generará alta afluencia. Aumentar stock de productos de alta rotación.',
                    'action_type': 'increase_inventory',
                    'category': 'inventory',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'urgent',
                        'medium': 'high',
                        'small': 'medium'
                    },
                    'estimated_hours': 8,
                    'days_threshold': 7,
                },
                {
                    'title': 'Campaña de marketing para {event_name}',
                    'description': 'Aprovechar festival para atraer clientes. Considerar promociones temáticas.',
                    'action_type': 'create_promotion',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 10,
                    'days_threshold': 14,
                },
                {
                    'title': 'Contratar personal adicional',
                    'description': 'Festival traerá volumen excepcional de clientes. Evaluar necesidad de staff temporal.',
                    'action_type': 'hire_staff',
                    'category': 'staffing',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 8,
                    'days_threshold': 10,
                }
            ]
        },
        'food_event': {
            'business_types': ['restaurant', 'coffee_shop', 'pub'],
            'templates': [
                {
                    'title': 'Considerar participación en {event_name}',
                    'description': 'Evento gastronómico ofrece oportunidad de visibilidad y networking con clientes potenciales.',
                    'action_type': 'partner_collaboration',
                    'category': 'partnerships',
                    'priority_by_scale': {
                        'massive': 'medium',
                        'large': 'medium',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 20,
                    'days_threshold': 30,
                },
                {
                    'title': 'Analizar tendencias gastronómicas',
                    'description': 'Estudiar tendencias presentadas en el evento. Considerar incorporar ideas innovadoras al menú.',
                    'action_type': 'menu_modification',
                    'category': 'operations',
                    'priority_by_scale': {
                        'massive': 'low',
                        'large': 'low',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 6,
                    'days_threshold': 60,
                },
                {
                    'title': 'Monitorear actividad de competidores',
                    'description': 'Evento gastronómico puede revelar estrategias de competencia. Estar atento a nuevas ofertas.',
                    'action_type': 'social_campaign',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'medium',
                        'large': 'low',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 4,
                    'days_threshold': 14,
                }
            ]
        },
        'cultural': {
            'business_types': ['coffee_shop', 'restaurant', 'bookstore'],
            'templates': [
                {
                    'title': 'Promoción pre-función para {event_name}',
                    'description': 'Eventos culturales atraen público que busca cenar/tomar café antes del evento.',
                    'action_type': 'create_promotion',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'medium',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 6,
                    'days_threshold': 14,
                },
                {
                    'title': 'Ajustar horarios para evento cultural',
                    'description': 'Considerar extender horario si el evento termina tarde. Capturar tráfico post-función.',
                    'action_type': 'adjust_hours',
                    'category': 'operations',
                    'priority_by_scale': {
                        'massive': 'medium',
                        'large': 'medium',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 2,
                    'days_threshold': 7,
                }
            ]
        },
        'nightlife': {
            'business_types': ['pub', 'restaurant'],
            'templates': [
                {
                    'title': 'Aumentar inventario de bebidas alcohólicas',
                    'description': 'Evento nocturno generará alta demanda. Asegurar stock suficiente de productos populares.',
                    'action_type': 'increase_inventory',
                    'category': 'inventory',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 4,
                    'days_threshold': 5,
                },
                {
                    'title': 'Contratar personal de seguridad/servicio',
                    'description': 'Evento nocturno puede atraer multitudes. Considerar reforzar staff.',
                    'action_type': 'hire_staff',
                    'category': 'staffing',
                    'priority_by_scale': {
                        'massive': 'urgent',
                        'large': 'high',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 6,
                    'days_threshold': 7,
                }
            ]
        },
        'conference': {
            'business_types': ['coffee_shop', 'restaurant'],
            'templates': [
                {
                    'title': 'Paquetes especiales para asistentes de conferencia',
                    'description': 'Ofrecer menús ejecutivos o descuentos para grupos. Conferencias atraen profesionales.',
                    'action_type': 'create_promotion',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'medium',
                        'medium': 'medium',
                        'small': 'low'
                    },
                    'estimated_hours': 8,
                    'days_threshold': 14,
                },
                {
                    'title': 'Preparar para incremento en almuerzos',
                    'description': 'Conferencias generan alta demanda en horario de almuerzo. Aumentar staff y stock.',
                    'action_type': 'increase_inventory',
                    'category': 'inventory',
                    'priority_by_scale': {
                        'massive': 'high',
                        'large': 'medium',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 6,
                    'days_threshold': 7,
                }
            ]
        },
        'exposition': {
            'business_types': ['coffee_shop', 'restaurant', 'bookstore'],
            'templates': [
                {
                    'title': 'Promoción cruzada con {event_name}',
                    'description': 'Exposiciones atraen visitantes culturales. Considerar promociones temáticas.',
                    'action_type': 'create_promotion',
                    'category': 'marketing',
                    'priority_by_scale': {
                        'massive': 'medium',
                        'large': 'medium',
                        'medium': 'low',
                        'small': 'low'
                    },
                    'estimated_hours': 6,
                    'days_threshold': 14,
                }
            ]
        }
    }

    def generate(self, article: NewsArticle, business: Business, relevance_score: float) -> List[Recommendation]:
        """
        Generate recommendations for business based on article

        Args:
            article: NewsArticle object with extracted features
            business: Business object
            relevance_score: Pre-calculated relevance score

        Returns:
            List of Recommendation objects (not yet saved)
        """
        event_type = article.event_type_detected
        if not event_type or event_type not in self.TEMPLATES:
            return []

        # Check if this event type is applicable to this business type
        event_config = self.TEMPLATES[event_type]
        if business.business_type not in event_config.get('business_types', []):
            return []

        templates = event_config['templates']
        recommendations = []
        article_content_type = ContentType.objects.get_for_model(NewsArticle)

        # Check for existing recommendations to avoid duplicates
        # If recommendations already exist for this article-business pair, delete them
        # (we're regenerating with potentially updated logic)
        existing_recs = Recommendation.objects.filter(
            business=business,
            content_type=article_content_type,
            object_id=article.id
        )
        if existing_recs.exists():
            logger.info(f"Deleting {existing_recs.count()} existing recommendations for article {article.id}, business {business.id}")
            existing_recs.delete()

        # Calculate days until event
        days_until_event = None
        if article.event_start_datetime:
            time_diff = article.event_start_datetime - timezone.now()
            days_until_event = max(0, time_diff.days)

        # Get event scale (default to medium if not set)
        event_scale = article.event_scale or 'medium'

        # Generate recommendations (max 3)
        for template in templates[:3]:
            # Check if recommendation is within time threshold
            if days_until_event is not None:
                days_threshold = template.get('days_threshold', 365)
                if days_until_event > days_threshold:
                    continue  # Skip recommendations that are too far in advance

            # Get priority based on scale
            priority_by_scale = template.get('priority_by_scale', {})
            priority = priority_by_scale.get(event_scale, template.get('priority', 'medium'))

            # Adjust priority based on timing (if event is very soon, increase urgency)
            if days_until_event is not None and days_until_event <= 2:
                if priority == 'high':
                    priority = 'urgent'
                elif priority == 'medium':
                    priority = 'high'

            # Format template with article data
            event_name = article.title[:80]

            # Build enhanced reasoning
            reasoning_parts = [
                f"Recomendación generada por evento: {event_type}",
                f"Título: {article.title[:100]}"
            ]

            if article.venue_name:
                reasoning_parts.append(f"Lugar: {article.venue_name}")

            if article.primary_city:
                city_info = article.primary_city
                if article.neighborhood:
                    city_info += f", {article.neighborhood}"
                reasoning_parts.append(f"Ubicación: {city_info}")

            if days_until_event is not None:
                reasoning_parts.append(f"Fecha: {article.event_start_datetime.strftime('%d/%m/%Y')} ({days_until_event} días)")

            if article.expected_attendance:
                reasoning_parts.append(f"Asistencia esperada: {article.expected_attendance:,} personas")

            reasoning_parts.append(f"Escala del evento: {event_scale}")

            # Calculate impact score based on relevance, scale, and timing
            impact_score = relevance_score * 0.7  # Base from relevance

            # Scale bonus
            scale_bonus = {
                'massive': 0.3,
                'large': 0.2,
                'medium': 0.1,
                'small': 0.05
            }.get(event_scale, 0.1)
            impact_score += scale_bonus

            # Timing bonus (sooner = higher impact)
            if days_until_event is not None and days_until_event <= 7:
                impact_score += 0.1

            impact_score = min(1.0, impact_score)

            # Calculate effort score (normalize to 0-1 range)
            effort_score = min(1.0, template['estimated_hours'] / 24.0)

            rec = Recommendation(
                business=business,
                content_type=article_content_type,
                object_id=article.id,
                title=template['title'].format(event_name=event_name),
                description=template['description'],
                category=template['category'],
                action_type=template['action_type'],
                priority=priority,
                confidence_score=relevance_score,
                impact_score=impact_score,
                effort_score=effort_score,
                estimated_duration_hours=template['estimated_hours'],
                reasoning='\n'.join(reasoning_parts),
                recommended_start_date=article.event_start_datetime,
                recommended_end_date=article.event_end_datetime,
            )
            recommendations.append(rec)

        return recommendations


class MLOrchestrator:
    """Main orchestrator for the complete ML pipeline"""

    def __init__(self):
        self.nlp = NLPProcessor()
        self.feature_extractor = FeatureExtractor()
        self.llm_extractor = LLMExtractor()
        self.broadcastability_calc = BroadcastabilityCalculator()  # task-9.7
        self.prefilter = PreFilter()
        self.geo_matcher = GeographicMatcher()
        self.business_matcher = BusinessMatcher()
        self.rec_generator = RecommendationGenerator()

    def _compare_extractions(self, spacy_features: Dict[str, Any], llm_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare spaCy and LLM extraction results

        Args:
            spacy_features: Features extracted by spaCy
            llm_features: Features extracted by LLM

        Returns:
            Dictionary with comparison metrics
        """
        comparison = {
            'timestamp': timezone.now().isoformat(),
            'fields_compared': [],
            'fields_matched': 0,
            'fields_different': 0,
            'differences': {}
        }

        # Define fields to compare
        comparable_fields = [
            'event_type', 'event_subtype', 'city', 'neighborhood', 'venue',
            'scale', 'event_country', 'colombian_involvement'
        ]

        for field in comparable_fields:
            spacy_value = spacy_features.get(field)
            llm_value = llm_features.get(field)

            comparison['fields_compared'].append(field)

            # Normalize values for comparison
            spacy_str = str(spacy_value).lower().strip() if spacy_value else ''
            llm_str = str(llm_value).lower().strip() if llm_value else ''

            if spacy_str == llm_str:
                comparison['fields_matched'] += 1
            else:
                comparison['fields_different'] += 1
                comparison['differences'][field] = {
                    'spacy': spacy_value,
                    'llm': llm_value
                }

        # Calculate completeness scores
        def count_filled_fields(features):
            filled = 0
            for field in comparable_fields:
                value = features.get(field)
                if value and value != '' and value is not None and value != False:
                    filled += 1
            # Also check temporal fields
            if features.get('event_date'):
                filled += 1
            if features.get('attendance'):
                filled += 1
            return filled

        spacy_filled = count_filled_fields(spacy_features)
        llm_filled = count_filled_fields(llm_features)
        total_fields = len(comparable_fields) + 2  # +2 for event_date and attendance

        comparison['spacy_completeness'] = spacy_filled / total_fields
        comparison['llm_completeness'] = llm_filled / total_fields
        comparison['agreement_rate'] = comparison['fields_matched'] / len(comparable_fields) if comparable_fields else 0

        logger.info(
            f"Extraction comparison: {comparison['fields_matched']}/{len(comparable_fields)} fields matched, "
            f"spaCy completeness: {comparison['spacy_completeness']:.2f}, "
            f"LLM completeness: {comparison['llm_completeness']:.2f}"
        )

        return comparison

    @transaction.atomic
    def process_article(self, article: NewsArticle, save: bool = True) -> Dict[str, Any]:
        """
        Process a single article through the complete pipeline.

        Uses @transaction.atomic to ensure feature extraction and recommendation
        generation happen atomically - either both succeed or both rollback.

        Args:
            article: NewsArticle object
            save: Whether to save results to database

        Returns:
            Dictionary with processing results
        """
        try:
            # Step 1: Extract features
            features = self.feature_extractor.extract_all(article.content, article.title)

            article.event_type_detected = features['event_type'] or ''
            article.event_subtype = features['event_subtype'] or ''
            article.primary_city = features['city'] or ''
            article.neighborhood = features['neighborhood'] or ''
            article.venue_name = features['venue'] or ''
            article.event_start_datetime = features['event_date']
            article.event_end_datetime = features.get('event_end_datetime')
            article.event_duration_hours = features.get('event_duration_hours')
            article.expected_attendance = features['attendance']
            article.event_scale = features['scale'] or ''
            article.event_country = features['event_country'] or ''
            article.colombian_involvement = features['colombian_involvement']
            article.extracted_keywords = features.get('keywords', [])
            article.entities = features.get('entities', [])

            # task-9.7: Extract sport_type and competition_level (initially from spaCy)
            article.sport_type = features.get('sport_type', '') or ''
            article.competition_level = features.get('competition_level', '') or ''

            # Map event_type to category and subcategory
            category_map = {
                'sports_match': ('deportes', 'futbol'),
                'marathon': ('deportes', 'atletismo'),
                'concert': ('entretenimiento', 'musica'),
                'festival': ('eventos', 'festival'),
                'conference': ('negocios', 'conferencia'),
                'exposition': ('cultura', 'exposicion'),
                'food_event': ('gastronomia', 'festival-gastronomico'),
                'cultural': ('cultura', 'evento-cultural'),
                'nightlife': ('entretenimiento', 'vida-nocturna'),
                'politics': ('comunidad', 'politica'),
                'international': ('comunidad', 'internacional'),
                'conflict': ('comunidad', 'seguridad'),
                'crime': ('comunidad', 'seguridad'),
            }

            if article.event_type_detected:
                category, subcategory = category_map.get(article.event_type_detected, ('comunidad', 'otros'))
                article.category = category
                article.subcategory = subcategory

            # Step 2: Calculate business suitability
            # Use primary business (business_id=1) for general suitability scoring
            primary_business = Business.objects.filter(id=1).first()
            article.business_suitability_score = self.prefilter.calculate_suitability(
                article, features['event_type'], business=primary_business
            )

            # Mark as processed
            article.features_extracted = True
            article.feature_extraction_date = timezone.now()
            article.feature_extraction_confidence = 0.8  # Default confidence

            # Clear old processing errors on successful extraction
            article.processing_error = ''

            # Calculate feature completeness score
            from news.utils import calculate_feature_completeness
            article.feature_completeness_score = calculate_feature_completeness(article)

            # Step 2.5: Run LLM extraction if suitability is high enough (task-9.6)
            llm_features = None
            if article.business_suitability_score >= 0.3:
                logger.info(f"Article {article.id} passed suitability threshold, running LLM extraction")
                try:
                    llm_features = self.llm_extractor.extract_all(article.content, article.title)

                    if llm_features:
                        # Store LLM extraction results
                        article.llm_features_extracted = True
                        article.llm_extraction_date = timezone.now()
                        article.llm_extraction_results = llm_features

                        # Compare spaCy and LLM results
                        comparison = self._compare_extractions(features, llm_features)
                        article.extraction_comparison = comparison

                        logger.info(
                            f"LLM extraction completed for article {article.id}. "
                            f"Agreement: {comparison.get('agreement_rate', 0):.2%}, "
                            f"LLM completeness: {comparison.get('llm_completeness', 0):.2%}"
                        )
                    else:
                        logger.warning(f"LLM extraction returned no results for article {article.id}")
                except Exception as e:
                    logger.error(f"LLM extraction failed for article {article.id}: {e}", exc_info=True)
                    # Continue with spaCy results even if LLM fails
            else:
                logger.debug(
                    f"Article {article.id} below suitability threshold ({article.business_suitability_score:.2f}), "
                    "skipping LLM extraction"
                )

            # Step 2.6: Calculate broadcastability for sports events (task-9.7)
            # Update sport_type and competition_level from LLM if available
            if llm_features:
                if llm_features.get('sport_type'):
                    article.sport_type = llm_features['sport_type']
                if llm_features.get('competition_level'):
                    article.competition_level = llm_features['competition_level']

            # Calculate broadcastability score
            try:
                broadcast_result = self.broadcastability_calc.calculate(article)
                article.broadcastability_score = broadcast_result['broadcastability_score']
                article.hype_score = broadcast_result['hype_score']
                article.is_broadcastable = broadcast_result['is_broadcastable']

                # Update sport_type and competition_level from calculator if detected
                if broadcast_result.get('sport_type'):
                    article.sport_type = broadcast_result['sport_type']
                if broadcast_result.get('competition_level'):
                    article.competition_level = broadcast_result['competition_level']

                if article.is_broadcastable:
                    logger.info(
                        f"Article {article.id} is broadcastable! "
                        f"Score: {article.broadcastability_score:.2f} "
                        f"(sport: {article.sport_type}, competition: {article.competition_level})"
                    )
            except Exception as e:
                logger.error(f"Broadcastability calculation failed for article {article.id}: {e}", exc_info=True)
                # Set defaults on error
                article.broadcastability_score = 0.0
                article.hype_score = 0.0
                article.is_broadcastable = False

            if save:
                article.save()

            # Step 3: Early exit if not suitable
            if article.business_suitability_score < 0.3:
                return {
                    'success': True,
                    'processed': False,
                    'reason': f'Low suitability score: {article.business_suitability_score:.2f}',
                    'features_extracted': True
                }

            # Step 4: Find matching businesses and calculate max relevance
            matching_businesses = []
            max_relevance = 0.0

            for business in Business.objects.filter(is_active=True):
                if not self.geo_matcher.is_relevant(article, business):
                    continue

                relevance = self.business_matcher.calculate_relevance(article, business)

                # Track highest relevance score across all businesses
                if relevance > max_relevance:
                    max_relevance = relevance

                # Lower threshold to 0.4 to catch more potential matches
                if relevance > 0.4:
                    matching_businesses.append((business, relevance))

            # Set article's business_relevance_score to max relevance found
            # This represents how relevant this article is to the MOST interested business
            article.business_relevance_score = max_relevance

            if save:
                article.save()

            # Step 5: Generate recommendations
            recommendations_created = 0
            for business, relevance in matching_businesses:
                recs = self.rec_generator.generate(article, business, relevance)
                if save:
                    for rec in recs:
                        rec.save()
                        recommendations_created += 1

            return {
                'success': True,
                'processed': True,
                'features_extracted': True,
                'suitability_score': article.business_suitability_score,
                'business_relevance_score': article.business_relevance_score,
                'matching_businesses': len(matching_businesses),
                'recommendations_created': recommendations_created,
                'features': features
            }

        except Exception as e:
            logger.error(f"Error processing article {article.id}: {e}")
            if save:
                article.processing_error = str(e)
                article.save()
            return {
                'success': False,
                'error': str(e)
            }
