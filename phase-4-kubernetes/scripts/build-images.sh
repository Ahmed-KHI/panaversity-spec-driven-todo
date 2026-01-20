#!/bin/bash

# [Task]: T027
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 4
# [Description]: Build frontend and backend Docker images with version tags

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Building Docker Images"
echo "========================================="
echo ""

# Configuration
FRONTEND_IMAGE="ahmed-khi/todo-frontend"
BACKEND_IMAGE="ahmed-khi/todo-backend"
VERSION="v4.0.0"
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "Project Root: $PROJECT_ROOT"
echo "Frontend Image: ${FRONTEND_IMAGE}:${VERSION}"
echo "Backend Image: ${BACKEND_IMAGE}:${VERSION}"
echo ""

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ ERROR: Docker is not running"
    echo "Please start Docker Desktop"
    exit 1
fi

# Build Frontend Image
echo "========================================="
echo "1/2: Building Frontend Image"
echo "========================================="
echo ""

cd "$PROJECT_ROOT"

echo "🔨 Building ${FRONTEND_IMAGE}:${VERSION}..."
echo "   Context: phase-2-fullstack/frontend"
echo "   Dockerfile: phase-4-kubernetes/docker/frontend/Dockerfile"
echo ""

docker build \
    -t "${FRONTEND_IMAGE}:${VERSION}" \
    -t "${FRONTEND_IMAGE}:latest" \
    -f phase-4-kubernetes/docker/frontend/Dockerfile \
    phase-2-fullstack/frontend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Frontend image built successfully"
    
    # Check image size
    FRONTEND_SIZE=$(docker images "${FRONTEND_IMAGE}:${VERSION}" --format "{{.Size}}")
    echo "   Image size: $FRONTEND_SIZE"
    
    # Verify size is under target (200MB)
    SIZE_MB=$(docker images "${FRONTEND_IMAGE}:${VERSION}" --format "{{.Size}}" | sed 's/MB//' | awk '{print int($1)}')
    if [ "$SIZE_MB" -lt 200 ] 2>/dev/null; then
        echo "   ✅ Size under target (< 200MB)"
    else
        echo "   ⚠️  Size may exceed target (200MB)"
    fi
else
    echo ""
    echo "❌ Frontend build failed"
    exit 1
fi

echo ""

# Build Backend Image
echo "========================================="
echo "2/2: Building Backend Image"
echo "========================================="
echo ""

echo "🔨 Building ${BACKEND_IMAGE}:${VERSION}..."
echo "   Context: phase-2-fullstack/backend"
echo "   Dockerfile: phase-4-kubernetes/docker/backend/Dockerfile"
echo ""

docker build \
    -t "${BACKEND_IMAGE}:${VERSION}" \
    -t "${BACKEND_IMAGE}:latest" \
    -f phase-4-kubernetes/docker/backend/Dockerfile \
    phase-2-fullstack/backend

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Backend image built successfully"
    
    # Check image size
    BACKEND_SIZE=$(docker images "${BACKEND_IMAGE}:${VERSION}" --format "{{.Size}}")
    echo "   Image size: $BACKEND_SIZE"
    
    # Verify size is under target (150MB)
    SIZE_MB=$(docker images "${BACKEND_IMAGE}:${VERSION}" --format "{{.Size}}" | sed 's/MB//' | awk '{print int($1)}')
    if [ "$SIZE_MB" -lt 150 ] 2>/dev/null; then
        echo "   ✅ Size under target (< 150MB)"
    else
        echo "   ⚠️  Size may exceed target (150MB)"
    fi
else
    echo ""
    echo "❌ Backend build failed"
    exit 1
fi

echo ""

# Summary
echo "========================================="
echo "✅ Build Complete!"
echo "========================================="
echo ""

echo "Built Images:"
docker images | grep -E "ahmed-khi/todo-(frontend|backend)" | grep -E "${VERSION}|latest"

echo ""
echo "Next Steps:"
echo "  Option 1 (Minikube): Load images locally"
echo "    ./scripts/load-images-minikube.sh"
echo ""
echo "  Option 2 (Docker Hub): Push to registry"
echo "    ./scripts/push-images.sh"
echo ""
