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

Phase epics: task-7 (✅), task-8 (✅), task-9 (🔄), task-10 (📋)
To link subtask: Add `parent: task-9` to YAML frontmatter or use `-p task-9` flag in create command.

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