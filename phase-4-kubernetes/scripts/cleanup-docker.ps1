#!/usr/bin/env pwsh
# Docker Cleanup Script - Frees maximum space

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Docker Cleanup - Free C: Drive Space" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Remove all stopped containers
Write-Host "Removing stopped containers..." -ForegroundColor Yellow
docker container prune -f

# Remove all dangling images
Write-Host "Removing dangling images..." -ForegroundColor Yellow
docker image prune -f

# Remove all unused images (not just dangling)
Write-Host "Removing all unused images..." -ForegroundColor Yellow
docker image prune -a -f

# Remove all unused volumes
Write-Host "Removing unused volumes..." -ForegroundColor Yellow
docker volume prune -f

# Remove all unused networks
Write-Host "Removing unused networks..." -ForegroundColor Yellow
docker network prune -f

# Remove build cache
Write-Host "Removing build cache..." -ForegroundColor Yellow
docker builder prune -a -f

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Show disk usage
Write-Host "Current Docker disk usage:" -ForegroundColor Cyan
docker system df

Write-Host ""
Write-Host "Note: Your backend image (ahmed-khi/todo-backend:v4.0.0) was preserved" -ForegroundColor Yellow
Write-Host "      You can now rebuild the frontend image" -ForegroundColor Yellow
