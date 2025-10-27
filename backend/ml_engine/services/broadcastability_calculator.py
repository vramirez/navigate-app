"""
Broadcastability Calculator Service (task-9.7)

Calculates intelligent "broadcastability" scores for sports events to detect
TV broadcast appeal, even when articles don't explicitly say "será transmitido".

Formula:
broadcastability_score = (
    sport_appeal × 0.35 +          # Soccer: 0.95, Skiing: 0.10
    competition_level × 0.30 +      # World Cup: 3.0x, 2nd Division: 0.5x
    hype_indicators × 0.20 +        # Finals, clásicos, historic events
    attendance_scale × 0.15         # 50k+ attendance = massive
)

Examples:
- World Cup Final (non-Colombia): 0.85 → RELEVANT for TV pubs
- 2nd Division Match: 0.41 → NOT broadcastable
- Tour de France (Colombian rider): 0.78 → RELEVANT
"""

import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class BroadcastabilityCalculator:
    """
    Calculates broadcastability scores for sports events

    Uses database-driven configuration for:
    - Sport types with Latin America appeal ratings
    - Competition levels with broadcast multipliers
    - Hype indicator patterns
    - Configurable weights and thresholds
    """

    def __init__(self):
        """Initialize calculator with database configuration"""
        # Import here to avoid circular imports
        from event_taxonomy.models import (
            SportType,
            CompetitionLevel,
            HypeIndicator,
            BroadcastabilityConfig
        )

        # Load configuration (singleton)
        self.config = BroadcastabilityConfig.get_instance()

        # Cache active sport types {code: SportType object}
        self.sport_types = {
            st.code: st
            for st in SportType.objects.filter(is_active=True)
        }

        # Cache active competition levels
        self.competition_levels = list(
            CompetitionLevel.objects.filter(is_active=True)
                .select_related('sport_type')
        )

        # Cache active hype indicators
        self.hype_indicators = list(
            HypeIndicator.objects.filter(is_active=True)
        )

        logger.info(
            f"BroadcastabilityCalculator initialized: "
            f"{len(self.sport_types)} sports, "
            f"{len(self.competition_levels)} competition levels, "
            f"{len(self.hype_indicators)} hype indicators"
        )

    def calculate(self, article) -> Dict:
        """
        Calculate broadcastability score for an article

        Args:
            article: NewsArticle object (must have title, content, event_type,
                    expected_attendance)

        Returns:
            dict with keys:
                - broadcastability_score (0.0-1.0)
                - hype_score (0.0-1.0)
                - is_broadcastable (bool)
                - sport_type (str or None)
                - competition_level (str or None)
                - components (dict): breakdown of score components
        """
        text = f"{article.title} {article.content}".lower()

        # Only calculate for sports events
        if article.event_type_detected not in ['sports_match', 'marathon', 'tournament']:
            return self._zero_result(reason="Not a sports event")

        # 1. Sport Appeal Component
        sport_appeal, detected_sport = self._calculate_sport_appeal(text, article)

        # 2. Competition Level Component
        competition_score, detected_competition = self._calculate_competition_level(
            text,
            article,
            detected_sport
        )

        # 3. Hype Indicators Component
        hype_score = self._calculate_hype_score(text)

        # 4. Attendance Component
        attendance_score = self._calculate_attendance_score(article)

        # 5. Weighted Combination
        broadcastability = (
            sport_appeal * self.config.sport_appeal_weight +
            competition_score * self.config.competition_level_weight +
            hype_score * self.config.hype_indicators_weight +
            attendance_score * self.config.attendance_weight
        )

        # Clip to 0.0-1.0
        broadcastability = max(0.0, min(1.0, broadcastability))

        # Determine if broadcastable
        is_broadcastable = broadcastability >= self.config.min_broadcastability_score

        result = {
            'broadcastability_score': round(broadcastability, 3),
            'hype_score': round(hype_score, 3),
            'is_broadcastable': is_broadcastable,
            'sport_type': detected_sport,
            'competition_level': detected_competition,
            'components': {
                'sport_appeal': round(sport_appeal, 3),
                'competition_level': round(competition_score, 3),
                'hype_indicators': round(hype_score, 3),
                'attendance': round(attendance_score, 3),
            }
        }

        if is_broadcastable:
            logger.info(
                f"Broadcastable event detected: {article.title[:50]}... "
                f"Score: {broadcastability:.2f} "
                f"(sport={sport_appeal:.2f}, comp={competition_score:.2f}, "
                f"hype={hype_score:.2f}, att={attendance_score:.2f})"
            )

        return result

    def _calculate_sport_appeal(
        self,
        text: str,
        article
    ) -> Tuple[float, Optional[str]]:
        """
        Calculate sport appeal component (0.0-1.0)

        Returns:
            (appeal_score, detected_sport_code)
        """
        # Try to detect sport from article text using keywords
        best_match = None
        best_score = 0.0

        for sport_code, sport_type in self.sport_types.items():
            # Count keyword matches
            keyword_matches = sum(
                1 for keyword in sport_type.keywords
                if keyword.lower() in text
            )

            if keyword_matches > best_score:
                best_score = keyword_matches
                best_match = sport_type

        if best_match:
            logger.debug(
                f"Sport detected: {best_match.code} "
                f"(appeal: {best_match.latin_america_appeal})"
            )
            return best_match.latin_america_appeal, best_match.code

        # Default to medium appeal if no sport detected
        logger.debug("No sport detected, using default appeal 0.5")
        return 0.5, None

    def _calculate_competition_level(
        self,
        text: str,
        article,
        detected_sport: Optional[str]
    ) -> Tuple[float, Optional[str]]:
        """
        Calculate competition level component (0.0-1.0)

        Matches competition keywords from database and returns normalized score.

        Returns:
            (normalized_score, detected_competition_code)
        """
        best_match = None
        best_multiplier = 1.0  # Default: regular competition

        for competition in self.competition_levels:
            # Filter by sport if detected
            if detected_sport and competition.sport_type:
                if competition.sport_type.code != detected_sport:
                    continue  # Skip competitions from other sports

            # Count keyword matches
            keyword_matches = sum(
                1 for keyword in competition.keywords
                if keyword.lower() in text
            )

            if keyword_matches > 0:
                # Use highest multiplier among matches
                if competition.broadcast_multiplier > best_multiplier:
                    best_multiplier = competition.broadcast_multiplier
                    best_match = competition

        # Normalize multiplier to 0.0-1.0 (max multiplier is 3.0)
        normalized_score = min(1.0, best_multiplier / 3.0)

        if best_match:
            logger.debug(
                f"Competition detected: {best_match.code} "
                f"(multiplier: {best_multiplier}x, score: {normalized_score:.2f})"
            )
            return normalized_score, best_match.code

        logger.debug("No competition level detected, using default 0.33")
        return 0.33, None  # Default: low-level competition

    def _calculate_hype_score(self, text: str) -> float:
        """
        Calculate hype indicators component (0.0-1.0)

        Sums up hype_boost values from all matching patterns.
        Multiple matches compound the hype score.
        """
        total_hype = 0.0
        matched_categories = []

        for indicator in self.hype_indicators:
            try:
                if re.search(indicator.pattern, text, re.IGNORECASE):
                    total_hype += indicator.hype_boost
                    matched_categories.append(indicator.category)
            except re.error as e:
                logger.warning(
                    f"Invalid regex pattern in HypeIndicator {indicator.id}: "
                    f"{indicator.pattern} - {e}"
                )
                continue

        # Clip to 1.0 max
        hype_score = min(1.0, total_hype)

        if matched_categories:
            logger.debug(
                f"Hype indicators matched: {set(matched_categories)} "
                f"(score: {hype_score:.2f})"
            )

        return hype_score

    def _calculate_attendance_score(self, article) -> float:
        """
        Calculate attendance component (0.0-1.0)

        Scales expected_attendance using configurable thresholds:
        - < 5k: 0.0 (very small)
        - 5k-20k: 0.2-0.5 (small to medium)
        - 20k-50k: 0.5-0.8 (medium to large)
        - >= 50k: 1.0 (massive)
        """
        attendance = article.expected_attendance

        if not attendance or attendance <= 0:
            return 0.0

        # Get thresholds from config
        small = self.config.attendance_small
        medium = self.config.attendance_medium
        large = self.config.attendance_large

        if attendance < small:
            # Scale 0.0-0.2 for very small events
            score = (attendance / small) * 0.2
        elif attendance < medium:
            # Scale 0.2-0.5 for small to medium
            ratio = (attendance - small) / (medium - small)
            score = 0.2 + (ratio * 0.3)
        elif attendance < large:
            # Scale 0.5-0.8 for medium to large
            ratio = (attendance - medium) / (large - medium)
            score = 0.5 + (ratio * 0.3)
        else:
            # 1.0 for massive events
            score = 1.0

        logger.debug(
            f"Attendance score: {score:.2f} for {attendance:,} attendees"
        )

        return score

    def _zero_result(self, reason: str = "") -> Dict:
        """Return zero broadcastability result"""
        if reason:
            logger.debug(f"Zero broadcastability: {reason}")

        return {
            'broadcastability_score': 0.0,
            'hype_score': 0.0,
            'is_broadcastable': False,
            'sport_type': None,
            'competition_level': None,
            'components': {
                'sport_appeal': 0.0,
                'competition_level': 0.0,
                'hype_indicators': 0.0,
                'attendance': 0.0,
            }
        }

    def refresh_config(self):
        """Reload configuration from database (call after updating DB)"""
        from event_taxonomy.models import (
            SportType,
            CompetitionLevel,
            HypeIndicator,
            BroadcastabilityConfig
        )

        self.config = BroadcastabilityConfig.get_instance()
        self.sport_types = {
            st.code: st
            for st in SportType.objects.filter(is_active=True)
        }
        self.competition_levels = list(
            CompetitionLevel.objects.filter(is_active=True)
                .select_related('sport_type')
        )
        self.hype_indicators = list(
            HypeIndicator.objects.filter(is_active=True)
        )

        logger.info("BroadcastabilityCalculator configuration refreshed")
