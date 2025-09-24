# Quick Start Guide

Get the Agent Investment Platform running in 10 minutes with this streamlined setup process.

## Prerequisites

Before starting, ensure you have:

- **Windows 10/11** (primary support) or **Linux/macOS**
- **Administrator privileges** (for Windows installation)
- **Stable internet connection** (for downloading dependencies)
- **8GB+ RAM** recommended for optimal performance

## Method 1: One-Command Installation (Recommended)

### Windows PowerShell
1. **Right-click PowerShell** and select "Run as Administrator"
2. **Run the installer**:
   ```powershell
   git clone https://github.com/eightbitreaper/agent-investment-platform.git
   cd agent-investment-platform
   .\scripts\deployment\master-installer.ps1
   ```

### Windows Batch Alternative
1. **Right-click Command Prompt** and select "Run as Administrator"
2. **Run the batch installer**:
   ```batch
   git clone https://github.com/eightbitreaper/agent-investment-platform.git
   cd agent-investment-platform
   .\scripts\deployment\install-everything.bat
   ```

### Linux/Mac
```bash
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
pwsh ./scripts/deployment/user-installer.ps1
```

## Method 2: VS Code Integration

For developers who prefer VS Code:

1. **Clone the repository**
2. **Open in VS Code**: `code agent-investment-platform`
3. **Run initialization**: Use VS Code command palette and run the setup prompt

## What Gets Installed

The installation process automatically sets up:

- ✅ **Docker Desktop** - Container orchestration
- ✅ **Python 3.11** - Virtual environment with all packages
- ✅ **Node.js 18+** - JavaScript runtime for MCP servers
- ✅ **PostgreSQL & Redis** - Database and caching
- ✅ **4 MCP Servers** - Financial data, analysis, news, reports
- ✅ **Ollama + Web UI** - Local AI chat interface
- ✅ **Monitoring Stack** - Grafana and Prometheus

## Verification

After installation completes:

1. **Check Services**: All Docker containers should be running
2. **Access Web UI**: Visit http://localhost:8080 for AI chat
3. **Test Health**: Platform health check should pass
4. **Try Analysis**: Generate a test investment report

## Next Steps

Once installation is complete:

### Start Using the Platform
- **[AI Investment Assistant](ollama-chat-guide.md)** - Chat with real-time financial data
- **[Investment Analysis](analysis-workflow.md)** - Generate automated reports
- **[Web Interfaces](web-interfaces.md)** - Access monitoring dashboards

### For Developers
- **[Development Setup](../development/development-setup.md)** - Contributing to the project
- **[API Documentation](../api/)** - MCP server integration details
- **[Debugging Guides](../development/debugging/)** - Troubleshooting components

## Troubleshooting Quick Start

**Installation Fails:**
1. Check internet connection
2. Verify administrator privileges
3. Review installation logs
4. See [Common Issues](../troubleshooting/common-issues.md)

**Services Won't Start:**
1. Ensure Docker Desktop is running
2. Check port availability (8080, 3000, 5432, 6379)
3. Verify system resources (RAM, disk space)
4. See [Docker Troubleshooting](../troubleshooting/docker-troubleshooting.md)

**Can't Access Web Interface:**
1. Confirm services are running
2. Check firewall settings
3. Try different browser
4. See [Web Interface Guide](web-interfaces.md)

## Getting Help

- **Quick Issues**: Check [troubleshooting guides](../troubleshooting/)
- **Development**: See [development documentation](../development/)
- **Community**: Create GitHub issue with installation logs

---

**⏱️ Installation Time**: 5-15 minutes depending on internet speed
**💾 Disk Space**: ~5GB including all dependencies and models
**🔧 Maintenance**: Automatic updates and health monitoring included
