# Python Repo Template

A starting point for Python projects in Cursor, with built-in support for AI-assisted development.

## Features

- **uv** for fast dependency management
- **pytest** + **pytest-cov** for TDD workflow
- **ruff** for linting and formatting
- **Cursor rules** for consistent AI agent behavior
- **Context engineering** with structured logs and implementation planning

## Quick Start

```bash
# Clone and navigate
git clone <this-repo> my-project
cd my-project

# Install dependencies
uv sync

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
.cursor/
  rules/                # Cursor agent rules
  skills/               # Reusable agent skills
  commands/             # Custom commands
DESIGN.md               # System design and goals
IMPLEMENTATION_PLAN.md  # Task tracking
memories.md             # Personal preferences
```

## Cursor Workflow

This template includes workflow rules for AI agents:

1. **Session Start** — Read `logs/.active`, check recent logs, create/continue log file
2. **Every Turn** — Think in logs, stay in scope, ask before switching context
3. **TDD** — Write tests before implementation
4. **Git Flow** — Atomic commits, feature branches for story work

See `.cursor/rules/workflow.mdc` for full details.
