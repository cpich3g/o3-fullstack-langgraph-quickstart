# Deep Research AI - Windows Deployment Script
# This script builds and deploys the application using Docker on Windows

param(
    [switch]$Clean,
    [switch]$Build,
    [switch]$Logs,
    [switch]$Stop
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deep Research AI - Windows Deployment Script" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Function to check if .env file exists and validate
function Test-Environment {
    if (-not (Test-Path ".env")) {
        Write-Host "❌ .env file not found. Please copy .env.example to .env and configure your settings." -ForegroundColor Red
        Write-Host "   Copy-Item .env.example .env" -ForegroundColor Yellow
        Write-Host "   # Then edit .env with your Azure OpenAI and other settings" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Environment file found" -ForegroundColor Green
    
    # Check required variables
    $envContent = Get-Content ".env" | Where-Object { $_ -notmatch '^#' -and $_ -match '=' }
    $envVars = @{}
    foreach ($line in $envContent) {
        if ($line -match '([^=]+)=(.*)') {
            $envVars[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
    
    $requiredVars = @("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "POSTGRES_PASSWORD")
    foreach ($var in $requiredVars) {
        if (-not $envVars[$var] -or $envVars[$var] -eq "") {
            Write-Host "❌ Required environment variable $var is not set in .env file" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✅ Required environment variables validated" -ForegroundColor Green
}

# Function to clean up containers and volumes
function Stop-Services {
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    try {
        docker-compose -f docker-compose.production.yml down
        Write-Host "✅ Services stopped" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Error stopping services: $_" -ForegroundColor Yellow
    }
}

# Function to clean up everything
function Clean-Environment {
    Write-Host "🧹 Cleaning up Docker environment..." -ForegroundColor Yellow
    Stop-Services
    
    try {
        docker-compose -f docker-compose.production.yml down -v --remove-orphans
        docker system prune -f
        Write-Host "✅ Environment cleaned" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Error during cleanup: $_" -ForegroundColor Yellow
    }
}

# Function to show logs
function Show-Logs {
    Write-Host "📋 Showing service logs..." -ForegroundColor Cyan
    docker-compose -f docker-compose.production.yml logs -f
}

# Function to build and deploy
function Start-Deployment {
    Test-Environment
    
    Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
    try {
        docker-compose -f docker-compose.production.yml build --no-cache
        Write-Host "✅ Docker images built successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to build Docker images: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🏃 Starting services..." -ForegroundColor Cyan
    try {
        docker-compose -f docker-compose.production.yml up -d
        Write-Host "✅ Services started" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to start services: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Check service health
    Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
    $maxAttempts = 20
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Application is healthy and ready!" -ForegroundColor Green
                break
            }
        }
        catch {
            # Continue trying
        }
        
        if ($attempt -eq $maxAttempts) {
            Write-Host "❌ Application failed to start properly after $maxAttempts attempts" -ForegroundColor Red
            Write-Host "📋 Service status:" -ForegroundColor Yellow
            docker-compose -f docker-compose.production.yml ps
            Write-Host "📋 Recent logs:" -ForegroundColor Yellow
            docker-compose -f docker-compose.production.yml logs --tail=50
            exit 1
        }
        
        Write-Host "⏳ Attempt $attempt/$maxAttempts - waiting for application to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    # Display success information
    Write-Host ""
    Write-Host "🎉 Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Service Information:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "🌐 Deep Research AI:  http://localhost:8000" -ForegroundColor White
    Write-Host "🔍 API Documentation: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "📊 Health Check:      http://localhost:8000/health" -ForegroundColor White
    Write-Host "🗄️  PostgreSQL:       localhost:5432" -ForegroundColor White
    Write-Host "🔴 Redis:             localhost:6379" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
    Write-Host "  View logs:          .\deploy.ps1 -Logs" -ForegroundColor White
    Write-Host "  Stop services:      .\deploy.ps1 -Stop" -ForegroundColor White
    Write-Host "  Clean environment:  .\deploy.ps1 -Clean" -ForegroundColor White
    Write-Host "  Rebuild:            .\deploy.ps1 -Build" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Your Deep Research AI is now running!" -ForegroundColor Green
}

# Main script logic
try {
    if ($Clean) {
        Clean-Environment
    }
    elseif ($Stop) {
        Stop-Services
    }
    elseif ($Logs) {
        Show-Logs
    }
    elseif ($Build) {
        Start-Deployment
    }
    else {
        # Default action - start deployment
        Start-Deployment
    }
}
catch {
    Write-Host "❌ Script execution failed: $_" -ForegroundColor Red
    exit 1
}
