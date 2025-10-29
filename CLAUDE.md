# NaviGate - Claude Development Notes

## Your constitutional rules

1. First think through the problem, read the codebase for relevant files
2. Check existing tasks: `backlog task list --plain` or `backlog overview`
3. Create or update task before starting work (use backlog CLI or Edit tool)
4. Work on dedicated feature branch: `git checkout -b task-X-description`
5. Update task status as you progress (To Do → In Progress → Review)
6. Make every code change as simple as possible - avoid massive or complex changes
7. Every change should impact as little code as possible - simplicity is key
8. Mark task as "Review" when ready for human validation
9. Add detailed implementation notes to task's Progress Log section
10. High-level explanation at each step of what changes were made
11. Every temporary script or input and its output, needed for temporary testing some functonality or feature must be placed in test/ folder
12. Any parameter should be stored and modified in the database thru GUI.

## Task Management with Backlog.md

### Before Starting Work
- **Check existing tasks:** `backlog task list --plain` or `backlog overview`
- **Read task details:** `backlog task view task-X --plain` or read file directly
- **Search tasks:** `backlog search --plain --type task "keyword"`
- **Verify task ID:** Always check last ID before creating new tasks
  ```bash
  ls backlog/tasks/ | grep -oP 'task-\d+' | sort -V | tail -1
  ```
- **Create new tasks** when needed with proper metadata:
  - Use CLI: `backlog task create "Title" -d "Description" -s "To Do" -a @claude`
  - Or manually: Write to `backlog/tasks/task-X - Title.md` following template

### During Implementation
- **Update task status:** Move from "To Do" → "In Progress" → "Review"
- **Add progress notes:** Update task file's Progress Log section with:
  - Date and what was implemented
  - Decisions made and why
  - Blockers or issues encountered
  - Files modified
- **Work on feature branch:** `git checkout -b task-X-brief-description`
- **Commit regularly:** Reference task ID in commits: `git commit -m "task-X: Description"`

### After Completion
- **Change status to Review:** Edit task file or use `backlog task edit task-X -s "Review"`
- **Document completion:** Add final notes about implementation
- **Request human merge:** Mention task is ready for review
- **Never push directly:** Human reviews and merges the feature branch

### Task File Format

**Key YAML fields:** `id`, `title`, `status`, `assignee`, `priority`, `parent`, `milestone`
**Key sections:** Description, Implementation Plan, Acceptance Criteria, Progress Log
**Example:** See any existing task in `backlog/tasks/` for full template.

### Essential Backlog Commands

**IMPORTANT for Claude:** Always use `--plain` flag with backlog commands to get text output instead of interactive UIs.

**Recommended Workflow for Claude:**

```bash
# View all tasks (ALWAYS use --plain flag)
backlog task list --plain                      # List all tasks grouped by status
backlog overview                                # Project statistics and health metrics

# View specific task
backlog task view task-X --plain                # Full task details with formatting
# Or use Read tool: backlog/tasks/task-X - Title.md

# Search tasks (ALWAYS use --plain flag)
backlog search --plain "keyword"                # Search all content
backlog search --plain --type task "frontend"   # Search only tasks
backlog search --plain --status "To Do"         # Filter by status
backlog search --plain --priority high          # Filter by priority

# Create new task
backlog task create "Title" -d "Description" -s "To Do" -a @claude -l label1,label2 -p high

# Update task status (use Edit tool on task file)
# Edit YAML frontmatter: status: To Do → In Progress → Review
# Example: Edit backlog/tasks/task-X - Title.md

# Quick file-based operations (alternative to CLI)
ls backlog/tasks/                               # List task files
# Glob pattern: "backlog/tasks/*.md"
# Grep pattern in: backlog/tasks/

# Archive completed tasks (Victor runs this)
backlog cleanup                                 # Moves old completed tasks to archive
```

**Task Status Workflow:**
- `Backlog` - Future task, not prioritized yet
- `To Do` - Task ready to be worked on (prioritized)
- `In Progress` - Claude actively working on task
- `Review` - Task complete, awaiting human validation
- `Done` - Human approved and merged (human changes this)
- `Blocked` - Cannot proceed, needs human intervention

**Priority Levels:**
- `high` - Critical path, must do soon
- `medium` - Important but not urgent (default)
- `low` - Nice to have, low priority

**Epic/Parent Task Hierarchy:**

Phase epics: task-7 (✅), task-8 (✅), task-9 (🔄), task-10 (📋), task-18 (🔄)
To link subtask: Add `parent: task-9` to YAML frontmatter or use `-p task-9` flag in create command.

**Current Major Refactor (task-18):**
- Per-business-type relevance scoring system in progress
- Database schema complete (Phase 1 ✅)
- Backend code updates in progress (Phase 2-4)
- See "Per-Business-Type Relevance System" section below for details

## Quick Reference

**For project overview, tech stack, and ML architecture:** See [README.md](README.md)

**Project Structure:**
```
navigate-app/
├── backend/          # Django: businesses, news, recommendations, ml_engine apps
├── frontend/         # React + Vite PWA
├── backlog/          # Task management (tasks/, completed/, archive/)
├── scripts/          # Development utilities (start/stop/setup/reset)
└── docker/           # Docker configuration
```

**Development Scripts:** See `/scripts/` directory. [README.md](README.md) documents all scripts and workflow.

**Access URLs:** Frontend http://localhost:3001 | Backend http://localhost:8000 | Admin http://localhost:8000/admin

**Project Status:** See [README.md](README.md) for current phase status and roadmap.

**Phase 2 Crawler System:** Complete. See [README.md](README.md) for architecture, API endpoints, and usage instructions.

## Per-Business-Type Relevance System (task-18)

**Status**: Database ✅ Complete | Backend ⚠️ In Progress | Frontend ⚠️ Pending

### Overview

Major architectural refactor to support **per-business-type relevance scoring**. Each article now gets 4 separate relevance scores (pub, restaurant, coffee_shop, bookstore) instead of one global score. Users see articles filtered and sorted by their business type's specific relevance score.

### Key Changes

**Database Schema (Phase 1 - COMPLETE ✅)**
- `BusinessType` model: Dynamic business type configuration with customizable weights
  - 4 initial types: pub, restaurant, coffee_shop, bookstore
  - Configurable relevance calculation weights (suitability, keyword, event_scale, neighborhood)
  - Configurable thresholds per type
- `ArticleBusinessTypeRelevance` model: Stores per-type relevance scores
  - Each article has 4 separate relevance_score entries (one per business type)
  - Component scores stored for transparency (suitability, keyword, event, neighborhood)
- `Business.business_type`: Migrated from CharField to FK(BusinessType)
- `BusinessTypeKeyword.business_type`: Migrated from CharField to FK(BusinessType)

**Backend Code (Phase 2-3 - IN PROGRESS ⚠️)**
- Subtasks 18.1-18.10 update ML pipeline, API, serializers, and frontend
- See task-18 file for complete subtask breakdown

**Critical Migration Notes:**
- Old field: `NewsArticle.business_relevance_score` (single global score) - DEPRECATED, to be removed
- New system: `ArticleBusinessTypeRelevance` model (4 scores per article)
- **DO NOT run `process_articles` until tasks 18.1-18.3 are complete!**
- Backend code still uses old single-score system until Phase 2 complete

### Migrations Applied

```
businesses/0006_businesstype.py
businesses/0007_seed_business_types.py
businesses/0008_migrate_business_type_to_fk_step1.py
businesses/0009_complete_fk_migration.py
news/0015_articlebusinesstyperelevance.py
```

### Implementation Phases

**Phase 1: Database Schema** ✅
- All migrations run successfully
- Data integrity verified
- 4 business types seeded
- 83 business type keywords migrated

**Phase 2: Backend Code Updates** (tasks 18.1-18.7)
- Remove old business_relevance_score field
- Add calculate_relevance_for_type to BusinessMatcher
- Update MLOrchestrator for per-type scoring
- Create user profile API endpoint
- Update NewsArticleViewSet to filter by business_type
- Create BusinessType ViewSet and serializers
- Update NewsArticleSerializer for per-type scores

**Phase 3: Frontend Updates** (tasks 18.8-18.10)
- Create AuthContext for user/business context
- Update newsApi.js to pass business_type parameter
- Update Dashboard to use business type context

**Phase 4: Data & Testing** (tasks 18.11-18.15)
- Seed business type keywords
- Reprocess all articles with new ML pipeline
- Update admin interfaces
- Test with different business types
- Documentation and cleanup

### How It Works

**Before (Old System):**
```python
article.business_relevance_score = 0.75  # Single global score
```

**After (New System):**
```python
# Each article has 4 separate scores
ArticleBusinessTypeRelevance(article=article, business_type=pub, relevance_score=0.85)
ArticleBusinessTypeRelevance(article=article, business_type=restaurant, relevance_score=0.45)
ArticleBusinessTypeRelevance(article=article, business_type=coffee_shop, relevance_score=0.60)
ArticleBusinessTypeRelevance(article=article, business_type=bookstore, relevance_score=0.25)

# Users only see articles filtered by THEIR business type
pub_owner.sees_articles_with(business_type='pub', min_score=0.5)  # Shows article (0.85)
bookstore_owner.sees_articles_with(business_type='bookstore', min_score=0.5)  # Hides article (0.25)
```

### Business Type Configuration

Each BusinessType has customizable parameters:

**Relevance Weights** (sum to 1.0):
- `suitability_weight` (0.3): Weight of business_suitability_score
- `keyword_weight` (0.2): Weight of keyword matching
- `event_scale_weight` (0.2): Weight of event scale/attendance
- `neighborhood_weight` (0.3): Weight of geographic proximity

**Thresholds**:
- `min_relevance_threshold` (0.5): Minimum score to show article to user
- `min_suitability_threshold` (0.5): Minimum business_suitability_score to process article

These parameters are stored in the database and configurable via admin GUI (no code changes needed).

### Backward Compatibility Warning

**IMPORTANT**: Until Phase 2 is complete, the system is in a transitional state:
- Database supports per-type scoring
- Backend code still uses old `business_relevance_score` field
- Running ML pipeline will fail or produce incorrect results
- Wait for tasks 18.1-18.3 completion before processing articles

### Files to Update (Phase 2-4)

**Backend:**
- `backend/news/models.py` - Remove business_relevance_score field
- `backend/ml_engine/business_matcher.py` - Add calculate_relevance_for_type
- `backend/ml_engine/orchestrator.py` - Update process_article logic
- `backend/businesses/api/views.py` - Add user profile endpoint
- `backend/news/api/views.py` - Update filtering by business_type
- `backend/news/api/serializers.py` - Include per-type scores

**Frontend:**
- `frontend/src/contexts/AuthContext.jsx` - Add business type context
- `frontend/src/services/newsApi.js` - Pass business_type parameter
- `frontend/src/pages/Dashboard.jsx` - Use business type filtering

See individual task files (task-18.1 through task-18.15) for detailed implementation code.