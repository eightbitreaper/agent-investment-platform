@echo off
setlocal EnableDelayedExpansion

echo ================================================================
echo      🚀 Agent Investment Platform - Master Installer
echo ================================================================
echo.
echo This script will install and configure everything needed:
echo - Docker Desktop
echo - Python 3.11 + Virtual Environment
echo - Node.js 18+
echo - Git + VS Code
echo - All Python dependencies
echo - Complete platform deployment
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ This script requires administrator privileges
    echo.
    echo Please:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Running as Administrator

REM Set up project root path and navigate to it
cd /d "%~dp0..\.."
set "PROJECT_ROOT=%CD%"
echo 📁 Project root: %PROJECT_ROOT%
echo.

REM ============================================================================
REM STEP 1: Install Package Managers
REM ============================================================================

echo ========================================
echo STEP 1: Installing Package Managers
echo ========================================

REM Install Chocolatey if not present
choco --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Chocolatey package manager...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

    REM Refresh environment
    call refreshenv
    echo ✅ Chocolatey installed
) else (
    echo ✅ Chocolatey is already installed
)

REM ============================================================================
REM STEP 2: Install System Requirements
REM ============================================================================

echo.
echo ========================================
echo STEP 2: Installing System Requirements
echo ========================================

REM Install Git
echo Checking Git installation...
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Git...
    choco install git -y
    call refreshenv
    echo ✅ Git installed
) else (
    echo ✅ Git is already installed
)

REM Install Python 3.11
echo Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Python 3.11...
    choco install python311 -y
    call refreshenv
    echo ✅ Python installed
) else (
    echo ✅ Python is already installed
)

REM Install Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Node.js...
    choco install nodejs -y
    call refreshenv
    echo ✅ Node.js installed
) else (
    echo ✅ Node.js is already installed
)

REM Install VS Code (optional but recommended)
echo Checking VS Code installation...
code --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing VS Code...
    choco install vscode -y
    call refreshenv
    echo ✅ VS Code installed
) else (
    echo ✅ VS Code is already installed
)

REM ============================================================================
REM STEP 3: Install Docker Desktop
REM ============================================================================

echo.
echo ========================================
echo STEP 3: Installing Docker Desktop
echo ========================================

docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Docker Desktop...
    choco install docker-desktop -y

    echo.
    echo ⚠️  IMPORTANT: Docker Desktop installed!
    echo.
    echo Please:
    echo 1. RESTART your computer now
    echo 2. Launch Docker Desktop after restart
    echo 3. Complete the Docker setup wizard
    echo 4. Run this script again to continue
    echo.
    pause
    exit /b 0
) else (
    echo ✅ Docker Desktop is installed

    REM Check if Docker is running
    docker info >nul 2>&1
    if %errorLevel% neq 0 (
        echo ⚠️  Docker is installed but not running
        echo Please start Docker Desktop and wait for it to initialize
        echo (Look for the green whale icon in your system tray)
        echo.
        echo Press any key when Docker Desktop is running...
        pause
    ) else (
        echo ✅ Docker is running
    )

    REM Test Docker Hub connectivity and authenticate if needed
    echo Testing Docker Hub connectivity...
    docker pull hello-world >nul 2>&1
    if %errorLevel% neq 0 (
        echo ⚠️  Docker Hub requires authentication for image pulls
        echo.
        echo Docker Hub now requires authentication to pull images.
        echo You need a free Docker Hub account to continue.
        echo.
        echo If you don't have an account:
        echo 1. Visit https://hub.docker.com and create a free account
        echo 2. Come back and continue with the web-based login below
        echo.
        echo The installer will use Docker's secure device activation method.
        echo This will open your browser for safe authentication - no passwords needed here.
        echo.

        REM Prompt for Docker Hub login with retry logic
        set /a attempt=1
        set /a maxAttempts=3
        set loginSuccess=false

        :dockerLoginLoop
        echo Docker Hub login attempt !attempt! of !maxAttempts!
        echo Using web-based device activation for secure login...
        echo This will open your browser for authentication.
        echo.

        REM Use Docker's device activation flow (web-based login)
        docker login

        REM Verify authentication by testing Docker Hub access
        echo Verifying Docker Hub access...
        docker pull hello-world >nul 2>&1
        if %errorLevel% equ 0 (
            echo ✅ Docker Hub login successful!
            echo ✅ Docker Hub access verified
            set loginSuccess=true
            goto :dockerLoginSuccess
        ) else (
            echo ❌ Docker Hub login failed - unable to pull test image
            set /a attempt+=1

            if !attempt! leq !maxAttempts! (
                echo Please try again with correct credentials
                echo.
                goto :dockerLoginLoop
            )
        )

        :dockerLoginFailed
        if "!loginSuccess!"=="false" (
            echo ❌ Failed to authenticate with Docker Hub after !maxAttempts! attempts
            echo.
            echo Please ensure you have:
            echo 1. A valid Docker Hub account (free at https://hub.docker.com)
            echo 2. Correct username and password/token
            echo 3. Stable internet connection
            echo.
            echo You can also run 'docker login' manually and then re-run this installer
            pause
            exit /b 1
        )

        :dockerLoginSuccess
    ) else (
        echo ✅ Docker Hub access is working
    )
)

REM ============================================================================
REM STEP 4: Setup Python Environment
REM ============================================================================

echo.
echo ========================================
echo STEP 4: Setting up Python Environment
echo ========================================

REM Create virtual environment if it doesn't exist
if not exist "%PROJECT_ROOT%\.venv" (
    echo Creating Python virtual environment...
    python -m venv "%PROJECT_ROOT%\.venv"
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Install Python dependencies
echo Installing Python dependencies...
"%PROJECT_ROOT%\.venv\Scripts\python.exe" -m pip install --upgrade pip
if exist "%PROJECT_ROOT%\requirements.txt" (
    "%PROJECT_ROOT%\.venv\Scripts\pip.exe" install -r "%PROJECT_ROOT%\requirements.txt"
    echo ✅ Python dependencies installed from requirements.txt
) else (
    echo ⚠️  requirements.txt not found at: %PROJECT_ROOT%\requirements.txt
    echo Skipping package installation - you may need to install packages manually
)

REM ============================================================================
REM STEP 5: Configure Environment
REM ============================================================================

echo.
echo ========================================
echo STEP 5: Configuring Environment
echo ========================================

REM Create .env file if it doesn't exist
if not exist "%PROJECT_ROOT%\.env" (
    if exist "%PROJECT_ROOT%\.env.example" (
        copy "%PROJECT_ROOT%\.env.example" "%PROJECT_ROOT%\.env"
        echo ✅ Environment file created from template
    ) else (
        echo ⚠️  .env.example not found - creating basic .env file
        echo # Basic environment configuration > "%PROJECT_ROOT%\.env"
        echo ENVIRONMENT=production >> "%PROJECT_ROOT%\.env"
        echo LOG_LEVEL=INFO >> "%PROJECT_ROOT%\.env"
    )
) else (
    echo ✅ Environment file already exists
)

REM Create necessary directories
if not exist "%PROJECT_ROOT%\data" mkdir "%PROJECT_ROOT%\data"
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"
if not exist "%PROJECT_ROOT%\reports" mkdir "%PROJECT_ROOT%\reports"
if not exist "%PROJECT_ROOT%\models" mkdir "%PROJECT_ROOT%\models"
if not exist "%PROJECT_ROOT%\.memory" mkdir "%PROJECT_ROOT%\.memory"
echo ✅ Required directories created

REM ============================================================================
REM STEP 6: Deploy Platform
REM ============================================================================

echo.
echo ========================================
echo STEP 6: Deploying Platform
echo ========================================

echo Building Docker images (this may take several minutes)...
docker-compose build --no-cache
if %errorLevel% neq 0 (
    echo ❌ Failed to build Docker images
    echo Please check Docker Desktop is running and try again
    pause
    exit /b 1
)
echo ✅ Docker images built successfully

echo Starting platform services...
docker-compose --profile production up -d
if %errorLevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo ✅ Services started successfully

REM ============================================================================
REM STEP 7: Validation
REM ============================================================================

echo.
echo ========================================
echo STEP 7: Validating Deployment
echo ========================================

echo Waiting for services to initialize...
timeout /t 30 /nobreak

echo Running health checks...
if exist "%PROJECT_ROOT%\scripts\health-check.py" (
    "%PROJECT_ROOT%\.venv\Scripts\python.exe" "%PROJECT_ROOT%\scripts\health-check.py"
) else (
    echo ⚠️  Health check script not found - skipping
)

echo Running deployment test...
if exist "%PROJECT_ROOT%\deployment_test.py" (
    "%PROJECT_ROOT%\.venv\Scripts\python.exe" "%PROJECT_ROOT%\deployment_test.py"
) else (
    echo ⚠️  Deployment test script not found - skipping
)

REM ============================================================================
REM COMPLETION
REM ============================================================================

echo.
echo ================================================================
echo 🎉 INSTALLATION COMPLETE!
echo ================================================================
echo.
echo ✅ Agent Investment Platform is now fully deployed!
echo.
echo 🌐 Access URLs:
echo    Main Application:     http://localhost:8000
echo    Grafana Monitoring:   http://localhost:3000
echo    Prometheus Metrics:   http://localhost:9090
echo.
echo 🗄️  Database Connections:
echo    PostgreSQL:           localhost:5432
echo    Redis:               localhost:6379
echo.
echo 🔧 Management Commands:
echo    Check status:         docker-compose ps
echo    View logs:           docker-compose logs -f
echo    Stop services:       docker-compose down
echo    Restart services:    docker-compose restart
echo.
echo 📚 Documentation:
echo    Setup Guide:         DOCKER_SETUP.md
echo    API Docs:           docs/api/README.md
echo    User Guide:         docs/README.md
echo.
echo 🎯 Next Steps:
echo 1. Configure additional API keys in .env file
echo 2. Customize investment strategies in config/strategies.yaml
echo 3. Access the web interface at http://localhost:8000
echo 4. Set up automated reports via the scheduler
echo.
echo ✅ Platform is ready for AI-powered investment analysis!
echo.

REM Show final status
echo Current Service Status:
docker-compose ps

echo.
pause
