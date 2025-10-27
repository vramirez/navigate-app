"""
LLM Feature Extractor Service

Uses Ollama (Llama 3.2 1B) to extract structured features from news articles.
Designed to run in parallel with spaCy-based FeatureExtractor for comparison.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import dateparser
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extract structured features using LLM (Ollama)"""

    _instance = None

    def __new__(cls):
        """Singleton pattern to reuse Ollama connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize Ollama client"""
        if self._initialized:
            return

        # Get configuration from environment
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
        self.model_name = getattr(settings, 'LLM_MODEL_NAME', 'llama3.2:1b')
        self.timeout = getattr(settings, 'LLM_TIMEOUT_SECONDS', 30)
        self.enabled = getattr(settings, 'LLM_EXTRACTION_ENABLED', True)

        # Import ollama library
        try:
            import ollama
            self.ollama = ollama
            self.client = ollama.Client(host=self.ollama_host)
            logger.info(f"LLM Extractor initialized with model {self.model_name} at {self.ollama_host}")
            self._initialized = True
        except ImportError:
            logger.error("Ollama library not installed. Install with: pip install ollama")
            self.enabled = False
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.enabled = False
            self._initialized = True

    def _build_prompt(self, article_text: str, article_title: str) -> str:
        """
        Build structured prompt for LLM feature extraction

        Args:
            article_text: Full article content
            article_title: Article title

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert at extracting structured information from Spanish news articles about events in Colombia.

Analyze the following article and extract information in JSON format.

ARTICLE TITLE: {article_title}

ARTICLE CONTENT:
{article_text[:2000]}  # Limit to 2000 chars for smaller model

Extract the following information and respond ONLY with valid JSON (no additional text):

{{
    "event_type": "REQUIRED - Choose ONE: sports_match, marathon, concert, festival, conference, exposition, food_event, cultural, nightlife, politics, international, conflict, crime, other. For sports news use 'sports_match'. NEVER leave empty.",
    "event_subtype": "specific subtype if applicable (e.g., 'soccer', 'rock concert', '10k race')",
    "sport_type": "for sports events, the sport name: soccer, cycling, combat_sports, basketball, baseball, formula_1, tennis, volleyball, american_football, motorsports, rugby, golf, ice_hockey, winter_sports, or null if not sports",
    "competition_level": "for sports events, competition name/tier: world_cup, copa_america, champions_league, libertadores, tour_de_france, giro_italia, vuelta_espana, primera_division, segunda_division, national_team_qualifier, olympics, or null. Look for: mundial, copa, torneo, liga, clasificatorias, eliminatorias, final, campeonato",
    "city": "primary Colombian city where event takes place (e.g., 'Medellín', 'Bogotá', 'Cali')",
    "neighborhood": "neighborhood or district if mentioned (e.g., 'El Poblado', 'Laureles')",
    "venue": "specific venue name if mentioned (e.g., 'Estadio Atanasio Girardot', 'Teatro Pablo Tobón')",
    "event_date": "event start date/time in ISO format (YYYY-MM-DDTHH:MM:SS) or null",
    "event_duration_hours": number of hours the event lasts (e.g., 2, 24, 72) or null,
    "attendance": estimated number of attendees as integer or null,
    "scale": "small|medium|large|massive",
    "event_country": "Colombia|México|Argentina|Brasil|Estados Unidos|España|Chile|Perú|Ecuador|other",
    "colombian_involvement": true if Colombian national team/artist/athlete participates, false otherwise,
    "keywords": ["keyword1", "keyword2", ...] - list of 10-15 most relevant keywords,
    "entities": {{
        "locations": ["location1", "location2"],
        "organizations": ["org1", "org2"],
        "people": ["person1", "person2"]
    }}
}}

IMPORTANT RULES:
1. Respond ONLY with valid JSON, no explanations
2. Use null for missing/unknown values, not empty strings
3. event_type must be one of the listed categories
4. Dates must be in ISO format or null
5. attendance must be a number or null
6. Keywords should be relevant Spanish terms from the article
7. If the article is about politics, international affairs, crime, or conflicts, mark event_type accordingly
8. sport_type examples: soccer (fútbol), cycling (ciclismo), combat_sports (boxeo/mma), basketball (baloncesto), baseball (béisbol), formula_1, tennis, volleyball
9. competition_level examples: world_cup (mundial), copa_america, champions_league (liga de campeones), libertadores, tour_de_france, giro_italia, vuelta_espana, primera_division, segunda_division, national_team_qualifier (eliminatorias), olympics (olímpicos)
10. Detect competition tier from context: "final", "semifinal", "clasificatorias", "mundial", "copa", "torneo", "liga"

JSON Response:"""

        return prompt

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Call Ollama API with timeout and error handling

        Args:
            prompt: Formatted prompt string

        Returns:
            LLM response text or None on error
        """
        if not self.enabled:
            logger.warning("LLM extraction is disabled")
            return None

        try:
            logger.debug(f"Calling Ollama model {self.model_name}")

            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for consistent extraction
                    'top_p': 0.9,
                    'num_predict': 800,  # Limit response length
                }
            )

            if response and 'response' in response:
                return response['response']
            else:
                logger.error("Invalid response from Ollama")
                return None

        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return None

    def _parse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse LLM JSON response into structured dict

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed dictionary or None on error
        """
        if not response_text:
            return None

        try:
            # Extract JSON from response (sometimes LLM adds extra text)
            # Look for the first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')

            if start_idx == -1 or end_idx == -1:
                logger.error("No JSON found in LLM response")
                return None

            json_str = response_text[start_idx:end_idx + 1]
            data = json.loads(json_str)

            # Validate required fields - reject if event_type is missing or generic
            if not data.get('event_type') or data.get('event_type') == 'other':
                logger.warning("LLM failed to classify event type properly, rejecting result")
                return None

            # Parse event_date string to datetime if present
            if data.get('event_date'):
                try:
                    parsed_date = dateparser.parse(
                        data['event_date'],
                        settings={'TIMEZONE': 'America/Bogota', 'RETURN_AS_TIMEZONE_AWARE': True}
                    )
                    # Convert to ISO format string for JSON serialization
                    data['event_date'] = parsed_date.isoformat() if parsed_date else None
                except Exception as e:
                    logger.warning(f"Failed to parse event_date: {e}")
                    data['event_date'] = None

            # Ensure attendance is int or None
            if data.get('attendance') and not isinstance(data['attendance'], int):
                try:
                    data['attendance'] = int(data['attendance'])
                except (ValueError, TypeError):
                    data['attendance'] = None

            # Ensure duration is float or None
            if data.get('event_duration_hours') and not isinstance(data['event_duration_hours'], (int, float)):
                try:
                    data['event_duration_hours'] = float(data['event_duration_hours'])
                except (ValueError, TypeError):
                    data['event_duration_hours'] = None

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None

    def extract_all(self, article_text: str, article_title: str = "") -> Optional[Dict[str, Any]]:
        """
        Extract all features from article using LLM

        Args:
            article_text: Full article content
            article_title: Article title

        Returns:
            Dictionary with extracted features (same format as FeatureExtractor) or None on error
        """
        if not self.enabled:
            logger.warning("LLM extraction is disabled")
            return None

        try:
            # Build prompt
            prompt = self._build_prompt(article_text, article_title)

            # Call LLM
            response_text = self._call_ollama(prompt)
            if not response_text:
                logger.error("No response from LLM")
                return None

            # Parse response
            extracted_data = self._parse_response(response_text)
            if not extracted_data:
                logger.error("Failed to parse LLM response")
                return None

            # Normalize to match FeatureExtractor output format
            return {
                'event_type': extracted_data.get('event_type', ''),
                'event_subtype': extracted_data.get('event_subtype', ''),
                'sport_type': extracted_data.get('sport_type', ''),  # task-9.7
                'competition_level': extracted_data.get('competition_level', ''),  # task-9.7
                'city': extracted_data.get('city', ''),
                'neighborhood': extracted_data.get('neighborhood', ''),
                'venue': extracted_data.get('venue', ''),
                'event_date': extracted_data.get('event_date'),
                'event_end_datetime': None,  # Will be calculated from duration if needed
                'event_duration_hours': extracted_data.get('event_duration_hours'),
                'attendance': extracted_data.get('attendance'),
                'scale': extracted_data.get('scale', 'medium'),
                'event_country': extracted_data.get('event_country', ''),
                'colombian_involvement': extracted_data.get('colombian_involvement', False),
                'keywords': extracted_data.get('keywords', []),
                'entities': extracted_data.get('entities', {}),
            }

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}", exc_info=True)
            return None

    def is_available(self) -> bool:
        """
        Check if LLM extraction is available

        Returns:
            Boolean indicating if LLM service is available
        """
        if not self.enabled:
            return False

        try:
            # Try to list models as a health check
            models = self.client.list()
            return self.model_name in [m['name'] for m in models.get('models', [])]
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False
