---
name: docker-containerization
description: Use when containerizing Python applications with Docker, creating Dockerfiles or docker-compose configurations, or deploying containers to platforms like Kubernetes, ECS, or Cloud Run. Ideal for FastAPI, Django, Flask, and other Python services that need development, production, or CI/CD containerization.
---

# Docker Containerization Skill

## Overview

Generate production-ready Docker configurations for Python services (FastAPI, Django, Flask, Celery workers, etc.). This skill provides guidance for Dockerfiles, docker-compose setups, and container management workflows, plus deployment guides for common orchestration platforms.

## Core Capabilities

### 1. Dockerfile Generation

Create optimized Dockerfiles for different environments:

**Production** (Python service):
- Multi-stage build to keep images small
- Slim base image (e.g. `python:3.11-slim`)
- Non-root user execution
- Health checks and resource limits
- Start with `uvicorn`/`gunicorn` for ASGI/WSGI apps

**Development**:
- Hot reload (e.g. `uvicorn --reload` for FastAPI)
- All dev dependencies included
- Volume mounts for live code updates

**Optional Nginx reverse proxy**:
- Use only if serving static assets or proxying to the app
- Otherwise skip and expose the app server directly

### 2. Docker Compose Configuration

Multi-container orchestration with `assets/docker-compose.yml`:
- Python app service + dependencies (Postgres, Redis, etc.)
- Dev/Prod profiles
- Network and volume management
- Health checks and logging
- Restart policies

### 3. Bash Scripts for Container Management

**docker-build.sh** - Build images with comprehensive options:
```bash
./docker-build.sh -e prod -t v1.0.0
./docker-build.sh -n my-app --no-cache --platform linux/amd64
```

**docker-run.sh** - Run containers with full configuration:
```bash
./docker-run.sh -i my-app -t v1.0.0 -d
./docker-run.sh -p 8080:3000 --env-file .env.production
```

**docker-push.sh** - Push to registries (Docker Hub, ECR, GCR, ACR):
```bash
./docker-push.sh -n my-app -t v1.0.0 --repo username/my-app
./docker-push.sh -r gcr.io/project --repo my-app --also-tag stable
```

**docker-cleanup.sh** - Free disk space:
```bash
./docker-cleanup.sh --all --dry-run  # Preview cleanup
./docker-cleanup.sh --containers --images  # Clean specific resources
```

### 4. Configuration Files

- **`.dockerignore`**: Exclude Python artifacts (`.venv`, `__pycache__`, `.pytest_cache`, etc.) plus `.git` and logs
- **`nginx.conf`**: Optional reverse proxy with compression, caching, security headers

### 5. Reference Documentation

**docker-best-practices.md** covers:
- Multi-stage builds explained
- Image optimization techniques (50-85% size reduction)
- Security best practices (non-root users, vulnerability scanning)
- Performance optimization
- Health checks and logging
- Troubleshooting guide

**container-orchestration.md** covers deployment to:
- Docker Compose (local development)
- Kubernetes (enterprise scale with auto-scaling)
- Amazon ECS (AWS-native orchestration)
- Google Cloud Run (serverless containers)
- Azure Container Instances
- Digital Ocean App Platform

Includes configuration examples, commands, auto-scaling setup, and monitoring.

## Workflow Decision Tree

### 1. What environment?
- **Development** → Python dev Dockerfile (hot reload, dev deps)
- **Production** → Python prod Dockerfile (minimal, secure, optimized)
- **Static assets / proxy** → Optional Nginx reverse proxy (only if needed)

### 2. Single or Multi-container?
- **Single** → Generate Dockerfile only
- **Multi** → Generate `docker-compose.yml` (app + database, microservices)

### 3. Which registry?
- **Docker Hub** → `docker.io/username/image`
- **AWS ECR** → `123456789012.dkr.ecr.region.amazonaws.com/image`
- **Google GCR** → `gcr.io/project-id/image`
- **Azure ACR** → `registry.azurecr.io/image`

### 4. Deployment platform?
- **Kubernetes** → See `references/container-orchestration.md` K8s section
- **ECS** → See ECS task definition examples
- **Cloud Run** → See deployment commands
- **Docker Compose** → Use provided compose file

### 5. Optimizations needed?
- **Image size** → Multi-stage builds, Alpine base
- **Build speed** → Layer caching, BuildKit
- **Security** → Non-root user, vulnerability scanning
- **Performance** → Resource limits, health checks

## Usage Examples

### Example 1: Containerize a FastAPI App for Production

**User**: "Containerize my FastAPI app for production"

**Steps**:
1. Create a production Dockerfile for Python (multi-stage, non-root)
2. Add a Python-appropriate `.dockerignore`
3. Build: `./docker-build.sh -e prod -n my-api -t v1.0.0`
4. Run: `./docker-run.sh -i my-api -t v1.0.0 -p 8000:8000 -d`
5. Push: `./docker-push.sh -n my-api -t v1.0.0 --repo username/my-api`

### Example 2: Development with Docker Compose (FastAPI + Postgres)

**User**: "Set up Docker Compose for local development with Postgres"

**Steps**:
1. Create a Python dev Dockerfile (hot reload)
2. Create `docker-compose.yml` with `app` + `db` services
3. Start: `docker-compose up -d`
4. Logs: `docker-compose logs -f app`

### Example 3: Deploy a Python API to Kubernetes

**User**: "Deploy my containerized FastAPI app to Kubernetes"

**Steps**:
1. Build and push image to registry
2. Review `references/container-orchestration.md` Kubernetes section
3. Create K8s manifests (deployment, service, ingress)
4. Apply: `kubectl apply -f deployment.yaml`
5. Verify: `kubectl get pods && kubectl logs -f deployment/app`

### Example 4: Deploy a Django App to AWS ECS

**User**: "Deploy my Django app to AWS ECS Fargate"

**Steps**:
1. Build and push to ECR
2. Review `references/container-orchestration.md` ECS section
3. Create task definition JSON (gunicorn entrypoint)
4. Register: `aws ecs register-task-definition --cli-input-json file://task-def.json`
5. Create service: `aws ecs create-service --cluster my-cluster --service-name app --desired-count 3`

## Best Practices

### Security
✅ Use multi-stage builds for production
✅ Run as non-root user
✅ Use specific image tags (not `latest`)
✅ Scan for vulnerabilities
✅ Never hardcode secrets
✅ Implement health checks

### Performance
✅ Optimize layer caching order
✅ Use Alpine images (~85% smaller)
✅ Enable BuildKit for parallel builds
✅ Set resource limits
✅ Use compression

### Maintainability
✅ Add comments for complex steps
✅ Use build arguments for flexibility
✅ Keep Dockerfiles DRY
✅ Version control all configs
✅ Document environment variables

## Troubleshooting

**Image too large (>500MB)**
→ Use multi-stage builds, Alpine base, comprehensive .dockerignore

**Build is slow**
→ Optimize layer caching, use BuildKit, review dependencies

**Container exits immediately**
→ Check logs: `docker logs container-name`
→ Verify CMD/ENTRYPOINT, check port conflicts

**Changes not reflecting**
→ Rebuild without cache, check .dockerignore, verify volume mounts

## Quick Reference

```bash
# Build
./docker-build.sh -e prod -t latest

# Run
./docker-run.sh -i app -t latest -d

# Logs
docker logs -f app

# Execute
docker exec -it app sh

# Cleanup
./docker-cleanup.sh --all --dry-run  # Preview
./docker-cleanup.sh --all            # Execute
```

## Integration with CI/CD

### GitHub Actions
```yaml
- run: |
    chmod +x docker-build.sh docker-push.sh
    ./docker-build.sh -e prod -t ${{ github.sha }}
    ./docker-push.sh -n app -t ${{ github.sha }} --repo username/app
```

### GitLab CI
```yaml
build:
  script:
    - chmod +x docker-build.sh
    - ./docker-build.sh -e prod -t $CI_COMMIT_SHA
```

## Resources

### Scripts (`scripts/`)
Production-ready bash scripts with comprehensive features:
- `docker-build.sh` - Build images (400+ lines, colorized output)
- `docker-run.sh` - Run containers (400+ lines, auto conflict resolution)
- `docker-push.sh` - Push to registries (multi-registry support)
- `docker-cleanup.sh` - Clean resources (dry-run mode, selective cleanup)

### References (`references/`)
Detailed documentation loaded as needed:
- `docker-best-practices.md` - Comprehensive Docker best practices (~500 lines)
- `container-orchestration.md` - Deployment guides for 6+ platforms (~600 lines)

### Assets (`assets/`)
Ready-to-use templates:
- `Dockerfile.production` - Multi-stage production Dockerfile
- `Dockerfile.development` - Development Dockerfile
- `Dockerfile.nginx` - Static export with Nginx
- `docker-compose.yml` - Multi-container orchestration
- `.dockerignore` - Optimized exclusion rules
- `nginx.conf` - Production Nginx configuration
  
Note: Treat templates as starting points. If any are Node/Next.js-specific, adapt them for Python (FastAPI/Django/Flask) before use.
