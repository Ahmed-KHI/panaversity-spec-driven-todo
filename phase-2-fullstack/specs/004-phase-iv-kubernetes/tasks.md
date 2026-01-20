# Implementation Tasks: Phase IV - Local Kubernetes Deployment

**Project:** Hackathon II - The Evolution of Todo  
**Phase:** IV - Local Kubernetes Deployment  
**Input:** [spec.md](spec.md), [plan.md](plan.md)  
**Status:** Ready for Implementation  
**Created:** January 18, 2026

---

## Format: `[ID] [P?] [Story] Description`

- **ID**: Sequential task number (T001-T999)
- **[P]**: Parallelizable task (can run simultaneously with others in same phase)
- **[Story]**: User Story reference (US1-US7)
- **Description**: Clear, actionable task with file paths

---

## Path Conventions

**Phase IV Artifacts:**
- Dockerfiles: `phase-4-kubernetes/docker/frontend/Dockerfile`, `phase-4-kubernetes/docker/backend/Dockerfile`
- Helm charts: `phase-4-kubernetes/helm-charts/todo/`
- Scripts: `phase-4-kubernetes/scripts/`
- Documentation: `phase-4-kubernetes/README.md`, `phase-4-kubernetes/DEPLOYMENT.md`

**Phase III Source (Read-Only):**
- Frontend: `phase-2-fullstack/frontend/`
- Backend: `phase-2-fullstack/backend/`
- Docker Compose: `phase-2-fullstack/docker-compose.yml`

---

## Phase 1: Prerequisites and Setup (8 tasks)

**Goal:** Install all required tools and verify Minikube cluster

**Dependencies:** None (starting point)

**Acceptance:** All tools installed, Minikube cluster running with ingress and metrics-server

---

- [ ] T001 [P] [Setup] Verify Docker Desktop 4.53+ installed and running (docker --version)
- [ ] T002 [P] [Setup] Enable Gordon (Docker AI) in Docker Desktop Beta features (optional but recommended)
- [ ] T003 [P] [Setup] Verify Minikube 1.33+ installed (minikube version)
- [ ] T004 [P] [Setup] Verify kubectl 1.31+ installed and configured (kubectl version --client)
- [ ] T005 [P] [Setup] Verify Helm 3.16+ installed (helm version)
- [ ] T006 [P] [Setup] Install kubectl-ai via brew/go/manual (optional) and configure with OpenAI API key
- [ ] T007 [P] [Setup] Install Kagent via manual install (optional) and verify installation
- [ ] T008 [Setup] Create setup script phase-4-kubernetes/scripts/setup-minikube.sh and setup-minikube.ps1 (start Minikube with --cpus=4 --memory=8192, enable ingress and metrics-server addons, add /etc/hosts entry for todo.local)

**Acceptance**: Run setup-minikube.sh successfully, kubectl get nodes shows Ready, minikube addons list shows ingress and metrics-server enabled

---

## Phase 2: Docker Images - Frontend (9 tasks)

**Goal:** Create production-ready frontend Docker image with multi-stage build

**Dependencies:** T001 (Docker installed)

**Acceptance:** Frontend image < 200MB, runs successfully with docker run, health check passes

---

- [ ] T009 [US1] Create phase-4-kubernetes/docker/frontend/.dockerignore (exclude node_modules, .next, .git, *.log, .env*)
- [ ] T010 [US1] Create phase-4-kubernetes/docker/frontend/Dockerfile with multi-stage build:
  - Stage 1 (deps): FROM node:22-alpine, WORKDIR /app, COPY package.json package-lock.json, RUN npm ci --only=production
  - Stage 2 (builder): COPY from deps, COPY frontend source, RUN npm run build (standalone output)
  - Stage 3 (runner): FROM node:22-alpine, create non-root user (nextjs:nodejs UID 1001), COPY standalone build, EXPOSE 3000, USER nextjs, CMD node server.js
- [ ] T011 [US1] Add health check endpoint verification: Ensure phase-2-fullstack/frontend/app/api/health/route.ts exists and returns 200 OK
- [ ] T012 [US1] Build frontend image: docker build -t ahmed-khi/todo-frontend:v4.0.0 -f phase-4-kubernetes/docker/frontend/Dockerfile phase-2-fullstack/frontend
- [ ] T013 [US1] Verify image size: docker images ahmed-khi/todo-frontend:v4.0.0 (should be < 200MB)
- [ ] T014 [US1] Test frontend image locally: docker run -p 3000:3000 ahmed-khi/todo-frontend:v4.0.0
- [ ] T015 [US1] Verify health check: curl http://localhost:3000/api/health (should return 200 OK with {"status":"ok"})
- [ ] T016 [P] [US3] Use Gordon AI to analyze Dockerfile: docker ai "Optimize this Dockerfile for size and security" -f phase-4-kubernetes/docker/frontend/Dockerfile
- [ ] T017 [US1] Document Gordon AI suggestions in phase-4-kubernetes/docker/README.md (if available)

**Acceptance**: Frontend image builds successfully, size < 200MB, runs without errors, health check passes, Gordon AI provides optimization feedback

---

## Phase 3: Docker Images - Backend (9 tasks)

**Goal:** Create production-ready backend Docker image with multi-stage build

**Dependencies:** T001 (Docker installed)

**Acceptance:** Backend image < 150MB, runs successfully with docker run, health check passes

---

- [ ] T018 [US1] Create phase-4-kubernetes/docker/backend/.dockerignore (exclude __pycache__, *.pyc, .pytest_cache, .git, *.log, .env*)
- [ ] T019 [US1] Create phase-4-kubernetes/docker/backend/Dockerfile with multi-stage build:
  - Stage 1 (builder): FROM python:3.12-alpine, install build dependencies (gcc, musl-dev, postgresql-dev), install UV, COPY pyproject.toml, RUN uv sync
  - Stage 2 (runner): FROM python:3.12-alpine, install runtime dependencies (libpq), create non-root user (fastapi:fastapi UID 1001), COPY virtual environment and source code, EXPOSE 8000, USER fastapi, CMD uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
- [ ] T020 [US1] Add health check endpoint verification: Ensure phase-2-fullstack/backend/src/main.py has GET /health endpoint returning 200 OK with database connectivity check
- [ ] T021 [US1] Build backend image: docker build -t ahmed-khi/todo-backend:v4.0.0 -f phase-4-kubernetes/docker/backend/Dockerfile phase-2-fullstack/backend
- [ ] T022 [US1] Verify image size: docker images ahmed-khi/todo-backend:v4.0.0 (should be < 150MB)
- [ ] T023 [US1] Test backend image locally: docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./test.db ahmed-khi/todo-backend:v4.0.0
- [ ] T024 [US1] Verify health check: curl http://localhost:8000/health (should return 200 OK with {"status":"ok","database":"connected"})
- [ ] T025 [P] [US3] Use Gordon AI to analyze Dockerfile: docker ai "How can I reduce the size of this FastAPI Dockerfile?" -f phase-4-kubernetes/docker/backend/Dockerfile
- [ ] T026 [US1] Document Gordon AI suggestions in phase-4-kubernetes/docker/README.md (if available)

**Acceptance**: Backend image builds successfully, size < 150MB, runs without errors, health check passes, Gordon AI provides optimization feedback

---

## Phase 4: Image Registry (3 tasks)

**Goal:** Push images to Docker Hub or load into Minikube

**Dependencies:** T012, T021 (images built)

**Acceptance:** Images available for Kubernetes to pull

---

- [ ] T027 [US1] Create phase-4-kubernetes/scripts/build-images.sh and build-images.ps1 (build frontend and backend images with version tags)
- [ ] T028 [US1] Push images to Docker Hub: docker push ahmed-khi/todo-frontend:v4.0.0 && docker push ahmed-khi/todo-backend:v4.0.0 (OR minikube image load for local testing)
- [ ] T029 [US1] Verify images in registry: docker pull ahmed-khi/todo-frontend:v4.0.0 (should succeed)

**Acceptance**: Images pushed to Docker Hub or loaded into Minikube, docker pull succeeds

---

## Phase 5: Helm Chart Structure (10 tasks)

**Goal:** Create Helm chart skeleton with metadata and default values

**Dependencies:** T005 (Helm installed)

**Acceptance:** Helm lint passes, chart structure follows best practices

---

- [ ] T030 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/ directory
- [ ] T031 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/Chart.yaml with metadata (apiVersion: v2, name: todo, version: 1.0.0, appVersion: 4.0.0, description, keywords, maintainers)
- [ ] T032 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/values.yaml with default configuration (frontend, backend, postgres sections with image, replicas, resources, autoscaling, healthCheck, service, ingress, config, secrets)
- [ ] T033 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/values-dev.yaml with Minikube-specific overrides (low resources, local image pull policy)
- [ ] T034 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/values-prod.yaml template for production overrides (high resources, TLS enabled)
- [ ] T035 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/templates/ directory
- [ ] T036 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/templates/_helpers.tpl with common template functions (todo.name, todo.fullname, todo.labels, todo.selectorLabels)
- [ ] T037 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/templates/NOTES.txt with post-install instructions (how to access application, verify deployment)
- [ ] T038 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/.helmignore (exclude .git, .DS_Store, *.swp, *.bak)
- [ ] T039 [US2] Run helm lint phase-4-kubernetes/helm-charts/todo (should pass without warnings)

**Acceptance**: Helm lint passes, Chart.yaml has all required fields, values.yaml includes all configurable parameters, _helpers.tpl has reusable functions

---

## Phase 6: Kubernetes Manifests - Frontend (7 tasks)

**Goal:** Create frontend Deployment, Service, and HPA templates

**Dependencies:** T030-T039 (Helm chart structure)

**Acceptance:** Frontend templates render correctly with helm template

---

- [ ] T040 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/frontend-deployment.yaml with:
  - Deployment metadata with labels from _helpers.tpl
  - RollingUpdate strategy (maxUnavailable: 0, maxSurge: 1)
  - Replicas from values.frontend.replicaCount
  - Pod template with image from values.frontend.image, securityContext (runAsNonRoot: true, runAsUser: 1001)
  - Liveness probe: GET /api/health, initialDelaySeconds: 10, periodSeconds: 10
  - Readiness probe: GET /api/health, initialDelaySeconds: 5, periodSeconds: 5
  - Resource requests/limits from values.frontend.resources
  - Environment variables from ConfigMap and Secret
- [ ] T041 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/frontend-service.yaml with ClusterIP service exposing port 3000, selector matching frontend deployment labels
- [ ] T042 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/frontend-hpa.yaml with HorizontalPodAutoscaler targeting frontend-deployment, minReplicas: 2, maxReplicas: 5, targetCPUUtilizationPercentage: 70 (from values.frontend.autoscaling)
- [ ] T043 [P] [US6] Use kubectl-ai to validate frontend deployment: kubectl-ai "check if the todo frontend deployment is configured correctly"
- [ ] T044 [US2] Test frontend template rendering: helm template todo phase-4-kubernetes/helm-charts/todo --show-only templates/frontend-deployment.yaml
- [ ] T045 [US2] Verify template includes all required fields: image, replicas, probes, resources, securityContext
- [ ] T046 [US2] Dry-run apply: helm template todo phase-4-kubernetes/helm-charts/todo | kubectl apply --dry-run=client -f -

**Acceptance**: Frontend templates render without errors, include all required fields, dry-run succeeds

---

## Phase 7: Kubernetes Manifests - Backend (7 tasks)

**Goal:** Create backend Deployment, Service, and HPA templates

**Dependencies:** T030-T039 (Helm chart structure)

**Acceptance:** Backend templates render correctly with helm template

---

- [ ] T047 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/backend-deployment.yaml with:
  - Deployment metadata with labels from _helpers.tpl
  - RollingUpdate strategy (maxUnavailable: 0, maxSurge: 1)
  - Replicas from values.backend.replicaCount
  - Pod template with image from values.backend.image, securityContext (runAsNonRoot: true, runAsUser: 1001)
  - Liveness probe: GET /health, initialDelaySeconds: 15, periodSeconds: 10
  - Readiness probe: GET /health, initialDelaySeconds: 10, periodSeconds: 5
  - Resource requests/limits from values.backend.resources
  - Environment variables from ConfigMap and Secret (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY)
  - Optional init container for database migrations
- [ ] T048 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/backend-service.yaml with ClusterIP service exposing port 8000, selector matching backend deployment labels
- [ ] T049 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/backend-hpa.yaml with HorizontalPodAutoscaler targeting backend-deployment, minReplicas: 2, maxReplicas: 5, targetCPUUtilizationPercentage: 70 (from values.backend.autoscaling)
- [ ] T050 [P] [US6] Use kubectl-ai to validate backend deployment: kubectl-ai "check if the todo backend deployment has correct resource limits"
- [ ] T051 [US2] Test backend template rendering: helm template todo phase-4-kubernetes/helm-charts/todo --show-only templates/backend-deployment.yaml
- [ ] T052 [US2] Verify template includes all required fields: image, replicas, probes, resources, securityContext, environment variables
- [ ] T053 [US2] Dry-run apply: helm template todo phase-4-kubernetes/helm-charts/todo | kubectl apply --dry-run=client -f -

**Acceptance**: Backend templates render without errors, include all required fields, dry-run succeeds

---

## Phase 8: Kubernetes Manifests - PostgreSQL (6 tasks)

**Goal:** Create PostgreSQL StatefulSet, Service, and PVC templates

**Dependencies:** T030-T039 (Helm chart structure)

**Acceptance:** PostgreSQL templates render correctly with persistent storage

---

- [ ] T054 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/postgres-statefulset.yaml with:
  - StatefulSet metadata with labels
  - Replicas: 1 (single instance for Minikube)
  - Pod template with image postgres:16-alpine, securityContext (runAsUser: 999 - postgres user)
  - Readiness probe: TCP port 5432, initialDelaySeconds: 5, periodSeconds: 10
  - Resource requests/limits from values.postgres.resources
  - Environment variables from Secret (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)
  - Volume mount for persistent data at /var/lib/postgresql/data
  - PersistentVolumeClaim template (storageClass: standard, accessMode: ReadWriteOnce, size: 10Gi)
- [ ] T055 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/postgres-service.yaml with ClusterIP service (headless for StatefulSet) exposing port 5432
- [ ] T056 [US2] Create phase-4-kubernetes/helm-charts/todo/templates/postgres-pvc.yaml (if using separate PVC instead of StatefulSet template) with storageClass: standard, size: 10Gi
- [ ] T057 [US2] Test postgres template rendering: helm template todo phase-4-kubernetes/helm-charts/todo --show-only templates/postgres-statefulset.yaml
- [ ] T058 [US2] Verify template includes PVC template or separate PVC resource
- [ ] T059 [US2] Dry-run apply: helm template todo phase-4-kubernetes/helm-charts/todo | kubectl apply --dry-run=client -f -

**Acceptance**: PostgreSQL templates render without errors, PVC defined for persistent storage, dry-run succeeds

---

## Phase 9: Kubernetes Manifests - Configuration (4 tasks)

**Goal:** Create ConfigMap, Secret, and Ingress templates

**Dependencies:** T030-T039 (Helm chart structure)

**Acceptance:** Configuration resources render correctly

---

- [ ] T060 [P] [US2] Create phase-4-kubernetes/helm-charts/todo/templates/configmap.yaml with:
  - ConfigMap metadata
  - Data fields: LOG_LEVEL, BACKEND_URL, FRONTEND_URL, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME (from values.config)
- [ ] T061 [P] [US6] Create phase-4-kubernetes/helm-charts/todo/templates/secrets.yaml.example (template only, not real secrets) with:
  - Secret metadata
  - Type: Opaque
  - Data fields (base64 encoded): POSTGRES_PASSWORD, JWT_SECRET_KEY, OPENAI_API_KEY (from values.secrets)
  - Add comment: "DO NOT commit real secrets to Git. Use kubectl create secret generic todo-secrets --from-literal=... instead"
- [ ] T062 [US3] Create phase-4-kubernetes/helm-charts/todo/templates/ingress.yaml with:
  - Ingress metadata with annotations (nginx.ingress.kubernetes.io/rewrite-target: /$2)
  - IngressClassName: nginx
  - Host: todo.local (from values.ingress.host)
  - Rules: Path / → frontend-service:3000, Path /api → backend-service:8000
  - TLS configuration (if values.ingress.tls.enabled)
- [ ] T063 [US2] Test configuration templates rendering: helm template todo phase-4-kubernetes/helm-charts/todo --show-only templates/configmap.yaml,templates/ingress.yaml

**Acceptance**: ConfigMap, Secret template, and Ingress render without errors, ingress routes correctly configured

---

## Phase 10: Deployment Scripts (8 tasks)

**Goal:** Automate cluster setup, image building, and application deployment

**Dependencies:** T008 (Minikube setup), T027 (build script)

**Acceptance:** Scripts run successfully on clean Minikube cluster

---

- [ ] T064 [P] [US3] Update phase-4-kubernetes/scripts/setup-minikube.sh with additional checks (verify Docker running, check Minikube status, enable dashboard addon)
- [ ] T065 [P] [US3] Create phase-4-kubernetes/scripts/setup-minikube.ps1 (PowerShell version for Windows) with same functionality as bash script
- [ ] T066 [P] [US3] Create phase-4-kubernetes/scripts/deploy.sh with:
  - Check if Minikube is running
  - Create Kubernetes secrets: kubectl create secret generic todo-secrets --from-literal=POSTGRES_PASSWORD=... --from-literal=JWT_SECRET_KEY=... --from-literal=OPENAI_API_KEY=... (or skip if exists)
  - Install Helm chart: helm install todo ./phase-4-kubernetes/helm-charts/todo -f ./phase-4-kubernetes/helm-charts/todo/values-dev.yaml
  - Wait for pods to be ready: kubectl wait --for=condition=ready pod -l app=todo --timeout=300s
  - Get Minikube IP and display access URL: echo "Application available at http://todo.local"
- [ ] T067 [P] [US3] Create phase-4-kubernetes/scripts/deploy.ps1 (PowerShell version)
- [ ] T068 [P] [US3] Create phase-4-kubernetes/scripts/port-forward.sh for local access if ingress fails (kubectl port-forward service/frontend-service 3000:3000)
- [ ] T069 [P] [US3] Create phase-4-kubernetes/scripts/port-forward.ps1 (PowerShell version)
- [ ] T070 [P] [US3] Create phase-4-kubernetes/scripts/cleanup.sh to delete all resources (helm uninstall todo, kubectl delete secret todo-secrets, minikube stop)
- [ ] T071 [P] [US3] Create phase-4-kubernetes/scripts/cleanup.ps1 (PowerShell version)

**Acceptance**: All scripts run without errors, deploy.sh successfully deploys application to Minikube

---

## Phase 11: Testing Scripts (6 tasks)

**Goal:** Create smoke tests and load tests for validation

**Dependencies:** T066 (application deployed)

**Acceptance:** Smoke tests pass, load tests trigger HPA scale-up

---

- [ ] T072 [P] [US4] Create phase-4-kubernetes/tests/smoke-test.sh with:
  - Check frontend health: curl -f http://todo.local/api/health || exit 1
  - Check backend health: curl -f http://todo.local/api/health || exit 1
  - Verify database connectivity via backend health endpoint
  - Test user registration: curl -X POST http://todo.local/api/auth/register -d '{"email":"test@example.com","password":"testpass123"}'
  - Test user login: curl -X POST http://todo.local/api/auth/login -d '{"email":"test@example.com","password":"testpass123"}'
  - Test task creation: curl -X POST http://todo.local/api/tasks -H "Authorization: Bearer $TOKEN" -d '{"title":"Test Task"}'
  - All tests pass: echo "Smoke tests passed!"
- [ ] T073 [P] [US4] Create phase-4-kubernetes/tests/smoke-test.ps1 (PowerShell version)
- [ ] T074 [P] [US5] Create phase-4-kubernetes/tests/load-test.sh with ApacheBench:
  - Install ab (Apache Bench) if not present
  - Run load test: ab -n 1000 -c 100 http://todo.local/
  - Monitor HPA: kubectl get hpa -w (expect frontend and backend to scale from 2 → 3+ pods)
  - Wait for scale-down after 5 minutes
- [ ] T075 [P] [US5] Create phase-4-kubernetes/tests/load-test.ps1 (PowerShell version)
- [ ] T076 [US4] Run smoke tests: ./phase-4-kubernetes/tests/smoke-test.sh (should pass)
- [ ] T077 [US5] Run load tests: ./phase-4-kubernetes/tests/load-test.sh (should trigger HPA scale-up)

**Acceptance**: Smoke tests pass (all health checks return 200 OK, CRUD operations work), load tests trigger HPA scale-up

---

## Phase 12: AI DevOps Validation (9 tasks)

**Goal:** Validate Gordon, kubectl-ai, and Kagent integrations

**Dependencies:** T002, T006, T007 (AI tools installed)

**Acceptance:** All AI tools provide useful outputs, documented in README

---

- [ ] T078 [P] [US7] Test Gordon AI capabilities: docker ai "What can you do?" (document output)
- [ ] T079 [P] [US7] Test Gordon AI Dockerfile analysis: docker ai "Analyze the security of this Dockerfile" -f phase-4-kubernetes/docker/frontend/Dockerfile
- [ ] T080 [P] [US7] Test Gordon AI optimization: docker ai "How can I reduce the build time of this Dockerfile?" -f phase-4-kubernetes/docker/backend/Dockerfile
- [ ] T081 [P] [US7] Test kubectl-ai deployment: kubectl-ai "deploy the todo frontend with 2 replicas using image ahmed-khi/todo-frontend:v4.0.0"
- [ ] T082 [P] [US7] Test kubectl-ai scaling: kubectl-ai "scale the backend deployment to 3 replicas"
- [ ] T083 [P] [US7] Test kubectl-ai troubleshooting: kubectl-ai "why are my postgres pods in CrashLoopBackOff?" (simulate failure scenario)
- [ ] T084 [P] [US7] Test Kagent cluster analysis: kagent "analyze the overall health of my Kubernetes cluster"
- [ ] T085 [P] [US7] Test Kagent optimization: kagent "optimize the resource allocation for the todo application"
- [ ] T086 [US7] Document all AI tool outputs in phase-4-kubernetes/docker/README.md and phase-4-kubernetes/README.md with screenshots or command outputs

**Acceptance**: Gordon provides Dockerfile optimization suggestions, kubectl-ai successfully executes at least 3 commands, Kagent analyzes cluster health

---

## Phase 13: Documentation (10 tasks)

**Goal:** Create comprehensive deployment guides and demo materials

**Dependencies:** All previous phases complete

**Acceptance:** README enables 10-minute setup, troubleshooting guide covers common issues

---

- [ ] T087 [P] [US7] Create phase-4-kubernetes/README.md with:
  - Overview of Phase IV objectives
  - Prerequisites (Docker Desktop 4.53+, Minikube 1.33+, kubectl, Helm, kubectl-ai, Kagent)
  - Quickstart guide (10-minute setup): run setup-minikube.sh → build-images.sh → deploy.sh → verify
  - Architecture diagram (ASCII or link to diagram)
  - Gordon, kubectl-ai, Kagent usage examples with expected outputs
  - Troubleshooting section (common issues: ingress not working, pods failing, resource limits)
  - Rollback procedure: helm rollback todo
  - Links to DEPLOYMENT.md and TROUBLESHOOTING.md
- [ ] T088 [P] [US7] Create phase-4-kubernetes/DEPLOYMENT.md with detailed step-by-step guide:
  - Section 1: Environment setup (install Docker, Minikube, kubectl, Helm)
  - Section 2: Minikube cluster configuration (start, enable addons, verify)
  - Section 3: Docker image building (build frontend, build backend, push to registry)
  - Section 4: Helm chart deployment (create secrets, install chart, wait for pods)
  - Section 5: Ingress configuration (/etc/hosts entry, verify ingress routes)
  - Section 6: Validation (smoke tests, load tests, HPA verification)
  - Section 7: AI DevOps tools (Gordon, kubectl-ai, Kagent examples)
  - Section 8: Monitoring (kubectl logs, kubectl top, kubectl describe)
  - Section 9: Rolling updates (helm upgrade, zero-downtime verification)
  - Section 10: Cleanup (helm uninstall, delete secrets, minikube stop)
- [ ] T089 [P] [US7] Create phase-4-kubernetes/TROUBLESHOOTING.md with common issues and solutions:
  - Issue 1: Ingress not working → Check ingress controller pods, verify /etc/hosts entry, use port-forward as fallback
  - Issue 2: Pods in CrashLoopBackOff → Check logs (kubectl logs), verify resource limits, check image pull errors
  - Issue 3: Database connection failed → Verify postgres pod running, check DATABASE_URL, verify secret mounted
  - Issue 4: Health checks failing → Check probe configuration, verify endpoints return 200 OK, increase initial delay
  - Issue 5: HPA not scaling → Verify metrics-server addon enabled, check CPU usage (kubectl top pods), verify targetCPUUtilizationPercentage
  - Issue 6: Image pull errors → Verify image exists in registry, check imagePullPolicy, use minikube image load
  - Issue 7: Ingress 404 errors → Verify ingress rules, check path rewriting annotations, test services directly (port-forward)
  - Issue 8: Out of memory errors → Check resource limits, increase memory requests, verify no memory leaks
  - Issue 9: Helm install fails → Run helm lint, check template syntax, verify values.yaml structure
  - Issue 10: Minikube not starting → Check Docker daemon running, increase resources (--cpus=4 --memory=8192), delete and recreate cluster
- [ ] T090 [P] [US7] Create phase-4-kubernetes/docker/README.md documenting Docker image design:
  - Multi-stage build rationale (smaller images, faster builds, security)
  - Frontend Dockerfile explanation (deps → builder → runner stages)
  - Backend Dockerfile explanation (builder → runner stages)
  - .dockerignore patterns and rationale
  - Gordon AI optimization suggestions (if available)
  - Image size comparison (before/after multi-stage)
- [ ] T091 [P] [US7] Create phase-4-kubernetes/helm-charts/todo/README.md documenting Helm chart:
  - Chart structure (Chart.yaml, values.yaml, templates/)
  - Values configuration (frontend, backend, postgres, ingress, config, secrets)
  - Template helpers (_helpers.tpl functions)
  - Values overrides (values-dev.yaml, values-prod.yaml)
  - Helm commands (install, upgrade, rollback, uninstall)
- [ ] T092 [P] [US7] Create phase-4-kubernetes/scripts/README.md documenting automation scripts:
  - setup-minikube.sh: Initialize Minikube cluster with addons
  - build-images.sh: Build and push Docker images
  - deploy.sh: Deploy application with Helm
  - port-forward.sh: Port forwarding for local access
  - cleanup.sh: Delete all resources and stop Minikube
  - PowerShell equivalents for Windows users
- [ ] T093 [P] [US7] Create phase-4-kubernetes/tests/README.md documenting testing strategy:
  - Smoke tests: Health checks, CRUD operations, authentication
  - Load tests: ApacheBench with 100 concurrent requests, HPA verification
  - Expected results: All smoke tests pass, load tests trigger scale-up
- [ ] T094 [US7] Create demo video outline (90-second script):
  - 0:00-0:10: Introduction (Phase IV objective: Deploy on Kubernetes locally)
  - 0:10-0:20: Show Minikube cluster running (kubectl get nodes)
  - 0:20-0:30: Show Docker images (docker images ahmed-khi/todo-*)
  - 0:30-0:40: Deploy with Helm (helm install todo ...)
  - 0:40-0:50: Show pods running (kubectl get pods)
  - 0:50-0:60: Access application (http://todo.local in browser)
  - 0:60-0:70: Demonstrate AI DevOps tools (Gordon, kubectl-ai, Kagent)
  - 0:70-0:80: Show HPA scaling (kubectl get hpa)
  - 0:80-0:90: Conclusion (Phase IV complete, ready for Phase V)
- [ ] T095 [US7] Update constitution.md with Phase IV addendum (if needed): Add Kubernetes deployment standards, Helm chart requirements
- [ ] T096 [US7] Create ADR (Architecture Decision Record) for Phase IV Kubernetes deployment decision:
  - Title: ADR-0004-kubernetes-local-deployment-minikube
  - Status: Accepted
  - Context: Need local Kubernetes environment for Phase IV
  - Decision: Use Minikube with Helm charts, Gordon, kubectl-ai, Kagent
  - Consequences: Enables cloud-native deployment patterns, prepares for Phase V
  - File: phase-2-fullstack/history/adr/0004-kubernetes-local-deployment-minikube.md

**Acceptance**: README enables 10-minute setup, DEPLOYMENT.md has detailed steps, TROUBLESHOOTING.md covers 10+ issues, demo video outline complete, ADR created

---

## Phase 14: Validation and Polish (8 tasks)

**Goal:** Final validation, security checks, and documentation review

**Dependencies:** All previous phases complete

**Acceptance:** All acceptance criteria met, ready for submission

---

- [ ] T097 [P] [US4] Run complete validation checklist:
  - ✅ Minikube cluster running and accessible
  - ✅ All pods in Running state (kubectl get pods)
  - ✅ Application accessible at http://todo.local
  - ✅ Health checks passing for all services
  - ✅ Database data persists after pod restarts (kubectl delete pod postgres-0, verify data)
  - ✅ Rolling updates work without downtime (helm upgrade, verify)
  - ✅ HPA scales pods under load (run load test, watch kubectl get hpa)
  - ✅ All Phase III features work identically (register, login, CRUD, chatbot)
- [ ] T098 [P] [US6] Run security validation:
  - ✅ No secrets committed to Git (grep -r "POSTGRES_PASSWORD" .git/ should be empty)
  - ✅ All containers run as non-root users (kubectl describe pod, check securityContext)
  - ✅ Docker images have no critical vulnerabilities (trivy image ahmed-khi/todo-frontend:v4.0.0)
  - ✅ Network policies restrict pod-to-pod communication (optional for Minikube)
- [ ] T099 [P] [US7] Verify AI DevOps tools:
  - ✅ Gordon provides Dockerfile optimization suggestions (documented in README)
  - ✅ kubectl-ai executes at least 3 commands successfully (documented with outputs)
  - ✅ Kagent analyzes cluster health successfully (documented with recommendations)
- [ ] T100 [US7] Create validation checklist for reviewers in phase-4-kubernetes/VALIDATION-CHECKLIST.md:
  - Prerequisites checklist (tools installed, versions correct)
  - Deployment checklist (scripts run successfully, pods running)
  - Functional checklist (all Phase III features work)
  - Quality checklist (Docker images optimized, Helm lint passes, security checks pass)
  - Documentation checklist (README complete, troubleshooting guide exists, demo video outline ready)
  - AI DevOps checklist (Gordon, kubectl-ai, Kagent documented)
- [ ] T101 [US7] Review all documentation for completeness and accuracy
- [ ] T102 [US7] Test complete deployment flow on clean Minikube cluster (delete cluster, recreate, run all scripts)
- [ ] T103 [US7] Create submission package:
  - Phase IV artifacts: phase-4-kubernetes/ directory
  - Specs: specs/004-phase-iv-kubernetes/ (spec.md, plan.md, tasks.md)
  - Demo video outline: phase-4-kubernetes/DEMO-VIDEO-OUTLINE.md
  - ADR: phase-2-fullstack/history/adr/0004-kubernetes-local-deployment-minikube.md
  - README with GitHub repository link
- [ ] T104 [US7] Final review against Hackathon II rubric (90+ out of 100 target):
  - Spec-Driven Development: ✅ Spec → Plan → Tasks → Implementation
  - Kubernetes Deployment: ✅ Minikube, Helm charts, all services running
  - AI DevOps Tools: ✅ Gordon, kubectl-ai, Kagent documented and tested
  - Documentation: ✅ README, DEPLOYMENT.md, TROUBLESHOOTING.md complete
  - Demo Video: ✅ 90-second outline ready
  - Production Quality: ✅ Docker images optimized, security validated, HPA working

**Acceptance**: All validation checks pass, submission package ready, scores 90+ out of 100 on rubric

---

## Dependencies & Execution Order

### Critical Path

**Sequential (Must complete in order):**
1. Phase 1 (Setup) → Phase 2 (Frontend Docker) → Phase 4 (Push Images) → Phase 5 (Helm Structure) → Phase 6-9 (Manifests) → Phase 10 (Scripts) → Phase 11 (Tests) → Phase 12 (AI DevOps) → Phase 13 (Documentation) → Phase 14 (Validation)

**Parallel Opportunities:**

- **Phase 1 (Setup)**: All 8 tasks parallelizable (T001-T007)
- **Phase 2 & 3 (Docker Images)**: Frontend and backend can be built in parallel
- **Phase 5 (Helm Structure)**: All 10 tasks parallelizable (T030-T039)
- **Phase 6-9 (Manifests)**: Frontend, backend, postgres, config can be created in parallel
- **Phase 10 (Scripts)**: All scripts parallelizable (bash and PowerShell versions)
- **Phase 11 (Tests)**: Smoke tests and load tests parallelizable
- **Phase 12 (AI DevOps)**: All AI tool tests parallelizable (T078-T085)
- **Phase 13 (Documentation)**: All documentation files parallelizable (T087-T096)
- **Phase 14 (Validation)**: Validation, security checks, AI DevOps verification parallelizable (T097-T099)

---

## Task Summary

**Total Tasks:** 104

**By Phase:**
- Phase 1 (Setup): 8 tasks
- Phase 2 (Frontend Docker): 9 tasks
- Phase 3 (Backend Docker): 9 tasks
- Phase 4 (Image Registry): 3 tasks
- Phase 5 (Helm Structure): 10 tasks
- Phase 6 (Frontend Manifests): 7 tasks
- Phase 7 (Backend Manifests): 7 tasks
- Phase 8 (PostgreSQL Manifests): 6 tasks
- Phase 9 (Configuration Manifests): 4 tasks
- Phase 10 (Deployment Scripts): 8 tasks
- Phase 11 (Testing Scripts): 6 tasks
- Phase 12 (AI DevOps Validation): 9 tasks
- Phase 13 (Documentation): 10 tasks
- Phase 14 (Validation and Polish): 8 tasks

**Parallelizable Tasks:** 52 tasks marked [P]

**User Stories Coverage:**
- US1 (Containerize): T009-T029 (21 tasks)
- US2 (Helm Charts): T030-T063 (34 tasks)
- US3 (Deploy on Minikube): T064-T071, T087 (9 tasks)
- US4 (Health Checks): T072-T077, T097 (7 tasks)
- US5 (Resource Management): T074-T077 (4 tasks)
- US6 (Secret Management): T061, T098 (2 tasks)
- US7 (AI DevOps Tools): T078-T096, T099, T101-T104 (27 tasks)

---

## Implementation Strategy

### MVP Scope (Recommended First Deliverable)

**MVP = Phase 1-11 (Setup + Docker + Helm + Deployment + Testing)**

This delivers a working Kubernetes deployment where:
- Application runs on Minikube
- All services accessible via ingress
- Health checks passing
- HPA scaling working
- Smoke tests passing

**Value**: Complete Kubernetes deployment enables validation of all Phase III features in cloud-native environment. Independently testable and deployable.

### Incremental Delivery

1. **Milestone 1** (MVP): Phases 1-11 → Application deployed on Minikube, tests passing
2. **Milestone 2**: Add Phase 12 → AI DevOps tools validated and documented
3. **Milestone 3**: Add Phase 13 → Documentation complete, demo video outline ready
4. **Milestone 4**: Add Phase 14 → Final validation, submission package ready

### Recommended Execution

**Week 1:**
- Days 1-2: Phases 1-4 (Setup + Docker images + push)
- Days 3-4: Phases 5-9 (Helm chart structure + all manifests)
- Days 5-7: Phases 10-11 (Scripts + tests)

**Week 2:**
- Days 1-2: Phase 12 (AI DevOps validation)
- Days 3-5: Phase 13 (Documentation)
- Days 6-7: Phase 14 (Final validation + polish)

---

**END OF TASKS**
