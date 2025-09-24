# 🐋 Docker Setup Guide for Agent Investment Platform

## Quick Start

### Option 1: Automated Setup (Recommended)
```powershell
# Run as Administrator
.\setup-docker.ps1
```

### Option 2: Step-by-Step Setup
```powershell
# 1. Check Docker installation
python docker-manager.py check

# 2. If Docker not installed, run:
.\install-docker.bat

# 3. After Docker is installed:
python docker-manager.py build
python docker-manager.py start
```

## Installation Methods

### Method 1: Windows Package Manager (winget)
```powershell
# Run as Administrator
winget install Docker.DockerDesktop
```

### Method 2: Manual Download
1. Visit: https://docs.docker.com/desktop/install/windows-install/
2. Download "Docker Desktop for Windows"
3. Run installer with these options:
   - ✅ Use WSL 2 instead of Hyper-V
   - ✅ Add shortcut to desktop
4. Restart computer
5. Launch Docker Desktop
6. Complete initial setup

## Service Profiles

### Production (Default)
```powershell
python docker-manager.py start
```
- Main application
- PostgreSQL database
- Redis cache
- MCP servers

### Development
```powershell
python docker-manager.py start --dev
```
- All production services
- Development tools
- Hot reloading
- Debugging enabled

### With Monitoring
```powershell
python docker-manager.py start --monitoring
```
- All services
- Grafana dashboards
- Prometheus metrics
- System monitoring

## Service Access

| Service | URL | Purpose |
|---------|-----|---------|
| Main App | http://localhost:8000 | Web interface |
| Grafana | http://localhost:3000 | Monitoring |
| Prometheus | http://localhost:9090 | Metrics |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

## Common Commands

```powershell
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update images
docker-compose pull
docker-compose build --no-cache

# Reset all data (WARNING: Deletes everything!)
python docker-manager.py reset
```

## Troubleshooting

### Docker not installed
- Use `.\install-docker.bat` for automated installation
- Or manually download from Docker website

### Docker not running
- Launch Docker Desktop from Start menu
- Wait for green whale icon in system tray

### Services won't start
```powershell
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Reset and restart
docker-compose down -v
docker-compose up -d
```

### Port conflicts
- Stop other services using ports 8000, 3000, 5432, 6379
- Or modify ports in docker-compose.yml

### WSL 2 issues
- Enable WSL 2 in Windows Features
- Update WSL 2 kernel: https://aka.ms/wsl2kernel

## System Requirements

- Windows 10/11 (64-bit)
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space
- Hardware virtualization enabled
- WSL 2 support

## Security Notes

- Default passwords are in `.env.docker`
- Change passwords for production use
- Services are isolated in Docker network
- Data persisted in Docker volumes

For advanced configuration, see `docker-compose.yml` and modify as needed.
