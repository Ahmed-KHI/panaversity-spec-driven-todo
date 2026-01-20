# Phase IV: Local Kubernetes Deployment - SPECIFICATION

**Project:** Hackathon II - The Evolution of Todo  
**Phase:** IV - Local Kubernetes Deployment (Minikube, Helm Charts, kubectl-ai, Kagent)  
**Status:** Active  
**Version:** 1.0  
**Created:** January 18, 2026  
**Dependencies:** Phase III Complete (AI-Powered Todo Chatbot with MCP)

---

## 1. Executive Summary

### 1.1 Phase Objective

Deploy the Phase III Todo Chatbot application on a local Kubernetes cluster using cloud-native technologies and AI-powered DevOps tools:
- **Docker** for containerization (Docker Desktop 4.53+ with Gordon AI)
- **Kubernetes (Minikube)** for local orchestration
- **Helm Charts** for declarative deployments
- **kubectl-ai** and **Kagent** for AI-assisted Kubernetes operations
- **Gordon (Docker AI)** for intelligent Docker operations

### 1.2 Deliverables

1. **Production-ready Docker images** for frontend, backend, and database
2. **Helm charts** for all application components with configurable values
3. **Kubernetes manifests** (Deployments, Services, ConfigMaps, Secrets, Ingress)
4. **Minikube setup scripts** with automated cluster configuration
5. **AI DevOps integration** (Gordon, kubectl-ai, kagent command examples)
6. **Complete deployment documentation** and 90-second demo video

### 1.3 Success Criteria

- ✅ All Phase III features work identically in Kubernetes
- ✅ Application accessible via Minikube ingress (http://todo.local)
- ✅ Horizontal Pod Autoscaling configured for frontend and backend
- ✅ Health checks (liveness, readiness) functioning correctly
- ✅ Persistent volumes for PostgreSQL data
- ✅ Zero-downtime rolling updates supported
- ✅ Resource limits and requests defined for all containers
- ✅ Secrets managed securely (not hardcoded)
- ✅ Gordon, kubectl-ai, and Kagent successfully used for operations
- ✅ Complete deployment runbook with troubleshooting guide

---

## 2. User Stories

### 2.1 Core User Stories (Must Have)

#### US1: DevOps Engineer - Containerize Application
**As a** DevOps engineer  
**I want to** containerize the frontend and backend applications  
**So that** they can run in any container orchestration platform

**Acceptance Criteria:**
- [ ] Frontend Dockerfile with multi-stage build (builder + production)
- [ ] Backend Dockerfile with Python 3.12 and production WSGI server (Uvicorn)
- [ ] Docker images optimized (< 200MB for frontend, < 150MB for backend)
- [ ] Images follow security best practices (non-root user, minimal base)
- [ ] .dockerignore files prevent bloat
- [ ] Local testing with `docker run` successful
- [ ] Gordon AI can inspect and optimize Dockerfiles

**Related Requirements:** REQ-001, REQ-002, REQ-003

---

#### US2: DevOps Engineer - Create Helm Charts
**As a** DevOps engineer  
**I want to** package the application as Helm charts  
**So that** deployment is repeatable and version-controlled

**Acceptance Criteria:**
- [ ] Helm chart structure with Chart.yaml, values.yaml, templates/
- [ ] Separate charts for frontend, backend, postgres (or single umbrella chart)
- [ ] Templated configurations (replicas, resources, image tags)
- [ ] Values overrides for dev/staging/prod environments
- [ ] Helm lint passes without warnings
- [ ] `helm install` and `helm upgrade` work correctly
- [ ] kubectl-ai can generate chart templates from descriptions

**Related Requirements:** REQ-004, REQ-005, REQ-006

---

#### US3: DevOps Engineer - Deploy on Minikube
**As a** DevOps engineer  
**I want to** deploy the application on a local Minikube cluster  
**So that** I can test Kubernetes configurations locally

**Acceptance Criteria:**
- [ ] Minikube cluster running with sufficient resources (4GB+ RAM)
- [ ] Ingress controller enabled (nginx)
- [ ] Application accessible via http://todo.local
- [ ] All pods in Running state
- [ ] PostgreSQL data persists after pod restarts
- [ ] Logs accessible via `kubectl logs`
- [ ] kubectl-ai can diagnose and fix pod issues

**Related Requirements:** REQ-007, REQ-008, REQ-009

---

#### US4: DevOps Engineer - Configure Health Checks
**As a** DevOps engineer  
**I want to** configure liveness and readiness probes  
**So that** Kubernetes can automatically restart failed pods and route traffic correctly

**Acceptance Criteria:**
- [ ] Liveness probes for frontend and backend (HTTP /health)
- [ ] Readiness probes for frontend and backend (HTTP /ready)
- [ ] PostgreSQL readiness probe (TCP port 5432)
- [ ] Startup probes for slow-starting containers
- [ ] Probes configured with appropriate timeouts and thresholds
- [ ] Failed probes trigger pod restarts correctly
- [ ] Kagent can analyze probe configurations

**Related Requirements:** REQ-010, REQ-011

---

#### US5: DevOps Engineer - Implement Resource Management
**As a** DevOps engineer  
**I want to** define resource requests and limits for all containers  
**So that** the cluster can schedule pods efficiently and prevent resource starvation

**Acceptance Criteria:**
- [ ] CPU/memory requests defined for all containers
- [ ] CPU/memory limits defined for all containers
- [ ] Resource requests match realistic application needs
- [ ] Horizontal Pod Autoscaler configured (CPU > 70% → scale up)
- [ ] Resource quotas prevent over-allocation
- [ ] `kubectl top` shows resource usage
- [ ] Kagent can optimize resource allocation

**Related Requirements:** REQ-012, REQ-013

---

#### US6: DevOps Engineer - Manage Secrets Securely
**As a** DevOps engineer  
**I want to** manage sensitive data using Kubernetes Secrets  
**So that** credentials are never hardcoded or exposed in Git

**Acceptance Criteria:**
- [ ] Kubernetes Secrets for database credentials
- [ ] Kubernetes Secrets for JWT signing key
- [ ] Secrets mounted as environment variables (not in ConfigMaps)
- [ ] Secrets excluded from Git (.gitignore)
- [ ] Base64 encoding for secret values
- [ ] RBAC restricts secret access to appropriate service accounts
- [ ] Gordon can detect exposed secrets in Dockerfiles

**Related Requirements:** REQ-014, REQ-015

---

#### US7: DevOps Engineer - Use AI-Powered DevOps Tools
**As a** DevOps engineer  
**I want to** use Gordon, kubectl-ai, and Kagent for operations  
**So that** I can leverage AI to accelerate debugging and optimization

**Acceptance Criteria:**
- [ ] Gordon enabled in Docker Desktop (Beta features)
- [ ] Gordon successfully analyzes Dockerfiles and suggests optimizations
- [ ] kubectl-ai installed and configured
- [ ] kubectl-ai can deploy, scale, and troubleshoot resources
- [ ] Kagent installed and configured
- [ ] Kagent can analyze cluster health and optimize resources
- [ ] Documentation includes example commands for all three tools

**Related Requirements:** REQ-016, REQ-017, REQ-018

---

## 3. Functional Requirements

### 3.1 Container Requirements

#### REQ-001: Frontend Containerization (MUST HAVE)
**Description:** Frontend must be containerized with Next.js production build  
**Rationale:** Enable deployment in any container orchestration platform  
**Acceptance Criteria:**
- Multi-stage Dockerfile (build stage + production stage)
- Node.js 22 Alpine base image
- Next.js standalone output mode
- Port 3000 exposed
- Non-root user (nextjs:nodejs)
- Health check endpoint at /api/health
- Image size < 200MB
- Build time < 5 minutes

**Dependencies:** Phase III frontend complete  
**Priority:** P0 (Must Have)

---

#### REQ-002: Backend Containerization (MUST HAVE)
**Description:** Backend must be containerized with FastAPI production server  
**Rationale:** Enable deployment in any container orchestration platform  
**Acceptance Criteria:**
- Multi-stage Dockerfile (dependencies + production)
- Python 3.12 Alpine base image
- UV for dependency management
- Uvicorn production server with 4 workers
- Port 8000 exposed
- Non-root user (fastapi:fastapi)
- Health check endpoint at /api/health
- Image size < 150MB
- Build time < 3 minutes

**Dependencies:** Phase III backend complete  
**Priority:** P0 (Must Have)

---

#### REQ-003: Docker AI Integration (SHOULD HAVE)
**Description:** Use Gordon (Docker AI) for intelligent Docker operations  
**Rationale:** Leverage AI for Dockerfile optimization and troubleshooting  
**Acceptance Criteria:**
- Gordon enabled in Docker Desktop 4.53+
- Documentation includes Gordon commands:
  - `docker ai "What can you do?"`
  - `docker ai "Optimize this Dockerfile for size"`
  - `docker ai "Why is my container failing?"`
  - `docker ai "Generate multi-stage build for Next.js"`
- Gordon successfully analyzes project Dockerfiles
- Suggested optimizations documented in README

**Dependencies:** Docker Desktop 4.53+ installed  
**Priority:** P1 (Should Have)

---

### 3.2 Helm Chart Requirements

#### REQ-004: Helm Chart Structure (MUST HAVE)
**Description:** Application must be packaged as a valid Helm chart  
**Rationale:** Enable declarative, version-controlled deployments  
**Acceptance Criteria:**
- Chart.yaml with name, version, description, appVersion
- values.yaml with configurable parameters
- templates/ directory with all Kubernetes manifests
- templates/NOTES.txt with post-install instructions
- templates/_helpers.tpl with reusable template functions
- Helm lint passes without errors
- Chart versioning follows SemVer (1.0.0)

**Dependencies:** None  
**Priority:** P0 (Must Have)

---

#### REQ-005: Helm Values Configuration (MUST HAVE)
**Description:** Helm values must be templated and overridable  
**Rationale:** Support multiple environments (dev, staging, prod)  
**Acceptance Criteria:**
- Image tags configurable (frontend.image.tag, backend.image.tag)
- Replica counts configurable (frontend.replicaCount, backend.replicaCount)
- Resource requests/limits configurable
- Ingress hostname configurable (ingress.host)
- Database credentials overridable (postgres.password)
- Environment variables configurable (env.JWT_SECRET)
- Values validation with JSON Schema

**Dependencies:** REQ-004  
**Priority:** P0 (Must Have)

---

#### REQ-006: kubectl-ai Chart Generation (SHOULD HAVE)
**Description:** Use kubectl-ai to generate and validate Helm charts  
**Rationale:** Accelerate chart development with AI assistance  
**Acceptance Criteria:**
- kubectl-ai installed via `brew install kubectl-ai` or `go install`
- Documentation includes kubectl-ai commands:
  - `kubectl-ai "create helm chart for todo frontend"`
  - `kubectl-ai "add ingress to helm chart"`
  - `kubectl-ai "add HPA to deployment"`
- Generated charts reviewed and customized
- kubectl-ai commands documented in DEPLOYMENT.md

**Dependencies:** kubectl-ai installed  
**Priority:** P1 (Should Have)

---

### 3.3 Kubernetes Deployment Requirements

#### REQ-007: Minikube Cluster Setup (MUST HAVE)
**Description:** Minikube cluster must be configured for local development  
**Rationale:** Provide local Kubernetes environment for testing  
**Acceptance Criteria:**
- Minikube installed and running
- Kubernetes version 1.31+ (recommended 1.32+)
- Cluster resources: 4 CPUs, 8GB RAM, 20GB disk
- Ingress addon enabled (`minikube addons enable ingress`)
- Metrics server enabled (`minikube addons enable metrics-server`)
- Dashboard enabled (`minikube dashboard`)
- LoadBalancer support via `minikube tunnel`
- Persistent volume provisioner enabled

**Dependencies:** None  
**Priority:** P0 (Must Have)

---

#### REQ-008: Application Deployment (MUST HAVE)
**Description:** Application must deploy successfully on Minikube  
**Rationale:** Validate Kubernetes configurations locally  
**Acceptance Criteria:**
- `helm install todo ./helm-charts/todo` succeeds
- All pods reach Running state within 2 minutes
- Frontend accessible at http://todo.local (with /etc/hosts entry)
- Backend API accessible at http://todo.local/api
- Database migrations run automatically on deployment
- No CrashLoopBackOff or ImagePullBackOff errors
- Application logs show no errors

**Dependencies:** REQ-004, REQ-007  
**Priority:** P0 (Must Have)

---

#### REQ-009: Ingress Configuration (MUST HAVE)
**Description:** Ingress must route traffic to frontend and backend services  
**Rationale:** Provide single entry point for application access  
**Acceptance Criteria:**
- Ingress resource created with nginx.ingress.kubernetes.io/rewrite-target
- Frontend routes: /, /chat, /dashboard, /login, /register
- Backend routes: /api/*
- TLS support (optional for local, required for production)
- /etc/hosts entry: 192.168.49.2 todo.local (Minikube IP)
- Ingress controller logs show successful routing
- 404 page for unmatched routes

**Dependencies:** REQ-007, REQ-008  
**Priority:** P0 (Must Have)

---

#### REQ-010: Health Checks (MUST HAVE)
**Description:** All services must have liveness and readiness probes  
**Rationale:** Enable Kubernetes to detect and recover from failures  
**Acceptance Criteria:**
- Frontend probes:
  - Liveness: GET /api/health (200 OK)
  - Readiness: GET /api/health (200 OK)
  - Initial delay: 10s, period: 10s, timeout: 5s
- Backend probes:
  - Liveness: GET /health (200 OK)
  - Readiness: GET /health (200 OK + database connectivity)
  - Initial delay: 15s, period: 10s, timeout: 5s
- PostgreSQL probes:
  - Readiness: TCP port 5432 (socket connect)
  - Initial delay: 5s, period: 10s, timeout: 5s
- Failed probes trigger pod restarts automatically

**Dependencies:** Health endpoints implemented in Phase III  
**Priority:** P0 (Must Have)

---

#### REQ-011: Rolling Updates (MUST HAVE)
**Description:** Application must support zero-downtime rolling updates  
**Rationale:** Enable continuous deployment without service interruption  
**Acceptance Criteria:**
- Deployment strategy: RollingUpdate
- MaxUnavailable: 0 (zero downtime)
- MaxSurge: 1 (one extra pod during rollout)
- Readiness probes prevent traffic to unhealthy pods
- `helm upgrade` completes without downtime
- Old pods terminate gracefully (SIGTERM → 30s → SIGKILL)
- Database migrations run before new pods start

**Dependencies:** REQ-010  
**Priority:** P0 (Must Have)

---

#### REQ-012: Resource Management (MUST HAVE)
**Description:** All containers must have resource requests and limits  
**Rationale:** Ensure efficient resource allocation and prevent starvation  
**Acceptance Criteria:**
- Frontend resources:
  - Requests: 100m CPU, 128Mi memory
  - Limits: 200m CPU, 256Mi memory
- Backend resources:
  - Requests: 200m CPU, 256Mi memory
  - Limits: 500m CPU, 512Mi memory
- PostgreSQL resources:
  - Requests: 250m CPU, 512Mi memory
  - Limits: 500m CPU, 1Gi memory
- `kubectl top pods` shows usage within limits
- No OOMKilled errors in pod events

**Dependencies:** None  
**Priority:** P0 (Must Have)

---

#### REQ-013: Horizontal Pod Autoscaling (MUST HAVE)
**Description:** Frontend and backend must autoscale based on CPU usage  
**Rationale:** Handle variable load efficiently  
**Acceptance Criteria:**
- HPA configured for frontend:
  - Min replicas: 2, Max replicas: 5
  - Target CPU: 70%
- HPA configured for backend:
  - Min replicas: 2, Max replicas: 5
  - Target CPU: 70%
- Metrics server collecting pod metrics
- `kubectl get hpa` shows current/target values
- Load test triggers scale-up (e.g., ApacheBench with 100 concurrent requests)
- Scale-down delay: 5 minutes after load decreases

**Dependencies:** REQ-007 (metrics-server addon), REQ-012  
**Priority:** P0 (Must Have)

---

#### REQ-014: Secret Management (MUST HAVE)
**Description:** Sensitive data must be stored in Kubernetes Secrets  
**Rationale:** Prevent credential exposure in Git and container images  
**Acceptance Criteria:**
- Secret created: `todo-secrets`
- Secret data (base64 encoded):
  - POSTGRES_PASSWORD
  - JWT_SECRET_KEY
  - OPENAI_API_KEY (for Phase III chatbot)
- Secrets mounted as environment variables in pods
- Secrets not committed to Git (.gitignore includes secrets.yaml)
- Deployment references secrets: `secretRef: todo-secrets`
- Secret rotation supported (update + rollout restart)

**Dependencies:** None  
**Priority:** P0 (Must Have)

---

#### REQ-015: ConfigMap Management (MUST HAVE)
**Description:** Non-sensitive configuration must be stored in ConfigMaps  
**Rationale:** Separate configuration from application code  
**Acceptance Criteria:**
- ConfigMap created: `todo-config`
- ConfigMap data:
  - DATABASE_URL (without password)
  - BACKEND_URL
  - FRONTEND_URL
  - LOG_LEVEL (info/debug)
- ConfigMaps mounted as environment variables
- ConfigMaps version-controlled in Git
- ConfigMap changes trigger pod restarts (with annotation checksum)

**Dependencies:** None  
**Priority:** P0 (Must Have)

---

#### REQ-016: Persistent Storage (MUST HAVE)
**Description:** PostgreSQL data must persist across pod restarts  
**Rationale:** Prevent data loss during deployments or node failures  
**Acceptance Criteria:**
- PersistentVolumeClaim created: `postgres-pvc`
- Storage class: standard (Minikube default)
- Access mode: ReadWriteOnce
- Storage size: 10Gi
- Volume mounted at /var/lib/postgresql/data
- Data survives `kubectl delete pod postgres-...`
- Backup/restore strategy documented

**Dependencies:** REQ-007  
**Priority:** P0 (Must Have)

---

### 3.4 AI DevOps Requirements

#### REQ-017: kubectl-ai Integration (SHOULD HAVE)
**Description:** Use kubectl-ai for intelligent Kubernetes operations  
**Rationale:** Accelerate troubleshooting and resource management  
**Acceptance Criteria:**
- kubectl-ai installed and configured with OpenAI API key
- Documentation includes example commands:
  - `kubectl-ai "deploy the todo frontend with 2 replicas"`
  - `kubectl-ai "scale the backend to handle more load"`
  - `kubectl-ai "check why the pods are failing"`
  - `kubectl-ai "add health checks to deployment"`
  - `kubectl-ai "create ingress for todo.local"`
- Successful execution of at least 3 example commands
- Command outputs reviewed and validated

**Dependencies:** OpenAI API key  
**Priority:** P1 (Should Have)

---

#### REQ-018: Kagent Integration (SHOULD HAVE)
**Description:** Use Kagent for advanced cluster analysis and optimization  
**Rationale:** Leverage AI for cluster health monitoring and resource optimization  
**Acceptance Criteria:**
- Kagent installed and configured
- Documentation includes example commands:
  - `kagent "analyze the cluster health"`
  - `kagent "optimize resource allocation"`
  - `kagent "diagnose pod failures"`
  - `kagent "recommend cost savings"`
- Successful cluster health analysis
- Resource optimization recommendations documented
- Kagent vs kubectl-ai comparison in README (when to use each)

**Dependencies:** Kagent installation  
**Priority:** P1 (Should Have)

---

## 4. Non-Functional Requirements

### 4.1 Performance

#### NFR-001: Container Build Performance
- Frontend image build time: < 5 minutes
- Backend image build time: < 3 minutes
- Multi-stage builds with layer caching
- Docker BuildKit enabled for parallel builds

#### NFR-002: Deployment Performance
- Helm install/upgrade: < 2 minutes
- Pod startup time: < 30 seconds (frontend), < 45 seconds (backend)
- Rolling update time: < 3 minutes for complete rollout
- Image pull time: < 1 minute (with local registry)

#### NFR-003: Application Performance
- Frontend response time: < 100ms (p95)
- Backend API response time: < 200ms (p95)
- Database query time: < 50ms (p95)
- Performance identical to Phase III (no degradation)

---

### 4.2 Reliability

#### NFR-004: High Availability
- Minimum 2 replicas for frontend and backend (no single point of failure)
- Pod anti-affinity to spread replicas across nodes (if multi-node cluster)
- Graceful shutdown with preStop hooks (30s drain period)
- Circuit breakers for database connections (retry 3 times, then fail fast)

#### NFR-005: Fault Tolerance
- Pod restarts automatically on liveness probe failures
- Database connection retries on temporary failures
- Persistent data survives pod/node failures
- No data loss during rolling updates

#### NFR-006: Monitoring
- `kubectl get pods` shows healthy state (Running, Ready 1/1)
- `kubectl logs` accessible for all pods
- `kubectl top` shows resource usage
- Ingress controller logs show request routing

---

### 4.3 Security

#### NFR-007: Container Security
- Non-root users in all containers (UID > 1000)
- Read-only root filesystem where possible
- No privileged containers
- Security context with runAsNonRoot: true
- Minimal base images (Alpine) to reduce attack surface

#### NFR-008: Secret Security
- Secrets never committed to Git
- Secrets mounted as environment variables (not volumes where possible)
- Base64 encoding for secret values
- RBAC restricts secret access to necessary service accounts
- Secret rotation supported without downtime

#### NFR-009: Network Security
- Network policies restrict inter-pod communication (optional for Minikube)
- Ingress TLS support (optional for local, required for production)
- Backend not directly exposed (only via ingress)
- Database not exposed outside cluster

---

### 4.4 Maintainability

#### NFR-010: Documentation
- Complete README with:
  - Prerequisites (Docker Desktop, Minikube, kubectl, Helm)
  - Installation steps (step-by-step)
  - Gordon, kubectl-ai, Kagent usage examples
  - Troubleshooting guide (common issues + solutions)
  - Deployment runbook
- Inline comments in Dockerfiles
- Helm chart documentation in Chart.yaml and values.yaml

#### NFR-011: Reproducibility
- Pinned versions for all dependencies (Docker base images, Helm chart version)
- Deterministic builds (same inputs → same outputs)
- Setup scripts automate cluster configuration
- No manual steps required after initial Minikube install

#### NFR-012: Testability
- Health check endpoints for automated testing
- Smoke tests after deployment (curl /health, curl /api/health)
- Load testing guide with ApacheBench or k6
- Rollback procedure documented (`helm rollback todo`)

---

### 4.5 Scalability

#### NFR-013: Horizontal Scalability
- Frontend and backend scale independently
- HPA automatically adjusts replicas based on CPU
- Database connection pooling supports multiple backend replicas
- Session state stored in database (not in-memory)

#### NFR-014: Resource Efficiency
- Resource requests match actual usage (no over-provisioning)
- Unused resources can be reclaimed by other pods
- Cluster utilization > 60% (efficient packing)

---

## 5. Constraints

### 5.1 Technical Constraints

1. **Docker Desktop Version:** 4.53+ required for Gordon AI (optional)
2. **Kubernetes Version:** 1.31+ (Minikube default)
3. **Helm Version:** 3.x required (Helm 2 not supported)
4. **kubectl-ai:** Requires OpenAI API key (or compatible API)
5. **Kagent:** Installation and configuration may vary by platform
6. **Minikube Resources:** Minimum 4 CPUs, 8GB RAM on host machine
7. **Platform:** Development on Windows (PowerShell) or macOS/Linux (Bash)

### 5.2 Architectural Constraints

1. **Stateless Services:** All application state in database (no local file storage)
2. **12-Factor App:** Strict adherence to 12-factor principles
3. **Immutable Infrastructure:** No manual changes to running pods
4. **Declarative Configuration:** All resources defined in Git (no imperative kubectl)
5. **Container Security:** Non-root users, minimal attack surface

### 5.3 Operational Constraints

1. **Local Development Only:** Minikube not suitable for production
2. **Single Node:** Minikube runs single-node cluster (no multi-node HA)
3. **LoadBalancer:** Requires `minikube tunnel` running in separate terminal
4. **DNS:** /etc/hosts entry required for custom domain (todo.local)
5. **Storage:** Persistent volumes limited to local disk (no cloud storage)

---

## 6. Out of Scope (Phase V)

The following features are explicitly **NOT** included in Phase IV:

1. **Production Cloud Deployment:** AWS EKS, Azure AKS, Google GKE (deferred to Phase V)
2. **Dapr Integration:** Event-driven architecture, pub/sub, state management
3. **Kafka Integration:** Event streaming, asynchronous processing
4. **Multi-Cluster:** Federation, global load balancing
5. **Service Mesh:** Istio, Linkerd for advanced traffic management
6. **Observability:** Prometheus, Grafana, Jaeger, ELK stack
7. **GitOps:** ArgoCD, FluxCD for continuous deployment
8. **Backup/Restore:** Automated database backups to cloud storage
9. **Disaster Recovery:** Multi-region failover, cross-cluster replication
10. **Advanced Security:** Pod Security Policies, OPA, Falco

---

## 7. Acceptance Criteria (Phase IV Complete)

### 7.1 Deployment Criteria

- [ ] Minikube cluster running and accessible
- [ ] All pods in Running state (no CrashLoopBackOff)
- [ ] Application accessible at http://todo.local
- [ ] Health checks passing for all services
- [ ] Persistent data survives pod restarts
- [ ] Rolling updates work without downtime
- [ ] HPA scales pods under load

### 7.2 Functional Criteria

- [ ] User can register, login, and manage tasks (Phase III features intact)
- [ ] AI chatbot functionality works in Kubernetes
- [ ] Database queries execute successfully
- [ ] Frontend and backend communicate correctly
- [ ] Ingress routes traffic to correct services

### 7.3 Quality Criteria

- [ ] Docker images optimized (meet size requirements)
- [ ] Resource requests/limits defined for all containers
- [ ] Secrets managed securely (not in Git)
- [ ] Helm charts lint without errors
- [ ] Health checks configured correctly
- [ ] No security vulnerabilities in images (Trivy scan)

### 7.4 Documentation Criteria

- [ ] README includes all prerequisites
- [ ] Step-by-step deployment guide exists
- [ ] Gordon, kubectl-ai, Kagent examples documented
- [ ] Troubleshooting guide covers common issues
- [ ] Demo video (90 seconds) shows deployment and key features
- [ ] Architecture diagram shows Kubernetes components

### 7.5 AI DevOps Criteria

- [ ] Gordon successfully analyzes Dockerfiles
- [ ] kubectl-ai executes at least 3 example commands
- [ ] Kagent analyzes cluster health
- [ ] All AI tool outputs reviewed and documented

---

## 8. Dependencies and Assumptions

### 8.1 Dependencies

1. **Phase III Complete:** All Phase III features must be working
2. **Docker Desktop Installed:** Version 4.53+ with Gordon enabled (optional)
3. **Minikube Installed:** Latest version (1.33+)
4. **kubectl Installed:** Version matching Kubernetes cluster
5. **Helm Installed:** Version 3.x
6. **kubectl-ai Installed:** Via brew/go/manual install (optional)
7. **Kagent Installed:** Per Kagent documentation (optional)
8. **Sufficient Host Resources:** 4+ CPUs, 8+ GB RAM available

### 8.2 Assumptions

1. **Local Development:** Deployment targets local Minikube cluster (not cloud)
2. **Single User:** No multi-tenancy or production-scale load testing
3. **Stable Network:** Internet connectivity for image pulls and API calls
4. **Admin Access:** User has permissions to install software and modify /etc/hosts
5. **No Firewall Restrictions:** Ports 80, 443, 8000, 3000 accessible
6. **Phase III Database:** Schema extensions from Phase III compatible with Kubernetes deployment

---

## 9. Glossary

- **Minikube:** Local Kubernetes cluster for development and testing
- **Helm:** Package manager for Kubernetes (like npm for Node.js)
- **Helm Chart:** Bundle of Kubernetes manifests with templating support
- **kubectl:** Command-line tool for interacting with Kubernetes clusters
- **kubectl-ai:** AI-powered kubectl assistant for intelligent operations
- **Kagent:** Advanced AI agent for Kubernetes cluster analysis and optimization
- **Gordon:** Docker AI agent (Docker Desktop 4.53+ Beta feature)
- **Ingress:** Kubernetes resource for HTTP/HTTPS routing to services
- **HPA:** Horizontal Pod Autoscaler (scales pods based on metrics)
- **Liveness Probe:** Health check to detect and restart unhealthy pods
- **Readiness Probe:** Health check to determine if pod can receive traffic
- **PVC:** PersistentVolumeClaim (request for storage)
- **ConfigMap:** Kubernetes object for non-sensitive configuration
- **Secret:** Kubernetes object for sensitive data (passwords, API keys)
- **RollingUpdate:** Deployment strategy for zero-downtime updates
- **12-Factor App:** Methodology for building cloud-native applications

---

## 10. References

1. **Hackathon II Document:** https://docs.google.com/document/d/1KHxeDNnqG9uew-rEabQc5H8u3VmEN3OaJ_A1ZVVr9vY
2. **Reference Repository:** https://github.com/Ameen-Alam/Full-Stack-Web-Application
3. **Phase I Repository:** https://github.com/Ahmed-KHI/panaversity-spec-driven-todo
4. **Kubernetes Documentation:** https://kubernetes.io/docs/
5. **Helm Documentation:** https://helm.sh/docs/
6. **Minikube Documentation:** https://minikube.sigs.k8s.io/docs/
7. **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/
8. **kubectl-ai GitHub:** https://github.com/sozercan/kubectl-ai
9. **Kagent Documentation:** https://www.k8sgpt.ai/
10. **12-Factor App:** https://12factor.net/

---

## 11. Approval and Sign-Off

**Specification Approved By:**
- [ ] Product Owner: ___________________ Date: ___________
- [ ] Technical Lead: ___________________ Date: ___________
- [ ] DevOps Lead: ___________________ Date: ___________

**Version History:**
- v1.0 - January 18, 2026 - Initial Phase IV specification created

---

**END OF SPECIFICATION**

---

## Appendix A: AI DevOps Tools Comparison

| Feature | Gordon (Docker AI) | kubectl-ai | Kagent |
|---------|-------------------|------------|--------|
| **Primary Use** | Docker operations, Dockerfile optimization | Kubernetes resource management | Cluster analysis, optimization |
| **Natural Language** | ✅ Full support | ✅ Full support | ✅ Full support |
| **Docker Focus** | ✅ Expert-level | ❌ No Docker support | ❌ No Docker support |
| **Kubernetes Focus** | ❌ No K8s support | ✅ Expert-level | ✅ Expert-level |
| **Troubleshooting** | ✅ Container issues | ✅ Resource issues | ✅ Cluster-wide issues |
| **Optimization** | ✅ Image size, security | ⚠️ Limited | ✅ Resource allocation |
| **Cost Analysis** | ❌ No | ⚠️ Limited | ✅ Advanced |
| **Learning Curve** | Low (built-in) | Low (simple CLI) | Medium (requires setup) |
| **Installation** | Docker Desktop 4.53+ | brew/go install | Manual install |
| **API Key Required** | ❌ No | ✅ Yes (OpenAI) | ⚠️ Optional |

**Recommendation:**
1. **Use Gordon** for Dockerfile analysis and optimization
2. **Start with kubectl-ai** for day-to-day Kubernetes operations
3. **Layer in Kagent** for advanced cluster health and cost optimization
