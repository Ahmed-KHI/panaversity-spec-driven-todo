# Phase V: Advanced Cloud Deployment - Submission Guide

**Hackathon II - Panaversity**  
**Due Date:** January 18, 2026  
**Points:** 300

---

## 📋 Actual Submission Requirements

Based on the hackathon document, you must submit via https://forms.gle/KMKEKaFUD6ZX4UtY8:

1. ✅ **Public GitHub Repository** - All source code + `/specs` folder
2. ✅ **Deployed Application URL** - Cloud Kubernetes deployment (OKE/AKS/GKE)
3. ✅ **YouTube Demo Video** - Maximum 90 seconds (judges only watch first 90s)
4. ✅ **WhatsApp Number** - For live presentation invitation

---

## 🎯 Phase V Implementation Status

### Part A: Advanced Features ✅ **COMPLETE (47/55 tasks)**
- [x] Recurring Tasks (daily, weekly, monthly, yearly)
- [x] Due Dates & Reminders  
- [x] Priorities (Low, Medium, High, Urgent)
- [x] Tags for organization
- [x] Search, Filter, Sort
- [x] Event-driven architecture with Kafka
- [x] Dapr integration (components configured)

**Your Status:** Backend code is ready with all features implemented!

### Part B: Local Deployment (Minikube) ⚠️ **TODO**
- [ ] Deploy to Minikube
- [ ] Deploy Dapr on Minikube with Full Stack:
  - [ ] Pub/Sub (Kafka)
  - [ ] State Management (PostgreSQL)
  - [ ] Jobs API (scheduled reminders)
  - [ ] Secrets Management
  - [ ] Service Invocation

### Part C: Cloud Deployment ⚠️ **TODO - REQUIRED FOR SUBMISSION**
- [ ] Deploy to **Oracle Cloud (OKE)** ⭐ Recommended (Always Free)
- [ ] Deploy Dapr on OKE with Full Stack
- [ ] Use Kafka (Redpanda Cloud free tier OR Confluent $400 credit)
- [ ] Set up **CI/CD pipeline using GitHub Actions**
- [ ] Configure monitoring and logging

---

## Timeline Estimate

| Task | Time | Priority |
|------|------|----------|
| 1. Minikube Local Deployment | 2-3 hours | 🟡 Practice |
| 2. Oracle Cloud OKE Setup | 1 hour | 🔴 Critical |
| 3. Cloud Kubernetes Deployment | 2 hours | 🔴 Critical |
| 4. Kafka Setup (Redpanda Cloud) | 30 min | 🔴 Critical |
| 5. CI/CD GitHub Actions | 1 hour | 🔴 Critical |
| 6. Monitoring & Logging | 1 hour | 🟡 High |
| 7. Testing & Documentation | 1 hour | 🔴 Critical |
| 8. Demo Video (90 seconds) | 1 hour | 🔴 Critical |
| **TOTAL** | **~10 hours** | |

**Recommendation:** Skip Minikube if short on time. Go straight to Oracle Cloud OKE (it's free forever).

---

## 🚀 Quick Path to Submission (6 Hours)

If you're short on time, follow this path:

### Path 1: Cloud-First (Recommended)
1. ✅ **Oracle Cloud OKE** (1 hour) - Always free, 4 CPUs, 24GB RAM
2. ✅ **Deploy App to OKE** (2 hours) - Use existing Helm charts
3. ✅ **Redpanda Cloud** (30 min) - Free serverless Kafka
4. ✅ **GitHub Actions CI/CD** (1 hour) - Auto-deploy on push
5. ✅ **Demo Video** (1 hour) - Record 90 seconds
6. ✅ **Submit** (30 min) - Fill form + push to GitHub

### Path 2: Local Then Cloud (Safer but Longer)
1. Test on Minikube (2 hours)
2. Then deploy to OKE (follows same steps)
3. Total: ~10 hours

---

## 1️⃣ Part B: Local Deployment (Minikube)

### 1.1 Prerequisites Check

```powershell
# Check installations
minikube version          # Need v1.30+
kubectl version --client  # Need v1.28+
dapr --version           # Need v1.12+
helm version             # Need v3.12+
docker --version         # Need 24.0+

# If missing, install from:
# Minikube: https://minikube.sigs.k8s.io/docs/start/
# kubectl: https://kubernetes.io/docs/tasks/tools/
# Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/
# Helm: https://helm.sh/docs/intro/install/
```

### 1.2 Start Minikube Cluster

```powershell
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify
kubectl get nodes

# Enable addons
minikube addons enable metrics-server
minikube addons enable ingress
```

### 1.3 Initialize Dapr

```powershell
# Install Dapr control plane on Kubernetes
dapr init -k

# Verify Dapr system pods (should see 4 pods running)
kubectl get pods -n dapr-system

# Expected:
# dapr-operator-xxxxx
# dapr-sidecar-injector-xxxxx
# dapr-placement-server-xxxxx
# dapr-sentry-xxxxx
```

### 1.4 Deploy Kafka with Strimzi

```powershell
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

Create `kafka/kafka-cluster.yaml`:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
```

```powershell
# Deploy Kafka
kubectl apply -f kafka/kafka-cluster.yaml

# Wait for ready (2-3 minutes)
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka
```

Create topics (`kafka/topics.yaml`):

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
```

```powershell
kubectl apply -f kafka/topics.yaml
```

### 1.5 Build and Load Docker Images

```powershell
# Use Minikube's Docker daemon
& minikube docker-env --shell powershell | Invoke-Expression

# Build images inside Minikube
cd phase-2-fullstack

# Build backend
docker build -t todo-backend:5.0.0 ./backend

# Build frontend  
docker build -t todo-frontend:5.0.0 ./frontend

# Verify images
docker images | Select-String "todo"
```

### 1.6 Deploy Dapr Components

```powershell
# Create namespace
kubectl create namespace todo-app

# Create secrets
kubectl create secret generic postgres-secrets -n todo-app `
  --from-literal=connection-string="YOUR_NEON_DB_URL"

kubectl create secret generic app-secrets -n todo-app `
  --from-literal=openai-api-key="YOUR_KEY" `
  --from-literal=better-auth-secret="YOUR_SECRET" `
  --from-literal=jwt-secret="YOUR_JWT"

# Apply Dapr components
kubectl apply -f phase-5-dapr/components/ -n todo-app

# Verify
dapr components -k -n todo-app
```

### 1.7 Deploy Application with Helm

```powershell
# Deploy app
helm install todo-app ./phase-5-helm/todo-app `
  --namespace todo-app `
  --set backend.image.repository=todo-backend `
  --set backend.image.tag=5.0.0 `
  --set frontend.image.repository=todo-frontend `
  --set frontend.image.tag=5.0.0 `
  --set backend.env.KAFKA_BOOTSTRAP_SERVERS="todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"

# Watch pods start
kubectl get pods -n todo-app -w

# Wait for ready
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=300s
```

### 1.8 Access Application

```powershell
# Port forward frontend
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000

# Open browser: http://localhost:3000
```

### 1.9 Verify Dapr Integration

```powershell
# Check Dapr sidecars
kubectl get pods -n todo-app -o custom-columns=NAME:.metadata.name,CONTAINERS:.spec.containers[*].name

# Test pub/sub
kubectl exec -n todo-app deploy/todo-backend -c todo-backend -- `
  curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events `
  -H "Content-Type: application/json" `
  -d '{"test": "hello"}'

# Open Dapr dashboard
dapr dashboard -k -p 9999
# Visit: http://localhost:9999
```

---

## 2️⃣ Part C: Cloud Deployment (Oracle Cloud OKE)

### Why Oracle Cloud? ⭐ **Always Free Tier**
- **4 OCPUs, 24GB RAM** - Free forever (not trial)
- No credit card charges after trial ends
- Perfect for hackathon submission
- Better than Azure ($200/30 days) or GCP ($300/90 days)

### 2.1 Oracle Cloud Setup (15 minutes)

1. **Sign up:** https://www.oracle.com/cloud/free/
2. **Create OKE Cluster:**
   - Go to: **Developer Services** → **Kubernetes Clusters (OKE)**
   - Click **Create Cluster**
   - Choose **Quick Create**
   - Select **Free Tier** node pool:
     - Shape: **VM.Standard.A1.Flex**
     - OCPUs: **2** (use 2 nodes with 2 OCPUs each = 4 total)
     - Memory: **12GB per node** (24GB total)
   - Click **Create Cluster** (takes 7-10 minutes)

3. **Configure kubectl:**
   - Click **Access Cluster**
   - Copy the `oci ce cluster create-kubeconfig` command
   - Run in PowerShell

```powershell
# Example (your values will differ):
oci ce cluster create-kubeconfig --cluster-id ocid1.cluster.oc1... --file $HOME\.kube\config --region us-ashburn-1 --token-version 2.0.0

# Test connection
kubectl get nodes
# Should see 2 nodes in Ready state
```

### 2.2 Install Dapr on OKE

```powershell
# Same as Minikube
dapr init -k

# Verify
kubectl get pods -n dapr-system
```

### 2.3 Deploy Kafka (Redpanda Cloud - Free Tier)

**Why Redpanda Cloud?**
- Free serverless tier (no credit card)
- Kafka-compatible
- No cluster management

1. **Sign up:** https://redpanda.com/try-redpanda
2. **Create Cluster:**
   - Choose **Serverless** (free)
   - Region: **us-east-1**
   - Click **Create**

3. **Create Topics:**
   - Go to **Topics** tab
   - Create 3 topics: `task-events`, `reminders`, `task-updates`

4. **Get Connection Details:**
   - Go to **Connect** tab
   - Copy **Bootstrap Server URL** (e.g., `pkc-xxxxx.us-east-1.aws.redpanda.cloud:9092`)
   - Create **API Key** → Save Key + Secret

5. **Update Dapr Component:**

Edit `phase-5-dapr/components/kafka-pubsub.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "pkc-xxxxx.us-east-1.aws.redpanda.cloud:9092"
    - name: authType
      value: "password"
    - name: saslUsername
      value: "YOUR_API_KEY"
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: sasl-password
    - name: consumerGroup
      value: "todo-service"
```

```powershell
# Create Kafka secret
kubectl create secret generic kafka-secrets -n todo-app `
  --from-literal=sasl-password="YOUR_REDPANDA_SECRET"
```

### 2.4 Build and Push Docker Images

**Option A: Docker Hub (Free)**

```powershell
# Login to Docker Hub
docker login

# Tag images
docker tag todo-backend:5.0.0 YOUR_DOCKERHUB_USERNAME/todo-backend:5.0.0
docker tag todo-frontend:5.0.0 YOUR_DOCKERHUB_USERNAME/todo-frontend:5.0.0

# Push
docker push YOUR_DOCKERHUB_USERNAME/todo-backend:5.0.0
docker push YOUR_DOCKERHUB_USERNAME/todo-frontend:5.0.0
```

**Option B: Oracle Container Registry (OCIR)**

```powershell
# Login to OCIR
docker login <region-key>.ocir.io
# Username: <tenancy-namespace>/<oracle-cloud-username>
# Password: <auth-token from Oracle Cloud>

# Tag
docker tag todo-backend:5.0.0 <region>.ocir.io/<tenancy>/todo-backend:5.0.0

# Push
docker push <region>.ocir.io/<tenancy>/todo-backend:5.0.0
```

### 2.5 Deploy to OKE with Helm

```powershell
# Create namespace
kubectl create namespace todo-app

# Create secrets (same as Minikube)
kubectl create secret generic postgres-secrets -n todo-app `
  --from-literal=connection-string="YOUR_NEON_URL"

kubectl create secret generic app-secrets -n todo-app `
  --from-literal=openai-api-key="YOUR_KEY" `
  --from-literal=better-auth-secret="YOUR_SECRET" `
  --from-literal=jwt-secret="YOUR_JWT"

kubectl create secret generic kafka-secrets -n todo-app `
  --from-literal=sasl-password="YOUR_REDPANDA_SECRET"

# Apply Dapr components
kubectl apply -f phase-5-dapr/components/ -n todo-app

# Deploy app
helm install todo-app ./phase-5-helm/todo-app `
  --namespace todo-app `
  --set backend.image.repository=YOUR_DOCKERHUB_USERNAME/todo-backend `
  --set backend.image.tag=5.0.0 `
  --set frontend.image.repository=YOUR_DOCKERHUB_USERNAME/todo-frontend `
  --set frontend.image.tag=5.0.0 `
  --set backend.env.KAFKA_BOOTSTRAP_SERVERS="pkc-xxxxx.us-east-1.aws.redpanda.cloud:9092" `
  --set backend.env.KAFKA_ENABLED=true `
  --set ingress.enabled=true `
  --set ingress.host=todo.yourdomain.com

# Watch deployment
kubectl get pods -n todo-app -w
```

### 2.6 Expose Application with LoadBalancer

**Option A: LoadBalancer Service (Easiest)**

```powershell
# Get external IP
kubectl get svc -n todo-app

# Wait for EXTERNAL-IP (takes 2-3 minutes)
# Frontend: http://<EXTERNAL-IP>:3000
# Backend: http://<EXTERNAL-IP>:8000
```

**Option B: Ingress with Domain**

1. **Get a free domain:** https://www.freenom.com or use Cloudflare
2. **Point DNS to LoadBalancer IP**
3. **Access:** https://todo.yourdomain.com

---

## 3️⃣ CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Oracle Cloud OKE

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
  BACKEND_IMAGE: todo-backend
  FRONTEND_IMAGE: todo-frontend
  VERSION: ${{ github.sha }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push backend
      uses: docker/build-push-action@v5
      with:
        context: ./phase-2-fullstack/backend
        push: true
        tags: |
          ${{ env.DOCKERHUB_USERNAME }}/${{ env.BACKEND_IMAGE }}:${{ env.VERSION }}
          ${{ env.DOCKERHUB_USERNAME }}/${{ env.BACKEND_IMAGE }}:latest
    
    - name: Build and push frontend
      uses: docker/build-push-action@v5
      with:
        context: ./phase-2-fullstack/frontend
        push: true
        tags: |
          ${{ env.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE }}:${{ env.VERSION }}
          ${{ env.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE }}:latest
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
    
    - name: Configure kubectl for OKE
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
    
    - name: Deploy to Kubernetes
      run: |
        helm upgrade --install todo-app ./phase-5-helm/todo-app \
          --namespace todo-app \
          --set backend.image.repository=${{ env.DOCKERHUB_USERNAME }}/${{ env.BACKEND_IMAGE }} \
          --set backend.image.tag=${{ env.VERSION }} \
          --set frontend.image.repository=${{ env.DOCKERHUB_USERNAME }}/${{ env.FRONTEND_IMAGE }} \
          --set frontend.image.tag=${{ env.VERSION }} \
          --wait --timeout 5m
    
    - name: Verify deployment
      run: |
        kubectl rollout status deployment/todo-backend -n todo-app
        kubectl rollout status deployment/todo-frontend -n todo-app
```

**Setup GitHub Secrets:**
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `DOCKERHUB_USERNAME` - Your Docker Hub username
   - `DOCKERHUB_TOKEN` - Docker Hub access token
   - `KUBECONFIG` - Base64 encoded kubeconfig: `cat ~/.kube/config | base64 -w 0`

---

## 4️⃣ Monitoring and Logging

### 4.1 Deploy Prometheus + Grafana

```powershell
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install monitoring prometheus-community/kube-prometheus-stack `
  --namespace monitoring --create-namespace `
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Access Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
# Visit: http://localhost:3001
# Username: admin, Password: prom-operator
```

### 4.2 Dapr Monitoring

Dapr exports metrics to Prometheus automatically.

**Import Dapr Dashboards:**
1. Open Grafana: http://localhost:3001
2. Go to **Dashboards** → **Import**
3. Enter ID: **11747** (Dapr System Dashboard)
4. Click **Load** → **Import**

### 4.3 Logging with Fluent Bit

```powershell
# Add Helm repo
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update

# Install Fluent Bit
helm install fluent-bit fluent/fluent-bit `
  --namespace logging --create-namespace `
  --set backend.type=stdout

# View logs
kubectl logs -n logging -l app.kubernetes.io/name=fluent-bit --tail=50 -f
```

---

## 5️⃣ Demo Video (90 Seconds)

### Video Script Template

**[0:00-0:15] Introduction**
> "Hi, I'm [Name]. This is Phase 5 of the Hackathon - Todo App with advanced features deployed on Oracle Cloud Kubernetes with Kafka and Dapr."

**[0:15-0:30] Architecture Overview**
> "The architecture includes: Next.js frontend, FastAPI backend, Neon PostgreSQL, Kafka on Redpanda Cloud, and Dapr for pub/sub, state management, jobs, and secrets."

**[0:30-1:00] Live Demo**
> "Here's the live app running on OKE. [Show creating task with priority, due date, and tags. Show search/filter. Show task statistics. Mention events are published to Kafka.]"

**[1:00-1:20] Code Walkthrough**
> "In the code, when I create a task, it publishes to Kafka via Dapr. [Show event_publisher.py briefly]. The Jobs API schedules reminders at exact times."

**[1:20-1:30] Closing**
> "All code is on GitHub with full specs, Helm charts, and CI/CD. Running on Oracle Cloud free tier. Thank you!"

### Recording Tools
- **Loom** (easiest): https://loom.com
- **OBS Studio** (professional): https://obsproject.com
- **Windows Game Bar**: Win + G

### Upload to YouTube
1. Upload as **Unlisted**
2. **Title:** "Hackathon II Phase V: Cloud-Native Todo with Kafka + Dapr on OKE"
3. **Description:** Include GitHub and live app URL

---

## 6️⃣ Submission Checklist

### Before Submitting:

- [ ] **Code Complete**
  - [ ] All Phase V features working
  - [ ] Specs in `/specs/005-phase-v-cloud/`
  - [ ] CLAUDE.md with instructions
  - [ ] README.md comprehensive

- [ ] **Cloud Deployment Working**
  - [ ] Deployed to Oracle Cloud OKE
  - [ ] External IP/domain accessible
  - [ ] Can create/read/update/delete tasks
  - [ ] Advanced features functional (priority, tags, search)
  - [ ] Kafka events publishing (check Redpanda console)
  - [ ] Dapr sidecars running

- [ ] **CI/CD Pipeline**
  - [ ] GitHub Actions workflow created
  - [ ] Successfully deploys on push to main
  - [ ] Latest commit deployed to OKE

- [ ] **Monitoring**
  - [ ] Prometheus + Grafana installed
  - [ ] Dapr dashboard accessible
  - [ ] Logs viewable

- [ ] **Documentation**
  - [ ] README.md explains everything
  - [ ] Deployment guide included
  - [ ] Architecture diagrams

- [ ] **Demo Video**
  - [ ] Uploaded to YouTube (unlisted)
  - [ ] Exactly 90 seconds or less
  - [ ] Shows all Phase V features
  - [ ] Includes GitHub + live URL

### Submit via Form:

**Form URL:** https://forms.gle/KMKEKaFUD6ZX4UtY8

1. **GitHub URL:** `https://github.com/YOUR_USERNAME/hackathon-todo-app`
2. **Live App URL:** `http://<OKE-EXTERNAL-IP>:3000` or `https://todo.yourdomain.com`
3. **YouTube Video:** `https://youtu.be/YOUR_VIDEO_ID`
4. **WhatsApp:** Your number for presentation invitation

---

## 7️⃣ Troubleshooting

### Pods Not Starting
```powershell
# Check pod status
kubectl get pods -n todo-app

# Describe pod to see errors
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app -c todo-backend
```

### Dapr Sidecar Not Injecting
```powershell
# Verify Dapr annotation in deployment
kubectl get deployment todo-backend -n todo-app -o yaml | Select-String "dapr.io"

# Should see:
# dapr.io/enabled: "true"
# dapr.io/app-id: "backend-service"
# dapr.io/app-port: "8000"
```

### Kafka Connection Failed
```powershell
# Test Kafka from pod
kubectl exec -it -n todo-app deploy/todo-backend -c todo-backend -- sh
# Inside pod:
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"test": "hello"}'
```

### External IP Pending Forever
```powershell
# On Oracle Cloud, create Load Balancer manually:
# Networking → Load Balancers → Create Load Balancer
# Backend Set: Add backend servers (worker nodes)
# Listener: Port 3000 → Backend Port 30000 (NodePort)

# Then use LoadBalancer IP in DNS
```

---

## 🎉 You're Ready to Submit!

Your Phase V implementation is **code-complete**. Now you just need to:

1. ✅ Deploy to Oracle Cloud OKE (2 hours)
2. ✅ Set up Redpanda Cloud Kafka (30 min)
3. ✅ Create GitHub Actions CI/CD (1 hour)
4. ✅ Record 90-second demo (1 hour)
5. ✅ Push to GitHub + Submit form (30 min)

**Total: 5 hours to submission** 🚀

Good luck! 🍀
