# Agent Investment Platform - Docker Setup Script
# PowerShell version for better Windows compatibility

param(
    [switch]$SkipInstall,
    [switch]$DevMode,
    [switch]$Monitoring
)

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       Agent Investment Platform - Docker Setup" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check Docker installation
function Test-DockerInstalled {
    try {
        $null = docker --version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker info 2>$null
        return $true
    }
    catch {
        return $false
    }
}

# Check administrator privileges
if (-not (Test-Administrator)) {
    Write-Host "❌ This script requires administrator privileges" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green

# Check Docker installation
Write-Host ""
Write-Host "Checking Docker installation..." -ForegroundColor Yellow

if (Test-DockerInstalled) {
    Write-Host "✅ Docker is installed" -ForegroundColor Green
    docker --version

    if (Test-DockerRunning) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is installed but not running" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please:" -ForegroundColor Yellow
        Write-Host "1. Launch Docker Desktop from Start menu" -ForegroundColor White
        Write-Host "2. Wait for it to start (green whale icon in system tray)" -ForegroundColor White
        Write-Host "3. Run this script again" -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    if ($SkipInstall) {
        Write-Host "❌ Docker not installed and -SkipInstall specified" -ForegroundColor Red
        exit 1
    }

    Write-Host "❌ Docker not found. Installing..." -ForegroundColor Red
    Write-Host ""

    # Try winget first
    try {
        $null = winget --version 2>$null
        Write-Host "✅ Using Windows Package Manager (winget)" -ForegroundColor Green
        Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow

        winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker Desktop installed successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "IMPORTANT: Please restart your computer now!" -ForegroundColor Red
            Write-Host "After restart:" -ForegroundColor Yellow
            Write-Host "1. Launch Docker Desktop" -ForegroundColor White
            Write-Host "2. Complete initial setup" -ForegroundColor White
            Write-Host "3. Run this script again" -ForegroundColor White
            Read-Host "Press Enter to exit"
            exit 0
        } else {
            throw "winget installation failed"
        }
    }
    catch {
        Write-Host "❌ Automatic installation failed" -ForegroundColor Red
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host "                 Manual Installation Required" -ForegroundColor Yellow
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please follow these steps:" -ForegroundColor White
        Write-Host ""
        Write-Host "1. Open your web browser" -ForegroundColor White
        Write-Host "2. Go to: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Cyan
        Write-Host "3. Click 'Docker Desktop for Windows'" -ForegroundColor White
        Write-Host "4. Download and run 'Docker Desktop Installer.exe'" -ForegroundColor White
        Write-Host "5. During installation, ensure these options are checked:" -ForegroundColor White
        Write-Host "   - Use WSL 2 instead of Hyper-V" -ForegroundColor Gray
        Write-Host "   - Add shortcut to desktop" -ForegroundColor Gray
        Write-Host "6. Restart your computer when prompted" -ForegroundColor White
        Write-Host "7. Launch Docker Desktop after restart" -ForegroundColor White
        Write-Host "8. Complete the initial setup" -ForegroundColor White
        Write-Host "9. Run this script again" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    }
}

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ docker-compose.yml not found" -ForegroundColor Red
    Write-Host "Please run this script from the Agent Investment Platform root directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found Agent Investment Platform configuration" -ForegroundColor Green

# Check Python virtual environment
Write-Host ""
Write-Host "Checking Python environment..." -ForegroundColor Yellow

if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run the main setup first:" -ForegroundColor Yellow
    Write-Host "  python scripts/initialize.py --interactive" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}

# Determine Docker Compose profile
$profile = "production"
if ($DevMode) {
    $profile = "development"
}
if ($Monitoring) {
    $profile += ",monitoring"
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "              Building and Starting Services" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Profile: $profile" -ForegroundColor Yellow
Write-Host ""

# Build Docker images
Write-Host "Building Docker images (this may take several minutes)..." -ForegroundColor Yellow
docker-compose build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Docker images" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Docker images built successfully" -ForegroundColor Green

# Start services
Write-Host ""
Write-Host "Starting Docker services with profile: $profile" -ForegroundColor Yellow
docker-compose --profile $profile up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Services started successfully" -ForegroundColor Green

# Wait for services to be ready
Write-Host ""
Write-Host "Waiting for services to start up..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Show status
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                   Deployment Status" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
docker-compose ps

# Show access information
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "                   🎉 SUCCESS! Platform Ready" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Agent Investment Platform is now running!" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Main Application:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 Grafana Monitoring:   http://localhost:3000" -ForegroundColor Cyan
Write-Host "📈 Prometheus Metrics:   http://localhost:9090" -ForegroundColor Cyan
Write-Host "🗄️  Database (PostgreSQL): localhost:5432" -ForegroundColor Cyan
Write-Host "🔴 Cache (Redis):        localhost:6379" -ForegroundColor Cyan

if ($profile -match "monitoring") {
    Write-Host ""
    Write-Host "Monitoring services are enabled:" -ForegroundColor Yellow
    Write-Host "- Grafana username: admin" -ForegroundColor White
    Write-Host "- Grafana password: Check .env.docker file" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "                   Useful Commands" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "View logs:           docker-compose logs -f" -ForegroundColor White
Write-Host "Stop services:       docker-compose down" -ForegroundColor White
Write-Host "Restart services:    docker-compose restart" -ForegroundColor White
Write-Host "Check status:        docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "For advanced management:" -ForegroundColor White
Write-Host "  python docker-manager.py --help" -ForegroundColor Gray
Write-Host ""

# Health check
Write-Host "Running quick health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 10
    Write-Host "✅ Main application is responding" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Main application not yet ready (may take a few more minutes)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! The platform is ready for use." -ForegroundColor Green
Read-Host "Press Enter to finish"
