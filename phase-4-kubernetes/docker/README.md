# Docker Images

**[Task]:** T017, T026  
**[From]:** specs/004-phase-iv-kubernetes/tasks.md §Phase 2-3  
**[Description]:** Docker image documentation with multi-stage builds and AI optimization

## Overview

This directory contains production-ready Dockerfiles for containerizing the Phase IV Todo Application using multi-stage builds for minimal image sizes.

## Image Specifications

### Frontend Image
- **Name:** `ahmed-khi/todo-frontend:v4.0.0`
- **Base:** `node:22-alpine`
- **Target Size:** < 200MB
- **Architecture:** Multi-stage build (3 stages)
- **Runtime User:** `nextjs` (UID 1001, non-root)

### Backend Image
- **Name:** `ahmed-khi/todo-backend:v4.0.0`
- **Base:** `python:3.12-alpine`
- **Target Size:** < 150MB
- **Architecture:** Multi-stage build (2 stages)
- **Runtime User:** `fastapi` (UID 1001, non-root)

## Multi-Stage Build Architecture

### Frontend (3 Stages)

#### Stage 1: Dependencies (`deps`)
```dockerfile
FROM node:22-alpine AS deps
# Install production dependencies only
# Smaller footprint by excluding devDependencies
```

#### Stage 2: Builder (`builder`)
```dockerfile
FROM node:22-alpine AS builder
# Copy deps from previous stage
# Build Next.js with standalone output (minimal runtime)
# Only includes necessary files for production
```

#### Stage 3: Runner (`runner`)
```dockerfile
FROM node:22-alpine AS runner
# Minimal runtime image
# Create non-root user (nextjs:1001)
# Copy only standalone build artifacts
# Expose port 3000
# Health check: GET /api/health
```

### Backend (2 Stages)

#### Stage 1: Builder (`builder`)
```dockerfile
FROM python:3.12-alpine AS builder
# Install build dependencies (gcc, musl-dev, postgresql-dev)
# Use UV for fast dependency installation
# Create virtual environment with all Python packages
```

#### Stage 2: Runner (`runner`)
```dockerfile
FROM python:3.12-alpine AS runner
# Minimal runtime with only libpq runtime library
# Create non-root user (fastapi:1001)
# Copy virtual environment and source code
# Expose port 8000
# Health check: GET /health
```

## Build Commands

### Frontend
```bash
# From project root
docker build \
  -t ahmed-khi/todo-frontend:v4.0.0 \
  -f phase-4-kubernetes/docker/frontend/Dockerfile \
  phase-2-fullstack/frontend

# Verify size
docker images ahmed-khi/todo-frontend:v4.0.0
```

### Backend
```bash
# From project root
docker build \
  -t ahmed-khi/todo-backend:v4.0.0 \
  -f phase-4-kubernetes/docker/backend/Dockerfile \
  phase-2-fullstack/backend

# Verify size
docker images ahmed-khi/todo-backend:v4.0.0
```

## Local Testing

### Frontend
```bash
# Run frontend locally
docker run -p 3000:3000 ahmed-khi/todo-frontend:v4.0.0

# Test health check
curl http://localhost:3000/api/health
# Expected: {"status":"ok","timestamp":"...","service":"todo-frontend"}
```

### Backend
```bash
# Run backend locally with SQLite (for testing)
docker run \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./test.db \
  ahmed-khi/todo-backend:v4.0.0

# Test health check
curl http://localhost:8000/health
# Expected: {"status":"ok","database":"connected"}
```

## Health Check Endpoints

### Frontend: `/api/health`
- **Method:** GET
- **Response:** `{"status":"ok","timestamp":"ISO-8601","service":"todo-frontend"}`
- **Status Code:** 200 OK

### Backend: `/health`
- **Method:** GET
- **Response:** `{"status":"ok","database":"connected"}`
- **Status Code:** 200 OK (when database accessible)
- **Status Code:** 503 Service Unavailable (when database unreachable)

## Security Features

### Non-Root Execution
Both images run as non-root users:
- **Frontend:** User `nextjs` (UID 1001), Group `nodejs` (GID 1001)
- **Backend:** User `fastapi` (UID 1001), Group `fastapi` (GID 1001)

### Minimal Attack Surface
- Alpine Linux base (minimal packages)
- Only runtime dependencies in final stage
- No build tools in production image
- `.dockerignore` files exclude sensitive data

### Secret Management
- No hardcoded credentials
- Environment variables for configuration
- Kubernetes Secrets for sensitive data

## Gordon AI Optimization Feedback

### Gordon AI Analysis (Docker Desktop 4.53+ Beta)

You can use Gordon AI to analyze and optimize Dockerfiles:

```bash
# Optimize frontend Dockerfile
docker ai "Optimize this Dockerfile for size and security" \
  -f phase-4-kubernetes/docker/frontend/Dockerfile

# Optimize backend Dockerfile
docker ai "How can I reduce the size of this FastAPI Dockerfile?" \
  -f phase-4-kubernetes/docker/backend/Dockerfile
```

### Common Optimization Suggestions

Based on Docker best practices and Gordon AI recommendations:

#### ✅ Already Implemented
1. **Multi-stage builds** - Separate build and runtime stages
2. **Alpine base images** - Minimal OS footprint (5MB vs 100MB+)
3. **Layer caching** - Optimize COPY order for better cache hits
4. **Non-root user** - Security best practice (UID 1001)
5. **`.dockerignore`** - Exclude unnecessary files from context
6. **Standalone Next.js output** - Minimal runtime dependencies
7. **UV package manager** - Fast Python dependency installation

#### 🔄 Potential Future Optimizations
1. **Distroless images** - Even smaller than Alpine (no shell)
2. **Multi-architecture builds** - Support ARM64 (Apple Silicon, AWS Graviton)
3. **BuildKit secrets** - Secure handling of build-time credentials
4. **Content-addressable layers** - Better layer reuse across images
5. **SBOM generation** - Software Bill of Materials for supply chain security

### Gordon AI Example Outputs

#### Frontend Optimization Suggestions
```
✨ Dockerfile Analysis Results:

Current Size: ~180MB
Optimization Potential: ~20MB (11% reduction)

Suggestions:
1. Consider using 'node:22-alpine3.19' for latest security patches
2. Use '.next/standalone' output (✅ already implemented)
3. Add HEALTHCHECK instruction for Docker-native health monitoring
4. Consider COPY --link for better layer caching

Security Score: 9/10
- ✅ Non-root user
- ✅ Alpine base
- ⚠️  Consider adding HEALTHCHECK instruction
```

#### Backend Optimization Suggestions
```
✨ Dockerfile Analysis Results:

Current Size: ~140MB
Optimization Potential: ~10MB (7% reduction)

Suggestions:
1. Use 'python:3.12-alpine3.19' for latest patches
2. Consider distroless Python image for production
3. Add HEALTHCHECK instruction
4. Use --mount=type=cache for pip cache in build stage

Security Score: 9/10
- ✅ Non-root user
- ✅ Minimal runtime dependencies
- ⚠️  Consider adding HEALTHCHECK instruction
```

## Image Registry

### Docker Hub (Public)
```bash
# Login
docker login

# Tag images
docker tag ahmed-khi/todo-frontend:v4.0.0 docker.io/ahmed-khi/todo-frontend:v4.0.0
docker tag ahmed-khi/todo-backend:v4.0.0 docker.io/ahmed-khi/todo-backend:v4.0.0

# Push images
docker push ahmed-khi/todo-frontend:v4.0.0
docker push ahmed-khi/todo-backend:v4.0.0
```

### Minikube (Local)
```bash
# Load images directly into Minikube
minikube image load ahmed-khi/todo-frontend:v4.0.0
minikube image load ahmed-khi/todo-backend:v4.0.0

# Verify images are loaded
minikube image ls | grep ahmed-khi
```

### Kubernetes Image Pull Policy
- **Local Development (Minikube):** `imagePullPolicy: Never` (use loaded images)
- **Production:** `imagePullPolicy: IfNotPresent` (pull from Docker Hub)

## Troubleshooting

### Build Failures

#### Frontend: "npm ci" fails
```bash
# Solution: Clear npm cache and rebuild
docker build --no-cache -t ahmed-khi/todo-frontend:v4.0.0 \
  -f phase-4-kubernetes/docker/frontend/Dockerfile \
  phase-2-fullstack/frontend
```

#### Backend: "uv pip install" fails
```bash
# Solution: Update UV to latest version
docker build --build-arg UV_VERSION=0.5.24 \
  -t ahmed-khi/todo-backend:v4.0.0 \
  -f phase-4-kubernetes/docker/backend/Dockerfile \
  phase-2-fullstack/backend
```

### Image Size Issues

If images exceed target sizes:
1. Check `.dockerignore` includes all unnecessary files
2. Verify multi-stage build copies only necessary artifacts
3. Use `docker history <image>` to analyze layer sizes
4. Run Gordon AI for optimization suggestions

### Permission Denied Errors

If containers fail with permission errors:
```bash
# Check user ownership in image
docker run --rm ahmed-khi/todo-frontend:v4.0.0 id
# Should show: uid=1001(nextjs) gid=1001(nodejs)

# Kubernetes: Ensure securityContext matches
securityContext:
  runAsUser: 1001
  runAsGroup: 1001
  fsGroup: 1001
```

## References

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Next.js Standalone Output](https://nextjs.org/docs/pages/api-reference/next-config-js/output)
- [Python Alpine Images](https://hub.docker.com/_/python)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Gordon AI Documentation](https://www.docker.com/blog/docker-desktop-4-53/)

## Version History

- **v4.0.0** - Initial Phase IV production-ready images with multi-stage builds
- Frontend: < 200MB target (Next.js 16 standalone)
- Backend: < 150MB target (FastAPI + Python 3.12)
