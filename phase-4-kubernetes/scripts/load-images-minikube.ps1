# [Task]: T028
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 4
# [Description]: Load Docker images into Minikube for local deployment (PowerShell version)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Loading Images into Minikube" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$FRONTEND_IMAGE = "ahmed-khi/todo-frontend"
$BACKEND_IMAGE = "ahmed-khi/todo-backend"
$VERSION = "v4.0.0"

# Check if Minikube is running
$minikubeStatus = minikube status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Minikube is not running" -ForegroundColor Red
    Write-Host "Run: .\scripts\setup-minikube.ps1"
    exit 1
}

Write-Host "✅ Minikube is running" -ForegroundColor Green
Write-Host ""

# Load Frontend Image
Write-Host "📦 Loading frontend image into Minikube..." -ForegroundColor Cyan
Write-Host "   Image: ${FRONTEND_IMAGE}:${VERSION}"
minikube image load "${FRONTEND_IMAGE}:${VERSION}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Frontend image loaded" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to load frontend image" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Load Backend Image
Write-Host "📦 Loading backend image into Minikube..." -ForegroundColor Cyan
Write-Host "   Image: ${BACKEND_IMAGE}:${VERSION}"
minikube image load "${BACKEND_IMAGE}:${VERSION}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backend image loaded" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to load backend image" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verify images are loaded
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Verifying Loaded Images" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Images in Minikube:"
minikube image ls | Select-String "ahmed-khi"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Images Loaded Successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  Deploy application: .\scripts\deploy.ps1"
Write-Host ""
