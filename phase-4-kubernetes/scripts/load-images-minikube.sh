#!/bin/bash

# [Task]: T028
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 4
# [Description]: Load Docker images into Minikube for local deployment

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Loading Images into Minikube"
echo "========================================="
echo ""

# Configuration
FRONTEND_IMAGE="ahmed-khi/todo-frontend"
BACKEND_IMAGE="ahmed-khi/todo-backend"
VERSION="v4.0.0"

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ ERROR: Minikube is not running"
    echo "Run: ./scripts/setup-minikube.sh"
    exit 1
fi

echo "✅ Minikube is running"
echo ""

# Load Frontend Image
echo "📦 Loading frontend image into Minikube..."
echo "   Image: ${FRONTEND_IMAGE}:${VERSION}"
minikube image load "${FRONTEND_IMAGE}:${VERSION}"

if [ $? -eq 0 ]; then
    echo "   ✅ Frontend image loaded"
else
    echo "   ❌ Failed to load frontend image"
    exit 1
fi

echo ""

# Load Backend Image
echo "📦 Loading backend image into Minikube..."
echo "   Image: ${BACKEND_IMAGE}:${VERSION}"
minikube image load "${BACKEND_IMAGE}:${VERSION}"

if [ $? -eq 0 ]; then
    echo "   ✅ Backend image loaded"
else
    echo "   ❌ Failed to load backend image"
    exit 1
fi

echo ""

# Verify images are loaded
echo "========================================="
echo "Verifying Loaded Images"
echo "========================================="
echo ""

echo "Images in Minikube:"
minikube image ls | grep ahmed-khi

echo ""
echo "========================================="
echo "✅ Images Loaded Successfully!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "  Deploy application: ./scripts/deploy.sh"
echo ""
