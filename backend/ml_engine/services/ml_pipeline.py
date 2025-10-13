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

from news.models import NewsArticle
from businesses.models import Business
from recommendations.models import Recommendation
from .nlp_processor import NLPProcessor
from .feature_extractor import FeatureExtractor

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
    }

    HOSPITALITY_KEYWORDS = [
        'restaurante', 'caf[eé]', 'bar', 'pub', 'cerveza',
        'comida', 'gastronom[ií]a', 'reservas', 'mesa',
        'm[uú]sica en vivo', 'happy hour', 'brunch'
    ]

    NEGATIVE_KEYWORDS = [
        'asesinato', 'homicidio', 'accidente', 'muerto',
        'robo', 'atraco', 'incendio', 'tragedia',
        'corrupci[oó]n', 'esc[aá]ndalo'
    ]

    def calculate_suitability(self, article: NewsArticle, event_type: Optional[str] = None) -> float:
        """
        Calculate 0.0-1.0 score for business suitability

        Args:
            article: NewsArticle object
            event_type: Detected event type

        Returns:
            float between 0.0 and 1.0
        """
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

        # Boost for hospitality keywords
        text = f"{article.title} {article.content}".lower()
        hospitality_matches = sum(1 for kw in self.HOSPITALITY_KEYWORDS
                                   if re.search(kw, text))
        score += min(0.3, hospitality_matches * 0.1)

        # Penalize negative keywords
        negative_matches = sum(1 for kw in self.NEGATIVE_KEYWORDS
                                if re.search(kw, text))
        score -= negative_matches * 0.2

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

        Args:
            article: NewsArticle with extracted geographic features
            business: Business object

        Returns:
            True if relevant, False otherwise
        """
        # Exact city match (required for most cases)
        if article.primary_city:
            article_city = article.primary_city.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i')
            business_city = business.get_city_display().lower().replace('á', 'a').replace('é', 'e').replace('í', 'i')

            if article_city != business_city:
                # Check if business wants national events
                if not business.include_national_events:
                    return False
                # Only show truly massive national events
                if article.event_scale != 'massive':
                    return False

        # Same neighborhood = always relevant
        if (article.neighborhood and business.neighborhood and
                article.neighborhood.lower() == business.neighborhood.lower()):
            return True

        # Distance-based matching (if coordinates available)
        if all([article.latitude, article.longitude, business.latitude, business.longitude]):
            distance = self.haversine_distance(
                article.latitude, article.longitude,
                business.latitude, business.longitude
            )
            if distance <= business.geographic_radius_km:
                return True

        # Citywide events (if business opted in)
        if business.include_citywide_events and article.event_scale in ['large', 'massive']:
            return True

        return True  # Default to showing (let business_suitability_score filter)


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

        # Check business keywords
        keywords = business.keywords.filter(is_negative=False)
        for kw_obj in keywords:
            if kw_obj.keyword.lower() in text:
                score += kw_obj.weight * 0.2

        # Business type matching
        if business.business_type == 'pub':
            pub_keywords = ['cerveza', 'fútbol', 'partido', 'bar']
            score += sum(0.15 for kw in pub_keywords if kw in text)

        elif business.business_type == 'restaurant':
            rest_keywords = ['comida', 'gastronómico', 'chef', 'restaurante']
            score += sum(0.15 for kw in rest_keywords if kw in text)

        elif business.business_type == 'coffee_shop':
            cafe_keywords = ['café', 'brunch', 'desayuno']
            score += sum(0.15 for kw in cafe_keywords if kw in text)

        elif business.business_type == 'bookstore':
            book_keywords = ['libro', 'autor', 'lectura', 'literario']
            score += sum(0.15 for kw in book_keywords if kw in text)

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
            'categories': ['marketing', 'inventory', 'staffing'],
            'templates': [
                {
                    'title': 'Campaña Especial: {event_name}',
                    'description': 'Crear promoción especial para el evento deportivo. Incremento esperado de tráfico del {traffic_increase}%.',
                    'action_type': 'create_promotion',
                    'priority': 'urgent',
                    'estimated_hours': 12,
                },
                {
                    'title': 'Aumentar stock de cerveza en {percentage}% para el evento',
                    'description': 'Evento deportivo generará alta demanda. Contactar proveedores inmediatamente.',
                    'action_type': 'increase_inventory',
                    'priority': 'high',
                    'estimated_hours': 6,
                },
                {
                    'title': 'Contratar personal adicional para día del evento',
                    'description': 'Volumen de clientes será excepcional durante {event_name}.',
                    'action_type': 'hire_staff',
                    'priority': 'high',
                    'estimated_hours': 3,
                }
            ]
        },
        'concert': {
            'categories': ['marketing', 'operations'],
            'templates': [
                {
                    'title': 'Promoción especial: Pre y post concierto',
                    'description': 'Ofrecer descuentos antes/después del concierto de {event_name}.',
                    'action_type': 'create_promotion',
                    'priority': 'medium',
                    'estimated_hours': 8,
                },
                {
                    'title': 'Extender horario de atención por concierto',
                    'description': 'Considerar abrir más tarde el día del evento.',
                    'action_type': 'adjust_hours',
                    'priority': 'medium',
                    'estimated_hours': 2,
                }
            ]
        },
        'marathon': {
            'categories': ['inventory', 'operations'],
            'templates': [
                {
                    'title': 'Aumentar stock de bebidas isotónicas y agua',
                    'description': 'Maratón generará alta demanda de hidratación.',
                    'action_type': 'increase_inventory',
                    'priority': 'high',
                    'estimated_hours': 4,
                },
                {
                    'title': 'Menú especial para corredores (desayunos tempranos)',
                    'description': 'Ofrecer opciones saludables y energéticas.',
                    'action_type': 'menu_modification',
                    'priority': 'medium',
                    'estimated_hours': 8,
                }
            ]
        },
        'food_event': {
            'categories': ['partnerships', 'marketing'],
            'templates': [
                {
                    'title': 'Considerar participación en {event_name}',
                    'description': 'Oportunidad de visibilidad y networking.',
                    'action_type': 'partner_collaboration',
                    'priority': 'low',
                    'estimated_hours': 20,
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

        templates = self.TEMPLATES[event_type]['templates']
        recommendations = []
        article_content_type = ContentType.objects.get_for_model(NewsArticle)

        for template in templates[:2]:  # Max 2 recommendations per article
            # Format template with article data
            event_name = article.title[:100]
            traffic_increase = '300' if article.event_scale == 'massive' else '150'
            percentage = '400' if article.event_scale == 'massive' else '200'

            rec = Recommendation(
                business=business,
                content_type=article_content_type,
                object_id=article.id,
                title=template['title'].format(
                    event_name=event_name,
                    traffic_increase=traffic_increase,
                    percentage=percentage
                ),
                description=template['description'].format(
                    event_name=event_name,
                    traffic_increase=traffic_increase,
                    percentage=percentage
                ),
                category=template['action_type'].split('_')[0],  # Simplify
                action_type=template['action_type'],
                priority=template['priority'],
                confidence_score=relevance_score,
                impact_score=min(1.0, relevance_score + 0.1),
                effort_score=template['estimated_hours'] / 20.0,  # Normalize
                estimated_duration_hours=template['estimated_hours'],
                reasoning=f"Generado automáticamente basado en análisis de '{article.title[:50]}...'",
                
                
                
            )
            recommendations.append(rec)

        return recommendations


class MLOrchestrator:
    """Main orchestrator for the complete ML pipeline"""

    def __init__(self):
        self.nlp = NLPProcessor()
        self.feature_extractor = FeatureExtractor()
        self.prefilter = PreFilter()
        self.geo_matcher = GeographicMatcher()
        self.business_matcher = BusinessMatcher()
        self.rec_generator = RecommendationGenerator()

    def process_article(self, article: NewsArticle, save: bool = True) -> Dict[str, Any]:
        """
        Process a single article through the complete pipeline

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
            article.primary_city = features['city'] or ''
            article.neighborhood = features['neighborhood'] or ''
            article.venue_name = features['venue'] or ''
            article.event_start_datetime = features['event_date']
            article.expected_attendance = features['attendance']
            article.event_scale = features['scale'] or ''

            # Step 2: Calculate business suitability
            article.business_suitability_score = self.prefilter.calculate_suitability(
                article, features['event_type']
            )

            # Mark as processed
            article.features_extracted = True
            article.feature_extraction_date = timezone.now()
            article.feature_extraction_confidence = 0.8  # Default confidence

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
