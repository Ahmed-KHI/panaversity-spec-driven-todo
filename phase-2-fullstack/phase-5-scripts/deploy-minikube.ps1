# [Task]: T-E-008
# [From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md §E.8
# 
# Deploy Todo App to Minikube with Dapr and Kafka (PowerShell version)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Todo App - Minikube Deployment Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$commands = @("minikube", "kubectl", "helm", "dapr")
foreach ($cmd in $commands) {
    if (!(Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "Error: $cmd not installed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ All prerequisites installed" -ForegroundColor Green
Write-Host ""

# Start Minikube if not running
Write-Host "Starting Minikube..." -ForegroundColor Yellow
try {
    minikube status | Out-Null
    Write-Host "✓ Minikube already running" -ForegroundColor Green
} catch {
    minikube start --cpus=4 --memory=8192 --driver=docker
    Write-Host "✓ Minikube started" -ForegroundColor Green
}
Write-Host ""

# Initialize Dapr on Kubernetes
Write-Host "Initializing Dapr on Kubernetes..." -ForegroundColor Yellow
try {
    dapr status -k | Out-Null
    Write-Host "✓ Dapr already initialized" -ForegroundColor Green
} catch {
    dapr init -k --wait
    Write-Host "✓ Dapr initialized" -ForegroundColor Green
}
Write-Host ""

# Create namespace
Write-Host "Creating namespace..." -ForegroundColor Yellow
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -
Write-Host "✓ Namespace created" -ForegroundColor Green
Write-Host ""

# Apply secrets
Write-Host "Applying secrets..." -ForegroundColor Yellow
Write-Host "⚠ Remember to update secrets.yaml with real credentials!" -ForegroundColor Yellow
kubectl apply -f ..\phase-5-kubernetes\secrets.yaml
Write-Host "✓ Secrets applied" -ForegroundColor Green
Write-Host ""

# Apply Dapr components
Write-Host "Applying Dapr components..." -ForegroundColor Yellow
kubectl apply -f ..\phase-5-dapr\components\
Write-Host "✓ Dapr components applied" -ForegroundColor Green
Write-Host ""

# Apply RBAC
Write-Host "Applying RBAC..." -ForegroundColor Yellow
kubectl apply -f ..\phase-5-kubernetes\rbac.yaml
Write-Host "✓ RBAC applied" -ForegroundColor Green
Write-Host ""

# Deploy with Helm
Write-Host "Deploying application with Helm..." -ForegroundColor Yellow
helm upgrade --install todo-app ..\phase-5-helm\todo-app `
  --namespace todo-app `
  --set imageRegistry="ghcr.io/ahmed-khi" `
  --set backend.image.tag="v5.0.0" `
  --set frontend.image.tag="v5.0.0" `
  --set backend.replicaCount=2 `
  --set frontend.replicaCount=2 `
  --wait `
  --timeout=5m

Write-Host "✓ Application deployed" -ForegroundColor Green
Write-Host ""

# Wait for pods to be ready
Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app -n todo-app --timeout=300s
Write-Host "✓ All pods ready" -ForegroundColor Green
Write-Host ""

# Get service URLs
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend:" -ForegroundColor White
Write-Host "  minikube service todo-app-frontend -n todo-app --url" -ForegroundColor Gray
Write-Host ""
Write-Host "Backend:" -ForegroundColor White
Write-Host "  kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000" -ForegroundColor Gray
Write-Host "  Then visit: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Dapr Dashboard:" -ForegroundColor White
Write-Host "  dapr dashboard -k -p 9999" -ForegroundColor Gray
Write-Host "  Then visit: http://localhost:9999" -ForegroundColor Gray
Write-Host ""
Write-Host "View pods:" -ForegroundColor White
Write-Host "  kubectl get pods -n todo-app" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs:" -ForegroundColor White
Write-Host "  kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f" -ForegroundColor Gray
Write-Host ""
Write-Host "Delete deployment:" -ForegroundColor White
Write-Host "  helm uninstall todo-app -n todo-app" -ForegroundColor Gray
Write-Host "  kubectl delete namespace todo-app" -ForegroundColor Gray
Write-Host ""
