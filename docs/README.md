# 📚 Agent Investment Platform Documentation

Welcome to the Agent Investment Platform documentation. This comprehensive guide covers everything from quick start to advanced development.

## 🚀 Quick Start

### New Users - Get Started in 5 Minutes
1. **[Installation Guide](setup/installation-guide.md)** - Complete setup from scratch
2. **[Configuration Guide](setup/configuration-guide.md)** - Customize for your needs
3. **[Local LLM Setup](setup/local-llm-setup.md)** - Configure private AI models

**One-Command Setup**:
```powershell
git clone https://github.com/your-username/agent-investment-platform.git
cd agent-investment-platform
python scripts/initialize.py --interactive
```

### For Developers
1. **[API Documentation](api/README.md)** - Complete API reference
2. **[Development Guide](development/README.md)** - Development standards and workflows
3. **[Contributing Guide](development/contributing.md)** - How to contribute to the project

### For DevOps
1. **[Docker Deployment](deployment/docker-deployment.md)** - Production deployment
2. **[Troubleshooting](troubleshooting/common-issues.md)** - Problem resolution

## 📖 Complete Documentation Index

### ⚙️ Setup & Installation
| Document | Description | Status | Audience |
|----------|-------------|--------|----------|
| **[Installation Guide](setup/installation-guide.md)** | Complete platform setup for all platforms | ✅ Complete | All Users |
| **[Configuration Guide](setup/configuration-guide.md)** | LLM, strategies, and system configuration | ✅ Complete | All Users |
| **[Local LLM Setup](setup/local-llm-setup.md)** | Ollama, LM Studio, Hugging Face setup | ✅ Complete | Privacy-focused Users |
| [Initialize Prompt](setup/initialize.prompt.md) | VS Code agent one-command setup | ✅ Available | VS Code Users |
| [Prerequisites](prerequisites.md) | System requirements | ✅ Available | All Users |

### 🐋 Deployment & Infrastructure
| Document | Description | Status | Audience |
|----------|-------------|--------|----------|
| **[Docker Deployment](deployment/docker-deployment.md)** | Production containerized deployment | ✅ Complete | DevOps |

### 🔧 Troubleshooting & Support
| Document | Description | Status | Audience |
|----------|-------------|--------|----------|
| **[Common Issues](troubleshooting/common-issues.md)** | Comprehensive troubleshooting guide | ✅ Complete | All Users |

### 🔌 API & Development
| Document | Description | Status | Audience |
|----------|-------------|--------|----------|
| **[API Documentation](api/README.md)** | Complete API reference and examples | ✅ Complete | Developers |
| **[MCP Server Reference](api/mcp-server-reference.md)** | Detailed MCP server API docs | ✅ Complete | Advanced Developers |
| **[Development Guide](development/README.md)** | Development workflows and standards | ✅ Complete | Contributors |
| **[Contributing Guide](development/contributing.md)** | Contribution guidelines and process | ✅ Complete | Contributors |

### 🏗️ Architecture & Technical
| Document | Description | Status | Audience |
|----------|-------------|--------|----------|
| [Architecture Overview](architecture.md) | Technical system design | ✅ Available | Architects |
| [MCP Server Integration](mcp-server-integration.md) | MCP implementation details | ✅ Available | Developers |
| [Backtesting Framework](backtesting-framework-summary.md) | Investment backtesting system | ✅ Available | Quant Analysts |

### 📋 Project Information
| Document | Description | Status | Audience |
|----------|-------------|--------|----------|
| [Contributing Guidelines](development/contributing.md) | How to contribute | ✅ Available | Contributors |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Community standards | ✅ Available | All |
| [License](LICENSE.md) | MIT License | ✅ Available | Legal |

## 🏗️ Platform Architecture

The Agent Investment Platform follows a modular architecture with these key components:

```
📊 Data Layer          🤖 Processing Layer     📝 Output Layer
├── Stock APIs         ├── MCP Servers         ├── Report Generator
├── News Sources       ├── Sentiment Analysis  ├── GitHub Integration
├── YouTube Feeds      ├── Technical Analysis  └── Notifications
└── Market Data        └── Strategy Engine
```

## 📋 Project Resources

### Core Documents
- **[Product Requirements (PRD)](../tasks/prd.md)** - Complete project specification
- **[Task Roadmap](../tasks/tasks-prd.md)** - Development progress and next steps
- **[Architecture Overview](architecture.md)** - Technical system design

### Project Guidelines
- **[Contributing Guidelines](development/contributing.md)** - How to contribute code and documentation
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards and expectations
- **[License (MIT)](LICENSE.md)** - Usage rights and limitations

## 🔍 Quick Navigation

**Need help with...?**
- 🆕 **First-time setup** → [Initialize Platform](setup/initialize.prompt.md)
- 🏗️ **System architecture** → [Architecture Overview](architecture.md)
- 🤖 **MCP servers** → [MCP Server Integration](mcp-server-integration.md)
- 👩‍💻 **Contributing code** → [Contributing Guide](development/contributing.md)
- � **System requirements** → [Prerequisites](prerequisites.md)
- 📋 **Project overview** → [Documentation Index](README.md)

## 💡 Pro Tips

- **Use the VS Code initializer**: Run `@workspace run docs/setup/initialize.prompt` for automated setup
- **Check logs**: Most issues can be diagnosed in `logs/initialization.log`
- **Start with defaults**: The platform works out-of-the-box, customize later
- **Join discussions**: Use GitHub Discussions for questions and feature requests

---

📧 **Need more help?** [Open an issue](https://github.com/eightbitreaper/agent-investment-platform/issues) or [start a discussion](https://github.com/eightbitreaper/agent-investment-platform/discussions).
