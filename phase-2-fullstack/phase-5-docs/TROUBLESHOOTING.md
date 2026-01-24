# Phase V - Troubleshooting Guide

**Version:** 5.0.0  
**Last Updated:** January 23, 2026  
**Status:** Production Ready

---

## Table of Contents
1. [Common Issues & Solutions](#common-issues--solutions)
2. [Prerequisites Issues](#prerequisites-issues)
3. [Minikube Issues](#minikube-issues)
4. [Kafka Issues](#kafka-issues)
5. [Dapr Issues](#dapr-issues)
6. [Application Issues](#application-issues)
7. [Image Build Issues](#image-build-issues)
8. [Networking Issues](#networking-issues)
9. [Quick Fixes](#quick-fixes)
10. [Health Check Commands](#health-check-commands)

---

## Common Issues & Solutions

### Issue 1: `kafka-python` or `httpx` not found

**Error:**
```
ModuleNotFoundError: No module named 'kafka'
ModuleNotFoundError: No module named 'httpx'
```

**Solution:**
```bash
# Update requirements.txt (already fixed in this version)
cd phase-2-fullstack/backend
pip install kafka-python httpx

# Or rebuild Docker image
docker build -t todo-backend:5.0.0 .
```

**Root Cause:** Missing dependencies in `requirements.txt` (NOW FIXED)

---

### Issue 2: Port 7860 vs 8000 mismatch

**Error:**
```
Connection refused on localhost:8000
Backend running on wrong port
```

**Solution:**
The Dockerfile has been updated to use port 8000 (Kubernetes standard) instead of 7860 (HuggingFace Spaces).

Verify:
```bash
kubectl logs -n todo-app -l app=todo-backend | grep "Uvicorn running"
# Should show: Application startup complete on http://0.0.0.0:8000
```

**Root Cause:** Dockerfile used HuggingFace port 7860 (NOW FIXED)

---

### Issue 3: Namespace not found

**Error:**
```
Error from server (NotFound): namespaces "todo-app" not found
Error from server (NotFound): namespaces "kafka" not found
```

**Solution:**
```bash
# Apply namespace configuration (now included)
cd phase-5-minikube
kubectl apply -f namespace.yaml

# Verify
kubectl get namespaces | grep -E "todo-app|kafka"
```

**Root Cause:** Missing `namespace.yaml` (NOW FIXED)

---

### Issue 4: Kafka version incompatibility

**Error:**
```
Kafka version 4.1.1 not supported by Strimzi
Unsupported metadata version
```

**Solution:**
Kafka version downgraded to 3.7.0 (stable, well-supported by Strimzi).

```bash
# Verify Kafka version
kubectl get kafka todo-kafka -n kafka -o yaml | grep version
# Should show: version: 3.7.0
```

**Root Cause:** Kafka 4.1.1 too new for Strimzi (NOW FIXED)

---

### Issue 5: ImagePullPolicy: Never fails on cloud

**Error:**
```
Failed to pull image "todo-backend:5.0.0": ErrImageNeverPull
```

**Solution:**
ImagePullPolicy changed from `Never` to `IfNotPresent`.

For Minikube (local images):
```bash
# Build images in Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-backend:5.0.0 phase-2-fullstack/backend
docker build -t todo-frontend:5.0.0 phase-2-fullstack/frontend
```

For Cloud (registry images):
```bash
# Images will be pulled from ghcr.io automatically
# Or push to your registry:
docker tag todo-backend:5.0.0 ghcr.io/yourusername/todo-backend:5.0.0
docker push ghcr.io/yourusername/todo-backend:5.0.0
```

**Root Cause:** `imagePullPolicy: Never` too restrictive (NOW FIXED)

---

### Issue 6: Dapr Jobs API component missing

**Error:**
```
No Jobs API component configured
Reminders not scheduling
```

**Solution:**
```bash
# Apply Jobs API component (now included)
cd phase-5-minikube
kubectl apply -f jobs-api.yaml

# Verify
kubectl get components -n todo-app
```

**Root Cause:** Missing `jobs-api.yaml` (NOW FIXED)

---

## Prerequisites Issues

### Minikube not starting

**Error:**
```
Exiting due to PROVIDER_DOCKER_NOT_RUNNING
```

**Solution:**
```bash
# Check Docker is running
docker ps

# Start Docker Desktop (Windows/Mac)
# Or start Docker service (Linux)
sudo systemctl start docker

# Then start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker
```

---

### kubectl not connecting

**Error:**
```
The connection to the server localhost:8080 was refused
```

**Solution:**
```bash
# Point kubectl to Minikube
kubectl config use-context minikube

# Or reset context
minikube update-context

# Verify
kubectl cluster-info
```

---

### Dapr not initializing

**Error:**
```
Error: Dapr control plane not found
```

**Solution:**
```bash
# Uninstall old Dapr
dapr uninstall -k

# Reinstall
dapr init -k --wait --timeout 300

# Verify
dapr status -k
kubectl get pods -n dapr-system
```

---

## Minikube Issues

### Insufficient resources

**Error:**
```
Insufficient CPU/memory for cluster
```

**Solution:**
```bash
# Delete and recreate with more resources
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker

# Or adjust existing cluster
minikube stop
minikube config set cpus 4
minikube config set memory 8192
minikube start
```

---

### Addons not enabling

**Error:**
```
Addon metrics-server not found
```

**Solution:**
```bash
# List available addons
minikube addons list

# Enable required addons
minikube addons enable metrics-server
minikube addons enable ingress

# Verify
kubectl get pods -n kube-system | grep -E "metrics|ingress"
```

---

## Kafka Issues

### Strimzi operator not installing

**Error:**
```
Unable to install Strimzi operator
```

**Solution:**
```bash
# Create namespace first
kubectl create namespace kafka

# Install Strimzi
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
kubectl wait --for=condition=ready pod \
  -l name=strimzi-cluster-operator \
  -n kafka \
  --timeout=300s

# Check logs if failing
kubectl logs -n kafka -l name=strimzi-cluster-operator
```

---

### Kafka cluster not ready

**Error:**
```
Kafka cluster stuck in "NotReady" state
```

**Solution:**
```bash
# Check Kafka status
kubectl get kafka todo-kafka -n kafka -o yaml

# Check pod status
kubectl get pods -n kafka

# Check logs
kubectl logs -n kafka -l app.kubernetes.io/name=kafka

# If stuck, delete and recreate
kubectl delete kafka todo-kafka -n kafka
kubectl apply -f phase-5-minikube/kafka-cluster-v1.yaml
```

---

### Topics not creating

**Error:**
```
KafkaTopic "task-events" not found
```

**Solution:**
```bash
# Topics are created automatically by kafka-cluster-v1.yaml
# Verify they exist
kubectl get kafkatopic -n kafka

# If missing, apply Kafka cluster config again
kubectl apply -f phase-5-minikube/kafka-cluster-v1.yaml

# Wait for topics
sleep 30
kubectl get kafkatopic -n kafka
```

---

## Dapr Issues

### Pub/Sub component not working

**Error:**
```
Error publishing to Kafka via Dapr
Component 'kafka-pubsub' not found
```

**Solution:**
```bash
# Verify component exists
kubectl get components -n todo-app

# If missing, apply
kubectl apply -f phase-5-minikube/kafka-pubsub.yaml

# Check component logs
kubectl describe component kafka-pubsub -n todo-app

# Test Dapr sidecar
kubectl exec -n todo-app <backend-pod-name> -c daprd -- \
  curl http://localhost:3500/v1.0/metadata
```

---

### State store not connecting

**Error:**
```
Error connecting to PostgreSQL state store
```

**Solution:**
```bash
# Check PostgreSQL is running
kubectl get pods -n todo-app -l app=postgres

# Check connection string in secret
kubectl get secret postgres-secret -n todo-app -o yaml

# Verify statestore component
kubectl describe component statestore -n todo-app

# Test connection from backend pod
kubectl exec -n todo-app <backend-pod-name> -- \
  psql postgresql://todouser:todopass123@postgres:5432/tododb -c '\l'
```

---

## Application Issues

### Backend pod CrashLoopBackOff

**Error:**
```
Backend pod in CrashLoopBackOff
```

**Solution:**
```bash
# Check pod logs
kubectl logs -n todo-app -l app=todo-backend --tail=50

# Common causes:
# 1. Database not ready
kubectl get pods -n todo-app -l app=postgres

# 2. Missing environment variables
kubectl describe pod -n todo-app -l app=todo-backend | grep -A 20 "Environment"

# 3. Image build issue
kubectl describe pod -n todo-app -l app=todo-backend | grep "Image"

# Rebuild image if needed
eval $(minikube docker-env)
docker build -t todo-backend:5.0.0 phase-2-fullstack/backend
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

### Frontend not loading

**Error:**
```
Frontend returns 502/503 error
```

**Solution:**
```bash
# Check frontend pod
kubectl get pods -n todo-app -l app=todo-frontend

# Check logs
kubectl logs -n todo-app -l app=todo-frontend --tail=50

# Check service
kubectl get svc -n todo-app todo-frontend

# Test backend connectivity from frontend pod
kubectl exec -n todo-app <frontend-pod-name> -- \
  curl http://todo-backend:8000/health

# If backend unreachable, check service
kubectl describe svc todo-backend -n todo-app
```

---

### Database connection failed

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL pod
kubectl get pods -n todo-app -l app=postgres

# Check PostgreSQL logs
kubectl logs -n todo-app -l app=postgres

# Verify connection string
kubectl get secret postgres-secret -n todo-app -o jsonpath='{.data.connectionString}' | base64 -d

# Test connection
kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -- \
  psql postgresql://todouser:todopass123@postgres.todo-app:5432/tododb
```

---

## Image Build Issues

### Docker build failing

**Error:**
```
failed to solve with frontend dockerfile.v0
```

**Solution:**
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild with no cache
cd phase-2-fullstack/backend
docker build --no-cache -t todo-backend:5.0.0 .

# Check Dockerfile syntax
docker build --check .
```

---

### Images not in Minikube

**Error:**
```
ImagePullBackOff: image not found in Minikube
```

**Solution:**
```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Verify current context
docker context show  # Should show "minikube" or similar

# Rebuild images
docker build -t todo-backend:5.0.0 phase-2-fullstack/backend
docker build -t todo-frontend:5.0.0 phase-2-fullstack/frontend

# Verify images exist
docker images | grep todo

# Restart deployments
kubectl rollout restart deployment -n todo-app
```

---

## Networking Issues

### Service not accessible

**Error:**
```
curl: (7) Failed to connect to todo-backend
```

**Solution:**
```bash
# Check service exists
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app

# Port forward to service
kubectl port-forward -n todo-app svc/todo-backend 8000:8000

# Test from another pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://todo-backend.todo-app:8000/health
```

---

### LoadBalancer pending

**Error:**
```
EXTERNAL-IP shows <pending> for frontend service
```

**Solution:**
```bash
# For Minikube, use minikube service instead
minikube service todo-frontend -n todo-app

# Or use port forwarding
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000

# Or change to NodePort
kubectl patch svc todo-frontend -n todo-app -p '{"spec":{"type":"NodePort"}}'
minikube service todo-frontend -n todo-app --url
```

---

## Quick Fixes

### Complete reset

```bash
# Delete everything
kubectl delete namespace todo-app kafka
minikube delete

# Start fresh
minikube start --cpus=4 --memory=8192
dapr init -k --wait
# Then run deploy-phase5-complete.sh
```

---

### Restart all pods

```bash
kubectl rollout restart deployment -n todo-app
kubectl rollout restart deployment -n kafka
```

---

### View all events

```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
kubectl get events -n kafka --sort-by='.lastTimestamp'
```

---

## Health Check Commands

### Quick status check

```bash
#!/bin/bash
echo "=== Cluster Status ==="
minikube status

echo "=== Dapr Status ==="
dapr status -k

echo "=== Pods ==="
kubectl get pods -n todo-app
kubectl get pods -n kafka
kubectl get pods -n dapr-system

echo "=== Services ==="
kubectl get svc -n todo-app

echo "=== Components ==="
kubectl get components -n todo-app

echo "=== Kafka Topics ==="
kubectl get kafkatopic -n kafka

echo "=== Resource Usage ==="
kubectl top nodes
kubectl top pods -n todo-app
```

---

### Backend health check

```bash
# Port forward
kubectl port-forward -n todo-app svc/todo-backend 8000:8000 &
PF_PID=$!

# Wait for port forward
sleep 2

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Cleanup
kill $PF_PID
```

---

### Kafka health check

```bash
# Check Kafka cluster
kubectl get kafka -n kafka

# Check broker pods
kubectl get pods -n kafka -l app.kubernetes.io/name=kafka

# Check topics
kubectl get kafkatopic -n kafka

# Test producing/consuming (requires kafka-console tools)
kubectl run kafka-producer -it --rm --restart=Never \
  --image=quay.io/strimzi/kafka:latest-kafka-3.7.0 -- \
  bin/kafka-console-producer.sh \
  --bootstrap-server todo-kafka-kafka-bootstrap.kafka:9092 \
  --topic task-events
```

---

## Support & Resources

### Logs Location
```bash
# All backend logs
kubectl logs -n todo-app -l app=todo-backend --all-containers --tail=100 -f

# All frontend logs
kubectl logs -n todo-app -l app=todo-frontend --tail=100 -f

# Dapr sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd
```

### Documentation
- **Minikube**: https://minikube.sigs.k8s.io/docs/
- **Dapr**: https://docs.dapr.io/
- **Strimzi Kafka**: https://strimzi.io/docs/
- **Kubernetes**: https://kubernetes.io/docs/

### Contact
For issues not covered here, check:
1. Phase 5 specification: `specs/005-phase-v-cloud/phase5-cloud.specify.md`
2. GitHub issues: Create new issue with logs
3. Deployment logs: Run `kubectl get events`

---

**Last Updated:** January 23, 2026  
**Status:** All known issues FIXED ✓
