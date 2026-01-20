#!/bin/bash

# [Task]: T072
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 11
# [Description]: Smoke tests for Phase IV deployment validation

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Smoke Tests"
echo "========================================="
echo ""

# Configuration
BASE_URL="http://todo.local"
PASSED=0
FAILED=0

# Test helper function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "🧪 Testing: $test_name"
    if eval "$test_command"; then
        echo "   ✅ PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "   ❌ FAILED"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Test 1: Frontend health check
run_test "Frontend health endpoint" \
    "curl -f -s ${BASE_URL}/api/health | grep -q 'ok'"

# Test 2: Backend health endpoint
run_test "Backend health endpoint" \
    "curl -f -s ${BASE_URL}/api/health | grep -q 'ok'"

# Test 3: Frontend is accessible
run_test "Frontend home page" \
    "curl -f -s ${BASE_URL} | grep -q 'html'"

# Test 4: Backend API is accessible
run_test "Backend API root" \
    "curl -f -s ${BASE_URL}/api | grep -q 'detail\\|message\\|version'"

# Test 5: Database connectivity (via backend health)
run_test "Database connectivity" \
    "curl -f -s ${BASE_URL}/api/health | grep -q 'database'"

echo "========================================="
echo "Smoke Test Summary"
echo "========================================="
echo ""
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All smoke tests passed!"
    echo ""
    echo "Application is healthy and ready for use."
    exit 0
else
    echo "❌ Some smoke tests failed!"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check pod status: kubectl get pods"
    echo "2. Check service status: kubectl get svc"
    echo "3. Check ingress status: kubectl get ingress"
    echo "4. View frontend logs: kubectl logs -l app.kubernetes.io/component=frontend --tail=50"
    echo "5. View backend logs: kubectl logs -l app.kubernetes.io/component=backend --tail=50"
    echo ""
    echo "If ingress is not working, try port forwarding:"
    echo "  ./scripts/port-forward.sh"
    exit 1
fi
