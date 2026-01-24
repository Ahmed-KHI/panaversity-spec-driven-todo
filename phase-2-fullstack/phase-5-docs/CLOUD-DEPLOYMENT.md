# Phase V: Cloud Deployment Guide

**[Task]**: T-E-009 (Cloud Deployment Documentation)  
**[From]**: specs/005-phase-v-cloud/phase5-cloud.specify.md §6-7,  
           specs/005-phase-v-cloud/phase5-cloud.tasks.md §E.9-E.10

## Overview

This guide covers deploying the Todo Management Application (Phase V) to cloud Kubernetes platforms:
- **Azure Kubernetes Service (AKS)**
- **Google Kubernetes Engine (GKE)**
- **Oracle Kubernetes Engine (OKE)**

---

## Prerequisites

### 1. Cloud Provider Account
- Azure: [https://azure.microsoft.com/free/](https://azure.microsoft.com/free/)
- Google Cloud: [https://cloud.google.com/free](https://cloud.google.com/free)
- Oracle Cloud: [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/)

### 2. CLI Tools

**Azure (AKS)**:
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Install kubectl
az aks install-cli
```

**Google Cloud (GKE)**:
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Install kubectl
gcloud components install kubectl
```

**Oracle Cloud (OKE)**:
```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure
oci setup config

# Install kubectl
# (Manual download from Kubernetes.io)
```

### 3. Container Registry

**GitHub Container Registry (GHCR) - Recommended**:
```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push images
docker build -t ghcr.io/ahmed-khi/todo-backend:v5.0.0 ./backend
docker push ghcr.io/ahmed-khi/todo-backend:v5.0.0

docker build -t ghcr.io/ahmed-khi/todo-frontend:v5.0.0 ./frontend
docker push ghcr.io/ahmed-khi/todo-frontend:v5.0.0
```

---

## Azure Kubernetes Service (AKS) Deployment

### Step 1: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="todo-app-rg"
LOCATION="eastus"
CLUSTER_NAME="todo-app-aks"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 2: Create AKS Cluster

```bash
# Create AKS cluster with Dapr extension
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-managed-identity \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
```

### Step 3: Install Dapr on AKS

```bash
# Install Dapr extension
az k8s-extension create \
  --cluster-type managedClusters \
  --cluster-name $CLUSTER_NAME \
  --resource-group $RESOURCE_GROUP \
  --name dapr \
  --extension-type Microsoft.Dapr

# Verify
kubectl get pods -n dapr-system
```

### Step 4: Create PostgreSQL Database (Azure Database for PostgreSQL)

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name todo-postgres \
  --location $LOCATION \
  --admin-user todoadmin \
  --admin-password "YourStrongPassword123!" \
  --sku-name Standard_B2s \
  --tier Burstable \
  --storage-size 32 \
  --version 15

# Get connection string
az postgres flexible-server show-connection-string \
  --server-name todo-postgres \
  --database-name tododb
```

### Step 5: Create Secrets

```bash
# Base64 encode connection string
CONNECTION_STRING=$(echo -n "postgresql://todoadmin:YourStrongPassword123!@todo-postgres.postgres.database.azure.com/tododb?sslmode=require" | base64)

# Update secrets.yaml with encoded values
# Then apply:
kubectl apply -f phase-5-kubernetes/secrets.yaml
```

### Step 6: Deploy with Helm

```bash
# Add Helm repo (if using)
helm repo update

# Deploy
helm upgrade --install todo-app ./phase-5-helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set imageRegistry="ghcr.io/ahmed-khi" \
  --set backend.image.tag="v5.0.0" \
  --set frontend.image.tag="v5.0.0" \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host="todo.yourdomain.com" \
  --wait

# Check status
kubectl get pods -n todo-app
kubectl get svc -n todo-app
```

### Step 7: Configure DNS

```bash
# Get LoadBalancer IP
kubectl get svc todo-app-frontend -n todo-app

# Add DNS A record pointing to LoadBalancer IP
# todo.yourdomain.com -> LoadBalancer IP
```

---

## Google Kubernetes Engine (GKE) Deployment

### Step 1: Create GKE Cluster

```bash
# Set variables
PROJECT_ID="your-project-id"
CLUSTER_NAME="todo-app-gke"
REGION="us-central1"

# Set project
gcloud config set project $PROJECT_ID

# Create GKE cluster
gcloud container clusters create $CLUSTER_NAME \
  --region $REGION \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-stackdriver-kubernetes

# Get credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION
```

### Step 2: Install Dapr

```bash
# Install Dapr on GKE
dapr init -k

# Verify
kubectl get pods -n dapr-system
```

### Step 3: Create Cloud SQL (PostgreSQL)

```bash
# Create Cloud SQL instance
gcloud sql instances create todo-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create tododb --instance=todo-postgres

# Create user
gcloud sql users create todoadmin \
  --instance=todo-postgres \
  --password=YourStrongPassword123!

# Enable Cloud SQL Proxy (for secure connection)
# Get connection name
gcloud sql instances describe todo-postgres --format="value(connectionName)"
```

### Step 4: Deploy Application

```bash
# Update secrets.yaml with Cloud SQL connection string
# Deploy
helm upgrade --install todo-app ./phase-5-helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set imageRegistry="ghcr.io/ahmed-khi" \
  --set backend.image.tag="v5.0.0" \
  --set frontend.image.tag="v5.0.0" \
  --wait

# Check
kubectl get pods -n todo-app
```

### Step 5: Expose with Ingress

```bash
# Install nginx-ingress controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx

# Apply ingress
kubectl apply -f phase-5-kubernetes/ingress.yaml

# Get Ingress IP
kubectl get ingress -n todo-app
```

---

## Oracle Kubernetes Engine (OKE) Deployment

### Step 1: Create OKE Cluster

```bash
# Set variables
COMPARTMENT_ID="your-compartment-ocid"
CLUSTER_NAME="todo-app-oke"

# Create VCN and subnets (via OCI Console)
# Then create OKE cluster

oci ce cluster create \
  --compartment-id $COMPARTMENT_ID \
  --name $CLUSTER_NAME \
  --vcn-id $VCN_OCID \
  --kubernetes-version v1.28.0 \
  --node-shape VM.Standard.E4.Flex

# Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file $HOME/.kube/config
```

### Step 2: Install Dapr

```bash
dapr init -k
kubectl get pods -n dapr-system
```

### Step 3: Create Autonomous Database

```bash
# Create via OCI Console or CLI
oci db autonomous-database create \
  --compartment-id $COMPARTMENT_ID \
  --db-name tododb \
  --display-name "Todo App Database" \
  --admin-password "YourStrongPassword123!"

# Download wallet for connection
oci db autonomous-database generate-wallet \
  --autonomous-database-id $DB_OCID \
  --file wallet.zip \
  --password WalletPassword123!
```

### Step 4: Deploy Application

Similar to GKE deployment, adjust secrets for Autonomous Database connection.

---

## Post-Deployment Configuration

### 1. Setup External Kafka (Redpanda Cloud)

**Sign up**: [https://redpanda.com/try-redpanda](https://redpanda.com/try-redpanda)

**Update Dapr component**:
```yaml
# phase-5-dapr/components/kafka-pubsub.yaml
metadata:
- name: brokers
  value: "your-redpanda-cluster.redpanda.cloud:9092"
- name: authType
  value: "password"
- name: saslUsername
  secretKeyRef:
    name: kafka-secrets
    key: sasl-username
- name: saslPassword
  secretKeyRef:
    name: kafka-secrets
    key: sasl-password
```

Apply:
```bash
kubectl apply -f phase-5-dapr/components/kafka-pubsub.yaml
```

### 2. Enable TLS/HTTPS with Cert-Manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Update ingress to use TLS
# (Already configured in ingress.yaml)
```

### 3. Setup Monitoring (Prometheus + Grafana)

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials: admin / prom-operator
```

---

## Verification

### Check All Pods Running

```bash
kubectl get pods -n todo-app
kubectl get pods -n dapr-system
```

Expected output:
```
NAME                                READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxx-xxxxx        2/2     Running   0          5m
todo-app-backend-xxxxx-yyyyy        2/2     Running   0          5m
todo-app-backend-xxxxx-zzzzz        2/2     Running   0          5m
todo-app-frontend-xxxxx-xxxxx       2/2     Running   0          5m
todo-app-frontend-xxxxx-yyyyy       2/2     Running   0          5m
todo-app-frontend-xxxxx-zzzzz       2/2     Running   0          5m
```

### Test API

```bash
# Port-forward backend
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### Test Frontend

```bash
# Get frontend URL
kubectl get svc todo-app-frontend -n todo-app

# Or port-forward
kubectl port-forward -n todo-app svc/todo-app-frontend 3000:80

# Visit
open http://localhost:3000
```

### Verify Dapr Event Publishing

```bash
# Check Dapr sidecar logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend -c daprd

# Should see event publishing logs
```

---

## Scaling and Performance

### Horizontal Pod Autoscaler (HPA)

```bash
# Enable HPA for backend
kubectl autoscale deployment todo-app-backend \
  --namespace todo-app \
  --cpu-percent=80 \
  --min=3 \
  --max=10

# Enable HPA for frontend
kubectl autoscale deployment todo-app-frontend \
  --namespace todo-app \
  --cpu-percent=80 \
  --min=3 \
  --max=10
```

### Cluster Autoscaler

**AKS**:
```bash
az aks update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10
```

**GKE**:
Already enabled with `--enable-autoscaling` during creation.

---

## Cost Optimization

### 1. Use Spot/Preemptible Instances

**GKE**:
```bash
gcloud container node-pools create spot-pool \
  --cluster=$CLUSTER_NAME \
  --region=$REGION \
  --spot \
  --num-nodes=3
```

**AKS**:
```bash
az aks nodepool add \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --name spotpool \
  --priority Spot \
  --node-count 3
```

### 2. Right-size Resources

Update `values.yaml`:
```yaml
backend:
  resources:
    requests:
      cpu: 100m    # Start small
      memory: 256Mi
```

### 3. Schedule Non-Critical Workloads

Use `PodDisruptionBudget` and `PriorityClass` for critical pods.

---

## Cleanup

### Delete Application

```bash
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
```

### Delete Cluster

**AKS**:
```bash
az aks delete --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --yes --no-wait
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

**GKE**:
```bash
gcloud container clusters delete $CLUSTER_NAME --region $REGION --quiet
```

**OKE**:
```bash
oci ce cluster delete --cluster-id $CLUSTER_OCID --force
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app -c backend
kubectl logs <pod-name> -n todo-app -c daprd
```

### Database Connection Issues

```bash
# Test connection from pod
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql "postgresql://user:pass@host:5432/tododb"
```

### Dapr Issues

```bash
# Restart Dapr system pods
kubectl rollout restart deployment -n dapr-system
```

---

## Next Steps

1. ✅ Deploy to cloud (AKS/GKE/OKE)
2. 🔄 Configure production database (Neon/Supabase/Cloud SQL)
3. 🔄 Setup external Kafka (Redpanda Cloud)
4. 🔄 Configure domain and TLS certificates
5. 🔄 Enable monitoring and alerting
6. 🔄 Setup CI/CD pipeline (GitHub Actions)
7. 🔄 Load testing and performance tuning
8. 🔄 Security hardening (network policies, pod security)

---

**Congratulations! Your Phase V Todo App is now running in the cloud!** 🎉
