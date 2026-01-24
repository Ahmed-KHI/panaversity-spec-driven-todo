#!/bin/bash
# [Task]: T-E-008
# [From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md §E.8
# 
# Deploy Todo App to Minikube with Dapr and Kafka

set -e

echo "========================================="
echo "Todo App - Minikube Deployment Script"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: minikube not installed${NC}"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not installed${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm not installed${NC}"
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo -e "${RED}Error: dapr CLI not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites installed${NC}"
echo ""

# Start Minikube if not running
echo "Starting Minikube..."
minikube status > /dev/null 2>&1 || minikube start --cpus=4 --memory=8192 --driver=docker
echo -e "${GREEN}✓ Minikube running${NC}"
echo ""

# Initialize Dapr on Kubernetes
echo "Initializing Dapr on Kubernetes..."
dapr status -k > /dev/null 2>&1 || dapr init -k --wait
echo -e "${GREEN}✓ Dapr initialized${NC}"
echo ""

# Create namespace
echo "Creating namespace..."
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Apply secrets (you must update secrets.yaml with real values)
echo "Applying secrets..."
echo -e "${YELLOW}⚠ Remember to update secrets.yaml with real credentials!${NC}"
kubectl apply -f ../phase-5-kubernetes/secrets.yaml
echo -e "${GREEN}✓ Secrets applied${NC}"
echo ""

# Apply Dapr components
echo "Applying Dapr components..."
kubectl apply -f ../phase-5-dapr/components/
echo -e "${GREEN}✓ Dapr components applied${NC}"
echo ""

# Apply RBAC
echo "Applying RBAC..."
kubectl apply -f ../phase-5-kubernetes/rbac.yaml
echo -e "${GREEN}✓ RBAC applied${NC}"
echo ""

# Deploy with Helm
echo "Deploying application with Helm..."
helm upgrade --install todo-app ../phase-5-helm/todo-app \
  --namespace todo-app \
  --set imageRegistry="ghcr.io/ahmed-khi" \
  --set backend.image.tag="v5.0.0" \
  --set frontend.image.tag="v5.0.0" \
  --set backend.replicaCount=2 \
  --set frontend.replicaCount=2 \
  --wait \
  --timeout=5m

echo -e "${GREEN}✓ Application deployed${NC}"
echo ""

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app -n todo-app --timeout=300s
echo -e "${GREEN}✓ All pods ready${NC}"
echo ""

# Get service URLs
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Access your application:"
echo ""
echo "Frontend:"
echo "  minikube service todo-app-frontend -n todo-app --url"
echo ""
echo "Backend:"
echo "  kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000"
echo "  Then visit: http://localhost:8000/docs"
echo ""
echo "Dapr Dashboard:"
echo "  dapr dashboard -k -p 9999"
echo "  Then visit: http://localhost:9999"
echo ""
echo "View pods:"
echo "  kubectl get pods -n todo-app"
echo ""
echo "View logs:"
echo "  kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f"
echo ""
echo "Delete deployment:"
echo "  helm uninstall todo-app -n todo-app"
echo "  kubectl delete namespace todo-app"
echo ""
