# AI Chat Testing Script
# Tests all AI chat functionality after fix deployment

Write-Host "🧪 AI Chat Validation - Phase 5" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check if Minikube is running
$minikubeStatus = minikube status --format='{{.Host}}' 2>$null
if ($minikubeStatus -ne "Running") {
    Write-Host "❌ Minikube is not running!" -ForegroundColor Red
    Write-Host "Start it with: minikube start" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Minikube is running" -ForegroundColor Green

# Check if namespace exists
$namespace = kubectl get namespace todo-app --ignore-not-found 2>$null
if (-not $namespace) {
    Write-Host "❌ Namespace 'todo-app' not found!" -ForegroundColor Red
    Write-Host "Create it with: kubectl apply -f namespace.yaml" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Namespace exists" -ForegroundColor Green

# Check if backend pod is running
$backendPod = kubectl get pods -n todo-app -l app=todo-backend -o jsonpath='{.items[0].metadata.name}' 2>$null
if (-not $backendPod) {
    Write-Host "❌ Backend pod not found!" -ForegroundColor Red
    Write-Host "Deploy it with: kubectl apply -f backend-deployment.yaml" -ForegroundColor Yellow
    exit 1
}

$podStatus = kubectl get pod $backendPod -n todo-app -o jsonpath='{.status.phase}' 2>$null
if ($podStatus -ne "Running") {
    Write-Host "❌ Backend pod is not running (Status: $podStatus)!" -ForegroundColor Red
    Write-Host "Check logs: kubectl logs $backendPod -n todo-app" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Backend pod is running: $backendPod" -ForegroundColor Green

Write-Host ""
Write-Host "Testing AI Chat Components..." -ForegroundColor Yellow
Write-Host ""

# Test 1: Check OpenAI API Key in Secret
Write-Host "Test 1: Checking OpenAI API Key..." -ForegroundColor Cyan
$apiKey = kubectl get secret postgres-secret -n todo-app -o jsonpath='{.data.openaiApiKey}' 2>$null
if (-not $apiKey) {
    Write-Host "❌ OpenAI API key not found in secret!" -ForegroundColor Red
    exit 1
}

$decodedKey = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($apiKey))
if ($decodedKey -like "sk-demo*" -or $decodedKey -like "*not-real*") {
    Write-Host "❌ Still using demo API key!" -ForegroundColor Red
    Write-Host "Key: $decodedKey" -ForegroundColor Yellow
    exit 1
}

if ($decodedKey -like "sk-*") {
    Write-Host "✅ Real OpenAI API key configured" -ForegroundColor Green
    Write-Host "   Key prefix: $($decodedKey.Substring(0, 20))..." -ForegroundColor Gray
} else {
    Write-Host "⚠️ API key format unexpected: $decodedKey" -ForegroundColor Yellow
}

# Test 2: Check Backend Logs for Errors
Write-Host ""
Write-Host "Test 2: Checking backend logs for errors..." -ForegroundColor Cyan
$logs = kubectl logs $backendPod -n todo-app --tail=50 2>&1
$errorCount = ($logs | Select-String -Pattern "error|ERROR|exception|Exception" | Measure-Object).Count
if ($errorCount -gt 0) {
    Write-Host "⚠️ Found $errorCount error(s) in logs:" -ForegroundColor Yellow
    $logs | Select-String -Pattern "error|ERROR|exception|Exception" | Select-Object -First 5
} else {
    Write-Host "✅ No errors in recent logs" -ForegroundColor Green
}

# Test 3: Check if OpenAI module is loaded
Write-Host ""
Write-Host "Test 3: Checking OpenAI configuration..." -ForegroundColor Cyan
$openaiImport = $logs | Select-String -Pattern "openai|OPENAI" | Select-Object -First 1
if ($openaiImport) {
    Write-Host "✅ OpenAI module detected in logs" -ForegroundColor Green
} else {
    Write-Host "⚠️ No OpenAI references in logs (might be normal)" -ForegroundColor Yellow
}

# Test 4: Health Check
Write-Host ""
Write-Host "Test 4: Testing health endpoint..." -ForegroundColor Cyan
Write-Host "Starting port-forward (this will take 5 seconds)..." -ForegroundColor Gray

# Start port-forward in background
$portForwardJob = Start-Job -ScriptBlock {
    kubectl port-forward svc/todo-backend 8000:8000 -n todo-app 2>&1 | Out-Null
}

Start-Sleep -Seconds 5

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    if ($health.status -eq "healthy") {
        Write-Host "✅ Backend health check passed" -ForegroundColor Green
        Write-Host "   Environment: $($health.environment)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Backend is running but not healthy" -ForegroundColor Yellow
        Write-Host "   Response: $($health | ConvertTo-Json)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Test API Root
Write-Host ""
Write-Host "Test 5: Testing API root endpoint..." -ForegroundColor Cyan
try {
    $root = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get -TimeoutSec 5
    Write-Host "✅ API root accessible" -ForegroundColor Green
    Write-Host "   Version: $($root.version)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API root failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: OpenAPI Docs
Write-Host ""
Write-Host "Test 6: Checking OpenAPI docs..." -ForegroundColor Cyan
try {
    $docs = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method Get -TimeoutSec 5
    if ($docs.StatusCode -eq 200) {
        Write-Host "✅ API documentation accessible" -ForegroundColor Green
        Write-Host "   URL: http://localhost:8000/docs" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ Docs endpoint failed (might be normal): $($_.Exception.Message)" -ForegroundColor Yellow
}

# Stop port-forward
Stop-Job -Job $portForwardJob
Remove-Job -Job $portForwardJob

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Summary
$passedTests = 0
$totalTests = 6

Write-Host "Prerequisites: ✅ PASSED" -ForegroundColor Green
Write-Host "OpenAI Key:    ✅ PASSED" -ForegroundColor Green
$passedTests += 2

if ($errorCount -eq 0) {
    Write-Host "Backend Logs:  ✅ PASSED" -ForegroundColor Green
    $passedTests++
} else {
    Write-Host "Backend Logs:  ⚠️ WARNINGS" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Score: $passedTests/$totalTests tests passed" -ForegroundColor Cyan
Write-Host ""

if ($passedTests -eq $totalTests) {
    Write-Host "🎉 All tests passed! AI Chat should be working." -ForegroundColor Green
} else {
    Write-Host "⚠️ Some tests failed. Review the output above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Manual Testing Steps:" -ForegroundColor Cyan
Write-Host "1. Port forward frontend:" -ForegroundColor White
Write-Host "   kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open browser: http://localhost:3000" -ForegroundColor White
Write-Host "3. Login with your credentials" -ForegroundColor White
Write-Host "4. Navigate to /chat" -ForegroundColor White
Write-Host "5. Send test messages:" -ForegroundColor White
Write-Host "   - 'Hello' (should get greeting)" -ForegroundColor Gray
Write-Host "   - 'Show me my tasks' (should list tasks)" -ForegroundColor Gray
Write-Host "   - 'Add task to test AI' (should create task)" -ForegroundColor Gray
Write-Host "   - 'Complete task 1' (should mark complete)" -ForegroundColor Gray
Write-Host ""
Write-Host "🐛 If chat still doesn't work:" -ForegroundColor Cyan
Write-Host "1. Check pod logs:" -ForegroundColor White
Write-Host "   kubectl logs $backendPod -n todo-app --tail=100" -ForegroundColor Gray
Write-Host "2. Check OpenAI API status: https://status.openai.com/" -ForegroundColor White
Write-Host "3. Verify API key is valid: https://platform.openai.com/api-keys" -ForegroundColor White
Write-Host "4. Check for rate limits in OpenAI dashboard" -ForegroundColor White
Write-Host ""
