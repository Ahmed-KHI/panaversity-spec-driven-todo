#!/bin/bash

# [Task]: T066
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 10
# [Description]: Deploy Phase IV Todo Application to Kubernetes using Helm

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Deploying to Kubernetes"
echo "========================================="
echo ""

# Configuration
RELEASE_NAME="todo"
NAMESPACE="default"
HELM_CHART="./helm-charts/todo"
VALUES_FILE="./helm-charts/todo/values-dev.yaml"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ ERROR: Minikube is not running"
    echo "Run: ./scripts/setup-minikube.sh"
    exit 1
fi

echo "✅ Minikube is running"
echo ""

# Check if kubectl can connect
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ ERROR: kubectl cannot connect to cluster"
    exit 1
fi

echo "✅ kubectl connected to cluster"
echo ""

# Create secrets if they don't exist
echo "🔒 Creating Kubernetes Secrets..."
echo ""

# Database secret
if kubectl get secret todo-database-secret -n "$NAMESPACE" &> /dev/null; then
    echo "   ✅ Secret 'todo-database-secret' already exists"
else
    echo "   📝 Creating 'todo-database-secret'..."
    kubectl create secret generic todo-database-secret \
        -n "$NAMESPACE" \
        --from-literal=POSTGRES_PASSWORD=postgres123 \
        --from-literal=DATABASE_URL="postgresql://todo_user:postgres123@todo-postgres:5432/todo_db"
    echo "   ✅ Created 'todo-database-secret'"
fi

# OpenAI API secret
if kubectl get secret todo-openai-secret -n "$NAMESPACE" &> /dev/null; then
    echo "   ✅ Secret 'todo-openai-secret' already exists"
else
    echo "   📝 Creating 'todo-openai-secret'..."
    # Check if OPENAI_API_KEY environment variable is set
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "   ⚠️  OPENAI_API_KEY not set, using placeholder"
        OPENAI_KEY="sk-placeholder-key-for-development"
    else
        OPENAI_KEY="$OPENAI_API_KEY"
    fi
    kubectl create secret generic todo-openai-secret \
        -n "$NAMESPACE" \
        --from-literal=OPENAI_API_KEY="$OPENAI_KEY"
    echo "   ✅ Created 'todo-openai-secret'"
fi

# Better Auth secret
if kubectl get secret todo-auth-secret -n "$NAMESPACE" &> /dev/null; then
    echo "   ✅ Secret 'todo-auth-secret' already exists"
else
    echo "   📝 Creating 'todo-auth-secret'..."
    AUTH_SECRET=$(openssl rand -base64 32)
    kubectl create secret generic todo-auth-secret \
        -n "$NAMESPACE" \
        --from-literal=BETTER_AUTH_SECRET="$AUTH_SECRET" \
        --from-literal=BETTER_AUTH_URL="http://todo.local"
    echo "   ✅ Created 'todo-auth-secret'"
fi

echo ""

# Check if Helm chart exists
if [ ! -d "$HELM_CHART" ]; then
    echo "❌ ERROR: Helm chart not found at $HELM_CHART"
    exit 1
fi

# Check if release already exists
if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
    echo "⚠️  Helm release '$RELEASE_NAME' already exists"
    read -p "Do you want to upgrade it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Upgrading Helm release..."
        helm upgrade "$RELEASE_NAME" "$HELM_CHART" \
            -n "$NAMESPACE" \
            -f "$VALUES_FILE"
        echo "✅ Helm release upgraded"
    else
        echo "ℹ️  Skipping deployment"
        exit 0
    fi
else
    echo "📦 Installing Helm chart..."
    helm install "$RELEASE_NAME" "$HELM_CHART" \
        -n "$NAMESPACE" \
        -f "$VALUES_FILE"
    echo "✅ Helm chart installed"
fi

echo ""

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready (timeout: 300s)..."
echo ""

# Wait for frontend
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/component=frontend \
    -n "$NAMESPACE" \
    --timeout=300s || true

# Wait for backend
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/component=backend \
    -n "$NAMESPACE" \
    --timeout=300s || true

# Wait for postgres
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/component=database \
    -n "$NAMESPACE" \
    --timeout=300s || true

echo ""

# Display deployment status
echo "========================================="
echo "Deployment Status"
echo "========================================="
echo ""

echo "Pods:"
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
echo ""

echo "Services:"
kubectl get svc -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
echo ""

echo "Ingress:"
kubectl get ingress -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
echo ""

echo "HPA:"
kubectl get hpa -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Application URLs:"
echo "  → Frontend: http://todo.local"
echo "  → Backend API: http://todo.local/api"
echo ""
echo "Minikube IP: $MINIKUBE_IP"
echo ""
echo "Verify /etc/hosts contains:"
echo "  $MINIKUBE_IP todo.local"
echo ""
echo "Health Checks:"
echo "  curl http://todo.local/api/health"
echo "  curl http://todo.local/api/health"
echo ""
echo "View Logs:"
echo "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=frontend --tail=50"
echo "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=backend --tail=50"
echo ""
