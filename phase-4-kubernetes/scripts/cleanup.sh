#!/bin/bash

# [Task]: T070
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 10
# [Description]: Cleanup all Kubernetes resources and stop Minikube

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Cleanup Kubernetes Resources"
echo "========================================="
echo ""

# Configuration
RELEASE_NAME="todo"
NAMESPACE="default"

# Check if kubectl can connect
if ! kubectl cluster-info &> /dev/null; then
    echo "⚠️  kubectl cannot connect to cluster"
    echo "Minikube may already be stopped"
else
    echo "✅ kubectl connected to cluster"
    echo ""
    
    # Uninstall Helm release
    if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        echo "🗑️  Uninstalling Helm release '$RELEASE_NAME'..."
        helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"
        echo "✅ Helm release uninstalled"
    else
        echo "ℹ️  Helm release '$RELEASE_NAME' not found"
    fi
    
    echo ""
    
    # Delete secrets
    echo "🗑️  Deleting secrets..."
    kubectl delete secret todo-database-secret -n "$NAMESPACE" --ignore-not-found
    kubectl delete secret todo-openai-secret -n "$NAMESPACE" --ignore-not-found
    kubectl delete secret todo-auth-secret -n "$NAMESPACE" --ignore-not-found
    echo "✅ Secrets deleted"
    
    echo ""
    
    # Verify cleanup
    echo "Checking for remaining resources..."
    REMAINING_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME" 2>/dev/null | wc -l)
    if [ "$REMAINING_PODS" -gt 1 ]; then
        echo "⚠️  Some pods still terminating..."
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"
    else
        echo "✅ All resources cleaned up"
    fi
fi

echo ""

# Stop Minikube
read -p "Do you want to stop Minikube? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Stopping Minikube..."
    minikube stop
    echo "✅ Minikube stopped"
    
    echo ""
    read -p "Do you want to delete Minikube cluster? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Deleting Minikube cluster..."
        minikube delete
        echo "✅ Minikube cluster deleted"
    fi
else
    echo "ℹ️  Minikube left running"
fi

echo ""
echo "========================================="
echo "✅ Cleanup Complete!"
echo "========================================="
echo ""
