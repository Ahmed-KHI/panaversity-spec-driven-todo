#!/bin/bash
# [Task]: T-E-010
# [From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md §E.10
# 
# Verification script to check deployment health

set -e

NAMESPACE="todo-app"

echo "========================================="
echo "Todo App - Deployment Verification"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check namespace exists
echo "1. Checking namespace..."
if kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Namespace '$NAMESPACE' exists${NC}"
else
    echo -e "${RED}✗ Namespace '$NAMESPACE' not found${NC}"
    exit 1
fi
echo ""

# Check Dapr system
echo "2. Checking Dapr system..."
DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
if [ "$DAPR_PODS" -gt 0 ]; then
    echo -e "${GREEN}✓ Dapr system running ($DAPR_PODS pods)${NC}"
    kubectl get pods -n dapr-system --no-headers | awk '{print "  - " $1 ": " $3}'
else
    echo -e "${RED}✗ Dapr system not found${NC}"
fi
echo ""

# Check pods
echo "3. Checking application pods..."
TOTAL_PODS=$(kubectl get pods -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
RUNNING_PODS=$(kubectl get pods -n $NAMESPACE --no-headers 2>/dev/null | grep Running | wc -l)

if [ "$TOTAL_PODS" -eq 0 ]; then
    echo -e "${RED}✗ No pods found${NC}"
    exit 1
elif [ "$RUNNING_PODS" -eq "$TOTAL_PODS" ]; then
    echo -e "${GREEN}✓ All pods running ($RUNNING_PODS/$TOTAL_PODS)${NC}"
else
    echo -e "${YELLOW}⚠ Some pods not running ($RUNNING_PODS/$TOTAL_PODS)${NC}"
fi

kubectl get pods -n $NAMESPACE --no-headers | awk '{print "  - " $1 ": " $3 " (Ready: " $2 ")"}'
echo ""

# Check services
echo "4. Checking services..."
kubectl get svc -n $NAMESPACE --no-headers | while read line; do
    SVC_NAME=$(echo $line | awk '{print $1}')
    SVC_TYPE=$(echo $line | awk '{print $2}')
    echo -e "  - ${GREEN}$SVC_NAME${NC} (Type: $SVC_TYPE)"
done
echo ""

# Check Dapr components
echo "5. Checking Dapr components..."
COMPONENTS=$(kubectl get components -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
if [ "$COMPONENTS" -gt 0 ]; then
    echo -e "${GREEN}✓ Dapr components configured ($COMPONENTS)${NC}"
    kubectl get components -n $NAMESPACE --no-headers | awk '{print "  - " $1 ": " $2}'
else
    echo -e "${YELLOW}⚠ No Dapr components found${NC}"
fi
echo ""

# Check secrets
echo "6. Checking secrets..."
SECRETS=$(kubectl get secrets -n $NAMESPACE --no-headers 2>/dev/null | grep -v default-token | wc -l)
if [ "$SECRETS" -gt 0 ]; then
    echo -e "${GREEN}✓ Secrets configured ($SECRETS)${NC}"
    kubectl get secrets -n $NAMESPACE --no-headers | grep -v default-token | awk '{print "  - " $1}'
else
    echo -e "${YELLOW}⚠ No secrets found${NC}"
fi
echo ""

# Test backend health endpoint
echo "7. Testing backend health..."
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=backend --no-headers | head -1 | awk '{print $1}')
if [ -n "$BACKEND_POD" ]; then
    HEALTH_CHECK=$(kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- curl -s http://localhost:8000/health 2>/dev/null || echo "failed")
    if [ "$HEALTH_CHECK" != "failed" ]; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
        echo "  Response: $HEALTH_CHECK"
    else
        echo -e "${RED}✗ Backend health check failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No backend pod found${NC}"
fi
echo ""

# Test frontend
echo "8. Testing frontend..."
FRONTEND_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=frontend --no-headers | head -1 | awk '{print $1}')
if [ -n "$FRONTEND_POD" ]; then
    FRONTEND_CHECK=$(kubectl exec -n $NAMESPACE $FRONTEND_POD -c frontend -- curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "failed")
    if [ "$FRONTEND_CHECK" = "200" ]; then
        echo -e "${GREEN}✓ Frontend responding (HTTP 200)${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend returned: $FRONTEND_CHECK${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No frontend pod found${NC}"
fi
echo ""

# Check recent logs for errors
echo "9. Checking recent logs for errors..."
ERROR_COUNT=$(kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=backend --tail=100 --since=5m 2>/dev/null | grep -i error | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No errors in recent logs${NC}"
else
    echo -e "${YELLOW}⚠ Found $ERROR_COUNT error(s) in recent logs${NC}"
    echo "  Run: kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=backend --tail=50"
fi
echo ""

# Check resource usage
echo "10. Checking resource usage..."
echo "  Backend pods:"
kubectl top pods -n $NAMESPACE -l app.kubernetes.io/component=backend 2>/dev/null | tail -n +2 | awk '{print "    " $1 ": CPU=" $2 ", Memory=" $3}' || echo -e "${YELLOW}    ⚠ Metrics not available (install metrics-server)${NC}"
echo ""

# Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo ""
echo "Pods:        $RUNNING_PODS/$TOTAL_PODS running"
echo "Services:    $(kubectl get svc -n $NAMESPACE --no-headers | wc -l)"
echo "Components:  $COMPONENTS Dapr components"
echo "Secrets:     $SECRETS"
echo ""

if [ "$RUNNING_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
    echo -e "${GREEN}✓ Deployment verification PASSED${NC}"
    echo ""
    echo "Next steps:"
    echo "  - Access frontend: minikube service todo-app-frontend -n todo-app --url"
    echo "  - View logs: kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f"
    echo "  - Dapr dashboard: dapr dashboard -k -p 9999"
    exit 0
else
    echo -e "${YELLOW}⚠ Deployment verification had warnings${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check pod status: kubectl describe pod <pod-name> -n todo-app"
    echo "  - View logs: kubectl logs <pod-name> -n todo-app -c backend"
    echo "  - Check events: kubectl get events -n todo-app --sort-by=.lastTimestamp"
    exit 1
fi
