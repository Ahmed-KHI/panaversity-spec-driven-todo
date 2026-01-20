# [Task]: T027
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 4
# [Description]: Build frontend and backend Docker images with version tags (PowerShell version)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Building Docker Images" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$FRONTEND_IMAGE = "ahmed-khi/todo-frontend"
$BACKEND_IMAGE = "ahmed-khi/todo-backend"
$VERSION = "v4.0.0"
$PROJECT_ROOT = (Get-Item (Split-Path -Parent $PSScriptRoot)).Parent.FullName

Write-Host "Project Root: $PROJECT_ROOT"
Write-Host "Frontend Image: ${FRONTEND_IMAGE}:${VERSION}"
Write-Host "Backend Image: ${BACKEND_IMAGE}:${VERSION}"
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ ERROR: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop"
    exit 1
}

# Build Frontend Image
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "1/2: Building Frontend Image" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PROJECT_ROOT

Write-Host "🔨 Building ${FRONTEND_IMAGE}:${VERSION}..." -ForegroundColor Cyan
Write-Host "   Context: phase-2-fullstack\frontend"
Write-Host "   Dockerfile: phase-4-kubernetes\docker\frontend\Dockerfile"
Write-Host ""

docker build `
    -t "${FRONTEND_IMAGE}:${VERSION}" `
    -t "${FRONTEND_IMAGE}:latest" `
    -f phase-4-kubernetes\docker\frontend\Dockerfile `
    phase-2-fullstack\frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Frontend image built successfully" -ForegroundColor Green
    
    # Check image size
    $frontendSize = (docker images "${FRONTEND_IMAGE}:${VERSION}" --format "{{.Size}}")
    Write-Host "   Image size: $frontendSize"
    
    # Verify size is under target (200MB)
    if ($frontendSize -match '(\d+)MB') {
        $sizeMB = [int]$matches[1]
        if ($sizeMB -lt 200) {
            Write-Host "   Size under target (200MB)" -ForegroundColor Green
        } else {
            Write-Host "   Size may exceed target (200MB)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Build Backend Image
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "2/2: Building Backend Image" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔨 Building ${BACKEND_IMAGE}:${VERSION}..." -ForegroundColor Cyan
Write-Host "   Context: phase-2-fullstack\backend"
Write-Host "   Dockerfile: phase-4-kubernetes\docker\backend\Dockerfile"
Write-Host ""

docker build `
    -t "${BACKEND_IMAGE}:${VERSION}" `
    -t "${BACKEND_IMAGE}:latest" `
    -f phase-4-kubernetes\docker\backend\Dockerfile `
    phase-2-fullstack\backend

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Backend image built successfully" -ForegroundColor Green
    
    # Check image size
    $backendSize = (docker images "${BACKEND_IMAGE}:${VERSION}" --format "{{.Size}}")
    Write-Host "   Image size: $backendSize"
    
    # Verify size is under target (150MB)
    if ($backendSize -match '(\d+)MB') {
        $sizeMB = [int]$matches[1]
        if ($sizeMB -lt 150) {
            Write-Host "   Size under target (150MB)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Size may exceed target (150MB)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ Backend build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Build Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Built Images:"
docker images | Select-String "ahmed-khi/todo-(frontend|backend)" | Select-String "${VERSION}|latest"

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  Option 1 (Minikube): Load images locally"
Write-Host "    .\scripts\load-images-minikube.ps1"
Write-Host ""
Write-Host "  Option 2 (Docker Hub): Push to registry"
Write-Host "    .\scripts\push-images.ps1"
Write-Host ""
