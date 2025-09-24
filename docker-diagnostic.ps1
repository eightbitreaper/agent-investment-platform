# Docker Diagnostic and Restart Script
# Provides detailed Docker Desktop diagnostics and attempts recovery

param(
    [switch]$Force,
    [switch]$Verbose
)

# Color functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "[STEP] $Message" -ForegroundColor Blue }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "    Docker Desktop Diagnostic & Recovery Tool" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# Function to get Docker processes
function Get-DockerProcesses {
    $processes = Get-Process | Where-Object {$_.ProcessName -like "*docker*"} | Select-Object ProcessName, Id, StartTime, WorkingSet
    return $processes
}

# Function to test Docker connectivity with detailed output
function Test-DockerConnectivity {
    Write-Step "Testing Docker connectivity..."
    
    # Test 1: Docker CLI availability
    try {
        $version = docker --version 2>$null
        Write-Success "Docker CLI available: $version"
    } catch {
        Write-Error "Docker CLI not available: $_"
        return $false
    }
    
    # Test 2: Docker daemon ping
    try {
        $ping = docker system ping 2>&1
        if ($ping -match "OK") {
            Write-Success "Docker daemon is responding"
            return $true
        } else {
            Write-Warning "Docker daemon ping failed: $ping"
        }
    } catch {
        Write-Warning "Docker daemon ping exception: $_"
    }
    
    # Test 3: Docker info command
    try {
        $info = docker info 2>&1
        if ($info -match "Server:") {
            Write-Success "Docker daemon info available"
            return $true
        } else {
            Write-Warning "Docker daemon info not available"
            if ($Verbose) { Write-Host $info -ForegroundColor Gray }
        }
    } catch {
        Write-Warning "Docker info exception: $_"
    }
    
    return $false
}

# Function to diagnose Docker Desktop installation
function Test-DockerInstallation {
    Write-Step "Diagnosing Docker Desktop installation..."
    
    # Check Docker Desktop executable
    $dockerDesktopPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopPath) {
        Write-Success "Docker Desktop executable found"
    } else {
        Write-Error "Docker Desktop executable not found at: $dockerDesktopPath"
        return $false
    }
    
    # Check Docker CLI
    $dockerCliPath = "${env:ProgramFiles}\Docker\Docker\resources\bin\docker.exe"
    if (Test-Path $dockerCliPath) {
        Write-Success "Docker CLI found"
    } else {
        Write-Warning "Docker CLI not found at expected location"
    }
    
    # Check WSL2 if on Windows
    try {
        $wslVersion = wsl --version 2>$null
        if ($wslVersion) {
            Write-Success "WSL2 is available"
        } else {
            Write-Warning "WSL2 may not be properly configured"
        }
    } catch {
        Write-Warning "Could not check WSL2 status"
    }
    
    return $true
}

# Main diagnostic routine
Write-Info "Starting Docker Desktop diagnostics..."
Write-Host ""

# 1. Check installation
Write-Host "1. Installation Check" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
$installOk = Test-DockerInstallation
Write-Host ""

# 2. Check processes
Write-Host "2. Process Check" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
$processes = Get-DockerProcesses
if ($processes.Count -gt 0) {
    Write-Success "Found $($processes.Count) Docker-related processes:"
    $processes | Format-Table -AutoSize
} else {
    Write-Warning "No Docker processes found"
}
Write-Host ""

# 3. Test connectivity
Write-Host "3. Connectivity Test" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
$connectOk = Test-DockerConnectivity
Write-Host ""

# 4. Recovery actions
Write-Host "4. Recovery Actions" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

if (-not $connectOk) {
    Write-Warning "Docker daemon is not responding. Attempting recovery..."
    
    # Stop all Docker processes
    Write-Step "Stopping Docker processes..."
    Get-Process | Where-Object {$_.ProcessName -like "*docker*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    
    # Restart Docker Desktop
    Write-Step "Starting Docker Desktop..."
    Start-Process "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe" -WindowStyle Minimized
    
    # Wait and test again
    Write-Step "Waiting for Docker Desktop to initialize (60 seconds)..."
    $maxWait = 60
    $waitInterval = 5
    $waited = 0
    
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds $waitInterval
        $waited += $waitInterval
        
        Write-Host "." -NoNewline -ForegroundColor Yellow
        
        if (Test-DockerConnectivity) {
            Write-Host ""
            Write-Success "Docker Desktop is now running!"
            $connectOk = $true
            break
        }
    }
    
    if (-not $connectOk) {
        Write-Host ""
        Write-Error "Docker Desktop failed to start after $maxWait seconds"
    }
}

# 5. Final status
Write-Host ""
Write-Host "5. Final Status" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

if ($connectOk) {
    Write-Success "Docker Desktop is operational!"
    
    # Show Docker system info
    Write-Info "Docker system information:"
    try {
        docker system info | Select-String "Server Version|Operating System|Architecture|CPUs|Total Memory" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    } catch {
        Write-Warning "Could not retrieve system info"
    }
    
    Write-Host ""
    Write-Success "Ready for Docker deployment!"
    Write-Info "Next step: Run deployment script"
    
} else {
    Write-Error "Docker Desktop is not operational"
    Write-Host ""
    Write-Info "Possible solutions:"
    Write-Host "1. Manually start Docker Desktop from Start Menu" -ForegroundColor White
    Write-Host "2. Restart your computer and try again" -ForegroundColor White
    Write-Host "3. Reinstall Docker Desktop" -ForegroundColor White
    Write-Host "4. Check Windows features (WSL2, Hyper-V)" -ForegroundColor White
}

Write-Host ""
return $connectOk