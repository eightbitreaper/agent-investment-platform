```prompt
---
description: Initialize Agent Investment Platform - Complete Setup
globs:
alwaysApply: false
---
# Agent Investment Platform Initialization

## Goal
Set up the complete Agent-Driven Stock Investment Platform with all dependencies, configurations, and local development environment in a single command.

## Overview
This initialization process will:
1. Detect your operating system and platform
2. Install required dependencies (Docker, Python, etc.)
3. Set up local LLM options (Ollama, LMStudio) or API configurations
4. Configure MCP servers for data sources
5. Create necessary configuration files
6. Validate the complete setup
7. Generate initial reports to test the system

## Prerequisites Check
Before starting, the system will verify:
- Git is installed and repository is cloned
- VS Code is running with Copilot/Agent extensions
- Internet connection for downloading dependencies
- Administrative privileges (if needed for installations)

## Platform Detection and Setup

### Windows Setup
- Install Docker Desktop if not present
- Install Python 3.11+ if not available
- Set up Windows Subsystem for Linux (WSL) if needed
- Configure PowerShell execution policies

### Linux/WSL Setup
- Install Docker and Docker Compose
- Ensure Python 3.11+ with pip
- Install system dependencies (curl, wget, etc.)

### macOS Setup
- Install Docker Desktop
- Ensure Homebrew is available
- Install Python via pyenv or system package manager

## LLM Configuration Options

### Option 1: Local LLM Setup (Recommended for Privacy)
- Install Ollama for local model hosting
- Download recommended models (llama3.1, codellama, etc.)
- Configure local inference endpoints
- Set up model switching capabilities

### Option 2: API-based LLM Setup
- Configure OpenAI API keys
- Set up Anthropic Claude access
- Configure API rate limiting and fallback options

### Option 3: Hybrid Setup
- Local LLMs for analysis and processing
- API LLMs for complex reasoning and report generation

## MCP Server Configuration
The initialization will set up MCP servers for:
- **Stock Data**: Polygon API
- **News Sources**: Google News, Reddit, Twitter/X APIs
- **YouTube**: Transcript extraction from configured channels
- **Market Data**: Real-time and historical price feeds

## Configuration File Generation
Automatically create and populate:
- `config/llm-config.yaml` - LLM endpoints and settings
- `config/mcp-servers.json` - Data source configurations
- `config/strategies.yaml` - Investment strategy templates
- `config/data-sources.yaml` - API keys and endpoints
- `config/notification-config.yaml` - Alert settings
- `.env` - Environment variables (from .env.example)

## Docker Environment Setup
- Pull required Docker images
- Build custom containers for orchestration
- Start MCP server containers
- Configure networking between services
- Set up volume mounts for data persistence

## Validation and Testing
After setup completion:
- Test MCP server connectivity
- Verify LLM endpoints (local or API)
- Generate a sample report
- Test GitHub integration
- Validate notification systems
- Run system health checks

## Post-Installation Steps
1. Review generated configuration files
2. Add your API keys to appropriate config files
3. Customize investment strategies in `config/strategies.yaml`
4. Test the system with: `python orchestrator.py --test-mode`
5. Review the sample report in `reports/` directory

## Troubleshooting
If initialization fails:
- Check logs in `logs/initialization.log`
- Run `python scripts/setup/validate-setup.py`
- Review platform-specific requirements
- Consult `docs/troubleshooting/common-issues.md`

## Next Steps
After successful initialization:
1. Read `docs/setup/quick-start-guide.md`
2. Configure your investment strategies
3. Set up scheduled report generation
4. Join the community for support and updates

## Usage
To run this initialization:
```
@workspace run initialize.prompt
```

The system will guide you through each step with prompts and confirmations.
```
