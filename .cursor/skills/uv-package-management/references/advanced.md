# uv Advanced Topics

Reference: https://docs.astral.sh/uv/concepts/projects/

## Dependency Groups (PEP 735)

Define groups for dev, test, lint, etc. in `pyproject.toml`:

```toml
[dependency-groups]
dev = ["pytest", "ruff"]
test = ["pytest", "coverage"]
```

Add to a group:

```bash
uv add --group test coverage
```

Sync with specific groups:

```bash
uv sync --group test
uv sync --all-groups
```

The `dev` group is special—synced by default unless `--no-dev`.

## Optional Dependencies (Extras)

```toml
[project.optional-dependencies]
server = ["uvicorn", "gunicorn"]
```

Sync extras:

```bash
uv sync --extra server
uv sync --all-extras
```

## Workspaces

For monorepos with multiple packages:

```
my-workspace/
├── pyproject.toml          # workspace root
├── uv.lock                  # shared lockfile
├── packages/
│   ├── lib-a/
│   │   └── pyproject.toml
│   └── lib-b/
│       └── pyproject.toml
```

Root `pyproject.toml`:

```toml
[tool.uv.workspace]
members = ["packages/*"]
```

All members share one lockfile and can depend on each other.

## Alternative Dependency Sources

In `pyproject.toml`:

```toml
[tool.uv.sources]
my-package = { git = "https://github.com/org/my-package", tag = "v1.0.0" }
local-lib = { path = "../local-lib", editable = true }
```

Supported source types: index, git, url, path, workspace member.

## Resolution Strategies

Control version selection:

```bash
uv lock --resolution lowest       # pick lowest compatible versions
uv lock --upgrade                 # upgrade all deps
uv lock --upgrade-package httpx   # upgrade specific package
```

## Exporting Lockfiles

Generate `requirements.txt` from lockfile:

```bash
uv export --format requirements-txt > requirements.txt
```

Useful for compatibility with tools that don't read `uv.lock`.
