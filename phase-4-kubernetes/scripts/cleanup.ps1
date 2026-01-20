# [Task]: T071
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 10
# [Description]: Cleanup all Kubernetes resources and stop Minikube (PowerShell version)

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Cleanup Kubernetes Resources" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$RELEASE_NAME = "todo"
$NAMESPACE = "default"

# Check if kubectl can connect
try {
    kubectl cluster-info 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    
    Write-Host "✅ kubectl connected to cluster" -ForegroundColor Green
    Write-Host ""
    
    # Uninstall Helm release
    $releaseExists = helm list -n $NAMESPACE | Select-String $RELEASE_NAME
    if ($releaseExists) {
        Write-Host "🗑️  Uninstalling Helm release '$RELEASE_NAME'..." -ForegroundColor Yellow
        helm uninstall $RELEASE_NAME -n $NAMESPACE
        Write-Host "✅ Helm release uninstalled" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Helm release '$RELEASE_NAME' not found" -ForegroundColor Cyan
    }
    
    Write-Host ""
    
    # Delete secrets
    Write-Host "🗑️  Deleting secrets..." -ForegroundColor Yellow
    kubectl delete secret todo-database-secret -n $NAMESPACE --ignore-not-found
    kubectl delete secret todo-openai-secret -n $NAMESPACE --ignore-not-found
    kubectl delete secret todo-auth-secret -n $NAMESPACE --ignore-not-found
    Write-Host "✅ Secrets deleted" -ForegroundColor Green
    
    Write-Host ""
    
    # Verify cleanup
    Write-Host "Checking for remaining resources..."
    $remainingPods = kubectl get pods -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME" 2>$null
    if ($remainingPods) {
        Write-Host "⚠️  Some pods still terminating..." -ForegroundColor Yellow
        kubectl get pods -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME"
    } else {
        Write-Host "✅ All resources cleaned up" -ForegroundColor Green
    }
    
} catch {
    Write-Host "⚠️  kubectl cannot connect to cluster" -ForegroundColor Yellow
    Write-Host "Minikube may already be stopped"
}

Write-Host ""

# Stop Minikube
$response = Read-Host "Do you want to stop Minikube? (y/N)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "🛑 Stopping Minikube..." -ForegroundColor Yellow
    minikube stop
    Write-Host "✅ Minikube stopped" -ForegroundColor Green
    
    Write-Host ""
    $deleteResponse = Read-Host "Do you want to delete Minikube cluster? (y/N)"
    if ($deleteResponse -eq 'y' -or $deleteResponse -eq 'Y') {
        Write-Host "🗑️  Deleting Minikube cluster..." -ForegroundColor Yellow
        minikube delete
        Write-Host "✅ Minikube cluster deleted" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  Minikube left running" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
