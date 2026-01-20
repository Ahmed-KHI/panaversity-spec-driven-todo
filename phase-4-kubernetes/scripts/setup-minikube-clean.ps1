# [Task]: T008
# [From]: specs/004-phase-iv-kubernetes/tasks.md Phase 1
# [Description]: Initialize Minikube cluster with required configuration and addons (PowerShell version)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Minikube Cluster Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Minikube is installed
if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Minikube is not installed" -ForegroundColor Red
    Write-Host "Please install Minikube 1.33+ from https://minikube.sigs.k8s.io/"
    exit 1
}

# Check if kubectl is installed
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: kubectl is not installed" -ForegroundColor Red
    Write-Host "Please install kubectl 1.31+ from https://kubernetes.io/docs/tasks/tools/"
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop 4.53+"
    exit 1
}

Write-Host "Prerequisites verified" -ForegroundColor Green
Write-Host ""

# Check if Minikube is already running
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Minikube cluster already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to delete and recreate it? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Deleting existing cluster..." -ForegroundColor Yellow
        minikube delete
    } else {
        Write-Host "Using existing cluster" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Enabling required addons..."
        minikube addons enable ingress
        minikube addons enable metrics-server
        Write-Host ""
        Write-Host "Minikube setup complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Cluster Info:"
        kubectl cluster-info
        Write-Host ""
        Write-Host "Nodes:"
        kubectl get nodes
        Write-Host ""
        Write-Host "Enabled Addons:"
        minikube addons list | Select-String "enabled"
        exit 0
    }
}

Write-Host "Starting Minikube cluster..." -ForegroundColor Cyan
Write-Host "   - CPUs: 2"
Write-Host "   - Memory: 3072 MB (3 GB)" 
Write-Host "   - Driver: docker"
Write-Host ""

minikube start --cpus=2 --memory=3072 --driver=docker --kubernetes-version=v1.31.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start Minikube" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Minikube cluster started" -ForegroundColor Green
Write-Host ""

# Enable required addons
Write-Host "Enabling ingress addon..." -ForegroundColor Cyan
minikube addons enable ingress

Write-Host "Enabling metrics-server addon..." -ForegroundColor Cyan
minikube addons enable metrics-server

Write-Host ""
Write-Host "Addons enabled" -ForegroundColor Green
Write-Host ""

# Wait for ingress controller to be ready
Write-Host "Waiting for ingress controller to be ready..." -ForegroundColor Cyan
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s

Write-Host ""
Write-Host "Ingress controller ready" -ForegroundColor Green
Write-Host ""

# Add hosts entry
Write-Host "Adding hosts entry for todo.local..." -ForegroundColor Cyan
$minikubeIp = minikube ip

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsPath -Raw

if ($hostsContent -match "todo.local") {
    Write-Host "   - Entry already exists, updating IP..." -ForegroundColor Yellow
    $hostsContent = $hostsContent -replace ".*todo.local.*\r?\n?", ""
}

# Add new entry
Write-Host "   - Adding entry: $minikubeIp todo.local" -ForegroundColor Cyan
$newEntry = "$minikubeIp todo.local"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Add-Content -Path $hostsPath -Value "`r`n$newEntry"
    Write-Host "   - Successfully added to hosts file" -ForegroundColor Green
} else {
    Write-Host "Not running as Administrator. Please add this entry to hosts file manually:" -ForegroundColor Yellow
    Write-Host "   File: $hostsPath" -ForegroundColor Yellow
    Write-Host "   Entry: $newEntry" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Minikube Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cluster Info:"
kubectl cluster-info
Write-Host ""
Write-Host "Nodes:"
kubectl get nodes
Write-Host ""
Write-Host "Enabled Addons:"
minikube addons list | Select-String "enabled"
Write-Host ""
Write-Host "Minikube IP: $minikubeIp" -ForegroundColor Cyan
Write-Host "Application will be accessible at: http://todo.local" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Build Docker images: .\build-images.ps1"
Write-Host "2. Deploy application: .\deploy.ps1"
Write-Host "3. Access at http://todo.local"
Write-Host ""
