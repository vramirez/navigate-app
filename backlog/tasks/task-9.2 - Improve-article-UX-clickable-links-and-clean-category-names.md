---
id: task-9.2
title: 'Improve article UX: clickable links and clean category names'
status: Review
assignee:
  - '@claude'
created_date: '2025-10-13 21:45'
labels:
  - phase-3
  - frontend
  - ux
dependencies: []
parent_task_id: task-9
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make article titles clickable to open source URLs in new tab, and fix category display to show clean names instead of translation keys
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

1. **Fix Category Mapping** - Update `dataTransformers.js` to map event types to valid categories that exist in translation files
2. **Add Article Links (Expanded View)** - Wrap article titles in `<a>` tags with `target="_blank"`
3. **Add Article Links (Minimized View)** - Apply same clickable functionality to minimized/disliked cards
4. **Test in Browser** - Verify links open in new tab and categories display correctly

## Acceptance Criteria

- [x] Article titles are clickable in both expanded and minimized views
- [x] Clicking article opens source URL in new tab (NaviGate remains open)
- [x] Category badges show clean names (e.g., "Eventos", "Gastronomía") instead of translation keys
- [ ] All functionality tested in browser

## Progress Log

### 2025-10-13 21:45 - Implementation Complete

**Changes Made:**

1. **Fixed Category Mapping** ([dataTransformers.js:15-27](frontend/src/utils/dataTransformers.js#L15-L27))
   - Updated `mapEventTypeToCategory()` function to use only valid categories
   - Changed fallback from `'general'` to `'comunidad'` (valid category)
   - Updated mappings:
     - `cultural`: `cultura` → `eventos`
     - `entertainment`: `entretenimiento` → `eventos`
     - `business`: `negocios` → `economia`
     - `politics`: `politica` → `comunidad`
     - `weather`: `clima` → `clima-alertas`
   - **Reasoning**: All event types now map to categories that exist in translation files (es.json, en.json), preventing "newsCategories.public.general" display issue

2. **Added Clickable Links - Expanded View** ([Dashboard.jsx:327-336](frontend/src/pages/Dashboard.jsx#L327-L336))
   - Wrapped article title in `<a>` tag with:
     - `href={news.url}` - Links to article source
     - `target="_blank"` - Opens in new tab
     - `rel="noopener noreferrer"` - Security best practice
     - `className="hover:text-blue-600 transition-colors cursor-pointer"` - Maintained hover styling

3. **Added Clickable Links - Minimized View** ([Dashboard.jsx:279-288](frontend/src/pages/Dashboard.jsx#L279-L288))
   - Applied same link functionality to disliked/minimized articles
   - Used lighter hover color (`hover:text-blue-400`) appropriate for gray background
   - Ensures consistent behavior across both view modes

**Files Modified:**
- `frontend/src/utils/dataTransformers.js` - Category mapping fix
- `frontend/src/pages/Dashboard.jsx` - Clickable article titles (2 locations)

**Technical Decisions:**
- Used `target="_blank"` for new tab behavior as requested
- Added `rel="noopener noreferrer"` for security (prevents window.opener exploitation)
- Kept hover effects on `<a>` tag to maintain visual feedback
- Used valid category mappings instead of adding "general" to translations (cleaner solution)
