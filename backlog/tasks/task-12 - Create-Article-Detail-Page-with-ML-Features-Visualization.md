---
id: task-12
title: Create Article Detail Page with ML Features Visualization
status: Backlog
assignee:
  - '@claude'
reporter: '@victor'
created_date: ''
updated_date: '2025-10-16 15:27'
labels:
  - frontend
  - phase-3
  - ml-features
  - ux
milestone: Phase 3
dependencies:
  - task-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a comprehensive Article Detail page in the React frontend that displays all extracted ML features for individual news articles. Currently, users can only see basic article information (title, date, relevance badge) in the Dashboard, but there's no way to view the rich ML-extracted features like event details, location data, keywords, entities, and scoring breakdowns.

The Django API already exposes all these features via `/api/news/articles/{id}/`, but the frontend has no UI to display them. This page will provide transparency into the ML processing pipeline and help validate feature extraction quality.

## Business Value

- **Transparency**: Users can see what the ML engine detected from each article
- **Trust Building**: Understanding how relevance scores are calculated builds confidence
- **Quality Assurance**: Easier to spot ML misclassifications and improvement opportunities
- **User Education**: Helps users understand why certain recommendations were generated
- **Debugging**: Developers can quickly validate feature extraction without using Django Admin
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Article detail page accessible via `/news/:articleId` route
- [ ] #2 Dashboard article cards link to detail page (clickable or "View Details" button)
- [ ] #3 All ML-extracted features displayed in organized sections
- [ ] #4 Loading state with skeleton screens during fetch
- [ ] #5 Error states for 404 and API failures handled gracefully
- [ ] #6 Responsive design works on mobile and desktop
- [ ] #7 Back navigation returns to Dashboard preserving scroll position
- [ ] #8 External article link opens in new tab
- [ ] #9 Map visualization shows event location (if lat/long available)
- [ ] #10 Scoring indicators use color-coded visual representations
- [ ] #11 Keywords and entities displayed as interactive tags
- [ ] #12 Empty states for missing optional data handled gracefully
- [ ] #13 All text in Spanish with proper i18n
- [ ] #14 Related recommendations section shows linked recommendations (if any)
- [ ] #15 Processing errors displayed clearly (if present)
- [ ] #16 Page performance < 2 seconds load time

## Technical Specifications

**API Endpoint:**
```javascript
GET /api/news/articles/{id}/
```

**Response Fields to Display:**
```javascript
{
  id, title, content, first_paragraph, url,
  source_name, source_country, author, published_date,
  section, crawl_section,

  // ML extracted features
  event_type_detected, event_subtype,
  primary_city, neighborhood, venue_name, venue_address,
  latitude, longitude,
  event_start_datetime, event_end_datetime, event_duration_hours,
  expected_attendance, event_scale,
  business_suitability_score, urgency_score,
  business_relevance_score, sentiment_score,

  // Keywords & entities
  extracted_keywords, entities,

  // Processing metadata
  features_extracted, feature_extraction_date,
  feature_extraction_confidence,
  is_processed, processing_error,

  // Category system
  category, subcategory,

  created_at, updated_at
}
```

**Map Integration:**
- Use React Leaflet library (lightweight, free)
- Only render map if `latitude` and `longitude` are present
- Center map on event location with marker
- Zoom level: 15 (neighborhood level)
- Fallback to text-only location if no coordinates

**Recommended Libraries:**
- `react-leaflet`: Map visualization (free, no API key needed)
- `date-fns`: Date formatting (already in project)
- `react-query`: Data fetching (already in project)
- `@heroicons/react`: Icons (already in project)

## Files to Create/Modify

**New Files:**
- `frontend/src/pages/ArticleDetail.jsx` - Main detail page component
- `frontend/src/components/EventMap.jsx` - Map component for location visualization
- `frontend/src/components/ScoreIndicator.jsx` - Reusable score visualization component
- `frontend/src/components/KeywordTags.jsx` - Keyword/entity tag display component

**Modified Files:**
- `frontend/src/App.jsx` - Add article detail route
- `frontend/src/services/newsApi.js` - Add `getArticleById()` function
- `frontend/src/pages/Dashboard.jsx` - Add click handlers to article cards for navigation
- `frontend/public/locales/es/translation.json` - Add Spanish translations for new labels
- `frontend/public/locales/en/translation.json` - Add English translations (fallback)

## Testing Checklist

- [ ] #17 Navigate from Dashboard to article detail and back
- [ ] #18 Verify all ML features display correctly for article with full features
- [ ] #19 Verify graceful handling for article with minimal/no features
- [ ] #20 Test 404 error for non-existent article ID
- [ ] #21 Test map rendering for articles with lat/long
- [ ] #22 Test map section hidden for articles without location data
- [ ] #23 Verify scoring indicators use correct colors
- [ ] #24 Test mobile responsive layout (320px, 768px, 1024px)
- [ ] #25 Verify external article link opens in new tab
- [ ] #26 Test back navigation preserves Dashboard state
- [ ] #27 Verify Spanish translations display correctly
- [ ] #28 Test loading states during slow network
- [ ] #29 Test error states with backend offline

## Success Metrics

- Users can view detailed ML extraction results for any article
- Average time to understand article relevance reduced by 40%
- Improved trust in ML recommendations through transparency
- Easier identification of ML misclassifications for future improvements
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
### 1. Create Article Detail Route & Page Component
- Add route `/news/:articleId` in `frontend/src/App.jsx`
- Create `frontend/src/pages/ArticleDetail.jsx` component
- Implement URL routing and navigation from Dashboard article cards
- Add "View Details" button or make entire article card clickable

### 2. Build API Integration
- Add `getArticleById(id)` function to `frontend/src/services/newsApi.js`
- Use React Query for data fetching with caching
- Implement loading states, error handling, and retry logic
- Handle 404 for non-existent articles

### 3. Design Information Architecture

Organize extracted features into logical sections:

**A. Article Header Section**
- Article title (large, prominent)
- Publication date (relative time in Spanish: "Hace 3 días")
- News source name and country
- Relevance badge (reuse RelevanceBadge component)
- Category and subcategory badges
- "Read Original" button linking to article URL (opens in new tab)

**B. Article Content Section**
- First paragraph preview (if available)
- Full article content (collapsible if very long)
- Reading time estimate

**C. Event Information Section** (if event detected)
- Event type and subtype
- Event dates: start datetime, end datetime, duration
- Event scale (local, city-wide, national, international)
- Expected attendance (if available)
- Location details:
  - Primary city
  - Neighborhood
  - Venue name
  - Venue address
  - Map visualization (if lat/long available) - use Leaflet or Google Maps

**D. ML Extraction Details Section**
- Feature extraction date
- Extraction confidence score
- Business suitability score (0-1 scale with visual indicator)
- Urgency score (0-1 scale with visual indicator)
- Business relevance score (the main score, 0-1)
- Sentiment score (-1 to 1 with positive/negative/neutral indicator)

**E. Keywords & Entities Section**
- Extracted keywords as tag pills (colored badges)
- Named entities detected (people, places, organizations)
- Click on tags to potentially filter/search related articles (future enhancement)

**F. Processing Status Section** (collapsible)
- `is_processed` status
- `features_extracted` status
- Processing errors (if any) - show `processing_error` field
- Internal IDs for debugging (article ID, source ID)

**G. Related Recommendations Section**
- Show any recommendations generated from this article
- Link to the recommendation detail or action
- Display recommendation status (pending, done, ignored)

### 4. UI/UX Implementation Details

**Visual Design:**
- Use Tailwind CSS for consistent styling with rest of app
- Card-based layout with clear section separation
- Responsive design for mobile viewing
- Color-coded scoring indicators:
  - 0.0-0.3: Red/low
  - 0.3-0.6: Yellow/medium
  - 0.6-1.0: Green/high
- Empty state handling when features are not available

**Navigation:**
- Breadcrumb: Dashboard > Article Title
- Back button to return to Dashboard
- Share button (copy article URL to clipboard)
- Previous/Next article navigation (optional enhancement)

**Interactive Elements:**
- Expandable/collapsible sections for long content
- Tooltips explaining ML scores and technical terms
- Map pins for location data (if coordinates available)
- Copy buttons for IDs and URLs

### 5. Accessibility & Spanish i18n
- All labels and descriptions in Spanish (primary)
- ARIA labels for screen readers
- Keyboard navigation support
- Semantic HTML structure
- Add translations to `frontend/public/locales/es/translation.json`

### 6. Error Handling & Edge Cases
- Article not found (404) - friendly error message
- Article with no ML features extracted - show "Processing pending" message
- Missing optional fields (venue, dates, etc.) - gracefully hide sections
- Failed API requests - retry button and error message
- Very long articles - implement "Read More" collapse
<!-- SECTION:PLAN:END -->

## Notes

**Phase 3 Context:**
This task builds on task-1 (real news integration) and task-4 (ML pipeline integration). The API already exposes all necessary fields, so this is primarily a frontend UX task.

**Future Enhancements (Phase 4):**
- Edit ML features directly from UI (admin only)
- Flag articles for reprocessing if features are incorrect
- Search/filter by specific keywords or entities
- Compare multiple articles side-by-side
- Export feature data as JSON/CSV
- Article similarity recommendations
- User feedback on feature accuracy

**Design Reference:**
Look at Django Admin's article detail page for inspiration on organizing information, but make it more user-friendly and visual for non-technical users.

## Dependencies

- Requires task-1 (Dashboard with real news data) to be merged
- Requires task-4 (ML pipeline integration) to have feature-extracted articles
- No new backend changes needed - API already complete

## Related Tasks

- task-1: Update frontend Dashboard with real news data (provides base data)
- task-4: Integrate real news data with ML recommendation pipeline (provides features)
- task-9.1: Add first_paragraph field (used in detail view)
- task-9.2: Improve article UX (clickable links implemented here)

## Progress Log

### 2025-10-16 - Task Created
- Identified user need for ML feature transparency
- Reviewed existing API capabilities (all features available)
- Drafted comprehensive implementation plan
- Ready for development when approved
