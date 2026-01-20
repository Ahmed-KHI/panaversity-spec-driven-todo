#!/bin/bash

# [Task]: T028
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 4
# [Description]: Push Docker images to Docker Hub registry

set -e  # Exit on error

echo "========================================="
echo "Phase IV: Pushing Images to Docker Hub"
echo "========================================="
echo ""

# Configuration
FRONTEND_IMAGE="ahmed-khi/todo-frontend"
BACKEND_IMAGE="ahmed-khi/todo-backend"
VERSION="v4.0.0"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ ERROR: Docker is not running"
    echo "Please start Docker Desktop"
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username:"; then
    echo "⚠️  Not logged in to Docker Hub"
    echo ""
    echo "Please login:"
    docker login
    
    if [ $? -ne 0 ]; then
        echo "❌ Docker login failed"
        exit 1
    fi
fi

echo "✅ Docker is running and authenticated"
echo ""

# Push Frontend Image
echo "========================================="
echo "1/2: Pushing Frontend Image"
echo "========================================="
echo ""

echo "📤 Pushing ${FRONTEND_IMAGE}:${VERSION}..."
docker push "${FRONTEND_IMAGE}:${VERSION}"

if [ $? -eq 0 ]; then
    echo "✅ Frontend image pushed successfully"
else
    echo "❌ Failed to push frontend image"
    exit 1
fi

echo ""
echo "📤 Pushing ${FRONTEND_IMAGE}:latest..."
docker push "${FRONTEND_IMAGE}:latest"

if [ $? -eq 0 ]; then
    echo "✅ Frontend latest tag pushed successfully"
else
    echo "⚠️  Failed to push frontend latest tag (non-critical)"
fi

echo ""

# Push Backend Image
echo "========================================="
echo "2/2: Pushing Backend Image"
echo "========================================="
echo ""

echo "📤 Pushing ${BACKEND_IMAGE}:${VERSION}..."
docker push "${BACKEND_IMAGE}:${VERSION}"

if [ $? -eq 0 ]; then
    echo "✅ Backend image pushed successfully"
else
    echo "❌ Failed to push backend image"
    exit 1
fi

echo ""
echo "📤 Pushing ${BACKEND_IMAGE}:latest..."
docker push "${BACKEND_IMAGE}:latest"

if [ $? -eq 0 ]; then
    echo "✅ Backend latest tag pushed successfully"
else
    echo "⚠️  Failed to push backend latest tag (non-critical)"
fi

echo ""

# Verify images in registry (T029)
echo "========================================="
echo "Verifying Images in Registry"
echo "========================================="
echo ""

echo "🔍 Testing pull for frontend..."
docker pull "${FRONTEND_IMAGE}:${VERSION}" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Frontend image pull successful"
else
    echo "   ❌ Frontend image pull failed"
    exit 1
fi

echo ""
echo "🔍 Testing pull for backend..."
docker pull "${BACKEND_IMAGE}:${VERSION}" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Backend image pull successful"
else
    echo "   ❌ Backend image pull failed"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ Images Pushed and Verified!"
echo "========================================="
echo ""
echo "Public Registry URLs:"
echo "  Frontend: https://hub.docker.com/r/ahmed-khi/todo-frontend"
echo "  Backend:  https://hub.docker.com/r/ahmed-khi/todo-backend"
echo ""
echo "Next Steps:"
echo "  Deploy to Kubernetes: ./scripts/deploy.sh"
echo ""
