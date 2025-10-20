# LLM Feature Extraction Prompt Template

This document contains a prompt template for using Claude API (or GPT) to extract features from news articles when regex+NLP extraction fails or has low completeness.

## When to Use LLM Extraction

Use this as a **fallback** when:
- Feature completeness score < 0.7 (70%)
- Critical fields are missing (event_start_datetime, event_type_detected)
- Cost-effective: Only call LLM for articles that need it

## Implementation Strategy

1. **First pass:** Run standard regex + NLP extraction (free, fast)
2. **Check completeness:** Calculate feature_completeness_score
3. **Conditional LLM call:** If score < 0.7, call LLM with this prompt
4. **Merge results:** Combine LLM results with existing extraction
5. **Recalculate completeness:** Should now be 80-95%

## API Setup

```python
# Install: pip install anthropic
from anthropic import Anthropic

client = Anthropic(api_key="YOUR_API_KEY")
```

## Prompt Template

```python
EXTRACTION_PROMPT = """
You are an expert at extracting structured information from Spanish news articles about events in Colombia.

Extract the following information from the article below. Return ONLY valid JSON with no additional text.

**Required fields to extract:**

1. **event_start_datetime** (ISO 8601 format YYYY-MM-DDTHH:MM:SS or null)
   - The date and time when the event starts
   - Examples: "2025-03-15T20:00:00", "2025-04-01T09:00:00"
   - If only date mentioned, use 00:00:00 for time

2. **event_end_datetime** (ISO 8601 format or null)
   - The date and time when the event ends
   - Can be null if not mentioned

3. **event_duration_hours** (number or null)
   - Duration in hours
   - Examples: 2, 4.5, 24, 48

4. **event_type_detected** (string or null)
   - One of: sports_match, marathon, concert, festival, conference, exposition, food_event, cultural, nightlife
   - Choose the most appropriate category

5. **event_subtype** (string or null)
   - More specific classification if applicable
   - Examples: "colombian_soccer", "rock_concert", "food_festival"

6. **primary_city** (string or null)
   - Main Colombian city where event occurs
   - Examples: "Medellín", "Bogotá", "Cali", "Cartagena"

7. **neighborhood** (string or null)
   - Specific neighborhood in the city
   - Examples: "El Poblado", "Laureles", "Chapinero"

8. **venue_name** (string or null)
   - Name of the venue/location
   - Examples: "Estadio Atanasio Girardot", "Teatro Metropolitano"

9. **venue_address** (string or null)
   - Full address if mentioned

10. **expected_attendance** (integer or null)
    - Expected number of attendees
    - Examples: 5000, 50000

11. **event_scale** (string or null)
    - One of: "small" (<500), "medium" (500-5000), "large" (5000-50000), "massive" (>50000)

12. **event_country** (string or null)
    - Country where event occurs
    - Usually "Colombia" for local events

13. **colombian_involvement** (boolean)
    - true if Colombian national team, artists, or representatives are involved
    - true if event directly affects Colombia

14. **extracted_keywords** (array of strings)
    - 10-15 most important keywords from the article
    - Focus on: event names, participant names, locations, event type terms

15. **category** (string or null)
    - High-level category: "Sports", "Entertainment", "Culture", "Business", "Food & Drink"

16. **subcategory** (string or null)
    - More specific subcategory

**Output format:**
Return ONLY a JSON object with these exact field names. Use null for any field you cannot determine.

**Article URL:** {article_url}

**Article Title:** {article_title}

**Article Content:**
{article_content}

**JSON Output:**
"""

def extract_with_llm(article_url: str, article_title: str, article_content: str) -> dict:
    """
    Extract features from article using Claude API

    Args:
        article_url: URL of the article
        article_title: Article title
        article_content: Full article text

    Returns:
        Dictionary with extracted features
    """
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Truncate content to ~4000 chars to save tokens (adjust as needed)
    truncated_content = article_content[:4000]

    prompt = EXTRACTION_PROMPT.format(
        article_url=article_url,
        article_title=article_title,
        article_content=truncated_content
    )

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # or "claude-3-haiku-20240307" for cheaper
        max_tokens=1024,
        temperature=0,  # Deterministic for structured extraction
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse JSON response
    import json
    response_text = message.content[0].text

    # Extract JSON from response (may be wrapped in markdown)
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    return json.loads(response_text)


def hybrid_extraction(article):
    """
    Hybrid extraction: Regex+NLP first, LLM fallback

    Args:
        article: NewsArticle instance

    Returns:
        Dictionary with extracted features
    """
    # Step 1: Standard extraction (free)
    from ml_engine.services.feature_extractor import FeatureExtractor
    extractor = FeatureExtractor()
    features = extractor.extract_all(article.content, article.title)

    # Step 2: Calculate completeness
    # (Create temporary article-like dict to check completeness)
    temp_article = {
        'business_relevance_score': 0.5,
        'business_suitability_score': 0.5,
        'urgency_score': 0.5,
        'sentiment_score': 0.0,
        'category': features.get('event_type'),
        'feature_extraction_confidence': 0.8,
        'event_type_detected': features.get('event_type'),
        'event_subtype': features.get('event_subtype'),
        'primary_city': features.get('city'),
        'neighborhood': features.get('neighborhood'),
        'venue_name': features.get('venue'),
        'event_start_datetime': features.get('event_date'),
        'event_end_datetime': features.get('event_end_datetime'),
        'event_duration_hours': features.get('event_duration_hours'),
        'expected_attendance': features.get('attendance'),
        'event_scale': features.get('scale'),
        'event_country': features.get('event_country'),
        'colombian_involvement': features.get('colombian_involvement'),
        'extracted_keywords': features.get('keywords', []),
        'entities': features.get('entities', []),
        'subcategory': None,
    }

    from news.utils import calculate_feature_completeness
    completeness = calculate_feature_completeness(temp_article)

    # Step 3: Conditional LLM call
    if completeness < 0.7:
        logger.info(f"Article {article.id} has low completeness ({completeness:.2f}), calling LLM")

        try:
            llm_features = extract_with_llm(
                article_url=article.url,
                article_title=article.title,
                article_content=article.content
            )

            # Merge: LLM features override null/empty regex features
            for key, value in llm_features.items():
                if value is not None and value != '' and value != []:
                    # Map LLM field names to our feature names
                    feature_key = key
                    if key == 'event_start_datetime':
                        feature_key = 'event_date'
                    elif key == 'primary_city':
                        feature_key = 'city'
                    elif key == 'venue_name':
                        feature_key = 'venue'
                    elif key == 'expected_attendance':
                        feature_key = 'attendance'

                    # Only override if our extraction failed
                    if not features.get(feature_key):
                        features[feature_key] = value

        except Exception as e:
            logger.error(f"LLM extraction failed for article {article.id}: {e}")
            # Fall back to regex-only features

    return features
```

## Cost Estimation

**Claude 3.5 Sonnet:**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens
- Average article: ~1000 input tokens + 200 output tokens
- Cost per article: ~$0.006 (less than a cent)
- 1000 articles: ~$6

**Claude 3 Haiku (cheaper, faster):**
- Input: ~$0.25 per million tokens
- Output: ~$1.25 per million tokens
- Cost per article: ~$0.0005 (half a cent)
- 1000 articles: ~$0.50

## Alternative: OpenAI GPT

```python
from openai import OpenAI

def extract_with_gpt(article_url: str, article_title: str, article_content: str) -> dict:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Cheaper than GPT-4
        messages=[
            {"role": "system", "content": "You are an expert at extracting structured information from Spanish news articles. Always return valid JSON."},
            {"role": "user", "content": EXTRACTION_PROMPT.format(
                article_url=article_url,
                article_title=article_title,
                article_content=article_content[:4000]
            )}
        ],
        temperature=0,
        response_format={"type": "json_object"}  # Ensures JSON output
    )

    return json.loads(response.choices[0].message.content)
```

## Integration into ml_pipeline.py

```python
# In MLOrchestrator.process_article() - modify Step 1:

# Step 1: Extract features with hybrid approach
if os.environ.get('ENABLE_LLM_EXTRACTION', 'false').lower() == 'true':
    features = hybrid_extraction(article)
else:
    features = self.feature_extractor.extract_all(article.content, article.title)
```

## Environment Variables

```bash
# Add to .env
ENABLE_LLM_EXTRACTION=true  # Set to false to disable
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...
```

## Monitoring

Track LLM usage:
```python
# Add to ml_pipeline.py
if llm_was_called:
    article.llm_extraction_used = True
    article.llm_extraction_cost = 0.006  # Track cost
```

## Next Steps

1. Add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to environment
2. Test with single article first
3. Monitor accuracy and cost
4. Adjust threshold (0.7) and truncation (4000 chars) as needed
5. Consider caching LLM results to avoid re-extraction
