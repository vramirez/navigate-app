# NaviGate Task Management with Backlog.md

This directory contains all project tasks managed with [Backlog.md](https://github.com/MrLesk/Backlog.md), a git-native task management tool designed for human-AI collaboration.

## Directory Structure

```
backlog/
├── tasks/         # Active tasks (To Do, In Progress, Review)
├── completed/     # Completed tasks
├── archive/       # Archived tasks (moved periodically)
├── drafts/        # Draft tasks
├── docs/          # Project documentation
├── decisions/     # Architecture decision records
├── config.yml     # Backlog.md configuration
└── README.md      # This file
```

## Quick Start

### View Tasks

```bash
# List all tasks
backlog task list

# View Kanban board (terminal)
backlog board

# Open Web UI (http://localhost:6420)
backlog browser

# Search tasks
backlog search "keyword"
```

### Create Tasks

```bash
# Using CLI
backlog task create "Task title" \
  -d "Description" \
  -s "To Do" \
  -a @claude \
  -l frontend,phase-3 \
  --priority high

# Or manually create file in backlog/tasks/
# Follow the template in existing task files
```

### Update Tasks

```bash
# Change status
backlog task edit task-5 -s "In Progress"

# Or edit the task file directly
# File: backlog/tasks/task-X - Title.md
```

### Maintenance

```bash
# Archive completed tasks
backlog cleanup
```

## Workflow

### Status Progression

```
Backlog → To Do → In Progress → Review → Done
```

### Human (Victor)
1. Create tasks via CLI or Web UI
2. Assign to @claude or @victor
3. Review Claude's work (PR review)
4. Merge approved changes
5. Archive completed tasks

### AI (Claude)
1. Check tasks: `backlog task list`
2. Read assigned tasks
3. Create feature branch: `git checkout -b task-X-description`
4. Update status to "In Progress"
5. Implement feature
6. Add progress notes to task file
7. Change status to "Review"
8. Wait for human to review and merge

## Configuration

Current settings (see `config.yml`):

- **Project**: NaviGate
- **Auto-commit**: Disabled (manual git control preferred)
- **Remote operations**: Disabled (offline mode)
- **Cross-branch checking**: Disabled (performance)
- **Statuses**: Backlog, To Do, In Progress, Review, Done
- **Web UI Port**: 6420

## Task File Format

Each task is a Markdown file with YAML frontmatter:

```markdown
---
id: task-X
title: Brief descriptive title
status: To Do
assignee:
  - '@claude'
reporter: '@victor'
createdDate: '2025-10-05 15:00'
labels:
  - frontend
  - phase-3
priority: high
dependencies:
  - task-Y
milestone: Phase 3
---

## Description
What needs to be done and why.

## Implementation Plan
1. Step one
2. Step two

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Notes
Additional context.

## Progress Log
### 2025-10-05
- Started implementation
- Completed X, Y, Z
```

## Current Tasks (Phase 3)

### High Priority
- **task-1**: Update frontend Dashboard with real news data (@claude)
- **task-3**: Test crawler with Colombian news websites (@victor)
- **task-4**: Integrate real news with ML pipeline (@claude, depends on task-3)

### Medium Priority
- **task-2**: Create legacy news admin page (@victor)
- **task-5**: Enhanced ML processing (depends on task-4)
- **task-6**: Performance optimization

## Best Practices

### For Victor
- Use Web UI for quick task overview: `backlog browser`
- Create tasks via CLI for consistency
- Review Claude's branches before merging
- Archive completed tasks regularly: `backlog cleanup`

### For Claude
- **Always** check last task ID before creating new tasks:
  ```bash
  ls backlog/tasks/ | grep -oP 'task-\d+' | sort -V | tail -1
  ```
- Work in feature branches: `git checkout -b task-X-name`
- Update task status as you progress
- Add detailed notes to Progress Log section
- Mark as "Review" when ready for human validation
- **Never push directly** - human reviews and merges

## Git Integration

All task files are version controlled:

```bash
# Task changes are tracked in git
git log backlog/tasks/task-1*

# Commit task updates separately from code
git add backlog/tasks/task-1*
git commit -m "task-1: Update status to In Progress"

# Code and task updates can be in same commit
git add src/ backlog/tasks/task-1*
git commit -m "task-1: Implement dashboard API integration"
```

## Troubleshooting

### CLI Commands Timeout
- The CLI may have issues with git remote operations
- Configuration already disables remote operations
- Worst case: Edit task files directly (they're just Markdown!)

### Task ID Conflicts
- Always check last ID before creating tasks
- Use sequential IDs (task-1, task-2, task-3...)
- For subtasks: Use dotted notation (task-24.1, task-24.2)

### Web UI Won't Start
```bash
# Check if port 6420 is in use
lsof -i :6420

# Use custom port
backlog browser --port 8080
```

## Resources

- **Backlog.md GitHub**: https://github.com/MrLesk/Backlog.md
- **Documentation**: See repo README and examples
- **Issues**: Report to Backlog.md GitHub issues

## Migration Notes

- **High-level roadmap**: Still maintained in `/backlog.md` (project root)
- **Tactical tasks**: Managed here in `backlog/` directory
- **Phase 3 tasks**: Migrated from backlog.md (2025-10-05)
- **Future tasks**: Create in Backlog.md format

---

*Last updated: 2025-10-05*
*Backlog.md version: Latest from npm*
