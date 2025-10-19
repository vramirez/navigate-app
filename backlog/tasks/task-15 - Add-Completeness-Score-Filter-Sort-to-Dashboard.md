---
id: task-15
title: Add Completeness Score Filter/Sort to Dashboard
status: To Do
assignee:
  - '@claude'
reporter: '@claude'
created_date: '2025-10-19'
updated_date: '2025-10-19'
labels:
  - frontend
  - phase-3
  - ml-features
  - ux
  - dashboard
milestone: Phase 3
dependencies:
  - task-1
  - task-12
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add ability to filter and sort Dashboard news articles by ML extraction completeness score. Currently, the completeness score (0.0-1.0) is calculated in the ArticleDebugPanel component on the article detail page, showing how many ML features were successfully extracted (e.g., "18/24 campos (75%)").

This feature would allow users to:
- **Sort** articles by completeness (highest to lowest, or vice versa)
- **Filter** articles by completeness threshold (e.g., only show articles with >70% completeness)
- Quickly identify high-quality vs incomplete ML extractions
- Focus on articles with the most complete data for business decisions

The completeness calculation logic already exists in `ArticleDebugPanel.jsx` and should be:
1. Extracted to a shared utility function
2. Applied to article list in Dashboard
3. Made available as a sort/filter option in UI

## Business Value

- **Data Quality Focus**: Users can prioritize articles with complete ML feature extraction
- **Debugging Tool**: Quickly identify articles with poor extraction for ML pipeline improvements
- **User Trust**: Transparency about data completeness builds confidence in recommendations
- **Quality Control**: Filter out low-quality extractions when making business decisions
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Extract completeness calculation logic to shared utility function (e.g., `utils/completenessScore.js`)
- [ ] #2 Calculate completeness score for each article in Dashboard article list
- [ ] #3 Add "Sort by: Completeness" option to Dashboard sort dropdown
- [ ] #4 Add completeness score visual indicator to article cards (optional: small progress bar or badge)
- [ ] #5 Add filter control for minimum completeness threshold (e.g., slider or dropdown)
- [ ] #6 Display current completeness percentage on article cards when hovering or as a badge
- [ ] #7 Sorting works correctly (descending/ascending)
- [ ] #8 Filtering updates article list in real-time
- [ ] #9 Completeness indicator uses same color coding as debug panel (green/yellow/orange/red)
- [ ] #10 Performance: calculation doesn't slow down Dashboard rendering
- [ ] #11 UI in Spanish with proper i18n
<!-- AC:END -->

## Technical Specifications

### 1. Shared Utility Function

**File**: `frontend/src/utils/completenessScore.js` (NEW)

```javascript
/**
 * Calculate ML feature extraction completeness score
 * Returns percentage of populated fields vs total expected fields
 */
export const calculateCompletenessScore = (article) => {
  // Same logic as ArticleDebugPanel
  // Returns: { populated, total, percentage, percentageDisplay }
}

export const getCompletenessColor = (percentage) => {
  // Same color logic as ArticleDebugPanel
}

export const getCompletenessLabel = (percentage) => {
  if (percentage >= 0.8) return 'Excelente'
  if (percentage >= 0.5) return 'Moderado'
  if (percentage >= 0.3) return 'Pobre'
  return 'Muy pobre'
}
```

### 2. Dashboard Integration

**Modify**: `frontend/src/pages/Dashboard.jsx`

- Import completeness utility
- Calculate score for each article in `filteredArticles`
- Add to sort options: "Completitud (mayor a menor)", "Completitud (menor a mayor)"
- Add filter slider/dropdown for minimum completeness

### 3. Article Card Enhancement

**Option A** (minimal): Add small badge showing completeness %
**Option B** (visual): Add thin progress bar at bottom of card
**Option C** (on-hover): Show completeness tooltip on hover

### 4. Sort/Filter UI

Add to existing filter section in Dashboard:
- **Sort dropdown**: Add "Completitud" options
- **Filter control**: Slider (0-100%) or dropdown (All / >50% / >70% / >90%)

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
### Phase 1: Extract Shared Logic
1. Create `utils/completenessScore.js`
2. Move calculation logic from ArticleDebugPanel to shared utility
3. Update ArticleDebugPanel to use imported utility
4. Verify debug panel still works correctly

### Phase 2: Dashboard Calculation
1. Import completeness utility in Dashboard
2. Calculate score for each article in article list
3. Add score to article objects for sorting/filtering
4. Verify performance (should be negligible for <100 articles)

### Phase 3: Sort Implementation
1. Add "Completitud" options to sort dropdown
2. Implement sort logic in `filteredArticles` memo
3. Test sorting works correctly

### Phase 4: Filter Implementation
1. Add filter UI control (recommend slider for UX)
2. Implement filter logic to exclude articles below threshold
3. Show current filter state to user
4. Test filtering updates correctly

### Phase 5: Visual Indicator (Optional)
1. Decide on visual approach (badge vs progress bar)
2. Add to ArticleCard component
3. Use color coding for quick scanning
4. Test responsive design
<!-- SECTION:PLAN:END -->

## Design Considerations

### Performance
- Calculation is O(n) per article
- For 50 articles: ~50ms total (negligible)
- Use `useMemo` to prevent recalculation on every render

### UX
- Don't overwhelm users with too many filters
- Consider making this an "Advanced" or "Debug" mode feature
- Default sort should remain "Fecha de publicación"
- Clear indication when filters are active

### Visual Design
- Match existing Dashboard filter/sort styling
- Use same color scheme as debug panel for consistency
- Consider making completeness indicator subtle (not prominent)

## Future Enhancements (Phase 4)

- Filter by specific missing fields (e.g., "Show only articles with location data")
- Bulk reprocess articles with low completeness scores
- Completeness trends over time (analytics)
- Alert when completeness drops below threshold

## Dependencies

- Requires task-1 (Dashboard with real news data)
- Requires task-12 (ArticleDetail with completeness calculation)
- No backend changes needed (pure frontend feature)

## Related Tasks

- task-1: Update frontend Dashboard with real news data
- task-12: Create Article Detail Page (where completeness score was introduced)
- task-4: ML pipeline integration (source of features being measured)

## Notes

**Priority: Low** - This is primarily a debugging/quality control feature. Not critical for MVP but very useful for:
- Developers validating ML pipeline
- QA identifying data quality issues
- Power users who want to see data completeness

Consider implementing this as a toggle-able "Advanced mode" or "Debug view" in Dashboard rather than always-on feature to avoid overwhelming non-technical users.

## Progress Log

### 2025-10-19 - Task Created
- Identified need while implementing ArticleDebugPanel completeness score
- Completeness calculation logic already exists and works well
- Ready for implementation when prioritized
