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

# Set up project root path
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Write-Info "Project root: $projectRoot"
Set-Location $projectRoot

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

    # Test Docker Hub connectivity and authenticate if needed
    Write-Step "Testing Docker Hub connectivity..."
    try {
        docker pull hello-world 2>$null | Out-Null
        Write-Success "Docker Hub access is working"
    } catch {
        Write-Warning "Docker Hub requires authentication for image pulls"
        Write-Info ""
        Write-Info "Docker Hub now requires authentication to pull images."
        Write-Info "You need a free Docker Hub account to continue."
        Write-Info ""
        Write-Info "If you don't have an account:"
        Write-Info "1. Visit https://hub.docker.com and create a free account"
        Write-Info "2. Come back and continue with the web-based login below"
        Write-Info ""
        Write-Info "The installer will use Docker's secure device activation method."
        Write-Info "This will open your browser for safe authentication - no need to enter passwords here."
        Write-Info ""

        # Prompt for Docker Hub login
        $maxAttempts = 3
        $attempt = 1
        $loginSuccess = $false

        while ($attempt -le $maxAttempts -and -not $loginSuccess) {
            Write-Step "Docker Hub login attempt $attempt of $maxAttempts"
            Write-Info "Using web-based device activation for secure login..."
            Write-Info "This will open your browser for authentication."
            Write-Host ""

            # Use Docker's device activation flow (web-based login)
            docker login

            # Verify authentication by testing Docker Hub access
            Write-Step "Verifying Docker Hub access..."
            try {
                docker pull hello-world 2>$null | Out-Null
                Write-Success "Docker Hub login successful!"
                Write-Success "Docker Hub access verified"
                $loginSuccess = $true
            } catch {
                Write-Error "Docker Hub login failed - unable to pull test image"
                $attempt++

                if ($attempt -le $maxAttempts) {
                    Write-Info "Please try again with correct credentials"
                    Write-Info ""
                }
            }
        }

        if (-not $loginSuccess) {
            Write-Error "Failed to authenticate with Docker Hub after $maxAttempts attempts"
            Write-Info ""
            Write-Info "Please ensure you have:"
            Write-Info "1. A valid Docker Hub account (free at https://hub.docker.com)"
            Write-Info "2. Correct username and password/token"
            Write-Info "3. Stable internet connection"
            Write-Info ""
            Write-Info "You can also run 'docker login' manually and then re-run this installer"
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
$venvPath = Join-Path $projectRoot ".venv"
if (Test-Path $venvPath) {
    Write-Success "Virtual environment exists"
} else {
    python -m venv "$venvPath"
    Write-Success "Virtual environment created"
}

# Activate virtual environment and install dependencies
Write-Step "Installing Python dependencies..."
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"
& "$pythonExe" -m pip install --upgrade pip
$requirementsPath = Join-Path $projectRoot "requirements.txt"
if (Test-Path $requirementsPath) {
    & "$pipExe" install -r "$requirementsPath"
    Write-Success "Python dependencies installed from requirements.txt"
} else {
    Write-Warning "requirements.txt not found at: $requirementsPath"
    Write-Info "Skipping package installation - you may need to install packages manually"
}

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

# Function to generate secure passwords
function Generate-SecurePassword {
    param([int]$Length = 24)
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

# Create or update .env file with secure defaults and user input
Write-Host ""
Write-Info "Setting up environment configuration..."
Write-Info "The installer will generate secure passwords automatically"
Write-Info "and prompt you for optional API keys for enhanced functionality"
Write-Host ""

# Generate secure passwords
$postgresPassword = Generate-SecurePassword -Length 32
$redisPassword = Generate-SecurePassword -Length 32
$secretKey = Generate-SecurePassword -Length 48
$grafanaPassword = Generate-SecurePassword -Length 16

Write-Success "Generated secure passwords for database services"

# Create comprehensive .env file
$envContent = @"
# Agent Investment Platform Environment Variables
# Generated by master installer on $(Get-Date)

# =============================================================================
# Database Configuration (Auto-generated secure passwords)
# =============================================================================
POSTGRES_PASSWORD=$postgresPassword
REDIS_PASSWORD=$redisPassword

# =============================================================================
# LLM Configuration
# =============================================================================
LLM_PROVIDER=local

# For local LLM (Ollama)
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1

# For API-based LLMs (configured during setup)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# =============================================================================
# Data Source API Keys (Optional - configure for live data)
# =============================================================================
# Stock Data APIs
ALPHA_VANTAGE_API_KEY=
YAHOO_FINANCE_API_KEY=
FINNHUB_API_KEY=

# News APIs
NEWS_API_KEY=
GOOGLE_NEWS_API_KEY=

# Social Media APIs
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
TWITTER_BEARER_TOKEN=

# YouTube API
YOUTUBE_API_KEY=

# =============================================================================
# GitHub Integration
# =============================================================================
GITHUB_TOKEN=
GITHUB_REPO=eightbitreaper/agent-investment-platform
GITHUB_REPORTS_BRANCH=reports

# =============================================================================
# Notification Settings
# =============================================================================
EMAIL_ENABLED=false
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_TO_ADDRESS=

DISCORD_ENABLED=false
DISCORD_WEBHOOK_URL=

# =============================================================================
# System Configuration
# =============================================================================
ENVIRONMENT=production
LOG_LEVEL=INFO
DATA_RETENTION_DAYS=30
TIMEZONE=UTC

# Report generation schedule (cron format)
REPORT_SCHEDULE_HOURLY=0 * * * *
REPORT_SCHEDULE_DAILY=0 9 * * *
REPORT_SCHEDULE_WEEKLY=0 9 * * 1

# =============================================================================
# Security (Auto-generated)
# =============================================================================
SECRET_KEY=$secretKey
API_RATE_LIMIT_PER_HOUR=1000

# =============================================================================
# Monitoring (Auto-generated)
# =============================================================================
GRAFANA_PASSWORD=$grafanaPassword
"@

# Write the .env file
$envFile = Join-Path $projectRoot ".env"
$envContent | Out-File -FilePath "$envFile" -Encoding UTF8
Write-Success "Created .env file with secure defaults at: $envFile"

# Now prompt user for optional configurations
Write-Host ""
Write-Info "Optional Configuration Setup"
Write-Info "You can configure these now or skip and add them later to the .env file"
Write-Host ""

# LLM Provider choice
Write-Host "🧠 LLM Provider Configuration:" -ForegroundColor Cyan
Write-Host "1. Local (Ollama) - Free, private, runs on your machine"
Write-Host "2. OpenAI - Paid API, high quality, cloud-based"
Write-Host "3. Anthropic (Claude) - Paid API, excellent analysis"
Write-Host "4. Hybrid - Local + API for different tasks"
Write-Host ""

$llmChoice = Read-Host "Choose LLM provider (1-4) [default: 1]"
if ([string]::IsNullOrEmpty($llmChoice)) { $llmChoice = "1" }

$llmProviders = @{
    "1" = "local"
    "2" = "openai"
    "3" = "anthropic"
    "4" = "hybrid"
}

$selectedProvider = $llmProviders[$llmChoice]
if ($selectedProvider) {
    (Get-Content "$envFile") -replace "LLM_PROVIDER=local", "LLM_PROVIDER=$selectedProvider" | Set-Content "$envFile"
    Write-Success "Set LLM provider to: $selectedProvider"

    # Get API keys if needed
    if ($selectedProvider -eq "openai" -or $selectedProvider -eq "hybrid") {
        $openaiKey = Read-Host "Enter OpenAI API key (or press Enter to skip)"
        if (-not [string]::IsNullOrEmpty($openaiKey)) {
            (Get-Content "$envFile") -replace "OPENAI_API_KEY=", "OPENAI_API_KEY=$openaiKey" | Set-Content "$envFile"
            Write-Success "OpenAI API key configured"
        }
    }

    if ($selectedProvider -eq "anthropic" -or $selectedProvider -eq "hybrid") {
        $anthropicKey = Read-Host "Enter Anthropic API key (or press Enter to skip)"
        if (-not [string]::IsNullOrEmpty($anthropicKey)) {
            (Get-Content "$envFile") -replace "ANTHROPIC_API_KEY=", "ANTHROPIC_API_KEY=$anthropicKey" | Set-Content "$envFile"
            Write-Success "Anthropic API key configured"
        }
    }
}

# Email notifications setup
Write-Host ""
$setupEmail = Read-Host "Setup email notifications? (y/N)"
if ($setupEmail -eq "y" -or $setupEmail -eq "Y") {
    $emailUser = Read-Host "Enter email address"
    $emailPass = Read-Host "Enter email app password (for Gmail use app-specific password)" -AsSecureString
    $emailPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($emailPass))

    if (-not [string]::IsNullOrEmpty($emailUser)) {
        (Get-Content "$envFile") -replace "EMAIL_ENABLED=false", "EMAIL_ENABLED=true" | Set-Content "$envFile"
        (Get-Content "$envFile") -replace "EMAIL_USERNAME=", "EMAIL_USERNAME=$emailUser" | Set-Content "$envFile"
        (Get-Content "$envFile") -replace "EMAIL_TO_ADDRESS=", "EMAIL_TO_ADDRESS=$emailUser" | Set-Content "$envFile"
        (Get-Content "$envFile") -replace "EMAIL_PASSWORD=", "EMAIL_PASSWORD=$emailPassPlain" | Set-Content "$envFile"
        Write-Success "Email notifications configured"
    }
}

# Discord notifications setup
Write-Host ""
$setupDiscord = Read-Host "Setup Discord notifications? (y/N)"
if ($setupDiscord -eq "y" -or $setupDiscord -eq "Y") {
    $discordWebhook = Read-Host "Enter Discord webhook URL"
    if (-not [string]::IsNullOrEmpty($discordWebhook)) {
        (Get-Content "$envFile") -replace "DISCORD_ENABLED=false", "DISCORD_ENABLED=true" | Set-Content "$envFile"
        (Get-Content "$envFile") -replace "DISCORD_WEBHOOK_URL=", "DISCORD_WEBHOOK_URL=$discordWebhook" | Set-Content "$envFile"
        Write-Success "Discord notifications configured"
    }
}

Write-Host ""
Write-Success "Environment configuration completed!"
Write-Info "Database passwords: Auto-generated and secure"
Write-Info "You can add more API keys later by editing: $envFile"
Write-Host ""

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

# Download appropriate model for financial analysis
Write-Step "Setting up LLM model for financial analysis..."
Write-Info "Waiting for Ollama service to be ready..."

# Wait for Ollama to be available
$maxWait = 60
$waitTime = 0
$ollamaReady = $false

while ($waitTime -lt $maxWait -and -not $ollamaReady) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction SilentlyContinue
        $ollamaReady = $true
        Write-Success "Ollama service is ready"
    } catch {
        Start-Sleep -Seconds 3
        $waitTime += 3
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
}

if ($ollamaReady) {
    Write-Host ""
    Write-Info "Downloading finance-optimized LLM model..."
    Write-Info "This may take 5-15 minutes depending on your internet connection"
    
    # Use a smaller, efficient model good for financial analysis
    # Mistral 7B is excellent for structured analysis and reasoning
    Write-Step "Downloading Mistral 7B Instruct (optimized for analysis tasks)..."
    
    docker-compose exec -T ollama ollama pull mistral:7b-instruct
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Financial analysis model downloaded successfully!"
        Write-Info "Model 'mistral:7b-instruct' is now available in Ollama"
        
        # Update the .env file to use the downloaded model
        $envFile = Join-Path $projectRoot ".env"
        if (Test-Path $envFile) {
            (Get-Content "$envFile") -replace "LOCAL_LLM_MODEL=llama3.1", "LOCAL_LLM_MODEL=mistral:7b-instruct" | Set-Content "$envFile"
            Write-Success "Updated .env file to use mistral:7b-instruct model"
        }
    } else {
        Write-Warning "Failed to download model automatically"
        Write-Info "You can download it manually later with:"
        Write-Info "docker-compose exec ollama ollama pull mistral:7b-instruct"
        Write-Info "Alternative smaller model: docker-compose exec ollama ollama pull llama3.2:3b"
    }
} else {
    Write-Warning "Ollama service not ready after $maxWait seconds"
    Write-Info "Services may still be starting. You can download models manually:"
    Write-Info "docker-compose exec ollama ollama pull mistral:7b-instruct"
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
