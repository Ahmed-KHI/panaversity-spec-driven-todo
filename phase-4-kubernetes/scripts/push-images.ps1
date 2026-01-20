# [Task]: T028
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 4
# [Description]: Push Docker images to Docker Hub registry (PowerShell version)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Pushing Images to Docker Hub" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$FRONTEND_IMAGE = "ahmed-khi/todo-frontend"
$BACKEND_IMAGE = "ahmed-khi/todo-backend"
$VERSION = "v4.0.0"

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ ERROR: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop"
    exit 1
}

# Check if logged in to Docker Hub
$dockerInfo = docker info 2>$null | Out-String
if (-not ($dockerInfo -match "Username:")) {
    Write-Host "⚠️  Not logged in to Docker Hub" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please login:"
    docker login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker login failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Docker is running and authenticated" -ForegroundColor Green
Write-Host ""

# Push Frontend Image
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "1/2: Pushing Frontend Image" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📤 Pushing ${FRONTEND_IMAGE}:${VERSION}..." -ForegroundColor Cyan
docker push "${FRONTEND_IMAGE}:${VERSION}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend image pushed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to push frontend image" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📤 Pushing ${FRONTEND_IMAGE}:latest..." -ForegroundColor Cyan
docker push "${FRONTEND_IMAGE}:latest"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend latest tag pushed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Failed to push frontend latest tag (non-critical)" -ForegroundColor Yellow
}

Write-Host ""

# Push Backend Image
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "2/2: Pushing Backend Image" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📤 Pushing ${BACKEND_IMAGE}:${VERSION}..." -ForegroundColor Cyan
docker push "${BACKEND_IMAGE}:${VERSION}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend image pushed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to push backend image" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📤 Pushing ${BACKEND_IMAGE}:latest..." -ForegroundColor Cyan
docker push "${BACKEND_IMAGE}:latest"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend latest tag pushed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Failed to push backend latest tag (non-critical)" -ForegroundColor Yellow
}

Write-Host ""

# Verify images in registry (T029)
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Verifying Images in Registry" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 Testing pull for frontend..." -ForegroundColor Cyan
docker pull "${FRONTEND_IMAGE}:${VERSION}" 2>$null | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Frontend image pull successful" -ForegroundColor Green
} else {
    Write-Host "   ❌ Frontend image pull failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 Testing pull for backend..." -ForegroundColor Cyan
docker pull "${BACKEND_IMAGE}:${VERSION}" 2>$null | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backend image pull successful" -ForegroundColor Green
} else {
    Write-Host "   ❌ Backend image pull failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Images Pushed and Verified!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Public Registry URLs:"
Write-Host "  Frontend: https://hub.docker.com/r/ahmed-khi/todo-frontend" -ForegroundColor Cyan
Write-Host "  Backend:  https://hub.docker.com/r/ahmed-khi/todo-backend" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  Deploy to Kubernetes: .\scripts\deploy.ps1"
Write-Host ""
