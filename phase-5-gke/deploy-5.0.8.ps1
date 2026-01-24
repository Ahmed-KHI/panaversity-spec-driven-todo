# Deploy Frontend 5.0.8 to GKE
# Fixed: Self-hosted fonts, no external dependencies

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Frontend 5.0.8 Deployment to GKE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$PROJECT_ID = "intense-optics-485323-f3"
$VERSION = "5.0.8"
$IMAGE = "todo-frontend"
$NAMESPACE = "todo-app"

# Step 1: Tag
Write-Host "Step 1: Tagging image..." -ForegroundColor Yellow
docker tag ${IMAGE}:${VERSION} gcr.io/${PROJECT_ID}/${IMAGE}:${VERSION}
Write-Host "Done`n" -ForegroundColor Green

# Step 2: Push to GCR
Write-Host "Step 2: Pushing to GCR (2-3 min)..." -ForegroundColor Yellow
docker push gcr.io/${PROJECT_ID}/${IMAGE}:${VERSION}
Write-Host "Done`n" -ForegroundColor Green

# Step 3: Deploy to GKE
Write-Host "Step 3: Updating GKE deployment..." -ForegroundColor Yellow
kubectl set image deployment/frontend frontend=gcr.io/${PROJECT_ID}/${IMAGE}:${VERSION} --namespace=${NAMESPACE}
Write-Host "Done`n" -ForegroundColor Green

# Step 4: Monitor
Write-Host "Step 4: Monitoring rollout..." -ForegroundColor Yellow
kubectl rollout status deployment/frontend --namespace=${NAMESPACE}

# Step 5: Show status
Write-Host "`nDeployment complete!" -ForegroundColor Green
kubectl get pods -n ${NAMESPACE} | Select-String "frontend"
kubectl get svc frontend-service -n ${NAMESPACE}

Write-Host "`nYour app: http://34.93.106.63" -ForegroundColor Cyan
