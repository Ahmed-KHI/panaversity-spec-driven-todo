#!/bin/bash

# [Task]: T001-T007
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 1
# [Description]: Verify all required tools are installed for Phase IV

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Prerequisites Verification"
echo "========================================="
echo ""

ERRORS=0
WARNINGS=0

# T001: Verify Docker Desktop 4.53+
echo "🐳 Checking Docker Desktop..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    echo "   ✅ Docker version: $DOCKER_VERSION"
    
    # Check if Docker is running
    if docker info &> /dev/null; then
        echo "   ✅ Docker daemon is running"
    else
        echo "   ❌ Docker daemon is not running"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ❌ Docker is not installed"
    echo "      Install from: https://www.docker.com/products/docker-desktop"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# T002: Check Gordon (Docker AI) - optional
echo "🤖 Checking Gordon (Docker AI)..."
if docker ai --help &> /dev/null; then
    echo "   ✅ Gordon (Docker AI) is available"
    echo "      Try: docker ai 'optimize my Dockerfile'"
else
    echo "   ⚠️  Gordon (Docker AI) not available (optional)"
    echo "      Enable in Docker Desktop → Settings → Beta features"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# T003: Verify Minikube 1.33+
echo "☸️  Checking Minikube..."
if command -v minikube &> /dev/null; then
    MINIKUBE_VERSION=$(minikube version --short 2>/dev/null | grep -oP '\d+\.\d+\.\d+')
    echo "   ✅ Minikube version: v$MINIKUBE_VERSION"
    
    # Check if Minikube is running
    if minikube status &> /dev/null; then
        echo "   ✅ Minikube cluster is running"
        MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "N/A")
        echo "      IP: $MINIKUBE_IP"
    else
        echo "   ⚠️  Minikube cluster is not running"
        echo "      Run: ./scripts/setup-minikube.sh"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ❌ Minikube is not installed"
    echo "      Install from: https://minikube.sigs.k8s.io/docs/start/"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# T004: Verify kubectl 1.31+
echo "🔧 Checking kubectl..."
if command -v kubectl &> /dev/null; then
    KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null | grep -oP '\d+\.\d+\.\d+' || kubectl version --client -o json 2>/dev/null | grep -oP '"gitVersion":"v\K\d+\.\d+\.\d+')
    echo "   ✅ kubectl version: v$KUBECTL_VERSION"
    
    # Check if kubectl can connect to cluster
    if kubectl cluster-info &> /dev/null; then
        echo "   ✅ kubectl can connect to cluster"
    else
        echo "   ⚠️  kubectl cannot connect to cluster"
        echo "      Run: ./scripts/setup-minikube.sh"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ❌ kubectl is not installed"
    echo "      Install from: https://kubernetes.io/docs/tasks/tools/"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# T005: Verify Helm 3.16+
echo "⎈  Checking Helm..."
if command -v helm &> /dev/null; then
    HELM_VERSION=$(helm version --short 2>/dev/null | grep -oP '\d+\.\d+\.\d+')
    echo "   ✅ Helm version: v$HELM_VERSION"
else
    echo "   ❌ Helm is not installed"
    echo "      Install from: https://helm.sh/docs/intro/install/"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# T006: Check kubectl-ai - optional
echo "🧠 Checking kubectl-ai..."
if command -v kubectl-ai &> /dev/null; then
    echo "   ✅ kubectl-ai is installed"
    
    # Check if OpenAI API key is configured
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "   ✅ OPENAI_API_KEY environment variable is set"
    else
        echo "   ⚠️  OPENAI_API_KEY not set"
        echo "      Set with: export OPENAI_API_KEY='your-key'"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ⚠️  kubectl-ai not installed (optional)"
    echo "      Install: brew install kubectl-ai"
    echo "      Or: go install github.com/sozercan/kubectl-ai@latest"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# T007: Check Kagent - optional
echo "📊 Checking Kagent (K8sGPT)..."
if command -v k8sgpt &> /dev/null; then
    echo "   ✅ Kagent (K8sGPT) is installed"
    K8SGPT_VERSION=$(k8sgpt version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
    echo "      Version: $K8SGPT_VERSION"
else
    echo "   ⚠️  Kagent (K8sGPT) not installed (optional)"
    echo "      Install from: https://docs.k8sgpt.ai/getting-started/installation/"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All prerequisites met!" -
    echo ""
    echo "You are ready to proceed with Phase IV implementation."
    echo ""
    echo "Next Steps:"
    echo "1. Setup Minikube: ./scripts/setup-minikube.sh"
    echo "2. Build Docker images: ./scripts/build-images.sh"
    echo "3. Deploy application: ./scripts/deploy.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "✅ Required prerequisites met"
    echo "⚠️  $WARNINGS optional warning(s)"
    echo ""
    echo "You can proceed, but consider installing optional tools for enhanced DevOps experience."
    echo ""
    echo "Next Steps:"
    echo "1. Setup Minikube: ./scripts/setup-minikube.sh"
    echo "2. Build Docker images: ./scripts/build-images.sh"
    echo "3. Deploy application: ./scripts/deploy.sh"
    exit 0
else
    echo "❌ $ERRORS critical error(s) found"
    echo "⚠️  $WARNINGS optional warning(s)"
    echo ""
    echo "Please install missing required tools before proceeding."
    exit 1
fi
