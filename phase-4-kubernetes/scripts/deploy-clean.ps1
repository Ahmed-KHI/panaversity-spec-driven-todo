#!/usr/bin/env pwsh
# Phase IV: Deploy Application with Helm
# Clean version without emoji characters

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Deploying Todo App to Minikube" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Helm is installed
if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Helm is not installed" -ForegroundColor Red
    exit 1
}

# Check if kubectl is available
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: kubectl is not installed" -ForegroundColor Red
    exit 1
}

# Check if Minikube is running
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Minikube is not running" -ForegroundColor Red
    Write-Host "Start Minikube with: minikube start" -ForegroundColor Yellow
    exit 1
}

Write-Host "Minikube is running" -ForegroundColor Green
Write-Host ""

# Get Minikube IP
$MINIKUBE_IP = minikube ip
Write-Host "Minikube IP: $MINIKUBE_IP" -ForegroundColor Cyan
Write-Host ""

# Create secrets
Write-Host "Creating Kubernetes secrets..." -ForegroundColor Yellow

# Database secret
Write-Host "  - Database credentials"
kubectl create secret generic postgres-secret `
    --from-literal=POSTGRES_DB=tododb `
    --from-literal=POSTGRES_USER=todouser `
    --from-literal=POSTGRES_PASSWORD=todopassword123 `
    --dry-run=client -o yaml | kubectl apply -f -

# OpenAI secret (use placeholder if not set)
Write-Host "  - OpenAI API key"
$OPENAI_KEY = $env:OPENAI_API_KEY
if (-not $OPENAI_KEY) {
    $OPENAI_KEY = "sk-placeholder-key-replace-with-real-key"
    Write-Host "    WARNING: Using placeholder OpenAI key" -ForegroundColor Yellow
}
kubectl create secret generic openai-secret `
    --from-literal=OPENAI_API_KEY=$OPENAI_KEY `
    --dry-run=client -o yaml | kubectl apply -f -

# Auth secrets
Write-Host "  - Auth configuration"
kubectl create secret generic auth-secret `
    --from-literal=BETTER_AUTH_SECRET="your-secret-key-min-32-chars-12345" `
    --from-literal=BETTER_AUTH_URL="http://todo.local" `
    --dry-run=client -o yaml | kubectl apply -f -

Write-Host "Secrets created successfully" -ForegroundColor Green
Write-Host ""

# Deploy with Helm
Write-Host "Deploying application with Helm..." -ForegroundColor Yellow
Write-Host ""

$HELM_CHART = "..\helm-charts\todo"
$VALUES_FILE = "..\helm-charts\todo\values-dev.yaml"

# Check if release already exists
$existingRelease = helm list -q | Select-String "^todo$"
if ($existingRelease) {
    Write-Host "Upgrading existing release..." -ForegroundColor Cyan
    helm upgrade todo $HELM_CHART -f $VALUES_FILE
} else {
    Write-Host "Installing new release..." -ForegroundColor Cyan
    helm install todo $HELM_CHART -f $VALUES_FILE
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Helm deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Helm deployment completed" -ForegroundColor Green
Write-Host ""

# Wait for pods to be ready
Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes..." -ForegroundColor Cyan
Write-Host ""

$timeout = 300  # 5 minutes
$elapsed = 0
$interval = 10

while ($elapsed -lt $timeout) {
    $notReady = kubectl get pods -o json | ConvertFrom-Json | 
        ForEach-Object { $_.items } | 
        Where-Object { 
            $_.status.phase -ne "Running" -or 
            $_.status.conditions | Where-Object { $_.type -eq "Ready" -and $_.status -ne "True" }
        }
    
    if (-not $notReady) {
        Write-Host "All pods are ready!" -ForegroundColor Green
        break
    }
    
    Write-Host "  Waiting... ($elapsed seconds elapsed)" -ForegroundColor Yellow
    Start-Sleep -Seconds $interval
    $elapsed += $interval
}

if ($elapsed -ge $timeout) {
    Write-Host "WARNING: Timeout waiting for pods" -ForegroundColor Yellow
    Write-Host "Check pod status with: kubectl get pods" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Show deployment status
Write-Host "Pods:" -ForegroundColor Yellow
kubectl get pods
Write-Host ""

Write-Host "Services:" -ForegroundColor Yellow
kubectl get services
Write-Host ""

Write-Host "Ingress:" -ForegroundColor Yellow
kubectl get ingress
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://todo.local" -ForegroundColor Cyan
Write-Host "  Backend API: http://todo.local/api" -ForegroundColor Cyan
Write-Host ""
Write-Host "Minikube IP: $MINIKUBE_IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verify hosts file contains:" -ForegroundColor Yellow
Write-Host "  $MINIKUBE_IP todo.local"
Write-Host ""
Write-Host "Health Checks:" -ForegroundColor Yellow
Write-Host "  curl http://todo.local/api/health"
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "  kubectl get pods"
Write-Host "  kubectl logs -l app.kubernetes.io/component=frontend"
Write-Host "  kubectl logs -l app.kubernetes.io/component=backend"
Write-Host "  kubectl describe pod <pod-name>"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run smoke tests: cd ..\tests; .\smoke-test.ps1"
Write-Host "  2. Run load tests: .\load-test.ps1"
Write-Host "  3. Access application: http://todo.local"
