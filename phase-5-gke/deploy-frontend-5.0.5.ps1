# Deploy Frontend 5.0.5 to GKE
# Run after docker build completes

Write-Host "`n📦 Step 1: Tagging Frontend 5.0.5 for GCR..." -ForegroundColor Cyan
docker tag todo-frontend:5.0.5 gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5

Write-Host "`n☁️  Step 2: Pushing to Google Container Registry..." -ForegroundColor Cyan
docker push gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5

Write-Host "`n📝 Step 3: Updating Kubernetes deployment manifest..." -ForegroundColor Yellow
Write-Host "   Updating image version from 5.0.4 to 5.0.5..." -ForegroundColor Gray

# Update the frontend-deployment.yaml file
$deploymentFile = "i:\hackathon II-full-stack web application\phase-5-gke\frontend-deployment.yaml"
$content = Get-Content $deploymentFile -Raw
$content = $content -replace 'gcr.io/intense-optics-485323-f3/todo-frontend:5.0.4', 'gcr.io/intense-optics-485323-f3/todo-frontend:5.0.5'
Set-Content $deploymentFile -Value $content

Write-Host "   ✅ Deployment manifest updated" -ForegroundColor Green

Write-Host "`n🚀 Step 4: Deploying to GKE..." -ForegroundColor Cyan
kubectl apply -f "i:\hackathon II-full-stack web application\phase-5-gke\frontend-deployment.yaml"

Write-Host "`n🔄 Step 5: Restarting frontend pods..." -ForegroundColor Cyan
kubectl delete pod -n todo-app -l app=todo-frontend

Write-Host "`n⏳ Step 6: Waiting 30 seconds for new pods to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`n📊 Step 7: Checking deployment status..." -ForegroundColor Cyan
Write-Host "`nPod Status:" -ForegroundColor White
kubectl get pods -n todo-app

Write-Host "`nImage Versions:" -ForegroundColor White
kubectl describe pod -l app=todo-frontend -n todo-app | Select-String "Image:"

Write-Host "`nFrontend Service:" -ForegroundColor White
kubectl get svc todo-frontend -n todo-app

Write-Host "`n✨ Deployment Complete!" -ForegroundColor Green
Write-Host "`n🌐 Access your app at: http://34.93.106.63" -ForegroundColor Cyan
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Clear browser cache (Ctrl+Shift+Delete → All time → Cached images)" -ForegroundColor Gray
Write-Host "   2. Test registration at http://34.93.106.63" -ForegroundColor Gray
Write-Host "   3. Verify no ECONNREFUSED errors in browser console (F12)" -ForegroundColor Gray
Write-Host "   4. Test AI Chat task creation" -ForegroundColor Gray
Write-Host "   5. Record 90-second demo video" -ForegroundColor Gray
Write-Host "   6. Upload to YouTube (Unlisted)" -ForegroundColor Gray
Write-Host "   7. Submit hackathon form" -ForegroundColor Gray
Write-Host ""
