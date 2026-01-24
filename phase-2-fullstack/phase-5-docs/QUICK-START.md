# Phase V - Quick Start Guide

**Version:** 5.0.0  
**Last Updated:** January 23, 2026  
**Deployment Time:** ~15 minutes

---

## 🚀 Quick Deployment (3 Options)

### Option 1: Automated Script (Recommended) ⭐

**For Linux/Mac:**
```bash
cd phase-2-fullstack/phase-5-scripts
chmod +x deploy-phase5-complete.sh
./deploy-phase5-complete.sh
```

**For Windows (PowerShell):**
```powershell
cd phase-2-fullstack\phase-5-scripts
.\deploy-phase5-complete.ps1
```

**Time:** ~10 minutes  
**Difficulty:** Easy  
**What it does:** Checks prerequisites, starts Minikube, installs everything, builds images, deploys app

---

### Option 2: Manual Step-by-Step

**Prerequisites:**
```bash
# Verify installations
minikube version  # v1.30+
kubectl version   # v1.28+
dapr version      # v1.12+
helm version      # v3.12+
docker version    # 24.0+
```

**Step 1: Start Minikube**
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress metrics-server
```

**Step 2: Initialize Dapr**
```bash
dapr init -k --wait --timeout 300
```

**Step 3: Install Strimzi Kafka**
```bash
kubectl create namespace kafka
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

**Step 4: Create Namespaces**
```bash
cd phase-5-minikube
kubectl apply -f namespace.yaml
```

**Step 5: Deploy Kafka**
```bash
kubectl apply -f kafka-cluster-v1.yaml
# Wait 2-3 minutes for Kafka to be ready
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka
```

**Step 6: Deploy PostgreSQL**
```bash
kubectl apply -f postgres-deployment.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s
```

**Step 7: Apply Secrets**
```bash
# Edit secrets.yaml with your actual values first!
kubectl apply -f secrets.yaml
```

**Step 8: Deploy Dapr Components**
```bash
kubectl apply -f kafka-pubsub.yaml
kubectl apply -f statestore.yaml
kubectl apply -f jobs-api.yaml
```

**Step 9: Build Images**
```bash
# Point Docker to Minikube
eval $(minikube docker-env)

# Build backend
cd ../../phase-2-fullstack/backend
docker build -t todo-backend:5.0.0 .

# Build frontend
cd ../frontend
docker build -t todo-frontend:5.0.0 .
```

**Step 10: Deploy Application**
```bash
cd ../../phase-5-minikube
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=180s
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=180s
```

**Time:** ~15 minutes  
**Difficulty:** Medium  
**Advantage:** Full control over each step

---

### Option 3: Using Helm Charts

```bash
# Prerequisites: Steps 1-8 from Option 2

# Deploy with Helm
cd phase-2-fullstack/phase-5-helm
helm upgrade --install todo-app ./todo-app \
  --namespace todo-app \
  --create-namespace \
  --set backend.image.tag=5.0.0 \
  --set frontend.image.tag=5.0.0 \
  --wait \
  --timeout=5m
```

**Time:** ~12 minutes  
**Difficulty:** Medium  
**Advantage:** Easier to manage configuration

---

## ✅ Verification Steps

### 1. Check All Pods are Running

```bash
kubectl get pods -n todo-app
kubectl get pods -n kafka
kubectl get pods -n dapr-system
```

**Expected output:**
```
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-xxx                2/2     Running   0          2m
todo-frontend-xxx               2/2     Running   0          2m
postgres-xxx                    1/1     Running   0          5m

NAME                                          READY   STATUS    RESTARTS   AGE
todo-kafka-kafka-0                            1/1     Running   0          5m
todo-kafka-entity-operator-xxx                2/2     Running   0          4m
strimzi-cluster-operator-xxx                  1/1     Running   0          6m
```

---

### 2. Check Services

```bash
kubectl get svc -n todo-app
```

**Expected output:**
```
NAME            TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
todo-backend    ClusterIP      10.96.xxx.xxx   <none>        8000/TCP
todo-frontend   LoadBalancer   10.96.xxx.xxx   <pending>     3000:xxxxx/TCP
postgres        ClusterIP      10.96.xxx.xxx   <none>        5432/TCP
```

---

### 3. Test Backend Health

```bash
kubectl port-forward -n todo-app svc/todo-backend 8000:8000 &
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

### 4. Access Frontend

```bash
minikube service todo-frontend -n todo-app
```

This will open the Todo app in your browser automatically.

---

## 🌐 Access Points

### Frontend (Web UI)
```bash
# Option 1: Minikube service (automatic browser open)
minikube service todo-frontend -n todo-app

# Option 2: Port forward
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000
# Then visit: http://localhost:3000

# Option 3: Get NodePort URL
minikube service todo-frontend -n todo-app --url
```

---

### Backend API (Swagger Docs)
```bash
kubectl port-forward -n todo-app svc/todo-backend 8000:8000
# Visit: http://localhost:8000/docs
```

---

### Dapr Dashboard
```bash
dapr dashboard -k -p 9999
# Visit: http://localhost:9999
```

---

### Kafka Topics
```bash
kubectl get kafkatopic -n kafka
```

---

## 🔍 Monitoring & Logs

### View Backend Logs
```bash
kubectl logs -n todo-app -l app=todo-backend -f
```

### View Frontend Logs
```bash
kubectl logs -n todo-app -l app=todo-frontend -f
```

### View Dapr Sidecar Logs
```bash
POD=$(kubectl get pod -n todo-app -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n todo-app $POD -c daprd -f
```

### View Kafka Logs
```bash
kubectl logs -n kafka -l app.kubernetes.io/name=kafka -f
```

### View All Events
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

---

## 🧪 Testing the Application

### 1. Test User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@1234",
    "name": "Test User"
  }'
```

---

### 2. Test Task Creation

```bash
# Get auth token first (from registration or login)
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing Phase V deployment",
    "priority": "high",
    "tags": ["testing"]
  }'
```

---

### 3. Test AI Chatbot

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all my tasks"
  }'
```

---

### 4. Verify Kafka Events

```bash
# Check Kafka topics
kubectl get kafkatopic -n kafka

# View events in backend logs (should show Kafka publish messages)
kubectl logs -n todo-app -l app=todo-backend | grep -i "kafka"
```

---

## 🔧 Configuration Updates

### Update Secrets
```bash
# Edit secrets
kubectl edit secret postgres-secret -n todo-app

# Or delete and reapply
kubectl delete secret postgres-secret -n todo-app
kubectl apply -f phase-5-minikube/secrets.yaml
kubectl rollout restart deployment -n todo-app
```

---

### Scale Services
```bash
# Scale backend to 3 replicas
kubectl scale deployment todo-backend -n todo-app --replicas=3

# Scale frontend to 2 replicas
kubectl scale deployment todo-frontend -n todo-app --replicas=2

# Verify
kubectl get pods -n todo-app
```

---

### Update Images
```bash
# Rebuild images
eval $(minikube docker-env)
docker build -t todo-backend:5.0.1 phase-2-fullstack/backend

# Update deployment
kubectl set image deployment/todo-backend \
  backend=todo-backend:5.0.1 \
  -n todo-app

# Or use Helm
helm upgrade todo-app phase-5-helm/todo-app \
  --set backend.image.tag=5.0.1 \
  -n todo-app
```

---

## 🧹 Cleanup

### Delete Application Only
```bash
kubectl delete namespace todo-app
```

---

### Delete Everything (Including Kafka)
```bash
kubectl delete namespace todo-app kafka
dapr uninstall -k
```

---

### Stop Minikube
```bash
minikube stop
```

---

### Complete Cleanup (Delete Minikube)
```bash
minikube delete
```

---

## ⚠️ Common Issues & Quick Fixes

### Issue: Pod stuck in "ImagePullBackOff"
**Fix:**
```bash
# Rebuild images in Minikube's Docker
eval $(minikube docker-env)
docker build -t todo-backend:5.0.0 phase-2-fullstack/backend
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

### Issue: Backend CrashLoopBackOff
**Fix:**
```bash
# Check logs
kubectl logs -n todo-app -l app=todo-backend --tail=50

# Common cause: PostgreSQL not ready
kubectl get pods -n todo-app -l app=postgres

# Wait for PostgreSQL and restart backend
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

### Issue: "kafka-python not found"
**Fix:** Already fixed in `requirements.txt`. Rebuild image:
```bash
eval $(minikube docker-env)
cd phase-2-fullstack/backend
docker build --no-cache -t todo-backend:5.0.0 .
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

### Issue: Kafka not ready
**Fix:**
```bash
# Wait longer (Kafka takes 2-3 minutes)
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka

# Check status
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

---

### Issue: Dapr components not found
**Fix:**
```bash
# Reapply Dapr components
cd phase-5-minikube
kubectl apply -f kafka-pubsub.yaml
kubectl apply -f statestore.yaml

# Verify
kubectl get components -n todo-app
```

---

## 📊 Resource Requirements

### Minimum Requirements
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Disk:** 20 GB

### Recommended for Production
- **CPU:** 8 cores
- **RAM:** 16 GB
- **Disk:** 50 GB

---

## 🎯 Next Steps

1. ✅ **Deploy Locally** - Use this guide to deploy on Minikube
2. ✅ **Test Features** - Verify all Phase V features work
3. ✅ **Setup CI/CD** - Configure GitHub Actions (`.github/workflows/phase5-deploy.yml`)
4. ✅ **Deploy to Cloud** - Use Oracle Cloud (OKE), Azure (AKS), or Google Cloud (GKE)
5. ✅ **Monitor & Scale** - Use Dapr dashboard and kubectl

---

## 📚 Additional Documentation

- **Troubleshooting:** `phase-5-docs/TROUBLESHOOTING.md`
- **Cloud Deployment:** `phase-5-docs/CLOUD-DEPLOYMENT.md`
- **Dapr Guide:** `phase-5-dapr/README.md`
- **Submission Guide:** `PHASE5-SUBMISSION-GUIDE.md`

---

## ✅ All Fixed Issues (Version 5.0.0)

- ✅ Missing `kafka-python` and `httpx` dependencies
- ✅ Dockerfile port mismatch (7860 → 8000)
- ✅ Missing namespace YAML
- ✅ Kafka version incompatibility (4.1.1 → 3.7.0)
- ✅ ImagePullPolicy too restrictive (Never → IfNotPresent)
- ✅ Missing Dapr Jobs API component
- ✅ Comprehensive deployment scripts
- ✅ CI/CD GitHub Actions workflow
- ✅ Complete troubleshooting guide

**Status:** Production Ready ✓

---

**Need Help?**  
Check `TROUBLESHOOTING.md` for detailed solutions to all known issues.
