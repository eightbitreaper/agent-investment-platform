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
| Document | Description | Status |
|----------|-------------|--------|
| [Initialize Prompt](setup/initialize.prompt.md) | VS Code agent one-command setup | ✅ Available |
| [Prerequisites Guide](prerequisites.md) | System requirements and setup prerequisites | ✅ Available |

### 🏗️ Architecture & Technical
| Document | Description | Status |
|----------|-------------|--------|
| [Architecture Overview](architecture.md) | Technical system design and components | ✅ Available |
| [MCP Server Integration](mcp-server-integration.md) | Complete MCP server documentation | ✅ Available |

### 🔧 Development & Contributing
| Document | Description | Status |
|----------|-------------|--------|
| [Contributing Guide](CONTRIBUTING.md) | How to contribute to the project | ✅ Available |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Community standards and expectations | ✅ Available |
| [License](LICENSE.md) | MIT License terms and conditions | ✅ Available |

### 📋 Project Management
| Document | Description | Status |
|----------|-------------|--------|
| [Documentation Index](index.md) | Complete documentation overview | ✅ Available |

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
- 🏗️ **System architecture** → [Architecture Overview](architecture.md)
- 🤖 **MCP servers** → [MCP Server Integration](mcp-server-integration.md)
- �‍💻 **Contributing code** → [Contributing Guide](CONTRIBUTING.md)
- � **System requirements** → [Prerequisites](prerequisites.md)
- � **Project overview** → [Documentation Index](index.md)

## 💡 Pro Tips

- **Use the VS Code initializer**: Run `@workspace run docs/setup/initialize.prompt` for automated setup
- **Check logs**: Most issues can be diagnosed in `logs/initialization.log`
- **Start with defaults**: The platform works out-of-the-box, customize later
- **Join discussions**: Use GitHub Discussions for questions and feature requests

---

📧 **Need more help?** [Open an issue](https://github.com/eightbitreaper/agent-investment-platform/issues) or [start a discussion](https://github.com/eightbitreaper/agent-investment-platform/discussions).
