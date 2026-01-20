# [Task]: T073
# [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 11
# [Description]: Smoke tests for Phase IV deployment validation (PowerShell version)

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase IV: Smoke Tests" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BASE_URL = "http://todo.local"
$PASSED = 0
$FAILED = 0

# Test helper function
function Run-Test {
    param(
        [string]$TestName,
        [scriptblock]$TestCommand
    )
    
    Write-Host "🧪 Testing: $TestName" -ForegroundColor Cyan
    try {
        $result = & $TestCommand
        if ($result) {
            Write-Host "   ✅ PASSED" -ForegroundColor Green
            $script:PASSED++
        } else {
            Write-Host "   ❌ FAILED" -ForegroundColor Red
            $script:FAILED++
        }
    } catch {
        Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
        $script:FAILED++
    }
    Write-Host ""
}

# Test 1: Frontend health check
Run-Test "Frontend health endpoint" {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/health" -UseBasicParsing -ErrorAction Stop
    $response.StatusCode -eq 200 -and $response.Content -match "ok"
}

# Test 2: Backend health endpoint
Run-Test "Backend health endpoint" {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/health" -UseBasicParsing -ErrorAction Stop
    $response.StatusCode -eq 200 -and $response.Content -match "ok"
}

# Test 3: Frontend is accessible
Run-Test "Frontend home page" {
    $response = Invoke-WebRequest -Uri "$BASE_URL" -UseBasicParsing -ErrorAction Stop
    $response.StatusCode -eq 200 -and $response.Content -match "html"
}

# Test 4: Backend API is accessible
Run-Test "Backend API root" {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api" -UseBasicParsing -ErrorAction Stop
    $response.StatusCode -eq 200
}

# Test 5: Database connectivity (via backend health)
Run-Test "Database connectivity" {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/health" -UseBasicParsing -ErrorAction Stop
    $response.Content -match "database"
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Smoke Test Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Passed: $PASSED" -ForegroundColor Green
Write-Host "Failed: $FAILED" -ForegroundColor $(if ($FAILED -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($FAILED -eq 0) {
    Write-Host "✅ All smoke tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application is healthy and ready for use."
    exit 0
} else {
    Write-Host "❌ Some smoke tests failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check pod status: kubectl get pods"
    Write-Host "2. Check service status: kubectl get svc"
    Write-Host "3. Check ingress status: kubectl get ingress"
    Write-Host "4. View frontend logs: kubectl logs -l app.kubernetes.io/component=frontend --tail=50"
    Write-Host "5. View backend logs: kubectl logs -l app.kubernetes.io/component=backend --tail=50"
    Write-Host ""
    Write-Host "If ingress is not working, try port forwarding:" -ForegroundColor Yellow
    Write-Host "  .\scripts\port-forward.ps1"
    exit 1
}
