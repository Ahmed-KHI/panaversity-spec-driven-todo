# Start Chat Testing Environment
# This script opens both frontend and backend for manual testing

Write-Host "🚀 Starting Chat Test Environment" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

# Start backend port-forward
Write-Host "Starting backend port-forward on localhost:8000..." -ForegroundColor Yellow
Start-Job -Name "backend-pf" -ScriptBlock { 
    kubectl port-forward svc/todo-backend 8000:8000 -n todo-app 
} | Out-Null

Start-Sleep -Seconds 2

# Start frontend port-forward
Write-Host "Starting frontend port-forward on localhost:3000..." -ForegroundColor Yellow
Start-Job -Name "frontend-pf" -ScriptBlock { 
    kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app 
} | Out-Null

Start-Sleep -Seconds 3

# Test backend
Write-Host "`nTesting backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($health.status -eq "healthy") {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "✅ Chat Test Environment Ready!" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Access Points:" -ForegroundColor Cyan
Write-Host "  • Frontend:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host "  • Backend:   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "  • API Docs:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""

Write-Host "🧪 Test Instructions:" -ForegroundColor Cyan
Write-Host "  1. Open: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host "  2. Login with your credentials" -ForegroundColor White
Write-Host "  3. Navigate to " -NoNewline -ForegroundColor White
Write-Host "/chat" -ForegroundColor Blue -NoNewline
Write-Host " page" -ForegroundColor White
Write-Host "  4. Test AI with:" -ForegroundColor White
Write-Host "     • 'Hello'" -ForegroundColor Gray
Write-Host "     • 'Show me my tasks'" -ForegroundColor Gray
Write-Host "     • 'Add task to test AI chat'" -ForegroundColor Gray
Write-Host "     • 'Complete task 1'" -ForegroundColor Gray
Write-Host ""

Write-Host "🛑 To stop port-forwards:" -ForegroundColor Yellow
Write-Host "   Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Gray
Write-Host ""

# Open browser automatically
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host "`n✨ Happy testing! Press Ctrl+C to exit." -ForegroundColor Green
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 10
        # Check if jobs are still running
        $jobs = Get-Job -Name "*-pf" -ErrorAction SilentlyContinue
        if ($jobs.Count -lt 2) {
            Write-Host "⚠️ Port-forward jobs stopped. Restarting..." -ForegroundColor Yellow
            Get-Job | Stop-Job
            Get-Job | Remove-Job
            & $PSCommandPath
            break
        }
    }
} finally {
    Write-Host "`n🛑 Stopping port-forwards..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}
