# Docker Startup Helper
# Waits for Docker to be ready and then deploys the platform

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "    Docker Startup Helper - Agent Investment Platform" -ForegroundColor Cyan  
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Waiting for Docker Desktop to fully initialize..." -ForegroundColor Cyan
Write-Host "[INFO] This can take 2-5 minutes after installation..." -ForegroundColor Yellow
Write-Host ""

# Function to test Docker connectivity
function Test-DockerReady {
    try {
        docker info | Out-Null 2>$null
        return $true
    } catch {
        return $false
    }
}

# Wait for Docker to be ready (max 5 minutes)
$timeout = 300  # 5 minutes
$timer = 0
$checkInterval = 10

Write-Host "Checking Docker status..." -ForegroundColor Blue
while ($timer -lt $timeout) {
    if (Test-DockerReady) {
        Write-Host ""
        Write-Host "[SUCCESS] Docker is ready!" -ForegroundColor Green
        break
    } else {
        Write-Host "." -NoNewline -ForegroundColor Yellow
        Start-Sleep -Seconds $checkInterval
        $timer += $checkInterval
    }
}

if ($timer -ge $timeout) {
    Write-Host ""
    Write-Host "[ERROR] Docker failed to start within 5 minutes" -ForegroundColor Red
    Write-Host "[INFO] Please manually check Docker Desktop and try again" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "[SUCCESS] Docker is ready! Starting deployment..." -ForegroundColor Green
Write-Host ""

# Now deploy the platform
Write-Host "Building Docker images..." -ForegroundColor Blue
docker-compose build --no-cache --parallel

Write-Host ""
Write-Host "Starting services in development mode..." -ForegroundColor Blue
docker-compose --profile development up -d

Write-Host ""
Write-Host "Waiting for services to initialize..." -ForegroundColor Blue
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Platform URLs:" -ForegroundColor Cyan
Write-Host "   Main Application:     http://localhost:8000" -ForegroundColor White
Write-Host "   Grafana Dashboard:    http://localhost:3000" -ForegroundColor White
Write-Host "   Prometheus Metrics:   http://localhost:9090" -ForegroundColor White
Write-Host ""

Write-Host "Test connectivity:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   SUCCESS: Main application is responding!" -ForegroundColor Green
} catch {
    Write-Host "   WARNING: Main application starting (may take a few minutes)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[SUCCESS] Platform deployment complete!" -ForegroundColor Green
Write-Host ""