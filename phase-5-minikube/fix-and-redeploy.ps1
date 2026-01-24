# Quick Fix Deployment Script for AI Chat
# Run this to apply all fixes and redeploy

Write-Host "🔧 AI Chat Fix - Phase 5 Redeployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Rebuild Backend Docker Image
Write-Host "Step 1: Rebuilding Backend Docker Image..." -ForegroundColor Yellow
Set-Location "i:\hackathon II-full-stack web application\phase-2-fullstack\backend"

docker build -t todo-backend:5.0.0 -f Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

# Load into Minikube
Write-Host "Loading image into Minikube..." -ForegroundColor Yellow
minikube image load todo-backend:5.0.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Minikube load failed - are you using Minikube?" -ForegroundColor Yellow
}

Write-Host "✅ Image built and loaded" -ForegroundColor Green
Write-Host ""

# Step 2: Navigate to Kubernetes configs
Write-Host "Step 2: Updating Kubernetes secrets..." -ForegroundColor Yellow
Set-Location "i:\hackathon II-full-stack web application\phase-5-minikube"

# Delete old secret
kubectl delete secret postgres-secret -n todo-app --ignore-not-found=true

# Apply new secret with real OpenAI API key
kubectl apply -f secrets.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Secret apply failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Secrets updated" -ForegroundColor Green
Write-Host ""

# Step 3: Restart backend deployment
Write-Host "Step 3: Restarting backend pods..." -ForegroundColor Yellow
kubectl delete pod -l app=todo-backend -n todo-app 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "No existing pods found, continuing..." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

# Wait for pods to be ready
Write-Host "Waiting for pods to restart..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=120s

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Pod not ready yet, check status with: kubectl get pods -n todo-app" -ForegroundColor Yellow
}

Write-Host "✅ Pods restarted" -ForegroundColor Green
Write-Host ""

# Step 4: Verify deployment
Write-Host "Step 4: Verifying deployment..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Pod Status:" -ForegroundColor Cyan
kubectl get pods -n todo-app -l app=todo-backend

Write-Host ""
Write-Host "Recent Logs:" -ForegroundColor Cyan
kubectl logs -l app=todo-backend -n todo-app --tail=20 2>$null

Write-Host ""
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Port forward to test:" -ForegroundColor White
Write-Host "   kubectl port-forward svc/todo-backend 8000:8000 -n todo-app" -ForegroundColor Gray
Write-Host "   kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open browser: http://localhost:3000" -ForegroundColor White
Write-Host "3. Login and navigate to /chat" -ForegroundColor White
Write-Host "4. Test AI: 'Add task to test AI chat'" -ForegroundColor White
Write-Host ""
Write-Host "🐛 Troubleshooting:" -ForegroundColor Cyan
Write-Host "   kubectl logs -l app=todo-backend -n todo-app --tail=50" -ForegroundColor Gray
Write-Host "   kubectl describe pod -l app=todo-backend -n todo-app" -ForegroundColor Gray
Write-Host ""

# Return to original directory
Set-Location "i:\hackathon II-full-stack web application"
