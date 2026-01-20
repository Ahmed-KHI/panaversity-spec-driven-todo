#!/bin/bash

# [Task]: T074
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 11
# [Description]: Load tests to verify HPA autoscaling

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Load Tests (HPA Validation)"
echo "========================================="
echo ""

# Configuration
BASE_URL="http://todo.local"
REQUESTS=1000
CONCURRENCY=100
NAMESPACE="default"

# Check if ApacheBench (ab) is installed
if ! command -v ab &> /dev/null; then
    echo "⚠️  ApacheBench (ab) not found"
    echo ""
    echo "Install it:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS: ab is pre-installed"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  Ubuntu/Debian: sudo apt-get install apache2-utils"
        echo "  RHEL/CentOS: sudo yum install httpd-tools"
    fi
    echo ""
    echo "Skipping load tests..."
    exit 1
fi

echo "✅ ApacheBench found: $(ab -V | head -1)"
echo ""

# Get initial HPA status
echo "========================================="
echo "Initial HPA Status"
echo "========================================="
echo ""
kubectl get hpa -n "$NAMESPACE"
echo ""

# Get initial pod count
INITIAL_FRONTEND_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=frontend --no-headers | wc -l)
INITIAL_BACKEND_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend --no-headers | wc -l)

echo "Initial pod counts:"
echo "  Frontend: $INITIAL_FRONTEND_PODS pods"
echo "  Backend: $INITIAL_BACKEND_PODS pods"
echo ""

# Run load test
echo "========================================="
echo "Running Load Test"
echo "========================================="
echo ""
echo "Target: $BASE_URL/"
echo "Requests: $REQUESTS"
echo "Concurrency: $CONCURRENCY"
echo ""

echo "Starting load test... (this will take ~30 seconds)"
ab -n $REQUESTS -c $CONCURRENCY "$BASE_URL/" > /tmp/load-test-results.txt 2>&1

# Display results
echo ""
echo "Load test complete!"
echo ""
echo "Results:"
grep "Requests per second" /tmp/load-test-results.txt || true
grep "Time per request" /tmp/load-test-results.txt || true
grep "Failed requests" /tmp/load-test-results.txt || true
echo ""

# Monitor HPA for scale-up
echo "========================================="
echo "Monitoring HPA Scale-Up (60 seconds)"
echo "========================================="
echo ""

echo "Watching for pod scaling..."
for i in {1..12}; do
    echo "Check $i/12 (${i}0 seconds elapsed)"
    kubectl get hpa -n "$NAMESPACE"
    kubectl get pods -n "$NAMESPACE" -l 'app.kubernetes.io/component in (frontend,backend)'
    echo ""
    
    sleep 5
done

# Get final pod count
FINAL_FRONTEND_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=frontend --no-headers | wc -l)
FINAL_BACKEND_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend --no-headers | wc -l)

echo "========================================="
echo "Load Test Summary"
echo "========================================="
echo ""
echo "Initial pods:"
echo "  Frontend: $INITIAL_FRONTEND_PODS → Final: $FINAL_FRONTEND_PODS"
echo "  Backend: $INITIAL_BACKEND_PODS → Final: $FINAL_BACKEND_PODS"
echo ""

if [ $FINAL_FRONTEND_PODS -gt $INITIAL_FRONTEND_PODS ] || [ $FINAL_BACKEND_PODS -gt $INITIAL_BACKEND_PODS ]; then
    echo "✅ HPA triggered scale-up successfully!"
    echo ""
    echo "Autoscaling is working correctly."
    echo ""
    echo "Note: Pods will scale down after ~5 minutes of low load."
else
    echo "⚠️  No scale-up detected"
    echo ""
    echo "Possible reasons:"
    echo "1. Load was not high enough to trigger scaling threshold (70% CPU)"
    echo "2. HPA needs more time to react (check again in 1-2 minutes)"
    echo "3. Pods already at maximum replicas"
    echo ""
    echo "Check HPA metrics:"
    echo "  kubectl get hpa -n $NAMESPACE"
    echo "  kubectl top pods -n $NAMESPACE"
fi

echo ""
