# [Task]: T001-T007
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 1
# [Description]: Verify all required tools are installed for Phase IV (PowerShell version)

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Prerequisites Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$ERRORS = 0
$WARNINGS = 0

# T001: Verify Docker Desktop 4.53+
Write-Host "🐳 Checking Docker Desktop..." -ForegroundColor Cyan
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVersion = (docker --version) -replace '.*version (\d+\.\d+\.\d+).*','$1'
    Write-Host "   ✅ Docker version: $dockerVersion" -ForegroundColor Green
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Host "   ✅ Docker daemon is running" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Docker daemon is not running" -ForegroundColor Red
        $ERRORS++
    }
} else {
    Write-Host "   ❌ Docker is not installed" -ForegroundColor Red
    Write-Host "      Install from: https://www.docker.com/products/docker-desktop"
    $ERRORS++
}
Write-Host ""

# T002: Check Gordon (Docker AI) - optional
Write-Host "🤖 Checking Gordon (Docker AI)..." -ForegroundColor Cyan
try {
    docker ai --help | Out-Null
    Write-Host "   ✅ Gordon (Docker AI) is available" -ForegroundColor Green
    Write-Host "      Try: docker ai 'optimize my Dockerfile'"
} catch {
    Write-Host "   ⚠️  Gordon (Docker AI) not available (optional)" -ForegroundColor Yellow
    Write-Host "      Enable in Docker Desktop → Settings → Beta features"
    $WARNINGS++
}
Write-Host ""

# T003: Verify Minikube 1.33+
Write-Host "☸️  Checking Minikube..." -ForegroundColor Cyan
if (Get-Command minikube -ErrorAction SilentlyContinue) {
    $minikubeVersion = (minikube version --short 2>$null) -replace 'v',''
    Write-Host "   ✅ Minikube version: v$minikubeVersion" -ForegroundColor Green
    
    # Check if Minikube is running
    $minikubeStatus = minikube status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Minikube cluster is running" -ForegroundColor Green
        $minikubeIp = minikube ip 2>$null
        if ($minikubeIp) {
            Write-Host "      IP: $minikubeIp"
        }
    } else {
        Write-Host "   ⚠️  Minikube cluster is not running" -ForegroundColor Yellow
        Write-Host "      Run: .\scripts\setup-minikube.ps1"
        $WARNINGS++
    }
} else {
    Write-Host "   ❌ Minikube is not installed" -ForegroundColor Red
    Write-Host "      Install from: https://minikube.sigs.k8s.io/docs/start/"
    $ERRORS++
}
Write-Host ""

# T004: Verify kubectl 1.31+
Write-Host "🔧 Checking kubectl..." -ForegroundColor Cyan
if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    $kubectlVersion = (kubectl version --client --short 2>$null) -replace '.*v(\d+\.\d+\.\d+).*','$1'
    if (-not $kubectlVersion) {
        $kubectlVersionJson = kubectl version --client -o json 2>$null | ConvertFrom-Json
        $kubectlVersion = $kubectlVersionJson.clientVersion.gitVersion -replace 'v',''
    }
    Write-Host "   ✅ kubectl version: v$kubectlVersion" -ForegroundColor Green
    
    # Check if kubectl can connect to cluster
    try {
        kubectl cluster-info 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ kubectl can connect to cluster" -ForegroundColor Green
        } else {
            throw
        }
    } catch {
        Write-Host "   ⚠️  kubectl cannot connect to cluster" -ForegroundColor Yellow
        Write-Host "      Run: .\scripts\setup-minikube.ps1"
        $WARNINGS++
    }
} else {
    Write-Host "   ❌ kubectl is not installed" -ForegroundColor Red
    Write-Host "      Install from: https://kubernetes.io/docs/tasks/tools/"
    $ERRORS++
}
Write-Host ""

# T005: Verify Helm 3.16+
Write-Host "⎈  Checking Helm..." -ForegroundColor Cyan
if (Get-Command helm -ErrorAction SilentlyContinue) {
    $helmVersion = (helm version --short 2>$null) -replace '.*v(\d+\.\d+\.\d+).*','$1'
    Write-Host "   ✅ Helm version: v$helmVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Helm is not installed" -ForegroundColor Red
    Write-Host "      Install from: https://helm.sh/docs/intro/install/"
    $ERRORS++
}
Write-Host ""

# T006: Check kubectl-ai - optional
Write-Host "🧠 Checking kubectl-ai..." -ForegroundColor Cyan
if (Get-Command kubectl-ai -ErrorAction SilentlyContinue) {
    Write-Host "   ✅ kubectl-ai is installed" -ForegroundColor Green
    
    # Check if OpenAI API key is configured
    if ($env:OPENAI_API_KEY) {
        Write-Host "   ✅ OPENAI_API_KEY environment variable is set" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  OPENAI_API_KEY not set" -ForegroundColor Yellow
        Write-Host "      Set with: `$env:OPENAI_API_KEY='your-key'"
        $WARNINGS++
    }
} else {
    Write-Host "   ⚠️  kubectl-ai not installed (optional tool)" -ForegroundColor Yellow
    Write-Host "      Install: go install github.com/sozercan/kubectl-ai@latest"
    $WARNINGS++
}
Write-Host ""

# T007: Check Kagent - optional
Write-Host "📊 Checking Kagent (K8sGPT)..." -ForegroundColor Cyan
if (Get-Command k8sgpt -ErrorAction SilentlyContinue) {
    Write-Host "   ✅ Kagent (K8sGPT) is installed" -ForegroundColor Green
    $k8sgptVersion = (k8sgpt version 2>$null) -replace '.*Version: (\d+\.\d+\.\d+).*','$1'
    if ($k8sgptVersion) {
        Write-Host "      Version: $k8sgptVersion"
    }
} else {
    Write-Host "   ⚠️  Kagent (K8sGPT) not installed (optional tool)" -ForegroundColor Yellow
    Write-Host "      Install from: https://docs.k8sgpt.ai/getting-started/installation/"
    $WARNINGS++
}
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($ERRORS -eq 0 -and $WARNINGS -eq 0) {
    Write-Host "✅ All prerequisites met!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You are ready to proceed with Phase IV implementation."
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Setup Minikube: .\scripts\setup-minikube.ps1"
    Write-Host "2. Build Docker images: .\scripts\build-images.ps1"
    Write-Host "3. Deploy application: .\scripts\deploy.ps1"
    exit 0
} elseif ($ERRORS -eq 0) {
    Write-Host "✅ Required prerequisites met" -ForegroundColor Green
    Write-Host "⚠️  $WARNINGS optional warning(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can proceed, but consider installing optional tools for enhanced DevOps experience."
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Setup Minikube: .\scripts\setup-minikube.ps1"
    Write-Host "2. Build Docker images: .\scripts\build-images.ps1"
    Write-Host "3. Deploy application: .\scripts\deploy.ps1"
    exit 0
} else {
    Write-Host "❌ $ERRORS critical error(s) found" -ForegroundColor Red
    Write-Host "⚠️  $WARNINGS optional warning(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install missing required tools before proceeding."
    exit 1
}
