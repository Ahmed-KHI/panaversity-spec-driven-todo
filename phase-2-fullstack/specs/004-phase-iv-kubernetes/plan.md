# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Project:** Hackathon II - The Evolution of Todo  
**Phase:** IV - Local Kubernetes Deployment  
**Status:** Planning  
**Created:** January 18, 2026  
**Version:** 1.0

---

## 1. Technical Context

### 1.1 Phase Transition

**From (Phase III):**
- Docker Compose orchestration
- Development environment with hot reload
- Services: frontend (Next.js), backend (FastAPI), postgres
- AI chatbot with MCP integration
- Phase III deployed on Vercel (frontend) + Hugging Face Spaces (backend)

**To (Phase IV):**
- Kubernetes orchestration (Minikube)
- Production-ready container images
- Helm charts for declarative deployments
- AI-powered DevOps (Gordon, kubectl-ai, Kagent)
- Infrastructure as Code (IaC) for reproducibility

**Backward Compatibility:**
- Phase III application code unchanged
- Database schema unchanged
- API contracts unchanged
- User experience identical
- Docker Compose still works for local development

---

### 1.2 Technology Stack

**Core Technologies:**
- **Containerization:** Docker 27+, Docker Desktop 4.53+ (Gordon AI)
- **Orchestration:** Kubernetes 1.31+ (Minikube 1.33+)
- **Package Manager:** Helm 3.x
- **AI DevOps:** Gordon (Docker AI), kubectl-ai, Kagent
- **Container Registry:** Docker Hub or local registry (Minikube)
- **Load Balancing:** Minikube Ingress (nginx)

**Application Stack (from Phase III):**
- **Frontend:** Next.js 16+, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.12, Uvicorn
- **Database:** PostgreSQL 16
- **AI:** OpenAI Agents SDK, MCP Server

**Infrastructure:**
- **Host OS:** Windows 11 (PowerShell), macOS, or Linux
- **Minikube Driver:** Docker (default) or Hyper-V (Windows)
- **Kubernetes Version:** 1.31+ (matches Minikube default)
- **Helm Version:** 3.16+

---

### 1.3 Constitution Check

**Reviewing constitution.md requirements for Phase IV:**

✅ **Section I: Core Principles**
- Principle 4: Testing - Health checks configured (liveness, readiness)
- Principle 5: Git Discipline - Kubernetes manifests version-controlled

✅ **Section II: Domain Model**
- Task and User models unchanged from Phase III
- Database schema migrations preserved

✅ **Section III: Technology Governance**
- Cloud & Kubernetes Standards (Phase IV+):
  - ✅ 12-Factor App principles enforced
  - ✅ Configuration via environment variables
  - ✅ Secrets in Kubernetes Secrets (never in code)
  - ✅ Docker images reproducible and minimal
  - ✅ Kubernetes manifests declarative (Helm)
  - ✅ Health checks required (liveness, readiness)
  - ✅ Resource limits defined
  - ✅ HPA configured
  - ❌ Hard-coded credentials forbidden
  - ❌ No imperative kubectl commands in production
  - ❌ No mutable infrastructure
  - ❌ No `latest` tag for images

✅ **Section IV: Repository Structure**
- Monorepo structure maintained
- Phase IV artifacts in `phase-4-kubernetes/` directory
- Specs in `specs/004-phase-iv-kubernetes/`

✅ **Section VII: Phase Evolution Rules**
- Previous phase (Phase III) complete and tested ✅
- ADR documenting phase transition required (create)
- Migration plan: No data migration needed (schema unchanged)
- Backward compatibility: Docker Compose still works ✅
- Regression testing: Phase III features must work identically

**Constitutional Violations:** None identified

---

## 2. Architecture

### 2.1 Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MINIKUBE CLUSTER                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    INGRESS CONTROLLER                       │ │
│  │                 (nginx.ingress.k8s.io)                     │ │
│  │                                                              │ │
│  │  http://todo.local/          → Frontend Service            │ │
│  │  http://todo.local/api/*     → Backend Service             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                     │            │
│         ▼                    ▼                     ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│  │  Frontend   │      │   Backend   │      │  PostgreSQL │   │
│  │   Service   │      │   Service   │      │   Service   │   │
│  │  ClusterIP  │      │  ClusterIP  │      │  ClusterIP  │   │
│  │  Port: 3000 │      │  Port: 8000 │      │  Port: 5432 │   │
│  └─────────────┘      └─────────────┘      └─────────────┘   │
│         │                    │                     │            │
│         ▼                    ▼                     ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│  │  Frontend   │      │   Backend   │      │  PostgreSQL │   │
│  │ Deployment  │      │ Deployment  │      │  StatefulSet│   │
│  │  (2-5 pods) │      │  (2-5 pods) │      │   (1 pod)   │   │
│  └─────────────┘      └─────────────┘      └─────────────┘   │
│         │                    │                     │            │
│         ▼                    ▼                     ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│  │     HPA     │      │     HPA     │      │     PVC     │   │
│  │  (CPU>70%)  │      │  (CPU>70%)  │      │   10Gi      │   │
│  └─────────────┘      └─────────────┘      └─────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              SHARED RESOURCES                            │  │
│  │  - ConfigMap: todo-config (DATABASE_URL, BACKEND_URL)   │  │
│  │  - Secret: todo-secrets (POSTGRES_PASSWORD, JWT_SECRET) │  │
│  │  - Namespace: default (or todo-app)                     │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Host Machine   │
                    │  /etc/hosts:    │
                    │  192.168.49.2   │
                    │  todo.local     │
                    └─────────────────┘
```

### 2.2 Component Responsibilities

#### Frontend Service
- **Purpose:** Serve Next.js production build
- **Type:** ClusterIP
- **Port:** 3000
- **Replicas:** 2-5 (HPA-managed)
- **Health Checks:**
  - Liveness: GET /api/health
  - Readiness: GET /api/health
- **Resources:**
  - Requests: 100m CPU, 128Mi memory
  - Limits: 200m CPU, 256Mi memory

#### Backend Service
- **Purpose:** Serve FastAPI REST API
- **Type:** ClusterIP
- **Port:** 8000
- **Replicas:** 2-5 (HPA-managed)
- **Health Checks:**
  - Liveness: GET /health
  - Readiness: GET /health (includes DB connectivity check)
- **Resources:**
  - Requests: 200m CPU, 256Mi memory
  - Limits: 500m CPU, 512Mi memory

#### PostgreSQL Service
- **Purpose:** Persistent data storage
- **Type:** ClusterIP (internal only)
- **Port:** 5432
- **Replicas:** 1 (StatefulSet)
- **Health Checks:**
  - Readiness: TCP port 5432
- **Resources:**
  - Requests: 250m CPU, 512Mi memory
  - Limits: 500m CPU, 1Gi memory
- **Storage:** PersistentVolumeClaim (10Gi)

#### Ingress Controller
- **Purpose:** Route external traffic to services
- **Implementation:** nginx.ingress.kubernetes.io
- **Rules:**
  - Host: todo.local
  - Path /: Frontend Service
  - Path /api: Backend Service (with path rewriting)

---

### 2.3 Data Flow

**User Request Flow:**
```
User Browser
    ↓ (http://todo.local/)
Ingress Controller
    ↓ (forwards to frontend-service:3000)
Frontend Pod
    ↓ (API request to /api/tasks)
Ingress Controller
    ↓ (forwards to backend-service:8000)
Backend Pod
    ↓ (SQL query)
PostgreSQL Pod
    ↓ (response)
Backend Pod → Ingress → Frontend Pod → User Browser
```

**Deployment Flow:**
```
Helm Chart → Kubernetes API Server → Scheduler → Nodes
                                   ↓
                    Deployments/StatefulSets/Services created
                                   ↓
                         Pods started on nodes
                                   ↓
                    Health checks pass → Ready for traffic
                                   ↓
                    Ingress routes traffic to services
```

---

## 3. Project Structure

### 3.1 Documentation (this feature)

```text
specs/004-phase-iv-kubernetes/
├── spec.md              # This specification (WHAT)
├── plan.md              # This file (HOW) - Technical architecture
├── tasks.md             # Task breakdown (BREAKDOWN) - Created by next phase
└── contracts/           # Kubernetes manifests and Helm values
    ├── values.yaml      # Helm chart values (dev/staging/prod)
    ├── deployment.yaml  # Example Deployment manifest
    ├── service.yaml     # Example Service manifest
    └── README.md        # Contract documentation
```

### 3.2 Source Code (Phase IV Implementation)

```text
phase-4-kubernetes/
├── README.md                     # Phase IV overview and quickstart
├── DEPLOYMENT.md                 # Detailed deployment guide
├── TROUBLESHOOTING.md            # Common issues and solutions
├── docker/                       # Dockerfiles
│   ├── frontend/
│   │   ├── Dockerfile           # Multi-stage build (production)
│   │   ├── Dockerfile.dev       # Development build (from Phase III)
│   │   ├── .dockerignore
│   │   └── nginx.conf           # Nginx configuration (if needed)
│   ├── backend/
│   │   ├── Dockerfile           # Multi-stage build (production)
│   │   ├── Dockerfile.dev       # Development build (from Phase III)
│   │   └── .dockerignore
│   └── README.md
├── helm-charts/                  # Helm chart definitions
│   └── todo/                     # Main application chart
│       ├── Chart.yaml            # Chart metadata
│       ├── values.yaml           # Default values
│       ├── values-dev.yaml       # Development overrides
│       ├── values-prod.yaml      # Production overrides
│       ├── templates/            # Kubernetes manifest templates
│       │   ├── NOTES.txt         # Post-install instructions
│       │   ├── _helpers.tpl      # Template helpers
│       │   ├── frontend-deployment.yaml
│       │   ├── frontend-service.yaml
│       │   ├── frontend-hpa.yaml
│       │   ├── backend-deployment.yaml
│       │   ├── backend-service.yaml
│       │   ├── backend-hpa.yaml
│       │   ├── postgres-statefulset.yaml
│       │   ├── postgres-service.yaml
│       │   ├── postgres-pvc.yaml
│       │   ├── configmap.yaml
│       │   ├── secrets.yaml.example
│       │   └── ingress.yaml
│       └── .helmignore
├── kubernetes/                   # Raw Kubernetes manifests (alternative to Helm)
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml.example
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── postgres/
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   └── pvc.yaml
│   └── ingress.yaml
├── scripts/                      # Automation scripts
│   ├── setup-minikube.sh         # Initialize Minikube cluster
│   ├── setup-minikube.ps1        # PowerShell version for Windows
│   ├── build-images.sh           # Build and push Docker images
│   ├── build-images.ps1          # PowerShell version
│   ├── deploy.sh                 # Deploy with Helm
│   ├── deploy.ps1                # PowerShell version
│   ├── port-forward.sh           # Port forwarding for local access
│   ├── port-forward.ps1          # PowerShell version
│   ├── cleanup.sh                # Delete all resources
│   ├── cleanup.ps1               # PowerShell version
│   └── README.md
├── tests/                        # Integration and smoke tests
│   ├── smoke-test.sh             # Basic health checks
│   ├── smoke-test.ps1            # PowerShell version
│   ├── load-test.sh              # ApacheBench load test
│   ├── load-test.ps1             # PowerShell version
│   └── README.md
├── .gitignore                    # Ignore secrets, temp files
└── docker-compose.override.yml   # Optional: local registry for Minikube
```

### 3.3 Existing Phase III Structure (Unchanged)

```text
phase-2-fullstack/
├── frontend/                     # Next.js 16+ application
│   ├── app/                      # Pages and layouts
│   ├── components/               # React components
│   ├── lib/                      # API client, utilities
│   ├── package.json
│   ├── next.config.js
│   └── tsconfig.json
├── backend/                      # FastAPI application
│   ├── src/
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── models/               # SQLModel database models
│   │   ├── routers/              # API route handlers
│   │   ├── agent/                # OpenAI Agent integration
│   │   ├── mcp/                  # MCP Server implementation
│   │   └── config.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile.dev
├── docker-compose.yml            # Phase III development environment
└── README.md
```

**Note:** Phase III code is **NOT modified** in Phase IV. Dockerfiles reference existing source code.

---

## 4. Detailed Design

### 4.1 Docker Images

#### 4.1.1 Frontend Dockerfile (Multi-Stage Build)

**File:** `phase-4-kubernetes/docker/frontend/Dockerfile`

**Design Decisions:**
- **Base Image:** node:22-alpine (minimal, security-focused)
- **Build Stage:** Full Node.js build tools
- **Production Stage:** Minimal runtime with standalone output
- **Non-root User:** `nextjs:nodejs` (UID 1001)
- **Port:** 3000 (standard Next.js)
- **Health Check:** Built-in (livenessProbe will call /api/health)

**Multi-Stage Rationale:**
1. **Stage 1 (deps):** Install dependencies with caching
2. **Stage 2 (builder):** Build Next.js app with standalone output
3. **Stage 3 (runner):** Copy only production files (no node_modules, no source)

**Expected Size:** ~150-200MB (vs ~1GB without multi-stage)

**Optimizations:**
- Layer caching for node_modules
- .dockerignore excludes dev files
- Standalone output mode reduces bundle size
- Static files served by Next.js (no separate nginx needed)

---

#### 4.1.2 Backend Dockerfile (Multi-Stage Build)

**File:** `phase-4-kubernetes/docker/backend/Dockerfile`

**Design Decisions:**
- **Base Image:** python:3.12-alpine (minimal, security-focused)
- **Build Stage:** Compile dependencies with build tools
- **Production Stage:** Runtime-only with compiled wheels
- **Non-root User:** `fastapi:fastapi` (UID 1001)
- **Port:** 8000 (standard FastAPI)
- **Server:** Uvicorn with 4 workers (production-grade)
- **Health Check:** Built-in (livenessProbe will call /health)

**Multi-Stage Rationale:**
1. **Stage 1 (builder):** Install UV, compile dependencies (includes gcc for psycopg2)
2. **Stage 2 (runner):** Copy only compiled wheels and source code

**Expected Size:** ~100-150MB (vs ~800MB without multi-stage)

**Optimizations:**
- UV for fast dependency resolution
- Virtual environment for isolation
- .dockerignore excludes tests, cache, pyc files
- Precompiled psycopg2 binary for PostgreSQL

---

#### 4.1.3 PostgreSQL Image

**Image:** `postgres:16-alpine` (official, no custom Dockerfile)

**Design Decisions:**
- Use official PostgreSQL image (security updates, stability)
- Alpine variant for smaller size (~100MB vs ~300MB Debian)
- Initialization scripts via ConfigMap (if needed)
- Data persistence via PersistentVolumeClaim

**Environment Variables (from Kubernetes Secret):**
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

---

### 4.2 Helm Chart Design

#### 4.2.1 Chart Metadata (Chart.yaml)

```yaml
apiVersion: v2
name: todo
description: Todo Application with AI Chatbot (Phase III + IV)
type: application
version: 1.0.0           # Helm chart version (SemVer)
appVersion: "4.0.0"      # Application version (Phase IV)
keywords:
  - todo
  - chatbot
  - ai
  - kubernetes
home: https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
sources:
  - https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
maintainers:
  - name: Ahmed KHI
    email: ahmed@example.com
```

---

#### 4.2.2 Default Values (values.yaml)

**Structure:**

```yaml
# Global settings
global:
  namespace: default
  environment: development  # development | staging | production

# Frontend configuration
frontend:
  replicaCount: 2
  image:
    repository: docker.io/ahmed-khi/todo-frontend
    tag: "v4.0.0"
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70
  healthCheck:
    livenessProbe:
      path: /api/health
      initialDelaySeconds: 10
      periodSeconds: 10
    readinessProbe:
      path: /api/health
      initialDelaySeconds: 5
      periodSeconds: 5

# Backend configuration
backend:
  replicaCount: 2
  image:
    repository: docker.io/ahmed-khi/todo-backend
    tag: "v4.0.0"
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70
  healthCheck:
    livenessProbe:
      path: /health
      initialDelaySeconds: 15
      periodSeconds: 10
    readinessProbe:
      path: /health
      initialDelaySeconds: 10
      periodSeconds: 5

# PostgreSQL configuration
postgres:
  enabled: true  # Set to false to use external database
  image:
    repository: postgres
    tag: "16-alpine"
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 5432
  persistence:
    enabled: true
    storageClass: standard  # Minikube default
    accessMode: ReadWriteOnce
    size: 10Gi
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
  env:
    POSTGRES_DB: todo_db
    POSTGRES_USER: postgres
    # POSTGRES_PASSWORD: Provided via secret

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
  host: todo.local
  tls:
    enabled: false  # Set to true for HTTPS (requires cert-manager)
    secretName: todo-tls

# ConfigMap data (non-sensitive)
config:
  logLevel: info
  backendUrl: http://backend-service:8000
  frontendUrl: http://todo.local

# Secret data (sensitive - override in values-prod.yaml)
secrets:
  postgresPassword: "changeme"  # MUST be overridden
  jwtSecretKey: "changeme"      # MUST be overridden
  openaiApiKey: "sk-..."        # MUST be overridden
```

**Override Files:**
- `values-dev.yaml`: Local Minikube settings (low resources)
- `values-prod.yaml`: Production settings (high resources, TLS, external DB)

---

#### 4.2.3 Template Helpers (_helpers.tpl)

**Common template functions:**

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo.labels" -}}
helm.sh/chart: {{ include "todo.chart" . }}
{{ include "todo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

### 4.3 Kubernetes Manifests (Templates)

#### 4.3.1 Frontend Deployment

**File:** `helm-charts/todo/templates/frontend-deployment.yaml`

**Key Features:**
- RollingUpdate strategy (maxUnavailable: 0, maxSurge: 1)
- Resource requests and limits from values.yaml
- Liveness and readiness probes
- Environment variables from ConfigMap and Secret
- securityContext (runAsNonRoot, readOnlyRootFilesystem where possible)
- Pod anti-affinity (spread replicas across nodes)

**Environment Variables:**
- BACKEND_URL (from ConfigMap)
- JWT_SECRET_KEY (from Secret)
- NODE_ENV=production

---

#### 4.3.2 Backend Deployment

**File:** `helm-charts/todo/templates/backend-deployment.yaml`

**Key Features:**
- RollingUpdate strategy
- Resource requests and limits from values.yaml
- Liveness and readiness probes (readiness checks DB connectivity)
- Environment variables from ConfigMap and Secret
- securityContext (runAsNonRoot)
- Init container for database migrations (optional)

**Environment Variables:**
- DATABASE_URL (from ConfigMap + Secret)
- JWT_SECRET_KEY (from Secret)
- OPENAI_API_KEY (from Secret)
- LOG_LEVEL (from ConfigMap)

---

#### 4.3.3 PostgreSQL StatefulSet

**File:** `helm-charts/todo/templates/postgres-statefulset.yaml`

**Key Features:**
- StatefulSet (not Deployment) for stable network identity
- PersistentVolumeClaim template
- Readiness probe (TCP port 5432)
- Resource requests and limits from values.yaml
- securityContext (runAsUser: 999 - postgres user)

**PersistentVolumeClaim:**
- StorageClass: standard (Minikube default)
- AccessMode: ReadWriteOnce
- Size: 10Gi (configurable)

---

#### 4.3.4 Services

**Frontend Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: ClusterIP
  ports:
    - port: 3000
      targetPort: 3000
      protocol: TCP
  selector:
    app: todo-frontend
```

**Backend Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP
  selector:
    app: todo-backend
```

**PostgreSQL Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
      protocol: TCP
  selector:
    app: todo-postgres
```

---

#### 4.3.5 Ingress

**File:** `helm-charts/todo/templates/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
    - host: todo.local
      http:
        paths:
          - path: /()(.*)
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 3000
          - path: /api(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: backend-service
                port:
                  number: 8000
```

**Path Rewriting:**
- `/` → Frontend (e.g., `/dashboard` stays `/dashboard`)
- `/api/tasks` → Backend (rewritten to `/tasks`)

---

#### 4.3.6 HorizontalPodAutoscaler

**Frontend HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend-deployment
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

**Backend HPA:** (similar structure)

---

#### 4.3.7 ConfigMap

**File:** `helm-charts/todo/templates/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
data:
  LOG_LEVEL: "{{ .Values.config.logLevel }}"
  BACKEND_URL: "{{ .Values.config.backendUrl }}"
  FRONTEND_URL: "{{ .Values.config.frontendUrl }}"
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "{{ .Values.postgres.env.POSTGRES_DB }}"
```

---

#### 4.3.8 Secret

**File:** `helm-charts/todo/templates/secrets.yaml.example` (excluded from Git)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
data:
  POSTGRES_PASSWORD: {{ .Values.secrets.postgresPassword | b64enc }}
  JWT_SECRET_KEY: {{ .Values.secrets.jwtSecretKey | b64enc }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | b64enc }}
```

**Note:** Real secrets created via:
```bash
kubectl create secret generic todo-secrets \
  --from-literal=POSTGRES_PASSWORD=securepass \
  --from-literal=JWT_SECRET_KEY=supersecret \
  --from-literal=OPENAI_API_KEY=sk-...
```

---

### 4.4 Deployment Scripts

#### 4.4.1 Setup Minikube (setup-minikube.sh / .ps1)

**Purpose:** Initialize Minikube cluster with required addons

**Steps:**
1. Start Minikube: `minikube start --cpus=4 --memory=8192 --disk-size=20g`
2. Enable addons:
   - `minikube addons enable ingress`
   - `minikube addons enable metrics-server`
   - `minikube addons enable dashboard`
3. Add /etc/hosts entry: `$(minikube ip) todo.local`
4. Verify cluster: `kubectl cluster-info`

---

#### 4.4.2 Build Images (build-images.sh / .ps1)

**Purpose:** Build Docker images and push to registry (Docker Hub or Minikube)

**Steps:**
1. Build frontend: `docker build -t ahmed-khi/todo-frontend:v4.0.0 -f docker/frontend/Dockerfile ../phase-2-fullstack/frontend`
2. Build backend: `docker build -t ahmed-khi/todo-backend:v4.0.0 -f docker/backend/Dockerfile ../phase-2-fullstack/backend`
3. Push to Docker Hub (or load into Minikube):
   - `docker push ahmed-khi/todo-frontend:v4.0.0`
   - OR `minikube image load ahmed-khi/todo-frontend:v4.0.0`

**Gordon AI Usage:**
```bash
docker ai "Optimize this Dockerfile for size and security" -f docker/frontend/Dockerfile
docker ai "Why is my backend image 1GB? How can I reduce it?"
```

---

#### 4.4.3 Deploy with Helm (deploy.sh / .ps1)

**Purpose:** Deploy application using Helm chart

**Steps:**
1. Create secrets: `kubectl create secret generic todo-secrets --from-literal=...`
2. Install Helm chart: `helm install todo ./helm-charts/todo -f helm-charts/todo/values-dev.yaml`
3. Wait for pods: `kubectl wait --for=condition=ready pod -l app=todo --timeout=300s`
4. Get ingress IP: `minikube ip`
5. Verify: `curl http://todo.local`

**kubectl-ai Usage:**
```bash
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"
```

**Kagent Usage:**
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation for todo app"
kagent "why is my postgres pod in CrashLoopBackOff?"
```

---

## 5. Implementation Phases

### Phase 0: Prerequisites and Setup

**Goal:** Ensure all tools installed and Minikube ready

**Deliverables:**
- Docker Desktop 4.53+ installed (with Gordon enabled)
- Minikube 1.33+ installed
- kubectl 1.31+ installed
- Helm 3.16+ installed
- kubectl-ai installed (optional)
- Kagent installed (optional)
- Minikube cluster running with ingress and metrics-server addons

**Acceptance Criteria:**
- `docker --version` shows 27+
- `docker ai "What can you do?"` works (if Gordon enabled)
- `minikube status` shows Running
- `kubectl get nodes` shows Ready
- `helm version` shows 3.16+
- `kubectl-ai version` works (if installed)

---

### Phase 1: Docker Images

**Goal:** Create production-ready Docker images

**Tasks:**
1. Create frontend Dockerfile with multi-stage build
2. Create frontend .dockerignore
3. Test frontend image locally: `docker run -p 3000:3000 todo-frontend:v4.0.0`
4. Create backend Dockerfile with multi-stage build
5. Create backend .dockerignore
6. Test backend image locally: `docker run -p 8000:8000 todo-backend:v4.0.0`
7. Use Gordon AI to optimize Dockerfiles
8. Build and tag images with version v4.0.0
9. Push images to Docker Hub (or load into Minikube)

**Acceptance Criteria:**
- Frontend image < 200MB
- Backend image < 150MB
- Both images run successfully with `docker run`
- Health checks pass: `/api/health` (frontend), `/health` (backend)
- Gordon AI provides optimization suggestions

---

### Phase 2: Helm Chart Structure

**Goal:** Create Helm chart skeleton

**Tasks:**
1. Create `helm-charts/todo/` directory
2. Create Chart.yaml with metadata
3. Create values.yaml with default configuration
4. Create values-dev.yaml with Minikube-specific settings
5. Create templates/ directory
6. Create templates/_helpers.tpl with common functions
7. Create templates/NOTES.txt with post-install instructions
8. Create .helmignore
9. Run `helm lint helm-charts/todo` (should pass)

**Acceptance Criteria:**
- `helm lint` passes without warnings
- Chart metadata includes name, version, appVersion
- values.yaml includes all configurable parameters
- _helpers.tpl includes name, fullname, labels functions

---

### Phase 3: Kubernetes Manifests (Templates)

**Goal:** Create all Kubernetes resource templates

**Tasks:**
1. Create frontend-deployment.yaml with RollingUpdate, probes, resources
2. Create frontend-service.yaml (ClusterIP)
3. Create frontend-hpa.yaml (2-5 replicas, CPU 70%)
4. Create backend-deployment.yaml with RollingUpdate, probes, resources
5. Create backend-service.yaml (ClusterIP)
6. Create backend-hpa.yaml (2-5 replicas, CPU 70%)
7. Create postgres-statefulset.yaml with PVC template
8. Create postgres-service.yaml (ClusterIP, headless for StatefulSet)
9. Create postgres-pvc.yaml (10Gi, ReadWriteOnce)
10. Create configmap.yaml with non-sensitive config
11. Create secrets.yaml.example (template, not real secrets)
12. Create ingress.yaml with nginx annotations and path rewriting
13. Use kubectl-ai to generate missing templates

**Acceptance Criteria:**
- All templates use `{{ .Values.* }}` for configuration
- All deployments have liveness and readiness probes
- All deployments have resource requests and limits
- HPA targets CPU 70%
- Ingress routes / to frontend, /api to backend
- secrets.yaml.example excluded from Git

---

### Phase 4: Deployment Scripts

**Goal:** Automate cluster setup and application deployment

**Tasks:**
1. Create setup-minikube.sh (Linux/macOS)
2. Create setup-minikube.ps1 (Windows PowerShell)
3. Create build-images.sh with Docker build commands
4. Create build-images.ps1 (PowerShell)
5. Create deploy.sh with Helm install
6. Create deploy.ps1 (PowerShell)
7. Create port-forward.sh for local access (if ingress fails)
8. Create port-forward.ps1 (PowerShell)
9. Create cleanup.sh to delete all resources
10. Create cleanup.ps1 (PowerShell)
11. Test all scripts on clean Minikube cluster

**Acceptance Criteria:**
- setup-minikube.sh completes without errors
- build-images.sh builds both images
- deploy.sh installs Helm chart successfully
- All pods reach Running state within 2 minutes
- curl http://todo.local returns frontend HTML

---

### Phase 5: Testing and Validation

**Goal:** Verify deployment and AI DevOps tools

**Tasks:**
1. Create smoke-test.sh with health check assertions
2. Create smoke-test.ps1 (PowerShell)
3. Create load-test.sh with ApacheBench (100 concurrent requests)
4. Create load-test.ps1 (PowerShell)
5. Test Gordon AI: `docker ai "Optimize this Dockerfile"`
6. Test kubectl-ai: `kubectl-ai "scale the backend to 3 replicas"`
7. Test Kagent: `kagent "analyze cluster health"`
8. Document AI tool outputs in README
9. Verify HPA scales up under load
10. Verify rolling updates work without downtime: `helm upgrade todo ...`

**Acceptance Criteria:**
- Smoke tests pass (all health checks return 200 OK)
- Load tests trigger HPA scale-up (2 → 3+ pods)
- kubectl-ai successfully scales resources
- Kagent provides cluster health analysis
- Rolling update completes with zero downtime

---

### Phase 6: Documentation

**Goal:** Complete deployment guides and demo materials

**Tasks:**
1. Create README.md with quickstart (10-minute setup)
2. Create DEPLOYMENT.md with detailed step-by-step guide
3. Create TROUBLESHOOTING.md with common issues and fixes
4. Create demo video outline (90-second script)
5. Document Gordon, kubectl-ai, Kagent usage examples
6. Create architecture diagram (Kubernetes components)
7. Update constitution.md with Phase IV addendum (if needed)
8. Create ADR for Phase IV Kubernetes deployment decision
9. Document rollback procedure: `helm rollback todo`
10. Create validation checklist for reviewers

**Acceptance Criteria:**
- README includes prerequisites, installation, usage
- DEPLOYMENT.md has screenshots or ASCII diagrams
- TROUBLESHOOTING.md covers 10+ common issues
- Demo video outline covers all key features
- AI tool examples documented with expected outputs

---

## 6. AI DevOps Integration

### 6.1 Gordon (Docker AI)

**Use Cases:**
1. **Dockerfile Optimization:**
   ```bash
   docker ai "How can I reduce the size of this Next.js Dockerfile?"
   docker ai "What security issues are in this backend Dockerfile?"
   docker ai "Generate a multi-stage build for FastAPI with UV"
   ```

2. **Troubleshooting:**
   ```bash
   docker ai "Why is my container failing with exit code 137?"
   docker ai "How do I add a non-root user to Alpine Linux?"
   docker ai "What's the difference between CMD and ENTRYPOINT?"
   ```

3. **Image Analysis:**
   ```bash
   docker ai "Analyze the layers of ahmed-khi/todo-frontend:v4.0.0"
   docker ai "What base image should I use for Node.js production?"
   ```

**Expected Outputs:** Documented in README with real examples

---

### 6.2 kubectl-ai

**Use Cases:**
1. **Resource Management:**
   ```bash
   kubectl-ai "deploy the todo frontend with 2 replicas using image ahmed-khi/todo-frontend:v4.0.0"
   kubectl-ai "scale the backend deployment to 3 replicas"
   kubectl-ai "delete all pods in namespace default"
   ```

2. **Troubleshooting:**
   ```bash
   kubectl-ai "why are my postgres pods in CrashLoopBackOff?"
   kubectl-ai "show me the logs of the frontend pod"
   kubectl-ai "describe the failing backend pod"
   ```

3. **Configuration:**
   ```bash
   kubectl-ai "create a service for the frontend deployment exposing port 3000"
   kubectl-ai "add an ingress rule for todo.local pointing to frontend-service"
   kubectl-ai "create a horizontal pod autoscaler for backend targeting 70% CPU"
   ```

**Expected Outputs:** Documented with command + kubectl output

---

### 6.3 Kagent

**Use Cases:**
1. **Cluster Analysis:**
   ```bash
   kagent "analyze the overall health of my Kubernetes cluster"
   kagent "what resources are consuming the most CPU and memory?"
   kagent "are there any pods with failing health checks?"
   ```

2. **Optimization:**
   ```bash
   kagent "optimize the resource allocation for the todo application"
   kagent "recommend cost savings for my cluster"
   kagent "should I increase or decrease my HPA settings?"
   ```

3. **Diagnostics:**
   ```bash
   kagent "diagnose why my application is slow"
   kagent "check if my persistent volumes are correctly mounted"
   kagent "analyze the network policies affecting my pods"
   ```

**Expected Outputs:** Cluster health report with recommendations

---

## 7. Testing Strategy

### 7.1 Unit Tests (Developer-Level)

**Dockerfile Tests:**
- Build frontend image: `docker build -t test-frontend -f docker/frontend/Dockerfile .`
- Build backend image: `docker build -t test-backend -f docker/backend/Dockerfile .`
- Run containers locally: `docker run -p 3000:3000 test-frontend`
- Health checks: `curl http://localhost:3000/api/health`

**Helm Chart Tests:**
- Lint chart: `helm lint helm-charts/todo`
- Dry run: `helm install todo helm-charts/todo --dry-run --debug`
- Template validation: `helm template todo helm-charts/todo | kubectl apply --dry-run=client -f -`

---

### 7.2 Integration Tests (Pre-Deployment)

**Minikube Cluster Tests:**
- Cluster status: `minikube status`
- Node ready: `kubectl get nodes`
- Ingress addon: `kubectl get pods -n ingress-nginx`
- Metrics server: `kubectl top nodes`

**Deployment Tests:**
- Install chart: `helm install todo helm-charts/todo -f values-dev.yaml`
- Wait for pods: `kubectl wait --for=condition=ready pod --all --timeout=300s`
- Check services: `kubectl get svc`
- Check ingress: `kubectl get ingress`

---

### 7.3 Smoke Tests (Post-Deployment)

**Health Checks:**
```bash
# Frontend health
curl -f http://todo.local/api/health || exit 1

# Backend health
curl -f http://todo.local/api/health || exit 1

# Database connectivity (via backend)
curl -f http://todo.local/api/health | grep -q "database.*ok" || exit 1
```

**Functional Tests:**
```bash
# Register user
curl -X POST http://todo.local/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Login user
TOKEN=$(curl -X POST http://todo.local/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r '.token')

# Create task
curl -X POST http://todo.local/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Created via smoke test"}'

# List tasks
curl -f http://todo.local/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.[] | select(.title=="Test Task")'
```

---

### 7.4 Load Tests (Performance Validation)

**ApacheBench:**
```bash
# 100 concurrent requests to frontend
ab -n 1000 -c 100 http://todo.local/

# Expected: HPA scales frontend from 2 → 3+ pods
kubectl get hpa -w
```

**Expected Results:**
- All requests succeed (no 5xx errors)
- Response time < 200ms (p95)
- HPA triggers scale-up when CPU > 70%
- Scale-down after 5 minutes of low load

---

### 7.5 Rollback Tests

**Scenario:** Deploy broken version, rollback to previous

**Steps:**
```bash
# Deploy v4.0.0 (working)
helm install todo helm-charts/todo --set backend.image.tag=v4.0.0

# Upgrade to v4.0.1 (broken)
helm upgrade todo helm-charts/todo --set backend.image.tag=v4.0.1-broken

# Verify failure (pods CrashLoopBackOff)
kubectl get pods | grep backend

# Rollback
helm rollback todo

# Verify recovery
kubectl get pods | grep backend  # Should show Running
```

**Expected Result:** Application returns to working state within 2 minutes

---

## 8. Security Considerations

### 8.1 Container Security

**Implemented:**
- ✅ Non-root users in all containers (UID > 1000)
- ✅ Minimal base images (Alpine Linux)
- ✅ Read-only root filesystem where possible
- ✅ No privileged containers
- ✅ Security context with `runAsNonRoot: true`

**Tools:**
- Trivy scan: `trivy image ahmed-khi/todo-frontend:v4.0.0`
- Docker Scout: `docker scout cves ahmed-khi/todo-backend:v4.0.0`

---

### 8.2 Secret Management

**Implemented:**
- ✅ Secrets stored in Kubernetes Secrets (base64 encoded)
- ✅ Secrets excluded from Git (.gitignore)
- ✅ Secrets mounted as environment variables
- ✅ No hardcoded credentials in code or Dockerfiles

**Future (Phase V):**
- External secret managers (Vault, AWS Secrets Manager)
- Secret rotation automation
- RBAC policies for secret access

---

### 8.3 Network Security

**Implemented:**
- ✅ Backend not exposed externally (only via ingress)
- ✅ PostgreSQL internal only (ClusterIP service)
- ✅ Ingress with TLS support (optional in Minikube, required in prod)

**Future (Phase V):**
- Network policies to restrict pod-to-pod communication
- Service mesh (Istio) for mTLS between services

---

## 9. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Minikube resource limits | High | Medium | Document minimum 4 CPUs, 8GB RAM |
| Docker image size too large | Medium | Low | Multi-stage builds, .dockerignore |
| Ingress not working | High | Medium | Provide port-forward alternative |
| Gordon AI not available | Low | High | Document optional, provide manual commands |
| kubectl-ai API key missing | Low | Medium | Document OpenAI API key requirement |
| Database data loss | High | Low | PersistentVolumeClaim with 10Gi storage |
| HPA not scaling | Medium | Low | Verify metrics-server addon enabled |
| Secrets exposed in Git | High | Low | .gitignore for secrets.yaml, use .example |

---

## 10. Success Metrics

**Deployment Metrics:**
- Helm install time: < 2 minutes ✅
- Pod startup time: < 30 seconds (frontend), < 45 seconds (backend) ✅
- Health check pass rate: 100% ✅
- Image size: < 200MB (frontend), < 150MB (backend) ✅

**Functional Metrics:**
- All Phase III features work identically ✅
- Zero downtime during rolling updates ✅
- HPA scales correctly under load ✅
- Database data persists after pod restarts ✅

**AI DevOps Metrics:**
- Gordon provides Dockerfile optimization suggestions ✅
- kubectl-ai executes at least 3 commands successfully ✅
- Kagent analyzes cluster health successfully ✅

**Documentation Metrics:**
- README enables 10-minute setup ✅
- Troubleshooting guide covers 10+ issues ✅
- Demo video is 90 seconds ✅

---

## 11. Future Enhancements (Phase V)

**Cloud Deployment:**
- Deploy to AWS EKS, Azure AKS, or Google GKE
- Use cloud-native services (RDS for database, ELB for load balancing)
- Implement autoscaling with Cluster Autoscaler

**Observability:**
- Prometheus + Grafana for metrics
- Jaeger for distributed tracing
- ELK stack for centralized logging

**CI/CD:**
- GitHub Actions for automated builds
- ArgoCD or FluxCD for GitOps continuous deployment
- Automated testing in CI pipeline

**Advanced Features:**
- Service mesh (Istio) for traffic management
- Dapr for event-driven architecture
- Kafka for asynchronous messaging

---

## 12. References

1. **Kubernetes Documentation:** https://kubernetes.io/docs/
2. **Helm Documentation:** https://helm.sh/docs/
3. **Minikube Documentation:** https://minikube.sigs.k8s.io/docs/
4. **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/
5. **kubectl-ai GitHub:** https://github.com/sozercan/kubectl-ai
6. **Kagent (K8sGPT) Documentation:** https://www.k8sgpt.ai/
7. **12-Factor App:** https://12factor.net/
8. **Hackathon II Document:** https://docs.google.com/document/d/1KHxeDNnqG9uew-rEabQc5H8u3VmEN3OaJ_A1ZVVr9vY
9. **Reference Repository:** https://github.com/Ameen-Alam/Full-Stack-Web-Application

---

**END OF PLAN**
