# [Task]: T067
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 10
# [Description]: Deploy Phase IV Todo Application to Kubernetes using Helm (PowerShell version)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Deploying to Kubernetes" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$RELEASE_NAME = "todo"
$NAMESPACE = "default"
$HELM_CHART = ".\helm-charts\todo"
$VALUES_FILE = ".\helm-charts\todo\values-dev.yaml"
$PROJECT_ROOT = (Get-Item (Split-Path -Parent $PSScriptRoot)).FullName

Set-Location $PROJECT_ROOT

# Check if Minikube is running
$minikubeStatus = minikube status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Minikube is not running" -ForegroundColor Red
    Write-Host "Run: .\scripts\setup-minikube.ps1"
    exit 1
}

Write-Host "✅ Minikube is running" -ForegroundColor Green
Write-Host ""

# Check if kubectl can connect
try {
    kubectl cluster-info 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✅ kubectl connected to cluster" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: kubectl cannot connect to cluster" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create secrets if they don't exist
Write-Host "🔒 Creating Kubernetes Secrets..." -ForegroundColor Cyan
Write-Host ""

# Database secret
$dbSecretExists = kubectl get secret todo-database-secret -n $NAMESPACE 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Secret 'todo-database-secret' already exists" -ForegroundColor Green
} else {
    Write-Host "   📝 Creating 'todo-database-secret'..." -ForegroundColor Cyan
    kubectl create secret generic todo-database-secret `
        -n $NAMESPACE `
        --from-literal=POSTGRES_PASSWORD=postgres123 `
        --from-literal=DATABASE_URL="postgresql://todo_user:postgres123@todo-postgres:5432/todo_db"
    Write-Host "   ✅ Created 'todo-database-secret'" -ForegroundColor Green
}

# OpenAI API secret
$openaiSecretExists = kubectl get secret todo-openai-secret -n $NAMESPACE 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Secret 'todo-openai-secret' already exists" -ForegroundColor Green
} else {
    Write-Host "   📝 Creating 'todo-openai-secret'..." -ForegroundColor Cyan
    # Check if OPENAI_API_KEY environment variable is set
    if (-not $env:OPENAI_API_KEY) {
        Write-Host "   ⚠️  OPENAI_API_KEY not set, using placeholder" -ForegroundColor Yellow
        $OPENAI_KEY = "sk-placeholder-key-for-development"
    } else {
        $OPENAI_KEY = $env:OPENAI_API_KEY
    }
    kubectl create secret generic todo-openai-secret `
        -n $NAMESPACE `
        --from-literal=OPENAI_API_KEY="$OPENAI_KEY"
    Write-Host "   ✅ Created 'todo-openai-secret'" -ForegroundColor Green
}

# Better Auth secret
$authSecretExists = kubectl get secret todo-auth-secret -n $NAMESPACE 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Secret 'todo-auth-secret' already exists" -ForegroundColor Green
} else {
    Write-Host "   📝 Creating 'todo-auth-secret'..." -ForegroundColor Cyan
    $AUTH_SECRET = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString()))
    kubectl create secret generic todo-auth-secret `
        -n $NAMESPACE `
        --from-literal=BETTER_AUTH_SECRET="$AUTH_SECRET" `
        --from-literal=BETTER_AUTH_URL="http://todo.local"
    Write-Host "   ✅ Created 'todo-auth-secret'" -ForegroundColor Green
}

Write-Host ""

# Check if Helm chart exists
if (-not (Test-Path $HELM_CHART)) {
    Write-Host "❌ ERROR: Helm chart not found at $HELM_CHART" -ForegroundColor Red
    exit 1
}

# Check if release already exists
$releaseExists = helm list -n $NAMESPACE | Select-String $RELEASE_NAME
if ($releaseExists) {
    Write-Host "WARNING: Helm release '$RELEASE_NAME' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to upgrade it? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Upgrading Helm release..." -ForegroundColor Cyan
        helm upgrade $RELEASE_NAME $HELM_CHART `
            -n $NAMESPACE `
            -f $VALUES_FILE
        Write-Host "✅ Helm release upgraded" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Skipping deployment" -ForegroundColor Cyan
        exit 0
    }
} else {
    Write-Host "📦 Installing Helm chart..." -ForegroundColor Cyan
    helm install $RELEASE_NAME $HELM_CHART `
        -n $NAMESPACE `
        -f $VALUES_FILE
    Write-Host "✅ Helm chart installed" -ForegroundColor Green
}

Write-Host ""

# Wait for pods to be ready
Write-Host "⏳ Waiting for pods to be ready (timeout: 300s)..." -ForegroundColor Cyan
Write-Host ""

# Wait for frontend
kubectl wait --for=condition=ready pod `
    -l app.kubernetes.io/component=frontend `
    -n $NAMESPACE `
    --timeout=300s

# Wait for backend
kubectl wait --for=condition=ready pod `
    -l app.kubernetes.io/component=backend `
    -n $NAMESPACE `
    --timeout=300s

# Wait for postgres
kubectl wait --for=condition=ready pod `
    -l app.kubernetes.io/component=database `
    -n $NAMESPACE `
    --timeout=300s

Write-Host ""

# Display deployment status
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pods:"
kubectl get pods -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME"
Write-Host ""

Write-Host "Services:"
kubectl get svc -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME"
Write-Host ""

Write-Host "Ingress:"
kubectl get ingress -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME"
Write-Host ""

Write-Host "HPA:"
kubectl get hpa -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME"
Write-Host ""

# Get Minikube IP
$MINIKUBE_IP = minikube ip

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
Write-Host "  curl http://todo.local/api/health"
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Yellow
Write-Host "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=frontend --tail=50"
Write-Host "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/component=backend --tail=50"
Write-Host ""
