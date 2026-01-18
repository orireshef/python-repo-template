# Python Repo Template

A starting point for Python projects in Cursor, with built-in support for AI-assisted development and multi-agent collaboration.

## What You Get

### Development Stack
- **uv** — Fast Python package management
- **pytest** + **pytest-cov** — TDD workflow with coverage
- **ruff** — Linting and formatting

### AI Agent Workflow
- **Context engineering** — Structured logs and implementation planning
- **Session management** — `/session` command to set context
- **Multi-agent safety** — Hooks prevent agents from stepping on each other's work

### Cursor Hooks (Automated Enforcement)

| Hook | What it does |
|------|--------------|
| `beforeSubmitPrompt` | Blocks prompts if no session context set |
| `beforeReadFile` | Guards log access to active context only |
| `afterFileEdit` | Tracks files, formats Python, syncs plan to master, auto-rotates logs |
| `beforeShellExecution` | Blocks dangerous git commands |
| `stop` | Logs session end |

### Stateful Artifacts

| File | Purpose |
|------|---------|
| `logs/.active` | Current agent's session state (context, log file, files touched) |
| `IMPLEMENTATION_PLAN.md` | Cross-agent source of truth for all stories/tasks |
| `logs/*.md` | Agent scratchpad for thinking and context offloading |

## Quick Start

```bash
# Clone and navigate
git clone <this-repo> my-project
cd my-project

# Install dependencies
uv sync

# Initialize context artifacts (if not present)
# Run /init command in Cursor

# Start a session
# Run /session root (or /session <story-name>) in Cursor

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
src/                    # Source code (src layout)
tests/                  # Test files
logs/                   # Agent scratchpad logs
  .active               # Session state file
.cursor/
  hooks/                # Automated workflow hooks
  rules/                # Cursor agent rules
  skills/               # Reusable agent skills
  commands/             # Custom commands (/init, /session)
DESIGN.md               # System design and goals
IMPLEMENTATION_PLAN.md  # Task tracking (syncs to master)
memories.md             # Personal preferences
```

## Cursor Commands

| Command | Purpose |
|---------|---------|
| `/init` | Initialize context artifacts (DESIGN.md, logs/, IMPLEMENTATION_PLAN.md, etc.) |
| `/session <name>` | Set session context to a story or `root` for ad-hoc work |

## Workflow Overview

### Session Start
1. Run `/session <story-name>` or `/session root`
2. Agent reads recent logs and IMPLEMENTATION_PLAN.md
3. If story is `planned`, agent does Story Planning before implementation

### Every Turn
1. Check context in `logs/.active`
2. Log thinking to active log file
3. Stay in scope — ask before switching context
4. Update IMPLEMENTATION_PLAN.md when tasks change (auto-syncs to master)

### Multi-Agent Safety
- Each agent is locked to their session context
- Edits to other agents' stories are **automatically reverted**
- IMPLEMENTATION_PLAN.md syncs to master after every edit
- Log files auto-rotate when they exceed ~4000 chars

### TDD & Git Flow
- Write tests before implementation
- Atomic commits (one per function/test)
- Quick tasks → commit to `master`
- Story work → `feature/<name>` branch with PR

## Full Documentation

See `.cursor/rules/workflow.mdc` for complete workflow rules.
