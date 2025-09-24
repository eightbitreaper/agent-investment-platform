@echo off
REM Quick Docker Setup Script for Agent Investment Platform
REM This script helps set up Docker for the first time

echo ========================================
echo Agent Investment Platform - Docker Setup
echo ========================================
echo.

REM Check if Docker is installed
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo.
    echo Please install Docker Desktop:
    echo 1. Go to: https://docs.docker.com/desktop/install/windows-install/
    echo 2. Download and install Docker Desktop
    echo 3. Restart your computer
    echo 4. Start Docker Desktop
    echo 5. Run this script again
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Docker is installed

REM Check if Docker is running
echo Checking if Docker is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo SUCCESS: Docker is running

REM Build and start services
echo.
echo Building Docker images...
docker-compose build

echo.
echo Starting services...
docker-compose --profile production up -d

echo.
echo ========================================
echo Docker Setup Complete!
echo ========================================
echo.
echo Services are starting up...
echo Please wait 30-60 seconds for all services to be ready
echo.
echo Access your platform at:
echo - Main Application: http://localhost:8000
echo - Grafana Dashboard: http://localhost:3000
echo - Prometheus Metrics: http://localhost:9090
echo.
echo To check status: docker-compose ps
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
pause
