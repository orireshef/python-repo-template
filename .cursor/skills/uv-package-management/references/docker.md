# uv Docker Integration

Reference: https://docs.astral.sh/uv/guides/integration/docker/

## Installing uv in Docker

**Option 1: Copy from official image**

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
```

**Option 2: Installer script**

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"
```

## Syncing Dependencies

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
```

Use `--frozen` to fail if lockfile is outdated.

## Optimizations

- **Bytecode compilation:** `UV_COMPILE_BYTECODE=1` or `--compile-bytecode`
- **Cache mounts:** Use Docker BuildKit cache for uv cache dir
- **Layer separation:** Copy `pyproject.toml` + `uv.lock` first, sync, then copy source—deps change less often

## .dockerignore

Add `.venv` so local venv (built for host OS) isn't copied into the image.

## Example Production Dockerfile (FastAPI)

```dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY . .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```
