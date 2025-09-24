# Agent Investment Platform - Master Installation Script
# This script installs ALL required tools and deploys the complete platform

param(
    [switch]$SkipChecks,
    [switch]$DevMode,
    [switch]$Force
)

# Set error handling
$ErrorActionPreference = "Stop"

# Color functions for better output
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "[STEP] $Message" -ForegroundColor Blue }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "    Agent Investment Platform - Master Installer" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Info "This script will install and configure everything needed for the platform"
Write-Host ""

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Error "This script requires administrator privileges"
    Write-Warning "Please:"
    Write-Host "1. Right-click PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "3. Navigate to: $PWD" -ForegroundColor White
    Write-Host "4. Run: .\master-installer.ps1" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Success "Running as Administrator"

# ============================================================================
# STEP 1: Install System Requirements
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 1: Installing System Requirements" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Install Chocolatey if not present
Write-Step "Checking Chocolatey package manager..."
try {
    choco --version | Out-Null
    Write-Success "Chocolatey is installed"
} catch {
    Write-Step "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    # Refresh environment
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    Write-Success "Chocolatey installed successfully"
}

# Install winget if not present (Windows 10/11)
Write-Step "Checking Windows Package Manager (winget)..."
try {
    winget --version | Out-Null
    Write-Success "winget is available"
} catch {
    Write-Warning "winget not available - will use Chocolatey as fallback"
}

# ============================================================================
# STEP 2: Install Docker Desktop
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 2: Installing Docker Desktop" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Step "Checking Docker installation..."
try {
    $dockerVersion = docker --version 2>$null
    Write-Success "Docker is installed: $dockerVersion"

    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
    } catch {
        Write-Warning "Docker is installed but not running"
        Write-Step "Starting Docker Desktop..."
        Start-Process "Docker Desktop" -WindowStyle Hidden
        Write-Info "Waiting for Docker to start..."

        $timeout = 120 # 2 minutes
        $timer = 0
        do {
            Start-Sleep -Seconds 5
            $timer += 5
            try {
                docker info | Out-Null
                Write-Success "Docker is now running"
                break
            } catch {
                Write-Host "." -NoNewline -ForegroundColor Yellow
            }
        } while ($timer -lt $timeout)

        if ($timer -ge $timeout) {
            Write-Error "Docker failed to start within $timeout seconds"
            Write-Info "Please manually start Docker Desktop and run this script again"
            exit 1
        }
    }
} catch {
    Write-Step "Docker not found. Installing Docker Desktop..."

    # Try winget first
    try {
        winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements --silent
        Write-Success "Docker Desktop installed via winget"
    } catch {
        # Fallback to Chocolatey
        try {
            choco install docker-desktop -y
            Write-Success "Docker Desktop installed via Chocolatey"
        } catch {
            Write-Error "Failed to install Docker Desktop automatically"
            Write-Info "Please manually install Docker Desktop from:"
            Write-Host "https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Cyan
            Read-Host "Press Enter after Docker Desktop is installed"
        }
    }

    Write-Warning "Docker Desktop installed - RESTART REQUIRED"
    Write-Info "Please:"
    Write-Host "1. Restart your computer now" -ForegroundColor White
    Write-Host "2. Launch Docker Desktop after restart" -ForegroundColor White
    Write-Host "3. Complete the Docker setup wizard" -ForegroundColor White
    Write-Host "4. Run this script again" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 0
}

# ============================================================================
# STEP 3: Install Python and Dependencies
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 3: Setting up Python Environment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Step "Checking Python installation..."
try {
    $pythonVersion = python --version 2>$null
    Write-Success "Python is installed: $pythonVersion"
} catch {
    Write-Step "Installing Python..."
    try {
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
        Write-Success "Python installed via winget"
    } catch {
        choco install python311 -y
        Write-Success "Python installed via Chocolatey"
    }

    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
}

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
& ".venv\Scripts\python.exe" -m pip install --upgrade pip
& ".venv\Scripts\pip.exe" install -r requirements.txt
Write-Success "Python dependencies installed"

# ============================================================================
# STEP 4: Install Node.js
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 4: Installing Node.js" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Step "Checking Node.js installation..."
try {
    $nodeVersion = node --version 2>$null
    Write-Success "Node.js is installed: $nodeVersion"
} catch {
    Write-Step "Installing Node.js..."
    try {
        winget install OpenJS.NodeJS --accept-package-agreements --accept-source-agreements --silent
        Write-Success "Node.js installed via winget"
    } catch {
        choco install nodejs -y
        Write-Success "Node.js installed via Chocolatey"
    }

    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
}

# ============================================================================
# STEP 5: Install Additional Tools
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 5: Installing Additional Tools" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Install Git if not present
Write-Step "Checking Git installation..."
try {
    git --version | Out-Null
    Write-Success "Git is installed"
} catch {
    Write-Step "Installing Git..."
    try {
        winget install Git.Git --accept-package-agreements --accept-source-agreements --silent
    } catch {
        choco install git -y
    }
    Write-Success "Git installed"

    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
}

# Install VS Code if not present (optional but recommended)
Write-Step "Checking VS Code installation..."
try {
    code --version | Out-Null
    Write-Success "VS Code is installed"
} catch {
    Write-Step "Installing VS Code..."
    try {
        winget install Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements --silent
    } catch {
        choco install vscode -y
    }
    Write-Success "VS Code installed"
}

# ============================================================================
# STEP 6: Configure Environment
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 6: Configuring Environment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Ensure .env file exists
Write-Step "Configuring environment variables..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Success "Environment file created from template"
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
# STEP 7: Build and Deploy Services
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 7: Building and Deploying Services" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Step "Building Docker images..."
docker-compose build --no-cache --parallel
if ($LASTEXITCODE -eq 0) {
    Write-Success "Docker images built successfully"
} else {
    Write-Error "Failed to build Docker images"
    Write-Info "Continuing with existing images..."
}

# Determine deployment profile
$profile = if ($DevMode) { "development" } else { "production" }
Write-Step "Starting services with profile: $profile"

docker-compose --profile $profile up -d
if ($LASTEXITCODE -eq 0) {
    Write-Success "Services started successfully"
} else {
    Write-Error "Failed to start some services"
    Write-Info "Checking service status..."
}

# ============================================================================
# STEP 8: Validation and Health Checks
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STEP 8: Validating Deployment" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Step "Waiting for services to initialize..."
Start-Sleep -Seconds 30

Write-Step "Running health checks..."
& ".venv\Scripts\python.exe" scripts\health-check.py

Write-Step "Running deployment test..."
& ".venv\Scripts\python.exe" deployment_test.py

# Show service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
docker-compose ps

# ============================================================================
# COMPLETION SUMMARY
# ============================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Success "Agent Investment Platform is now fully deployed!"
Write-Host ""

Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "   Main Application:     http://localhost:8000" -ForegroundColor White
Write-Host "   Grafana Monitoring:   http://localhost:3000" -ForegroundColor White
Write-Host "   Prometheus Metrics:   http://localhost:9090" -ForegroundColor White
Write-Host ""

Write-Host "Database Connections:" -ForegroundColor Cyan
Write-Host "   PostgreSQL:           localhost:5432" -ForegroundColor White
Write-Host "   Redis:               localhost:6379" -ForegroundColor White
Write-Host ""

Write-Host "Management Commands:" -ForegroundColor Cyan
Write-Host "   Check status:         docker-compose ps" -ForegroundColor White
Write-Host "   View logs:           docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services:       docker-compose down" -ForegroundColor White
Write-Host "   Restart services:    docker-compose restart" -ForegroundColor White
Write-Host "   Python manager:      python docker-manager.py --help" -ForegroundColor White
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "   Setup Guide:         DOCKER_SETUP.md" -ForegroundColor White
Write-Host "   API Docs:           docs/api/README.md" -ForegroundColor White
Write-Host "   User Guide:         docs/README.md" -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Configure additional API keys in .env file" -ForegroundColor White
Write-Host "2. Customize investment strategies in config/strategies.yaml" -ForegroundColor White
Write-Host "3. Access the web interface at http://localhost:8000" -ForegroundColor White
Write-Host "4. Set up automated reports via the scheduler" -ForegroundColor White
Write-Host ""

Write-Success "Platform is ready for AI-powered investment analysis!"
Write-Host ""

# Final health check
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 10 -UseBasicParsing
    Write-Success "Main application is responding!"
} catch {
    Write-Warning "Main application may still be starting (check logs with: docker-compose logs -f)"
}

Write-Host ""
Read-Host "Press Enter to finish"
