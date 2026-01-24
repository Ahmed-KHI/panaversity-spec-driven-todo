#!/bin/bash
# Phase V - Complete Minikube Deployment Script
# [Task]: T-E-008 (Enhanced with all fixes)
# [From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md

set -e

echo "=================================================="
echo "  Phase V: Todo App - Complete Minikube Setup"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
MINIKUBE_CPUS=4
MINIKUBE_MEMORY=8192
MINIKUBE_DRIVER=docker

echo "${BLUE}Step 1: Prerequisites Check${NC}"
echo "======================================================"

# Check all required tools
REQUIRED_TOOLS=("minikube" "kubectl" "helm" "dapr" "docker")
MISSING_TOOLS=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS+=("$tool")
        echo -e "${RED}✗ $tool not found${NC}"
    else
        VERSION=$($tool version --short 2>/dev/null || $tool version 2>/dev/null | head -n1)
        echo -e "${GREEN}✓ $tool found${NC} - $VERSION"
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo ""
    echo -e "${RED}Error: Missing required tools: ${MISSING_TOOLS[*]}${NC}"
    echo ""
    echo "Installation instructions:"
    echo "- minikube: https://minikube.sigs.k8s.io/docs/start/"
    echo "- kubectl: https://kubernetes.io/docs/tasks/tools/"
    echo "- helm: https://helm.sh/docs/intro/install/"
    echo "- dapr: https://docs.dapr.io/getting-started/install-dapr-cli/"
    echo "- docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo ""
echo "${BLUE}Step 2: Start Minikube${NC}"
echo "======================================================"

if minikube status &> /dev/null; then
    echo -e "${GREEN}✓ Minikube already running${NC}"
    MINIKUBE_IP=$(minikube ip)
    echo "  IP: $MINIKUBE_IP"
else
    echo "Starting Minikube with:"
    echo "  - CPUs: $MINIKUBE_CPUS"
    echo "  - Memory: ${MINIKUBE_MEMORY}MB"
    echo "  - Driver: $MINIKUBE_DRIVER"
    
    minikube start \
        --cpus=$MINIKUBE_CPUS \
        --memory=$MINIKUBE_MEMORY \
        --driver=$MINIKUBE_DRIVER \
        --kubernetes-version=stable
    
    echo -e "${GREEN}✓ Minikube started successfully${NC}"
    MINIKUBE_IP=$(minikube ip)
    echo "  IP: $MINIKUBE_IP"
fi

# Enable required addons
echo ""
echo "Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server
echo -e "${GREEN}✓ Addons enabled${NC}"

echo ""
echo "${BLUE}Step 3: Initialize Dapr${NC}"
echo "======================================================"

if dapr status -k &> /dev/null; then
    echo -e "${GREEN}✓ Dapr already initialized on Kubernetes${NC}"
    dapr status -k
else
    echo "Initializing Dapr on Kubernetes..."
    dapr init -k --wait --timeout 300
    echo -e "${GREEN}✓ Dapr initialized successfully${NC}"
    
    echo ""
    echo "Waiting for Dapr components to be ready..."
    kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/name=dapr \
        -n dapr-system \
        --timeout=300s
    
    echo -e "${GREEN}✓ Dapr components ready${NC}"
fi

echo ""
echo "${BLUE}Step 4: Install Strimzi Kafka Operator${NC}"
echo "======================================================"

# Check if Strimzi is already installed
if kubectl get deployment strimzi-cluster-operator -n kafka &> /dev/null; then
    echo -e "${GREEN}✓ Strimzi Kafka operator already installed${NC}"
else
    echo "Creating kafka namespace..."
    kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
    
    echo "Installing Strimzi operator..."
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    
    echo "Waiting for Strimzi operator to be ready..."
    kubectl wait --for=condition=ready pod \
        -l name=strimzi-cluster-operator \
        -n kafka \
        --timeout=300s
    
    echo -e "${GREEN}✓ Strimzi operator ready${NC}"
fi

echo ""
echo "${BLUE}Step 5: Create Namespaces${NC}"
echo "======================================================"

cd ../phase-5-minikube

echo "Creating application namespaces..."
kubectl apply -f namespace.yaml

echo -e "${GREEN}✓ Namespaces created${NC}"
kubectl get namespaces todo-app kafka

echo ""
echo "${BLUE}Step 6: Deploy Kafka Cluster${NC}"
echo "======================================================"

if kubectl get kafka todo-kafka -n kafka &> /dev/null; then
    echo -e "${GREEN}✓ Kafka cluster already exists${NC}"
else
    echo "Deploying Kafka cluster..."
    kubectl apply -f kafka-cluster-v1.yaml
    
    echo "Waiting for Kafka cluster to be ready (this may take 2-3 minutes)..."
    kubectl wait kafka/todo-kafka \
        --for=condition=Ready \
        --timeout=300s \
        -n kafka || echo "${YELLOW}Warning: Kafka may still be starting${NC}"
    
    echo -e "${GREEN}✓ Kafka cluster deployed${NC}"
fi

echo ""
echo "Kafka cluster status:"
kubectl get kafka -n kafka
kubectl get kafkatopic -n kafka

echo ""
echo "${BLUE}Step 7: Deploy PostgreSQL Database${NC}"
echo "======================================================"

if kubectl get deployment postgres -n todo-app &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL already deployed${NC}"
else
    echo "Deploying PostgreSQL..."
    kubectl apply -f postgres-deployment.yaml
    
    echo "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod \
        -l app=postgres \
        -n todo-app \
        --timeout=120s
    
    echo -e "${GREEN}✓ PostgreSQL ready${NC}"
fi

echo ""
echo "${BLUE}Step 8: Apply Secrets${NC}"
echo "======================================================"

echo -e "${YELLOW}⚠  Make sure to update secrets.yaml with your actual credentials!${NC}"
echo "Required secrets:"
echo "  - DATABASE_URL (connectionString)"
echo "  - JWT_SECRET (jwtSecret)"
echo "  - BETTER_AUTH_SECRET (betterAuthSecret)"
echo "  - OPENAI_API_KEY (openaiApiKey)"
echo ""
read -p "Press Enter to continue with current secrets (or Ctrl+C to exit and edit)..."

kubectl apply -f secrets.yaml
echo -e "${GREEN}✓ Secrets applied${NC}"

echo ""
echo "${BLUE}Step 9: Deploy Dapr Components${NC}"
echo "======================================================"

echo "Applying Dapr components..."
kubectl apply -f kafka-pubsub.yaml
kubectl apply -f statestore.yaml
kubectl apply -f jobs-api.yaml

echo -e "${GREEN}✓ Dapr components deployed${NC}"

echo ""
echo "Dapr components status:"
kubectl get components -n todo-app

echo ""
echo "${BLUE}Step 10: Build Docker Images${NC}"
echo "======================================================"

# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

echo "Building backend image..."
cd ../../phase-2-fullstack/backend
docker build -t todo-backend:5.0.0 .
echo -e "${GREEN}✓ Backend image built${NC}"

echo ""
echo "Building frontend image..."
cd ../frontend
docker build -t todo-frontend:5.0.0 .
echo -e "${GREEN}✓ Frontend image built${NC}"

# Return to scripts directory
cd ../phase-5-scripts

echo ""
echo "${BLUE}Step 11: Deploy Application${NC}"
echo "======================================================"

cd ../phase-5-minikube

echo "Deploying backend..."
kubectl apply -f backend-deployment.yaml

echo "Deploying frontend..."
kubectl apply -f frontend-deployment.yaml

echo ""
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
    -l app=todo-backend \
    -n todo-app \
    --timeout=180s || echo "${YELLOW}Backend may still be starting${NC}"

kubectl wait --for=condition=ready pod \
    -l app=todo-frontend \
    -n todo-app \
    --timeout=180s || echo "${YELLOW}Frontend may still be starting${NC}"

echo -e "${GREEN}✓ Application deployed${NC}"

echo ""
echo "${BLUE}Step 12: Deployment Status${NC}"
echo "======================================================"

echo ""
echo "Namespaces:"
kubectl get namespaces | grep -E "todo-app|kafka"

echo ""
echo "Pods:"
kubectl get pods -n todo-app
kubectl get pods -n kafka

echo ""
echo "Services:"
kubectl get svc -n todo-app

echo ""
echo "Dapr Components:"
kubectl get components -n todo-app

echo ""
echo "=================================================="
echo -e "${GREEN}  ✓ Phase V Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "Access your application:"
echo ""
echo "${YELLOW}Frontend:${NC}"
echo "  $ minikube service todo-frontend -n todo-app"
echo "  This will automatically open the app in your browser"
echo ""
echo "${YELLOW}Backend API:${NC}"
echo "  $ kubectl port-forward -n todo-app svc/todo-backend 8000:8000"
echo "  Then visit: http://localhost:8000/docs"
echo ""
echo "${YELLOW}Dapr Dashboard:${NC}"
echo "  $ dapr dashboard -k -p 9999"
echo "  Then visit: http://localhost:9999"
echo ""
echo "${YELLOW}Kafka Topics:${NC}"
echo "  $ kubectl get kafkatopic -n kafka"
echo ""
echo "${YELLOW}View Logs:${NC}"
echo "  Backend:  kubectl logs -n todo-app -l app=todo-backend -f"
echo "  Frontend: kubectl logs -n todo-app -l app=todo-frontend -f"
echo "  Kafka:    kubectl logs -n kafka -l app.kubernetes.io/name=kafka -f"
echo ""
echo "${YELLOW}Troubleshooting:${NC}"
echo "  Check pod status: kubectl describe pod <pod-name> -n todo-app"
echo "  Check events:     kubectl get events -n todo-app --sort-by='.lastTimestamp'"
echo ""
echo "${YELLOW}Cleanup:${NC}"
echo "  $ kubectl delete namespace todo-app kafka"
echo "  $ minikube stop"
echo ""
