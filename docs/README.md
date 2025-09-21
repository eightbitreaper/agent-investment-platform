# 📚 Agent Investment Platform Documentation

Welcome to the comprehensive documentation for the Agent Investment Platform. This guide will help you get started, configure the system, and contribute to the project.

## 🚀 Getting Started

### New User? Start Here!
- **[Initialize Platform](setup/initialize.prompt.md)** - One-command VS Code setup
- **[Installation Guide](setup/installation-guide.md)** - Detailed setup instructions
- **[Local LLM Setup](setup/local-llm-setup.md)** - Configure local AI models
- **[Configuration Guide](setup/configuration-guide.md)** - Customize strategies and settings

## 📖 Documentation Sections

### ⚙️ Setup & Installation
| Document | Description |
|----------|-------------|
| [Initialize Prompt](setup/initialize.prompt.md) | VS Code agent one-command setup |
| [Installation Guide](setup/installation-guide.md) | Step-by-step installation instructions |
| [Local LLM Setup](setup/local-llm-setup.md) | Configure Ollama, LMStudio, and other local models |
| [Configuration Guide](setup/configuration-guide.md) | LLM settings, strategies, and data sources |

### 🚀 Deployment
| Document | Description |
|----------|-------------|
| [Docker Deployment](deployment/docker-deployment.md) | Production Docker setup and scaling |

### 🔧 API & Development
| Document | Description |
|----------|-------------|
| [API Documentation](api/README.md) | MCP server APIs and endpoints |
| [MCP Server Reference](api/mcp-server-reference.md) | Detailed MCP server documentation |
| [Development Guide](development/README.md) | Architecture and development workflow |
| [Contributing Guide](development/contributing.md) | How to contribute to the project |

### 🆘 Support
| Document | Description |
|----------|-------------|
| [Troubleshooting](troubleshooting/common-issues.md) | Common issues and solutions |

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
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute code and documentation
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards and expectations
- **[License (MIT)](LICENSE.md)** - Usage rights and limitations

## 🔍 Quick Navigation

**Need help with...?**
- 🆕 **First-time setup** → [Initialize Platform](setup/initialize.prompt.md)
- 🤖 **Local AI models** → [Local LLM Setup](setup/local-llm-setup.md) 
- 🐋 **Docker deployment** → [Docker Guide](deployment/docker-deployment.md)
- 🔧 **API integration** → [API Documentation](api/README.md)
- 🚨 **Problems/Errors** → [Troubleshooting](troubleshooting/common-issues.md)
- 👨‍💻 **Contributing code** → [Development Guide](development/README.md)

## 💡 Pro Tips

- **Use the VS Code initializer**: Run `@workspace run docs/setup/initialize.prompt` for automated setup
- **Check logs**: Most issues can be diagnosed in `logs/initialization.log`
- **Start with defaults**: The platform works out-of-the-box, customize later
- **Join discussions**: Use GitHub Discussions for questions and feature requests

---

📧 **Need more help?** [Open an issue](https://github.com/eightbitreaper/agent-investment-platform/issues) or [start a discussion](https://github.com/eightbitreaper/agent-investment-platform/discussions).