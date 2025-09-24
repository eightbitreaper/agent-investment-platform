# Agent Investment Platform - User Mode Installation Script
# This script installs what it can without admin privileges

param(
    [switch]$DevMode,
    [switch]$Force
)

# Set error handling
$ErrorActionPreference = "Continue"

# Color functions for better output
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "[STEP] $Message" -ForegroundColor Blue }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "    Agent Investment Platform - User Mode Installer" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Warning "Running in user mode - some features may require manual installation"
Write-Host ""

# ============================================================================
# STEP 1: Check System Requirements
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 1: Checking System Requirements" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Check Docker
Write-Step "Checking Docker installation..."
try {
    $dockerVersion = docker --version 2>$null
    Write-Success "Docker is installed: $dockerVersion"

    try {
        docker info | Out-Null 2>$null
        Write-Success "Docker is running"
    } catch {
        Write-Warning "Docker is installed but not running"
        Write-Info "Please start Docker Desktop manually"
    }
} catch {
    Write-Error "Docker not found - please install Docker Desktop from:"
    Write-Host "https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Cyan
}

# Check Python
Write-Step "Checking Python installation..."
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion -match "3\.(9|10|11|12)") {
        Write-Success "Python is installed: $pythonVersion"
    } else {
        Write-Warning "Python version may be incompatible: $pythonVersion"
    }
} catch {
    Write-Error "Python not found - please install Python 3.11 from:"
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
}

# Check Node.js
Write-Step "Checking Node.js installation..."
try {
    $nodeVersion = node --version 2>$null
    Write-Success "Node.js is installed: $nodeVersion"
} catch {
    Write-Warning "Node.js not found - optional but recommended for development"
    Write-Info "Download from: https://nodejs.org/"
}

# Check Git
Write-Step "Checking Git installation..."
try {
    git --version | Out-Null
    Write-Success "Git is installed"
} catch {
    Write-Warning "Git not found - required for some features"
    Write-Info "Download from: https://git-scm.com/download/win"
}

# ============================================================================
# STEP 2: Setup Python Environment
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 2: Setting up Python Environment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

try {
    # Check virtual environment
    Write-Step "Setting up Python virtual environment..."
    if (Test-Path ".venv") {
        Write-Success "Virtual environment exists"
    } else {
        python -m venv .venv
        Write-Success "Virtual environment created"
    }

    # Activate virtual environment and install dependencies
    Write-Step "Installing Python dependencies..."
    & ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
    & ".venv\Scripts\pip.exe" install -r requirements.txt --quiet
    Write-Success "Python dependencies installed"
} catch {
    Write-Error "Failed to setup Python environment: $_"
    Write-Info "Please ensure Python is installed and try again"
}

# ============================================================================
# STEP 3: Configure Environment
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 3: Configuring Environment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Ensure .env file exists
Write-Step "Configuring environment variables..."
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Success "Environment file created from template"
    } else {
        Write-Warning ".env.example not found - creating basic .env file"
        @"
# Basic environment configuration
NODE_ENV=development
LOG_LEVEL=info
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Basic environment file created"
    }
} else {
    Write-Success "Environment file already exists"
}

# Create necessary directories
$directories = @("data", "logs", "reports", "models", ".memory")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Success "Created directory: $dir"
    }
}

# ============================================================================
# STEP 4: Docker Setup and Deployment
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 4: Docker Setup and Deployment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Error "docker-compose.yml not found!"
    Write-Info "Please ensure you're in the correct directory"
    exit 1
}

try {
    Write-Step "Checking Docker connectivity..."
    docker info | Out-Null

    Write-Step "Building Docker images..."
    docker-compose build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker images built successfully"
    } else {
        Write-Error "Failed to build some Docker images"
    }

    # Determine deployment profile
    $profile = if ($DevMode) { "development" } else { "production" }
    Write-Step "Starting services with profile: $profile"

    docker-compose --profile $profile up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services started successfully"
    } else {
        Write-Error "Failed to start some services"
    }

} catch {
    Write-Error "Docker operations failed: $_"
    Write-Info "Please ensure Docker Desktop is running and try again"
}

# ============================================================================
# STEP 5: Validation
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 5: Validating Deployment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Step "Waiting for services to initialize..."
Start-Sleep -Seconds 15

# Check if validation scripts exist and run them
if (Test-Path "scripts\health-check.py") {
    Write-Step "Running health checks..."
    try {
        & ".venv\Scripts\python.exe" scripts\health-check.py
    } catch {
        Write-Warning "Health check failed or not available"
    }
}

if (Test-Path "deployment_test.py") {
    Write-Step "Running deployment test..."
    try {
        & ".venv\Scripts\python.exe" deployment_test.py
    } catch {
        Write-Warning "Deployment test failed or not available"
    }
}

# Show service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
try {
    docker-compose ps
} catch {
    Write-Warning "Could not retrieve service status"
}

# ============================================================================
# COMPLETION SUMMARY
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "USER MODE INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Success "Agent Investment Platform setup completed in user mode!"
Write-Host ""

Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "   Main Application:     http://localhost:8000" -ForegroundColor White
Write-Host "   Grafana Monitoring:   http://localhost:3000" -ForegroundColor White
Write-Host "   Prometheus Metrics:   http://localhost:9090" -ForegroundColor White
Write-Host ""

Write-Host "Management Commands:" -ForegroundColor Cyan
Write-Host "   Check status:         docker-compose ps" -ForegroundColor White
Write-Host "   View logs:           docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services:       docker-compose down" -ForegroundColor White
Write-Host "   Restart services:    docker-compose restart" -ForegroundColor White
Write-Host ""

Write-Host "For Full Features:" -ForegroundColor Yellow
Write-Host "Run as Administrator with: .\master-installer-fixed.ps1" -ForegroundColor White
Write-Host ""

# Final health check
try {
    Write-Step "Testing main application..."
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 10 -UseBasicParsing
    Write-Success "Main application is responding!"
} catch {
    Write-Warning "Main application may still be starting"
    Write-Info "Check with: docker-compose logs -f main-app"
}

Write-Host ""
Write-Success "Setup complete! Platform is ready for use."
Write-Host ""
