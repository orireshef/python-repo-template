---
name: uv-package-management
description: Use when managing Python projects, dependencies, virtual environments, or Python versions with uv. Triggers include creating projects (uv init), adding deps (uv add), syncing envs (uv sync), running commands (uv run), locking (uv lock), managing Python versions (uv python), running tools (uvx), or writing scripts with inline deps. Also use for Docker builds that involve uv.
---

# uv Package & Environment Management

Reference: https://docs.astral.sh/uv/

## Core Workflow

| Task | Command |
|------|---------|
| Create project | `uv init` |
| Add dep | `uv add <pkg>` or `uv add "<pkg>>=1.0"` |
| Add dev dep | `uv add --dev <pkg>` |
| Remove dep | `uv remove <pkg>` |
| Lock | `uv lock` |
| Sync env | `uv sync` |
| Run in env | `uv run <cmd>` |

After clone: `uv sync` creates `.venv` and installs from `uv.lock`.

## Python Versions

```bash
uv python install 3.11 3.12      # install versions
uv python pin 3.12               # pin for project (.python-version)
uv venv --python 3.11            # create venv with specific version
```

## Tools (uvx)

Run CLI tools without global install:

```bash
uvx ruff check .                 # ephemeral run
uv tool install ruff             # persistent install
```

## Scripts with Inline Deps (PEP 723)

Add metadata to a single-file script:

```bash
uv add --script example.py requests rich
uv run example.py                # runs in isolated env with declared deps
```

## Advanced Topics

- **Dependency groups, workspaces, alternative sources:** See [references/advanced.md](references/advanced.md)
- **Docker integration:** See [references/docker.md](references/docker.md)

## Guidance

- Prefer `uv run` over bare `python`/`pytest` to ensure the correct `.venv`.
- Commit `uv.lock` for reproducible installs.
- Use project workflow (`pyproject.toml`) unless repo explicitly uses `requirements.txt`.
