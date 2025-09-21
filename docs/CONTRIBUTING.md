# Contributing Guide

Thank you for considering contributing to the **Agent Investment Platform** project!
We welcome contributions from developers, researchers, and financial technology enthusiasts.

## Table of Contents
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Testing](#testing)
- [Guidelines and Standards](#guidelines-and-standards)
- [Code of Conduct](#code-of-conduct)
- [Getting Help](#getting-help)

---

## Quick Start

### Prerequisites
- **Python 3.9+** for core platform and MCP servers
- **Node.js 18+** for JavaScript MCP servers
- **Git** for version control
- **VS Code** (recommended) for the best development experience

### One-Command Setup
The fastest way to get started:
```bash
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
code .  # Opens in VS Code
```

Then use the VS Code agent initialization:
```
@workspace /docs/setup/initialize.prompt.md
```

---

## Development Setup

### 1. Fork and Clone
```bash
# Fork the repository on GitHub first
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional for basic development)
```

### 3. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Node.js Dependencies (for JS MCP servers)
```bash
cd src/mcp-servers
npm install
```

### 5. Verify Setup
```bash
# Run system health check
python scripts/health-check.py

# Test MCP servers
python test_mcp_servers.py
```

---

## How to Contribute

### 1. Development Guidelines
**⚠️ CRITICAL: Before starting ANY work, read the [Development Guidelines](.vscode/guidelines.prompt.md)**

The guidelines cover:
- Documentation organization and structure
- File naming conventions
- Security requirements (API keys, sensitive data)
- Testing requirements
- Memory bank integration

### 2. Create a Feature Branch
```bash
git checkout -b feature/descriptive-name
# or
git checkout -b fix/issue-description
# or
git checkout -b docs/documentation-update
```

### 3. Make Your Changes
- **Follow the established project structure**
- **Place documentation in appropriate `docs/` subdirectories**
- **Update relevant README files with navigation links**
- **Test your changes thoroughly**

### 4. Commit Standards
We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat(mcp): add new stock analysis server"
git commit -m "fix(health-check): resolve encoding issues on Windows"
git commit -m "docs(setup): update installation guide with new requirements"
git commit -m "test(analysis): add unit tests for technical indicators"
```

**Commit Types:**
- `feat`: New features or capabilities
- `fix`: Bug fixes
- `docs`: Documentation updates
- `refactor`: Code restructuring without behavior change
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 5. Push and Create Pull Request
```bash
git push origin feature/your-branch-name
```

Then create a pull request on GitHub with:
- **Clear description** of what you've changed and why
- **Reference any related issues**
- **Screenshots** if UI changes are involved
- **Testing details** showing you've verified your changes work

---

## Testing

### Python Testing
```bash
# Run MCP server tests
python test_mcp_servers.py

# Run system health check
python scripts/health-check.py

# Validate setup
python scripts/setup/validate-setup.py
```

### Node.js Testing
```bash
cd src/mcp-servers
npm test        # Run Jest tests
npm run lint    # Check code style
```

### Integration Testing
```bash
# Test MCP server runner
python run_mcp_server.py --server stock-data

# Test Docker setup
docker-compose up --build
```

### Manual Testing Requirements
- **Test on target platform** (Windows PowerShell for this project)
- **Verify all scripts execute without errors**
- **Test API integrations** if you have API keys configured
- **Validate configuration files** load properly

---

## Guidelines and Standards

### Project Structure
```
agent-investment-platform/
├── docs/                   # ALL documentation goes here
│   ├── setup/             # Installation and configuration guides
│   ├── api/               # API documentation
│   ├── development/       # Development guides
│   └── troubleshooting/   # Common issues and solutions
├── src/                   # Source code
│   ├── mcp_servers/       # Python MCP servers
│   └── mcp-servers/       # Node.js MCP servers
├── scripts/               # Setup and utility scripts
├── config/                # Configuration files
└── tests/                 # Test files
```

### Code Quality
- **Follow existing patterns** and architectural decisions
- **Add comprehensive error handling**
- **Include input validation** for all user-facing functions
- **Write clear, descriptive variable and function names**
- **Add docstrings** to Python functions and classes

### Documentation Requirements
- **Update parent README files** when adding new documentation
- **Include cross-references** to related documentation
- **Provide examples** for complex concepts
- **Test all instructions** to ensure they work

### Security Requirements
- **NEVER commit API keys** or sensitive information
- **Use environment variables** for configuration
- **Validate all inputs** to prevent security issues
- **Follow data classification standards**

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

### Key Points:
- **Be respectful** and inclusive in all interactions
- **Provide constructive feedback** and accept it gracefully
- **Focus on the technical merits** of contributions
- **Help newcomers** and share knowledge openly

---

## Getting Help

### Resources
- **[Development Guidelines](.vscode/guidelines.prompt.md)** - Comprehensive development standards
- **[Architecture Documentation](architecture.md)** - Technical architecture overview
- **[Setup Guide](setup/initialize.prompt.md)** - Complete initialization instructions
- **[MCP Server Documentation](mcp-server-integration.md)** - MCP server implementation details

### Support Channels
- **[GitHub Issues](https://github.com/eightbitreaper/agent-investment-platform/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/eightbitreaper/agent-investment-platform/discussions)** - Questions and community discussion

### Before Asking for Help
1. **Check existing documentation** in the `docs/` directory
2. **Search existing issues** to see if your question has been answered
3. **Run the health check** to identify common setup issues
4. **Review the troubleshooting guide** for common problems

### When Reporting Issues
- **Include your operating system** and versions (Python, Node.js)
- **Provide the exact error message** and steps to reproduce
- **Include relevant configuration** (without sensitive information)
- **Mention what you've already tried** to resolve the issue

---

## Project Status

**Current Phase:** MCP Server Integration Complete (Tasks 0.0-2.0)
- ✅ Complete VS Code integration with one-command setup
- ✅ Docker infrastructure and environment management
- ✅ 4 production MCP servers with 20+ tools
- ✅ Comprehensive testing framework and health monitoring

**Next Phase:** Analysis Engine Development (Task 3.0)
- Ready for contributions to analysis algorithms
- Strategy engine implementation
- Backtesting framework development

---

Thank you for contributing to the Agent Investment Platform! Your contributions help build a powerful, open-source financial analysis platform. 🚀
