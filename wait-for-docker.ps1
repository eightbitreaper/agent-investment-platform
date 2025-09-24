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

# Function to test Docker connectivity with detailed feedback
function Test-DockerReady {
    try {
        $dockerInfo = docker info 2>&1
        if ($dockerInfo -match "Server:") {
            return @{ Status = "Ready"; Message = "Docker daemon is running" }
        } else {
            return @{ Status = "NotReady"; Message = "Docker daemon not responding" }
        }
    } catch {
        return @{ Status = "Error"; Message = $_.Exception.Message }
    }
}

# Function to test basic Docker operations
function Test-DockerOperations {
    try {
        # Test basic docker command
        docker --version | Out-Null

        # Test docker daemon connectivity
        docker system info | Out-Null

        # Test image pulling capability
        docker images | Out-Null

        return $true
    } catch {
        return $false
    }
}

# Enhanced Docker readiness check with active testing
$timeout = 300  # 5 minutes
$timer = 0
$checkInterval = 5  # Check every 5 seconds for more responsive feedback
$attempt = 1

Write-Host "Starting active Docker connectivity tests..." -ForegroundColor Blue
Write-Host ""

while ($timer -lt $timeout) {
    Write-Host "[$attempt] Testing Docker connectivity..." -ForegroundColor Cyan

    $dockerTest = Test-DockerReady
    Write-Host "    Status: $($dockerTest.Status)" -ForegroundColor $(if ($dockerTest.Status -eq "Ready") { "Green" } else { "Yellow" })
    Write-Host "    Message: $($dockerTest.Message)" -ForegroundColor Gray

    if ($dockerTest.Status -eq "Ready") {
        Write-Host "    Testing Docker operations..." -ForegroundColor Cyan
        if (Test-DockerOperations) {
            Write-Host "    Docker operations test: PASSED" -ForegroundColor Green
            Write-Host ""
            Write-Host "[SUCCESS] Docker is fully ready!" -ForegroundColor Green
            break
        } else {
            Write-Host "    Docker operations test: FAILED" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Start-Sleep -Seconds $checkInterval
    $timer += $checkInterval
    $attempt++
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
Write-Host "Monitoring service startup..." -ForegroundColor Blue

# Function to test service health
function Test-ServiceHealth {
    param($ServiceName, $Port, $Path = "/")
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port$Path" -TimeoutSec 3 -UseBasicParsing
        return @{ Status = "Healthy"; StatusCode = $response.StatusCode }
    } catch {
        return @{ Status = "Unhealthy"; Error = $_.Exception.Message }
    }
}

# Monitor services for up to 2 minutes
$serviceTimeout = 120
$serviceTimer = 0
$serviceCheckInterval = 10

$services = @(
    @{ Name = "Main App"; Port = 8000; Path = "/" },
    @{ Name = "Grafana"; Port = 3000; Path = "/api/health" },
    @{ Name = "Prometheus"; Port = 9090; Path = "/-/healthy" }
)

while ($serviceTimer -lt $serviceTimeout) {
    Write-Host ""
    Write-Host "Service Health Check (Attempt $([math]::Floor($serviceTimer / $serviceCheckInterval) + 1)):" -ForegroundColor Cyan

    $allHealthy = $true
    foreach ($service in $services) {
        $health = Test-ServiceHealth -ServiceName $service.Name -Port $service.Port -Path $service.Path
        $color = if ($health.Status -eq "Healthy") { "Green" } else { "Yellow" }
        Write-Host "    $($service.Name): $($health.Status)" -ForegroundColor $color
        if ($health.Status -ne "Healthy") { $allHealthy = $false }
    }

    if ($allHealthy) {
        Write-Host ""
        Write-Host "[SUCCESS] All services are healthy!" -ForegroundColor Green
        break
    } else {
        Write-Host "    Waiting for services to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds $serviceCheckInterval
        $serviceTimer += $serviceCheckInterval
    }
}

Write-Host ""
Write-Host "Final Service Status:" -ForegroundColor Yellow
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

Write-Host "Final Connectivity Test:" -ForegroundColor Cyan

# Test main endpoints
$endpoints = @(
    @{ Name = "Main Application"; Url = "http://localhost:8000"; Expected = 200 },
    @{ Name = "Health Check"; Url = "http://localhost:8000/health"; Expected = 200 },
    @{ Name = "Grafana"; Url = "http://localhost:3000"; Expected = 200 },
    @{ Name = "Prometheus"; Url = "http://localhost:9090"; Expected = 200 }
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq $endpoint.Expected) {
            Write-Host "   SUCCESS: $($endpoint.Name) is responding (HTTP $($response.StatusCode))" -ForegroundColor Green
        } else {
            Write-Host "   WARNING: $($endpoint.Name) returned HTTP $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ERROR: $($endpoint.Name) not accessible - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[SUCCESS] Platform deployment complete!" -ForegroundColor Green
Write-Host ""
