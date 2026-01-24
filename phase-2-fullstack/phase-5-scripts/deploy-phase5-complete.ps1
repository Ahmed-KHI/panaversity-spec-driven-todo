# Phase V - Complete Minikube Deployment Script (PowerShell)
# [Task]: T-E-008 (Enhanced with all fixes)
# [From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Phase V: Todo App - Complete Minikube Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$MINIKUBE_CPUS = 4
$MINIKUBE_MEMORY = 3584  # 3.5GB - maximum within Docker Desktop limit
$MINIKUBE_DRIVER = "docker"

Write-Host "Step 1: Prerequisites Check" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

# Check all required tools
$REQUIRED_TOOLS = @("minikube", "kubectl", "helm", "dapr", "docker")
$MISSING_TOOLS = @()

foreach ($tool in $REQUIRED_TOOLS) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        try {
            $version = & $tool version --short 2>$null
            if (-not $version) {
                $version = & $tool version 2>$null | Select-Object -First 1
            }
            Write-Host "[OK] $tool found" -ForegroundColor Green -NoNewline
            Write-Host " - $version"
        }
        catch {
            Write-Host "[OK] $tool found" -ForegroundColor Green
        }
    }
    else {
        $MISSING_TOOLS += $tool
        Write-Host "[FAIL] $tool not found" -ForegroundColor Red
    }
}

if ($MISSING_TOOLS.Count -gt 0) {
    Write-Host ""
    Write-Host "Error: Missing required tools: $($MISSING_TOOLS -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation instructions:"
    Write-Host "- minikube: https://minikube.sigs.k8s.io/docs/start/"
    Write-Host "- kubectl: https://kubernetes.io/docs/tasks/tools/"
    Write-Host "- helm: https://helm.sh/docs/intro/install/"
    Write-Host "- dapr: https://docs.dapr.io/getting-started/install-dapr-cli/"
    Write-Host "- docker: https://docs.docker.com/get-docker/"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Start Minikube" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

# Check if Minikube is running and healthy
$minikubeHealthy = $false
try {
    $status = minikube status --format='{{.Host}}' 2>&1
    if ($status -match "Running") {
        # Test if API server is accessible
        $null = kubectl cluster-info 2>&1
        if ($LASTEXITCODE -eq 0) {
            $minikubeHealthy = $true
            Write-Host "[OK] Minikube already running and healthy" -ForegroundColor Green
            $MINIKUBE_IP = minikube ip
            Write-Host "  IP: $MINIKUBE_IP"
        }
        else {
            Write-Host "[WARN] Minikube running but API server unreachable" -ForegroundColor Yellow
        }
    }
}
catch {
    Write-Host "[INFO] Minikube not running" -ForegroundColor Yellow
}

if (-not $minikubeHealthy) {
    Write-Host ""
    Write-Host "Cleaning up old Minikube cluster..."
    $ErrorActionPreference = "Continue"
    minikube delete 2>&1 | Out-Null
    $ErrorActionPreference = "Stop"
    
    Write-Host "Starting fresh Minikube with:"
    Write-Host "  - CPUs: $MINIKUBE_CPUS"
    Write-Host "  - Memory: ${MINIKUBE_MEMORY}MB"
    Write-Host "  - Driver: $MINIKUBE_DRIVER"
    Write-Host ""
    
    minikube start --cpus=$MINIKUBE_CPUS --memory=$MINIKUBE_MEMORY --driver=$MINIKUBE_DRIVER --kubernetes-version=stable
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Failed to start Minikube" -ForegroundColor Red
        Write-Host "Try: minikube start --memory=2048 --cpus=2" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "[OK] Minikube started successfully" -ForegroundColor Green
    $MINIKUBE_IP = minikube ip
    Write-Host "  IP: $MINIKUBE_IP"
    
    # Wait for API server to be ready
    Write-Host ""
    Write-Host "Waiting for Kubernetes API server..."
    $maxAttempts = 30
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        $null = kubectl cluster-info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] API server ready" -ForegroundColor Green
            break
        }
        $attempt++
        Start-Sleep -Seconds 2
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "[ERROR] API server did not become ready" -ForegroundColor Red
        exit 1
    }
}

# Enable required addons
Write-Host ""
Write-Host "Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server
Write-Host "[OK] Addons enabled" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Initialize Dapr" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

try {
    $null = dapr status -k 2>&1
    Write-Host "[OK] Dapr already initialized on Kubernetes" -ForegroundColor Green
    dapr status -k
}
catch {
    Write-Host "Initializing Dapr on Kubernetes..."
    dapr init -k --wait --timeout 300
    Write-Host "[OK] Dapr initialized successfully" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Waiting for Dapr components to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=dapr -n dapr-system --timeout=300s
    
    Write-Host "[OK] Dapr components ready" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Install Strimzi Kafka Operator" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

try {
    $null = kubectl get deployment strimzi-cluster-operator -n kafka 2>&1
    Write-Host "[OK] Strimzi Kafka operator already installed" -ForegroundColor Green
}
catch {
    Write-Host "Creating kafka namespace..."
    kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
    
    Write-Host "Installing Strimzi operator..."
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    
    Write-Host "Waiting for Strimzi operator to be ready..."
    kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
    
    Write-Host "[OK] Strimzi operator ready" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 5: Create Namespaces" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

Set-Location -Path ..\..\phase-5-minikube

Write-Host "Creating application namespaces..."
kubectl apply -f namespace.yaml

Write-Host "[OK] Namespaces created" -ForegroundColor Green
kubectl get namespaces todo-app kafka

Write-Host ""
Write-Host "Step 6: Deploy Kafka Cluster" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

try {
    $null = kubectl get kafka todo-kafka -n kafka 2>&1
    Write-Host "[OK] Kafka cluster already exists" -ForegroundColor Green
}
catch {
    Write-Host "Deploying Kafka cluster..."
    kubectl apply -f kafka-cluster-v1.yaml
    
    Write-Host "Waiting for Kafka cluster to be ready (this may take 2-3 minutes)..."
    try {
        kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka
    }
    catch {
        Write-Host "[WARN] Kafka may still be starting" -ForegroundColor Yellow
    }
    
    Write-Host "[OK] Kafka cluster deployed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Kafka cluster status:"
kubectl get kafka -n kafka
kubectl get kafkatopic -n kafka

Write-Host ""
Write-Host "Step 7: Deploy PostgreSQL Database" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

try {
    $null = kubectl get deployment postgres -n todo-app 2>&1
    Write-Host "[OK] PostgreSQL already deployed" -ForegroundColor Green
}
catch {
    Write-Host "Deploying PostgreSQL..."
    kubectl apply -f postgres-deployment.yaml
    
    Write-Host "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s
    
    Write-Host "[OK] PostgreSQL ready" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 8: Apply Secrets" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

Write-Host "[WARN] Make sure to update secrets.yaml with your actual credentials!" -ForegroundColor Yellow
Write-Host "Required secrets:"
Write-Host "  - DATABASE_URL (connectionString)"
Write-Host "  - JWT_SECRET (jwtSecret)"
Write-Host "  - BETTER_AUTH_SECRET (betterAuthSecret)"
Write-Host "  - OPENAI_API_KEY (openaiApiKey)"
Write-Host ""
Read-Host "Press Enter to continue with current secrets (or Ctrl+C to exit and edit)"

kubectl apply -f secrets.yaml
Write-Host "[OK] Secrets applied" -ForegroundColor Green

Write-Host ""
Write-Host "Step 9: Deploy Dapr Components" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

Write-Host "Applying Dapr components..."
kubectl apply -f kafka-pubsub.yaml
kubectl apply -f statestore.yaml
kubectl apply -f jobs-api.yaml

Write-Host "[OK] Dapr components deployed" -ForegroundColor Green

Write-Host ""
Write-Host "Dapr components status:"
kubectl get components -n todo-app

Write-Host ""
Write-Host "Step 10: Build Docker Images" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

# Point Docker to Minikube's Docker daemon
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

Write-Host "Building backend image..."
Set-Location -Path ..\phase-2-fullstack\backend
docker build -t todo-backend:5.0.0 .
Write-Host "[OK] Backend image built" -ForegroundColor Green

Write-Host ""
Write-Host "Building frontend image..."
Set-Location -Path ..\frontend
docker build -t todo-frontend:5.0.0 .
Write-Host "[OK] Frontend image built" -ForegroundColor Green

# Return to phase-5-minikube directory
Set-Location -Path ..\..\phase-5-minikube

Write-Host ""
Write-Host "Step 11: Deploy Application" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

Write-Host "Deploying backend..."
kubectl apply -f backend-deployment.yaml

Write-Host "Deploying frontend..."
kubectl apply -f frontend-deployment.yaml

Write-Host ""
Write-Host "Waiting for pods to be ready..."
try {
    kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=180s
}
catch {
    Write-Host "[WARN] Backend may still be starting" -ForegroundColor Yellow
}

try {
    kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=180s
}
catch {
    Write-Host "[WARN] Frontend may still be starting" -ForegroundColor Yellow
}

Write-Host "[OK] Application deployed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 12: Deployment Status" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

Write-Host ""
Write-Host "Namespaces:"
kubectl get namespaces | Select-String -Pattern "todo-app|kafka"

Write-Host ""
Write-Host "Pods:"
kubectl get pods -n todo-app
kubectl get pods -n kafka

Write-Host ""
Write-Host "Services:"
kubectl get svc -n todo-app

Write-Host ""
Write-Host "Dapr Components:"
kubectl get components -n todo-app

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  [SUCCESS] Phase V Deployment Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application:" -ForegroundColor White
Write-Host ""
Write-Host "Frontend:" -ForegroundColor Yellow
Write-Host "  minikube service todo-frontend -n todo-app"
Write-Host "  This will automatically open the app in your browser"
Write-Host ""
Write-Host "Backend API:" -ForegroundColor Yellow
Write-Host "  kubectl port-forward -n todo-app svc/todo-backend 8000:8000"
Write-Host "  Then visit: http://localhost:8000/docs"
Write-Host ""
Write-Host "Dapr Dashboard:" -ForegroundColor Yellow
Write-Host "  dapr dashboard -k -p 9999"
Write-Host "  Then visit: http://localhost:9999"
Write-Host ""
Write-Host "Kafka Topics:" -ForegroundColor Yellow
Write-Host "  kubectl get kafkatopic -n kafka"
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Yellow
Write-Host "  Backend:  kubectl logs -n todo-app -l app=todo-backend -f"
Write-Host "  Frontend: kubectl logs -n todo-app -l app=todo-frontend -f"
Write-Host "  Kafka:    kubectl logs -n kafka -l app.kubernetes.io/name=kafka -f"
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "  Check pod status: kubectl describe pod [pod-name] -n todo-app"
Write-Host "  Check events:     kubectl get events -n todo-app --sort-by='.lastTimestamp'"
Write-Host ""
Write-Host "Cleanup:" -ForegroundColor Yellow
Write-Host "  kubectl delete namespace todo-app kafka"
Write-Host "  minikube stop"
Write-Host ""
