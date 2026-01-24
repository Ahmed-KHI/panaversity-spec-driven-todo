# GKE Deployment Script for Panaversity Todo App
# Phase 5: Complete Cloud Deployment

Write-Host "`n🚀 Starting GKE Deployment..." -ForegroundColor Cyan
Write-Host "Project: intense-optics-485323-f3" -ForegroundColor White
Write-Host "Cluster: panaversity-todo (asia-south1)" -ForegroundColor White
Write-Host "Namespace: todo-app`n" -ForegroundColor White

# Step 1: Create namespace
Write-Host "📦 Step 1: Creating namespace..." -ForegroundColor Yellow
kubectl apply -f "i:\hackathon II-full-stack web application\phase-5-gke\namespace.yaml"

# Step 2: Deploy secrets (IMPORTANT: Update OpenAI API key first!)
Write-Host "`n🔐 Step 2: Deploying secrets..." -ForegroundColor Yellow
Write-Host "⚠️  Make sure you updated OPENAI_API_KEY in secrets.yaml!" -ForegroundColor Red
kubectl apply -f "i:\hackathon II-full-stack web application\phase-5-gke\secrets.yaml"

# Step 3: Deploy PostgreSQL
Write-Host "`n🐘 Step 3: Deploying PostgreSQL..." -ForegroundColor Yellow
kubectl apply -f "i:\hackathon II-full-stack web application\phase-5-gke\postgres-deployment.yaml"

Write-Host "`n⏳ Waiting 30 seconds for PostgreSQL to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Step 4: Deploy Backend
Write-Host "`n⚙️  Step 4: Deploying Backend (gcr.io/.../todo-backend:5.0.3)..." -ForegroundColor Yellow
kubectl apply -f "i:\hackathon II-full-stack web application\phase-5-gke\backend-deployment.yaml"

# Step 5: Deploy Frontend
Write-Host "`n🌐 Step 5: Deploying Frontend (gcr.io/.../todo-frontend:5.0.4)..." -ForegroundColor Yellow
kubectl apply -f "i:\hackathon II-full-stack web application\phase-5-gke\frontend-deployment.yaml"

# Step 6: Wait for LoadBalancer
Write-Host "`n⏳ Waiting 60 seconds for LoadBalancer to assign External IP..." -ForegroundColor Cyan
Start-Sleep -Seconds 60

# Step 7: Get External IP
Write-Host "`n✅ Deployment Complete! Getting Public URL..." -ForegroundColor Green
kubectl get svc -n todo-app todo-frontend

Write-Host "`n📋 Check pod status:" -ForegroundColor Cyan
kubectl get pods -n todo-app

Write-Host "`n🌍 To get your public URL:" -ForegroundColor Magenta
Write-Host "   kubectl get svc -n todo-app todo-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}'" -ForegroundColor White

Write-Host "`n✨ Your app will be accessible at: http://<EXTERNAL-IP>" -ForegroundColor Green
