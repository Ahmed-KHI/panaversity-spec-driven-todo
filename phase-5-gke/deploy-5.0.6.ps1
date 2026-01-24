# Complete Deployment Script for Frontend 5.0.6
# Run after docker build completes successfully

param(
    [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Frontend 5.0.6 Deployment to GKE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 0: Verify build (optional)
if (-not $SkipBuild) {
    Write-Host "📦 Verifying Docker image exists..." -ForegroundColor Yellow
    $imageCheck = docker images todo-frontend:5.0.6 --format "{{.Repository}}:{{.Tag}}"
    if ($imageCheck -ne "todo-frontend:5.0.6") {
        Write-Host "❌ Error: todo-frontend:5.0.6 image not found!" -ForegroundColor Red
        Write-Host "   Please build the image first: docker build -t todo-frontend:5.0.6 ." -ForegroundColor Gray
        exit 1
    }
    Write-Host "✅ Image found: $imageCheck`n" -ForegroundColor Green
}

# Step 1: Tag for GCR
Write-Host "📦 Step 1: Tagging Frontend 5.0.6 for GCR..." -ForegroundColor Cyan
docker tag todo-frontend:5.0.6 gcr.io/intense-optics-485323-f3/todo-frontend:5.0.6
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to tag image" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Tagged successfully`n" -ForegroundColor Green

# Step 2: Push to GCR
Write-Host "☁️  Step 2: Pushing to Google Container Registry..." -ForegroundColor Cyan
Write-Host "   (This will take 2-3 minutes...)" -ForegroundColor Gray
docker push gcr.io/intense-optics-485323-f3/todo-frontend:5.0.6
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push image to GCR" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Pushed successfully`n" -ForegroundColor Green

# Step 3: Update deployment manifest
Write-Host "📝 Step 3: Updating Kubernetes deployment manifest..." -ForegroundColor Cyan
$deploymentFile = "i:\hackathon II-full-stack web application\phase-5-gke\frontend-deployment.yaml"
$content = Get-Content $deploymentFile -Raw
$oldImage = "gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5"
$newImage = "gcr.io/intense-optics-485323-f3/todo-frontend:5.0.6"

if ($content -match [regex]::Escape($oldImage)) {
    $content = $content -replace [regex]::Escape($oldImage), $newImage
    Set-Content $deploymentFile -Value $content
    Write-Host "✅ Updated image version: 5.0.5 → 5.0.6`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Image 5.0.5 not found in manifest, updating manually..." -ForegroundColor Yellow
    $content = $content -replace "gcr\.io/intense-optics-485323-f3/todo-frontend:[0-9.]+", $newImage
    Set-Content $deploymentFile -Value $content
    Write-Host "✅ Updated to version 5.0.6`n" -ForegroundColor Green
}

# Step 4: Apply to GKE
Write-Host "🚀 Step 4: Deploying to GKE..." -ForegroundColor Cyan
kubectl apply -f $deploymentFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to apply deployment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Deployment applied`n" -ForegroundColor Green

# Step 5: Restart pods
Write-Host "🔄 Step 5: Restarting frontend pods..." -ForegroundColor Cyan
kubectl delete pod -n todo-app -l app=todo-frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Failed to delete pods (they may not exist)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Old pods deleted`n" -ForegroundColor Green
}

# Step 6: Wait for new pods
Write-Host "⏳ Step 6: Waiting 30 seconds for new pods to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 7: Verify deployment
Write-Host "`n📊 Step 7: Verifying deployment..." -ForegroundColor Cyan
Write-Host "`n--- Pod Status ---" -ForegroundColor White
kubectl get pods -n todo-app

Write-Host "`n--- Image Versions ---" -ForegroundColor White
$images = kubectl describe pod -l app=todo-frontend -n todo-app | Select-String "Image:"
$images | ForEach-Object {
    if ($_ -match "5\.0\.6") {
        Write-Host $_ -ForegroundColor Green
    } else {
        Write-Host $_ -ForegroundColor Yellow
    }
}

Write-Host "`n--- Frontend Service ---" -ForegroundColor White
$service = kubectl get svc todo-frontend -n todo-app -o wide
Write-Host $service

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✨ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "🌐 Access your app at: http://34.93.106.63" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Clear browser cache (Ctrl+Shift+Delete → All time)" -ForegroundColor Gray
Write-Host "   2. Navigate to http://34.93.106.63" -ForegroundColor Gray
Write-Host "   3. Register or login" -ForegroundColor Gray
Write-Host "   4. Verify redirect to dashboard works" -ForegroundColor Gray
Write-Host "   5. Test AI Chat" -ForegroundColor Gray
Write-Host "   6. Test Phase 5 features (priority, recurring, due dates)" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 To check backend logs:" -ForegroundColor Yellow
Write-Host "   kubectl logs -n todo-app -l app=todo-backend --tail=50" -ForegroundColor Gray
Write-Host ""
Write-Host "🐛 To troubleshoot pods:" -ForegroundColor Yellow
Write-Host "   kubectl describe pod -l app=todo-frontend -n todo-app" -ForegroundColor Gray
Write-Host "   kubectl logs -n todo-app -l app=todo-frontend --tail=100" -ForegroundColor Gray
Write-Host ""
