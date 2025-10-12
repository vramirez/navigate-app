"""
NLP Processor Service

Wrapper around spaCy Spanish NLP model for text processing.
Provides entity extraction, keyword extraction, and linguistic analysis.
"""

import spacy
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class NLPProcessor:
    """
    Singleton wrapper for spaCy Spanish NLP model.
    Loads model once and reuses for all processing.
    """

    _instance = None
    _nlp = None

    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load Spanish spaCy model"""
        try:
            self._nlp = spacy.load('es_core_news_md')
            logger.info("✅ Spanish NLP model loaded successfully")
        except OSError as e:
            logger.error(f"❌ Failed to load Spanish model: {e}")
            logger.error("Run: python -m spacy download es_core_news_md")
            raise

    def process_text(self, text: str) -> spacy.tokens.Doc:
        """
        Process text with spaCy pipeline

        Args:
            text: Input text to process

        Returns:
            spaCy Doc object with linguistic annotations
        """
        if not text or not isinstance(text, str):
            return None

        return self._nlp(text[:1000000])  # Limit to 1M chars for safety

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text

        Args:
            text: Input text

        Returns:
            List of entities with text, label, and start/end positions
            Example: [
                {'text': 'Medellín', 'label': 'LOC', 'start': 45, 'end': 53},
                {'text': 'Copa América', 'label': 'MISC', 'start': 15, 'end': 27}
            ]
        """
        doc = self.process_text(text)
        if not doc:
            return []

        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })

        return entities

    def extract_locations(self, text: str) -> List[str]:
        """
        Extract all location entities (LOC, GPE)

        Args:
            text: Input text

        Returns:
            List of location names
        """
        doc = self.process_text(text)
        if not doc:
            return []

        locations = []
        for ent in doc.ents:
            if ent.label_ in ['LOC', 'GPE']:
                locations.append(ent.text)

        return list(set(locations))  # Remove duplicates

    def extract_organizations(self, text: str) -> List[str]:
        """
        Extract organization entities (for venue names, companies)

        Args:
            text: Input text

        Returns:
            List of organization names
        """
        doc = self.process_text(text)
        if not doc:
            return []

        orgs = []
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                orgs.append(ent.text)

        return list(set(orgs))

    def extract_dates(self, text: str) -> List[str]:
        """
        Extract date/time entities

        Args:
            text: Input text

        Returns:
            List of date/time expressions
        """
        doc = self.process_text(text)
        if not doc:
            return []

        dates = []
        for ent in doc.ents:
            if ent.label_ in ['DATE', 'TIME']:
                dates.append(ent.text)

        return dates

    def extract_numbers(self, text: str) -> List[str]:
        """
        Extract numeric entities (for attendance, capacity, etc.)

        Args:
            text: Input text

        Returns:
            List of number expressions
        """
        doc = self.process_text(text)
        if not doc:
            return []

        numbers = []
        for ent in doc.ents:
            if ent.label_ in ['QUANTITY', 'CARDINAL']:
                numbers.append(ent.text)

        return numbers

    def get_noun_chunks(self, text: str) -> List[str]:
        """
        Extract noun phrases (useful for venue names, event names)

        Args:
            text: Input text

        Returns:
            List of noun phrases
        """
        doc = self.process_text(text)
        if not doc:
            return []

        return [chunk.text for chunk in doc.noun_chunks]

    def get_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract most important keywords using TF-IDF-like approach

        Args:
            text: Input text
            top_n: Number of keywords to return

        Returns:
            List of top keywords
        """
        doc = self.process_text(text)
        if not doc:
            return []

        # Filter to nouns, proper nouns, and adjectives
        # Exclude stopwords and very short words
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ']
                    and not token.is_stop
                    and len(token.text) > 3
                    and token.is_alpha):
                keywords.append(token.lemma_.lower())

        # Count frequencies
        from collections import Counter
        keyword_counts = Counter(keywords)

        # Return top N most common
        return [word for word, count in keyword_counts.most_common(top_n)]

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive text analysis with all features

        Args:
            text: Input text

        Returns:
            Dictionary with all extracted features
        """
        return {
            'entities': self.extract_entities(text),
            'locations': self.extract_locations(text),
            'organizations': self.extract_organizations(text),
            'dates': self.extract_dates(text),
            'numbers': self.extract_numbers(text),
            'keywords': self.get_keywords(text, top_n=15),
            'noun_chunks': self.get_noun_chunks(text)[:20]  # Limit to 20
        }
