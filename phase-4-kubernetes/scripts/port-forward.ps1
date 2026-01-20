# [Task]: T069
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 10
# [Description]: Port forward services for local access (fallback if ingress fails) - PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Port Forwarding Services" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$NAMESPACE = "default"
$RELEASE_NAME = "todo"

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

# Get service names
$FRONTEND_SERVICE = kubectl get svc -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME,app.kubernetes.io/component=frontend" -o jsonpath='{.items[0].metadata.name}' 2>$null
$BACKEND_SERVICE = kubectl get svc -n $NAMESPACE -l "app.kubernetes.io/instance=$RELEASE_NAME,app.kubernetes.io/component=backend" -o jsonpath='{.items[0].metadata.name}' 2>$null

if (-not $FRONTEND_SERVICE -or -not $BACKEND_SERVICE) {
    Write-Host "❌ ERROR: Services not found. Is the application deployed?" -ForegroundColor Red
    Write-Host "Run: .\scripts\deploy.ps1"
    exit 1
}

Write-Host "Found services:"
Write-Host "  Frontend: $FRONTEND_SERVICE"
Write-Host "  Backend: $BACKEND_SERVICE"
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting Port Forwarding" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop port forwarding" -ForegroundColor Yellow
Write-Host ""

# Start port forwarding in parallel
$frontendJob = Start-Job -ScriptBlock {
    param($ns, $svc)
    kubectl port-forward -n $ns "svc/$svc" 3000:3000
} -ArgumentList $NAMESPACE, $FRONTEND_SERVICE

$backendJob = Start-Job -ScriptBlock {
    param($ns, $svc)
    kubectl port-forward -n $ns "svc/$svc" 8000:8000
} -ArgumentList $NAMESPACE, $BACKEND_SERVICE

# Wait for Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if jobs are still running
        if ($frontendJob.State -ne 'Running' -or $backendJob.State -ne 'Running') {
            Write-Host ""
            Write-Host "⚠️  Port forwarding stopped unexpectedly" -ForegroundColor Yellow
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "Stopping port forwarding..." -ForegroundColor Yellow
    Stop-Job -Job $frontendJob, $backendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $frontendJob, $backendJob -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Port forwarding stopped" -ForegroundColor Green
}
