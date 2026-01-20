#!/bin/bash

# [Task]: T068
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 10
# [Description]: Port forward services for local access (fallback if ingress fails)

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Port Forwarding Services"
echo "========================================="
echo ""

# Configuration
NAMESPACE="default"
RELEASE_NAME="todo"

# Check if kubectl can connect
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ ERROR: kubectl cannot connect to cluster"
    exit 1
fi

echo "✅ kubectl connected to cluster"
echo ""

# Get service names
FRONTEND_SERVICE=$(kubectl get svc -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME",app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
BACKEND_SERVICE=$(kubectl get svc -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME",app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$FRONTEND_SERVICE" ] || [ -z "$BACKEND_SERVICE" ]; then
    echo "❌ ERROR: Services not found. Is the application deployed?"
    echo "Run: ./scripts/deploy.sh"
    exit 1
fi

echo "Found services:"
echo "  Frontend: $FRONTEND_SERVICE"
echo "  Backend: $BACKEND_SERVICE"
echo ""

echo "========================================="
echo "Starting Port Forwarding"
echo "========================================="
echo ""

echo "Frontend will be available at: http://localhost:3000"
echo "Backend will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop port forwarding"
echo ""

# Start port forwarding in parallel
kubectl port-forward -n "$NAMESPACE" "svc/$FRONTEND_SERVICE" 3000:3000 &
FRONTEND_PID=$!

kubectl port-forward -n "$NAMESPACE" "svc/$BACKEND_SERVICE" 8000:8000 &
BACKEND_PID=$!

# Trap Ctrl+C and kill background processes
trap "echo ''; echo 'Stopping port forwarding...'; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for both processes
wait $FRONTEND_PID $BACKEND_PID
