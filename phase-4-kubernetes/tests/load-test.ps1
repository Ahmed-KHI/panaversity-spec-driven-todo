# [Task]: T075
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 11
# [Description]: Load tests to verify HPA autoscaling (PowerShell version)

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Load Tests (HPA Validation)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BASE_URL = "http://todo.local"
$REQUESTS = 1000
$CONCURRENCY = 100
$NAMESPACE = "default"

# Check if we can use Invoke-WebRequest for load testing
# Note: PowerShell doesn't have a built-in ab equivalent
# We'll use a simple loop for demonstration

Write-Host "⚠️  Note: PowerShell doesn't have ApacheBench" -ForegroundColor Yellow
Write-Host "Using Invoke-WebRequest for basic load generation" -ForegroundColor Yellow
Write-Host "For production load testing, consider:" -ForegroundColor Yellow
Write-Host "  - Apache Bench (ab) via WSL"
Write-Host "  - hey (https://github.com/rakyll/hey)"
Write-Host "  - k6 (https://k6.io/)"
Write-Host ""

# Get initial HPA status
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Initial HPA Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
kubectl get hpa -n $NAMESPACE
Write-Host ""

# Get initial pod count
$INITIAL_FRONTEND_PODS = (kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=frontend --no-headers | Measure-Object).Count
$INITIAL_BACKEND_PODS = (kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=backend --no-headers | Measure-Object).Count

Write-Host "Initial pod counts:"
Write-Host "  Frontend: $INITIAL_FRONTEND_PODS pods"
Write-Host "  Backend: $INITIAL_BACKEND_PODS pods"
Write-Host ""

# Run load test
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running Load Test" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target: $BASE_URL/"
Write-Host "Requests: $REQUESTS (via parallel jobs)"
Write-Host ""

Write-Host "Starting load test... (this will take ~30 seconds)" -ForegroundColor Yellow

$startTime = Get-Date

# Create parallel jobs for load generation
$jobs = @()
for ($i = 0; $i -lt 10; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($url, $count)
        for ($j = 0; $j -lt $count; $j++) {
            try {
                Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5 | Out-Null
            } catch {
                # Ignore errors for load testing
            }
        }
    } -ArgumentList $BASE_URL, ($REQUESTS / 10)
}

# Wait for jobs to complete
$jobs | Wait-Job | Out-Null
$jobs | Remove-Job

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "Load test complete!" -ForegroundColor Green
Write-Host "Duration: $([math]::Round($duration, 2)) seconds"
Write-Host "Requests per second: $([math]::Round($REQUESTS / $duration, 2))"
Write-Host ""

# Monitor HPA for scale-up
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Monitoring HPA Scale-Up (60 seconds)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Watching for pod scaling..."
for ($i = 1; $i -le 12; $i++) {
    Write-Host "Check $i/12 ($($i * 5) seconds elapsed)" -ForegroundColor Cyan
    kubectl get hpa -n $NAMESPACE
    kubectl get pods -n $NAMESPACE -l 'app.kubernetes.io/component in (frontend,backend)'
    Write-Host ""
    
    Start-Sleep -Seconds 5
}

# Get final pod count
$FINAL_FRONTEND_PODS = (kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=frontend --no-headers | Measure-Object).Count
$FINAL_BACKEND_PODS = (kubectl get pods -n $NAMESPACE -l app.kubernetes.io/component=backend --no-headers | Measure-Object).Count

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Load Test Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Initial pods:"
Write-Host "  Frontend: $INITIAL_FRONTEND_PODS → Final: $FINAL_FRONTEND_PODS"
Write-Host "  Backend: $INITIAL_BACKEND_PODS → Final: $FINAL_BACKEND_PODS"
Write-Host ""

if ($FINAL_FRONTEND_PODS -gt $INITIAL_FRONTEND_PODS -or $FINAL_BACKEND_PODS -gt $INITIAL_BACKEND_PODS) {
    Write-Host "✅ HPA triggered scale-up successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Autoscaling is working correctly."
    Write-Host ""
    Write-Host "Note: Pods will scale down after ~5 minutes of low load."
} else {
    Write-Host "⚠️  No scale-up detected" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possible reasons:"
    Write-Host "1. Load was not high enough to trigger scaling threshold (70% CPU)"
    Write-Host "2. HPA needs more time to react (check again in 1-2 minutes)"
    Write-Host "3. Pods already at maximum replicas"
    Write-Host ""
    Write-Host "Check HPA metrics:"
    Write-Host "  kubectl get hpa -n $NAMESPACE"
    Write-Host "  kubectl top pods -n $NAMESPACE"
}

Write-Host ""
