---
id: task-2
title: Create legacy news admin page for mock data
status: To Do
assignee:
  - '@victor'
reporter: '@victor'
createdDate: '2025-10-05 15:05'
labels:
  - frontend
  - phase-3
  - admin
priority: medium
dependencies: []
parent: task-9
milestone: Phase 3
---

## Description

Create a separate admin/demo page that preserves access to the original 6 mock news scenarios created during Phase 1. These scenarios are valuable for demos, testing, and documentation purposes.

While the main Dashboard will now display real news (task-1), we want to preserve the carefully crafted mock scenarios that demonstrate the system's capabilities:

1. Medellín Marathon 2025
2. Copa América Final
3. Gastronomy Festival Bogotá
4. University Graduation Season
5. Shakira Concert Medellín
6. Christmas Season Approaches

## Implementation Plan

1. Create new route: `/admin/legacy-news` or `/demo/scenarios`
2. Create LegacyNewsPage component
3. Import existing mock data from Phase 1
4. Display scenarios in a grid or tabbed interface
5. Add explanatory text about mock data purpose
6. Include "Back to Dashboard" navigation
7. Update main navigation with link to legacy page (admin-only or demo mode)
8. Add documentation for accessing legacy scenarios

## Acceptance Criteria

- [ ] New page accessible at dedicated route
- [ ] All 6 mock scenarios display correctly
- [ ] Each scenario shows complete information (title, description, recommendations)
- [ ] Clear visual indication that this is demo/mock data
- [ ] Navigation between legacy page and main dashboard works
- [ ] Responsive design for mobile
- [ ] Page documented in README or user guide
- [ ] Mock data preserved in separate file (not deleted)

## Notes

**Mock Data Location:**
- Current location: `frontend/src/data/mockNews.js` (verify actual path)
- Keep this file for legacy access
- Consider renaming to `legacyScenarios.js` for clarity

**UI Design:**
- Use different theme/color to distinguish from real news
- Add banner: "Demo Scenarios - Mock Data"
- Consider adding "View Real News" CTA button

**Access Control:**
- Initially: Open access for all users
- Future: Consider admin-only or demo-mode toggle

## Related Tasks

- Related to: task-1 (main dashboard migration)
- Independent: Can be completed in parallel
