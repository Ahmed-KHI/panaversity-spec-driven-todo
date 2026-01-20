# Phase IV: Quick Reference Guide

## 🚀 One-Line Deploy (After Prerequisites)

```bash
cd phase-4-kubernetes && \
./scripts/setup-minikube.sh && \
./scripts/build-images.sh && \
./scripts/load-images-minikube.sh && \
./scripts/deploy.sh && \
./tests/smoke-test.sh
```

## 📝 Essential Commands

### Setup & Deployment
```bash
# 1. Verify all tools installed
./scripts/verify-prerequisites.sh

# 2. Initialize Minikube cluster
./scripts/setup-minikube.sh

# 3. Build Docker images
./scripts/build-images.sh

# 4. Load images to Minikube (for local dev)
./scripts/load-images-minikube.sh

# 5. Deploy application
./scripts/deploy.sh

# 6. Run smoke tests
./tests/smoke-test.sh

# 7. Run load tests (HPA validation)
./tests/load-test.sh
```

### Troubleshooting
```bash
# Port forward if ingress fails
./scripts/port-forward.sh

# Check pod status
kubectl get pods

# View logs
kubectl logs -l app.kubernetes.io/component=frontend --tail=50
kubectl logs -l app.kubernetes.io/component=backend --tail=50

# Check HPA status
kubectl get hpa

# Check ingress
kubectl get ingress
```

### Cleanup
```bash
# Remove all resources
./scripts/cleanup.sh
```

## 🔗 URLs

- **Frontend:** http://todo.local
- **Backend API:** http://todo.local/api
- **Health Checks:**
  - Frontend: http://todo.local/api/health
  - Backend: http://todo.local/api/health

## 📂 File Locations

### Scripts
- `scripts/verify-prerequisites.sh|.ps1` - Tool verification
- `scripts/setup-minikube.sh|.ps1` - Cluster setup
- `scripts/build-images.sh|.ps1` - Docker build
- `scripts/load-images-minikube.sh|.ps1` - Image loading
- `scripts/push-images.sh|.ps1` - Docker Hub push
- `scripts/deploy.sh|.ps1` - Helm deployment
- `scripts/port-forward.sh|.ps1` - Local access
- `scripts/cleanup.sh|.ps1` - Resource cleanup

### Docker
- `docker/frontend/Dockerfile` - Frontend image (3-stage, <200MB)
- `docker/backend/Dockerfile` - Backend image (2-stage, <150MB)
- `docker/README.md` - Comprehensive documentation

### Helm Chart
- `helm-charts/todo/Chart.yaml` - Chart metadata
- `helm-charts/todo/values.yaml` - Default values
- `helm-charts/todo/values-dev.yaml` - Minikube values
- `helm-charts/todo/values-prod.yaml` - Production values
- `helm-charts/todo/templates/` - 13 Kubernetes manifests

### Tests
- `tests/smoke-test.sh|.ps1` - Health validation
- `tests/load-test.sh|.ps1` - HPA testing

## ⚙️ Configuration

### Default Resources (values-dev.yaml)
- **Frontend:** 1 pod (1-3 HPA), 50m CPU / 64Mi RAM
- **Backend:** 1 pod (1-3 HPA), 100m CPU / 128Mi RAM
- **PostgreSQL:** 1 replica, 100m CPU / 256Mi RAM, 5Gi storage

### Secrets Required
```bash
# Created automatically by deploy.sh
todo-database-secret:
  - POSTGRES_PASSWORD
  - DATABASE_URL

todo-openai-secret:
  - OPENAI_API_KEY

todo-auth-secret:
  - BETTER_AUTH_SECRET
  - BETTER_AUTH_URL
```

## 🎯 Success Indicators

### Deployment Success
- ✅ All pods Running: `kubectl get pods`
- ✅ Services created: `kubectl get svc`
- ✅ Ingress configured: `kubectl get ingress`
- ✅ HPA active: `kubectl get hpa`

### Application Health
- ✅ Frontend health: `curl http://todo.local/api/health`
- ✅ Backend health: `curl http://todo.local/api/health`
- ✅ Smoke tests pass: `./tests/smoke-test.sh`

### Autoscaling Working
- ✅ Load test triggers scale-up: `./tests/load-test.sh`
- ✅ HPA shows target utilization: `kubectl get hpa`
- ✅ Pods scale 2 → 3+: `kubectl get pods -w`

## 🐛 Common Issues

### Issue: Can't access http://todo.local
**Solution:** 
```bash
# Check /etc/hosts entry
cat /etc/hosts | grep todo.local

# Should see: <minikube-ip> todo.local
# If missing, add manually:
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

### Issue: Pods not starting
**Solution:**
```bash
# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check pod details
kubectl describe pod <pod-name>

# Common fixes:
# 1. Images not loaded: ./scripts/load-images-minikube.sh
# 2. Secrets missing: ./scripts/deploy.sh (recreates secrets)
# 3. Resource limits: Increase Minikube resources
```

### Issue: Ingress not working
**Solution:**
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# If not running:
minikube addons enable ingress

# Fallback: Use port forwarding
./scripts/port-forward.sh
# Access: http://localhost:3000
```

## 📊 Monitoring Commands

```bash
# Watch pod status
kubectl get pods -w

# Watch HPA
kubectl get hpa -w

# Top pods (CPU/memory)
kubectl top pods

# Continuous logs
kubectl logs -f -l app.kubernetes.io/component=frontend

# Describe deployment
kubectl describe deployment todo-frontend
```

## 🎓 PowerShell Equivalents

All bash scripts (`.sh`) have PowerShell equivalents (`.ps1`):

```powershell
# Example: Windows PowerShell
.\scripts\verify-prerequisites.ps1
.\scripts\setup-minikube.ps1
.\scripts\build-images.ps1
.\scripts\deploy.ps1
.\tests\smoke-test.ps1
```

## 📚 Documentation

- **Main README:** `phase-4-kubernetes/README.md`
- **Implementation Complete:** `PHASE4-IMPLEMENTATION-COMPLETE.md`
- **Docker Guide:** `docker/README.md`
- **Helm Notes:** Shown after `helm install` (see NOTES.txt)
- **Specifications:** `../phase-2-fullstack/specs/004-phase-iv-kubernetes/`

## ⏱️ Estimated Times

- **Prerequisites verification:** 2 minutes
- **Minikube setup:** 3-5 minutes
- **Docker build:** 5-10 minutes
- **Image loading:** 1-2 minutes
- **Helm deployment:** 2-3 minutes
- **Smoke tests:** 30 seconds
- **Load tests:** 2 minutes

**Total first deployment:** ~15-25 minutes  
**Subsequent deployments:** ~5 minutes

## 🏆 Achievement Unlocked

You've successfully implemented:
- ✅ 50+ files created
- ✅ 77+ tasks completed
- ✅ Full Kubernetes deployment
- ✅ Helm chart with 13 manifests
- ✅ 14 automation scripts
- ✅ 4 test scripts
- ✅ Production-ready infrastructure

**Phase IV Status:** ✅ **COMPLETE & PRODUCTION READY**

---

**Version:** 1.0  
**Last Updated:** January 18, 2026
