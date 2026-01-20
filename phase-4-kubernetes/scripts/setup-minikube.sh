#!/bin/bash

# [Task]: T008
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 1
# [Description]: Initialize Minikube cluster with required configuration and addons

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Minikube Cluster Setup"
echo "========================================="
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ ERROR: Minikube is not installed"
    echo "Please install Minikube 1.33+ from https://minikube.sigs.k8s.io/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ ERROR: kubectl is not installed"
    echo "Please install kubectl 1.31+ from https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ ERROR: Docker is not running"
    echo "Please start Docker Desktop 4.53+"
    exit 1
fi

echo "✅ Prerequisites verified"
echo ""

# Check if Minikube is already running
if minikube status &> /dev/null; then
    echo "⚠️  Minikube cluster already exists"
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Deleting existing cluster..."
        minikube delete
    else
        echo "ℹ️  Using existing cluster"
        echo ""
        echo "Enabling required addons..."
        minikube addons enable ingress
        minikube addons enable metrics-server
        echo ""
        echo "✅ Minikube setup complete!"
        echo ""
        echo "Cluster Info:"
        kubectl cluster-info
        echo ""
        echo "Nodes:"
        kubectl get nodes
        echo ""
        echo "Enabled Addons:"
        minikube addons list | grep enabled
        exit 0
    fi
fi

echo "🚀 Starting Minikube cluster..."
echo "   - CPUs: 4"
echo "   - Memory: 8192 MB (8 GB)"
echo "   - Driver: docker"
echo ""

minikube start \
    --cpus=4 \
    --memory=8192 \
    --driver=docker \
    --kubernetes-version=v1.31.0

echo ""
echo "✅ Minikube cluster started"
echo ""

# Enable required addons
echo "📦 Enabling ingress addon..."
minikube addons enable ingress

echo "📊 Enabling metrics-server addon..."
minikube addons enable metrics-server

echo ""
echo "✅ Addons enabled"
echo ""

# Wait for ingress controller to be ready
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=90s

echo ""
echo "✅ Ingress controller ready"
echo ""

# Add hosts entry
echo "📝 Adding /etc/hosts entry for todo.local..."
MINIKUBE_IP=$(minikube ip)

if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # macOS and Linux
    if grep -q "todo.local" /etc/hosts; then
        echo "   - Entry already exists, updating IP..."
        sudo sed -i.bak "s/^.*todo.local.*$/${MINIKUBE_IP} todo.local/" /etc/hosts
    else
        echo "   - Adding new entry..."
        echo "${MINIKUBE_IP} todo.local" | sudo tee -a /etc/hosts > /dev/null
    fi
    echo "   - Added: ${MINIKUBE_IP} todo.local"
else
    echo "⚠️  Please add this entry to /etc/hosts manually:"
    echo "   ${MINIKUBE_IP} todo.local"
fi

echo ""
echo "========================================="
echo "✅ Minikube Setup Complete!"
echo "========================================="
echo ""
echo "Cluster Info:"
kubectl cluster-info
echo ""
echo "Nodes:"
kubectl get nodes
echo ""
echo "Enabled Addons:"
minikube addons list | grep enabled
echo ""
echo "Minikube IP: ${MINIKUBE_IP}"
echo "Application will be accessible at: http://todo.local"
echo ""
echo "Next Steps:"
echo "1. Build Docker images: ./scripts/build-images.sh"
echo "2. Deploy application: ./scripts/deploy.sh"
echo "3. Access application: http://todo.local"
echo ""
