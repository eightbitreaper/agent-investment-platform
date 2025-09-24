# Installation Guide

Complete step-by-step installation guide for the Agent Investment Platform, from prerequisites to a fully functional system.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Quick Start (One-Command Setup)](#quick-start-one-command-setup)
- [Manual Installation](#manual-installation)
- [Environment Configuration](#environment-configuration)
- [Validation and Testing](#validation-and-testing)
- [Post-Installation Setup](#post-installation-setup)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Docker Installation](#docker-installation)
- [Troubleshooting](#troubleshooting)

## Overview

The Agent Investment Platform is designed for easy setup with multiple installation paths:

- **🚀 One-Command Setup** - Automated installation via VS Code task (Recommended)
- **📋 Manual Installation** - Step-by-step manual setup
- **🐋 Docker Installation** - Containerized deployment
- **🛠️ Development Setup** - Full development environment

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **RAM**: 8 GB (16 GB recommended for local LLMs)
- **Storage**: 10 GB free space (50+ GB for local models)
- **Internet**: Required for initial setup and API access

### Recommended Specifications
- **CPU**: 8+ cores for better performance
- **RAM**: 32 GB for running large local LLMs
- **GPU**: NVIDIA RTX 3060+ with 12+ GB VRAM (for local LLM acceleration)
- **Storage**: SSD with 100+ GB free space

### Required Software
- **Git** - Version control and repository management
- **Python 3.9+** - Core platform runtime
- **VS Code** - Recommended development environment (optional but highly recommended)

### Optional Components
- **Docker Desktop** - For containerized deployment
- **Node.js 18+** - For JavaScript MCP servers
- **CUDA Toolkit** - For GPU acceleration of local LLMs

## Quick Start (One-Command Setup)

The fastest way to get started is using the automated initialization system.

### Prerequisites

1. **Install Required Software**:
   ```powershell
   # Verify Python 3.9+
   python --version

   # Verify Git
   git --version

   # Install VS Code (recommended)
   winget install Microsoft.VisualStudioCode
   ```

2. **Clone the Repository**:
   ```powershell
   git clone https://github.com/your-username/agent-investment-platform.git
   cd agent-investment-platform
   ```

3. **Open in VS Code**:
   ```powershell
   code .
   ```

### Automated Setup

Use the VS Code task system for one-command setup:

1. **Open Command Palette** (`Ctrl+Shift+P`)
2. **Type**: `Tasks: Run Task`
3. **Select**: `🚀 Initialize Platform`

Or run directly from terminal:
```powershell
python scripts/initialize.py --interactive
```

The interactive setup will:
- Detect your system configuration
- Install all required dependencies
- Configure environment variables
- Set up local LLM models (optional)
- Validate the complete installation
- Guide you through API key configuration

### Setup Options

During interactive setup, you'll choose your LLM configuration:

1. **Local LLM** (Recommended for privacy)
   - Downloads Hugging Face models automatically
   - Works offline after initial setup
   - No API costs

2. **API-based LLM** (OpenAI/Anthropic)
   - Requires API keys
   - Higher quality for complex analysis
   - Usage-based costs

3. **Hybrid Setup** (Best of both worlds)
   - Local models for basic tasks
   - API models for complex analysis
   - Balanced cost and performance

## Manual Installation

For users who prefer manual control or need custom configurations.

### Step 1: Environment Setup

1. **Create Project Directory**:
   ```powershell
   mkdir d:\code\agent-investment-platform
   cd d:\code\agent-investment-platform
   ```

2. **Clone Repository**:
   ```powershell
   git clone https://github.com/your-username/agent-investment-platform.git .
   ```

3. **Create Python Virtual Environment** (Optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

### Step 2: Install Dependencies

1. **Update pip**:
   ```powershell
   python -m pip install --upgrade pip>=25.2
   ```

2. **Install Python packages**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Verify Installation**:
   ```powershell
   python -c \"import yaml, requests, mcp; print('✓ Core dependencies installed')\"
   ```

### Step 3: System Configuration

1. **Run Dependency Installer**:
   ```powershell
   python scripts/setup/install-dependencies.py
   ```

2. **Configure Environment**:
   ```powershell
   python scripts/setup/configure-environment.py --interactive
   ```

3. **Setup Models** (Choose one):
   ```powershell
   # For local Hugging Face models (free)
   python scripts/setup/download-models.py

   # For Ollama setup
   python scripts/setup/download-models.py --provider ollama
   ```

### Step 4: Configuration Files

1. **Create Environment File**:
   ```powershell
   copy .env.example .env
   ```

2. **Edit Configuration** (Optional):
   - Update `config/llm-config.yaml` for LLM preferences
   - Update `config/data-sources.yaml` for API keys
   - Update `config/strategies.yaml` for investment strategies

### Step 5: Validation

1. **Run Setup Validation**:
   ```powershell
   python scripts/setup/validate-setup.py
   ```

2. **Quick Test**:
   ```powershell
   python orchestrator.py --test-mode
   ```

## Environment Configuration

### API Keys Setup

Create `.env` file with your API keys:

```bash
# Financial Data APIs (optional but recommended)
POLYGON_API_KEY=your_polygon_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here

# LLM APIs (optional - only if using API-based LLMs)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Notification APIs (optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_url
EMAIL_SMTP_USER=your_email@example.com
EMAIL_SMTP_PASSWORD=your_app_password

# GitHub Integration (optional)
GITHUB_TOKEN=your_github_personal_access_token
```

### Free API Keys

Get these free API keys to unlock full functionality:

1. **Polygon API** (Stock Data):
   - Visit: [https://polygon.io/](https://polygon.io/)
   - Sign up for free tier (5 API calls/minute)
   - Copy API key to `.env`

2. **Alpha Vantage** (Alternative Stock Data):
   - Visit: [https://www.alphavantage.co/](https://www.alphavantage.co/)
   - Free tier: 5 API requests per minute
   - Copy API key to `.env`

3. **NewsAPI** (News Data):
   - Visit: [https://newsapi.org/](https://newsapi.org/)
   - Free tier: 1,000 requests per day
   - Copy API key to `.env`

### Configuration Customization

Customize the platform behavior by editing configuration files:

- **`config/llm-config.yaml`** - LLM provider settings and model assignments
- **`config/strategies.yaml`** - Investment strategy configurations
- **`config/data-sources.yaml`** - API endpoints and data source settings
- **`config/notification-config.yaml`** - Alert and notification preferences
- **`config/risk_management.yaml`** - Risk management rules and thresholds

## Validation and Testing

### Comprehensive Validation

Run the complete validation suite:

```powershell
# Full validation (recommended)
python scripts/setup/validate-setup.py

# Quick validation (80% coverage)
python scripts/setup/validate-setup.py --quick

# Specific component validation
python scripts/setup/validate-setup.py --component mcp-servers
python scripts/setup/validate-setup.py --component llm-integration
```

### Test System Components

```powershell
# Test MCP servers
python test_mcp_servers.py

# Test analysis engines
python -m pytest tests/analysis/ -v

# Test end-to-end functionality
python orchestrator.py --test-mode
```

### Health Check

Monitor system health:

```powershell
# System health check
python scripts/health-check.py

# Real-time monitoring (starts web dashboard)
python src/monitoring/dashboard.py
```

## Post-Installation Setup

### 1. Configure Investment Strategies

Edit `config/strategies.yaml` to customize your investment approach:

```yaml
# Example strategy configuration
strategies:
  conservative:
    risk_tolerance: low
    max_position_size: 0.05  # 5% max per position
    stop_loss_percentage: 0.02  # 2% stop loss

  aggressive:
    risk_tolerance: high
    max_position_size: 0.15  # 15% max per position
    stop_loss_percentage: 0.05  # 5% stop loss
```

### 2. Set Up Notifications

Configure alerts in `config/notification-config.yaml`:

```yaml
notifications:
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587

  discord:
    enabled: true
    webhook_url: ${DISCORD_WEBHOOK_URL}
```

### 3. Schedule Automated Reports

Set up regular analysis reports:

```powershell
# Configure scheduler for daily reports
python scheduler.py --schedule \"0 9 * * *\" --task daily_analysis

# Test scheduled report generation
python orchestrator.py --generate-report
```

### 4. GitHub Integration

For automated report publishing:

1. Create a GitHub Personal Access Token
2. Add token to `.env` file
3. Configure repository in `config/github-config.yaml`

## Platform-Specific Instructions

### Windows Setup

```powershell
# Enable execution policy for scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install using Windows Package Manager
winget install Git.Git
winget install Python.Python.3.11
winget install Microsoft.VisualStudioCode

# Verify installations
python --version
git --version
code --version
```

### macOS Setup

```bash
# Install Homebrew (if not already installed)
/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"

# Install required tools
brew install python@3.11 git
brew install --cask visual-studio-code

# Verify installations
python3 --version
git --version
code --version
```

### Linux (Ubuntu/Debian) Setup

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip git curl

# Install VS Code
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Verify installations
python3 --version
git --version
code --version
```

## Docker Installation

For containerized deployment with full isolation.

### Prerequisites

1. **Install Docker Desktop**:
   - Windows/Mac: Download from [docker.com](https://www.docker.com/products/docker-desktop)
   - Linux: `sudo apt install docker.io docker-compose`

2. **Verify Docker**:
   ```powershell
   docker --version
   docker-compose --version
   ```

### Docker Setup

1. **Build and Start Services**:
   ```powershell
   # Build all services
   docker-compose build

   # Start in background
   docker-compose up -d

   # Check service status
   docker-compose ps
   ```

2. **Access Services**:
   - **Main Platform**: http://localhost:8000
   - **Monitoring Dashboard**: http://localhost:8080
   - **MCP Servers**: Various ports (see docker-compose.yml)

3. **View Logs**:
   ```powershell
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f orchestrator
   ```

4. **Stop Services**:
   ```powershell
   docker-compose down
   ```

### Docker Configuration

Customize `docker-compose.yml` for your environment:

```yaml
# Example environment variables for Docker
environment:
  - POLYGON_API_KEY=${POLYGON_API_KEY}
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - LLM_PROVIDER=ollama
  - LOG_LEVEL=INFO
```

## Troubleshooting

### Common Issues

#### Python Import Errors
```powershell
# Problem: ModuleNotFoundError
# Solution: Ensure virtual environment is activated and dependencies installed
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### Permission Errors (Windows)
```powershell
# Problem: Access denied errors
# Solution: Run PowerShell as Administrator
# Right-click PowerShell → \"Run as administrator\"
```

#### Port Already in Use
```powershell
# Problem: Port 8000 already in use
# Solution: Find and stop the process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

#### MCP Server Connection Errors
```powershell
# Problem: Cannot connect to MCP servers
# Solution: Check server status and restart
python scripts/run_mcp_server.py --health-check
python scripts/run_mcp_server.py --restart-all
```

#### GPU Not Detected (Local LLMs)
```python
# Problem: CUDA/GPU acceleration not working
# Solution: Verify CUDA installation
import torch
print(f\"CUDA available: {torch.cuda.is_available()}\")
print(f\"CUDA version: {torch.version.cuda}\")
```

### Getting Help

1. **Check Logs**:
   ```powershell
   # System logs
   Get-Content logs\\initialization.log -Tail 50

   # Component-specific logs
   Get-Content logs\\mcp-servers.log -Tail 50
   ```

2. **Run Diagnostics**:
   ```powershell
   # System diagnostic
   python scripts/setup/validate-setup.py --verbose

   # Component health check
   python scripts/health-check.py --detailed
   ```

3. **Reset Installation**:
   ```powershell
   # Clean installation (removes generated files)
   git clean -xdf
   python scripts/initialize.py --interactive
   ```

### Support Resources

- **Documentation**: Check other guides in `docs/`
- **Troubleshooting Guide**: [troubleshooting/common-issues.md](../troubleshooting/common-issues.md)
- **GitHub Issues**: Report bugs and get help from the community
- **Configuration Examples**: See `examples/` directory for working configurations

## Next Steps

After successful installation:

1. **Review Configuration**: Customize settings in `config/` directory
2. **Add API Keys**: Get free API keys and add to `.env` file
3. **Test System**: Run `python orchestrator.py --test-mode`
4. **Generate Report**: Create your first investment analysis report
5. **Set Up Monitoring**: Configure notifications and alerts
6. **Explore Features**: Check out the full feature set in the main README

## Related Documentation

- [Local LLM Setup Guide](local-llm-setup.md) - Configure local language models
- [Configuration Guide](configuration-guide.md) - Customize platform behavior
- [Docker Deployment Guide](../deployment/docker-deployment.md) - Production deployment
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common problems and solutions
- [API Documentation](../api/README.md) - Technical API reference

---

Welcome to the Agent Investment Platform! For questions or issues, please check the troubleshooting guide or open a GitHub issue.
