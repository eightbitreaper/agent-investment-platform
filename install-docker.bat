@echo off
setlocal EnableDelayedExpansion

echo ================================================================
echo          Agent Investment Platform - Docker Installer
echo ================================================================
echo.

REM Check Windows version
echo Checking Windows version...
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Windows version: %VERSION%

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ Not running as Administrator
    echo Please right-click this script and select "Run as administrator"
    pause
    exit /b 1
)

REM Check if Docker is already installed
echo.
echo Checking for existing Docker installation...
docker --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker is already installed!
    docker --version
    goto :start_docker
)

echo Docker not found. Starting installation...

REM Check if winget is available
echo.
echo Checking for Windows Package Manager (winget)...
winget --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ winget found. Installing Docker Desktop...
    winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    if %errorLevel% == 0 (
        echo ✅ Docker Desktop installed successfully!
        goto :post_install
    ) else (
        echo ❌ winget installation failed. Trying manual method...
        goto :manual_install
    )
) else (
    echo winget not available. Using manual installation...
    goto :manual_install
)

:manual_install
echo.
echo ================================================================
echo                    Manual Installation Required
echo ================================================================
echo.
echo Please follow these steps:
echo.
echo 1. Open your web browser
echo 2. Go to: https://docs.docker.com/desktop/install/windows-install/
echo 3. Click "Docker Desktop for Windows"
echo 4. Download and run "Docker Desktop Installer.exe"
echo 5. During installation, ensure these options are checked:
echo    - Use WSL 2 instead of Hyper-V
echo    - Add shortcut to desktop
echo 6. Restart your computer when prompted
echo 7. Launch Docker Desktop after restart
echo 8. Complete the initial setup
echo.
echo After installation, run this script again to continue setup.
echo.
pause
exit /b 0

:post_install
echo.
echo ================================================================
echo                    Post-Installation Setup
echo ================================================================
echo.
echo Docker Desktop has been installed. Please:
echo.
echo 1. RESTART your computer now
echo 2. After restart, launch Docker Desktop
echo 3. Complete the initial setup (sign in or skip)
echo 4. Wait for Docker to start (check system tray)
echo 5. Run this script again to continue
echo.
pause
exit /b 0

:start_docker
echo.
echo Checking if Docker service is running...
docker info >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker is running!
    goto :setup_platform
) else (
    echo ❌ Docker is installed but not running
    echo.
    echo Please:
    echo 1. Launch Docker Desktop from Start menu
    echo 2. Wait for it to start (green icon in system tray)
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

:setup_platform
echo.
echo ================================================================
echo              Setting up Agent Investment Platform
echo ================================================================
echo.

REM Navigate to platform directory
cd /d "%~dp0"

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found
    echo Please run this script from the Agent Investment Platform directory
    pause
    exit /b 1
)

echo ✅ Found Agent Investment Platform

REM Check Python environment
echo.
echo Checking Python environment...
if exist ".venv\Scripts\python.exe" (
    echo ✅ Virtual environment found
) else (
    echo ❌ Virtual environment not found
    echo Please run the main setup first: python scripts/initialize.py
    pause
    exit /b 1
)

REM Build Docker images
echo.
echo Building Docker images (this may take several minutes)...
docker-compose build --no-cache
if %errorLevel% neq 0 (
    echo ❌ Failed to build Docker images
    pause
    exit /b 1
)

echo ✅ Docker images built successfully

REM Start services
echo.
echo Starting Docker services...
docker-compose --profile production up -d
if %errorLevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo ✅ Services started successfully

REM Wait for services to be ready
echo.
echo Waiting for services to start up...
timeout /t 30 /nobreak

REM Show status
echo.
echo ================================================================
echo                      Deployment Status
echo ================================================================
echo.
docker-compose ps

echo.
echo ================================================================
echo                      Access Information
echo ================================================================
echo.
echo Your Agent Investment Platform is now running!
echo.
echo 🌐 Main Application:     http://localhost:8000
echo 📊 Grafana Monitoring:   http://localhost:3000
echo 📈 Prometheus Metrics:   http://localhost:9090
echo 🗄️  Database (PostgreSQL): localhost:5432
echo 🔴 Cache (Redis):        localhost:6379
echo.
echo ================================================================
echo                      Useful Commands
echo ================================================================
echo.
echo View logs:           docker-compose logs -f
echo Stop services:       docker-compose down
echo Restart services:    docker-compose restart
echo Check status:        docker-compose ps
echo.
echo For more management options, use:
echo   python docker-manager.py --help
echo.
pause
