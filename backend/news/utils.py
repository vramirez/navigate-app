"""
Utility functions for news app
"""


def calculate_feature_completeness(article):
    """
    Calculate ML feature extraction completeness score.

    Returns a float between 0.0 and 1.0 indicating what percentage
    of expected ML features were successfully extracted from the article.

    Args:
        article: NewsArticle instance or dict with article fields

    Returns:
        float: 0.0-1.0 representing completeness percentage

    Example:
        >>> article = NewsArticle.objects.get(pk=1)
        >>> score = calculate_feature_completeness(article)
        >>> print(f"Completeness: {score:.2%}")
        Completeness: 75.00%
    """
    total_fields = 0
    populated_fields = 0

    def is_populated(value):
        """Check if a field has a meaningful value"""
        if value is None or value == '':
            return False
        if isinstance(value, list):
            return len(value) > 0
        if isinstance(value, (int, float)):
            # For scores, 0.0 is a valid value (negative relevance)
            # But we expect scores to be set, so check they're not exactly 0.0 for all
            return True
        if isinstance(value, bool):
            # Booleans are always "populated" (default False is still a value)
            return True
        return True

    def get_field(field_name):
        """Get field value from article (works with model instances and dicts)"""
        if isinstance(article, dict):
            return article.get(field_name)
        return getattr(article, field_name, None)

    # Critical fields (always expected if features_extracted=True)
    critical_fields = [
        'business_suitability_score',
        'urgency_score',
        'sentiment_score',
        'category',
        'feature_extraction_confidence'
    ]

    # Event-related fields (optional but important for event articles)
    event_fields = [
        'event_type_detected',
        'event_subtype',
        'primary_city',
        'neighborhood',
        'venue_name',
        'venue_address',
        'latitude',
        'longitude',
        'event_country',
        'event_start_datetime',
        'event_end_datetime',
        'event_duration_hours',
        'expected_attendance',
        'event_scale',
        'colombian_involvement'
    ]

    # Keywords and entities (arrays)
    array_fields = [
        'extracted_keywords',
        'entities'
    ]

    # Additional categorization
    categorization_fields = [
        'subcategory'
    ]

    # Combine all fields to check
    all_fields = (
        critical_fields +
        event_fields +
        array_fields +
        categorization_fields
    )

    # Count populated vs total
    for field_name in all_fields:
        total_fields += 1
        value = get_field(field_name)

        if is_populated(value):
            populated_fields += 1

    # Calculate percentage
    if total_fields == 0:
        return 0.0

    completeness = populated_fields / total_fields

    # Round to 2 decimal places to avoid floating point precision issues
    return round(completeness, 2)
