# 🚀 Agent Investment Platform

> **One-command setup for AI-powered stock investment analysis**

An agent-driven platform that provides automated analysis of stocks, ETFs, and bonds with real-time insights, sentiment analysis, and comprehensive reporting.

⚠️ **Note**: The system does not execute trades. It informs the operator so they can act manually.

## ⚡ Quick Start

Get up and running in under 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform

# 2. Open in VS Code
code .

# 3. Initialize everything with one command
@workspace run docs/setup/initialize.prompt
```

That's it! The initialization will:
- ✅ Install all dependencies (Docker, Python, etc.)
- ✅ Set up local LLMs or configure API access
- ✅ Configure all data sources and MCP servers
- ✅ Create your first investment analysis report
- ✅ Validate the complete setup

## 🎯 What This Platform Does

- **📊 Real-time Analysis**: Continuously monitors stocks, ETFs, and bonds
- **🤖 AI-Powered Insights**: Uses LLMs for sentiment analysis and strategy recommendations
- **📰 Multi-Source Data**: Integrates news, YouTube transcripts, and market data
- **📝 Automated Reports**: Generates markdown reports with buy/sell/hold recommendations
- **🔄 Version Control**: All reports are versioned and stored in GitHub
- **🐋 Container Ready**: Full Docker deployment for any platform

## 📚 Documentation

| Section | Description |
|---------|-------------|
| **[📖 Full Documentation](docs/README.md)** | Complete documentation index |
| **[⚙️ Setup & Installation](docs/setup/)** | Detailed setup guides and configuration |
| **[🚀 Deployment](docs/deployment/)** | Docker and production deployment |
| **[🔧 API Reference](docs/api/)** | MCP server and API documentation |
| **[👨‍💻 Development](docs/development/)** | Contributing and development guides |
| **[🆘 Troubleshooting](docs/troubleshooting/)** | Common issues and solutions |

## 🏗️ Architecture

The platform follows a modular, agent-based architecture:

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│ MCP Servers  │───▶│ Analysis Engine │
└─────────────────┘    └──────────────┘    └─────────────────┘
│ • Stock APIs    │    │ • Stock Data │    │ • Sentiment     │
│ • News Feeds    │    │ • News Agent │    │ • Technical     │
│ • YouTube       │    │ • YouTube    │    │ • Strategy      │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ GitHub Reports  │◀───│ Report Gen   │◀───│ LLM Processing  │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🤝 Contributing

We welcome contributors! The platform is designed for easy extension:

1. **Run the initializer** to get your dev environment ready
2. **Read the [development guidelines](.vscode/guidelines.prompt.md)** for project standards
3. **Check the [development guide](docs/development/)** for architecture details
4. **Browse [open issues](https://github.com/eightbitreaper/agent-investment-platform/issues)** for ways to help
5. **Add new MCP servers** for additional data sources
6. **Create new analysis strategies** for different investment approaches

## 📄 Project Structure

- **`docs/`** — All project documentation (setup, API, development guides)
- **`src/`** — Application source code (agents, analysis, reports)
- **`scripts/`** — Setup and utility scripts
- **`config/`** — Configuration files for all services
- **`tasks/`** — Project requirements and task tracking
- **`tests/`** — Automated test files

## 🔗 Links

- **[Project Tasks & Roadmap](tasks/tasks-prd.md)** - Current development progress
- **[Product Requirements](tasks/prd.md)** - Detailed project specifications  
- **[Architecture Details](docs/architecture.md)** - Technical architecture overview
- **[GitHub Repository](https://github.com/eightbitreaper/agent-investment-platform)** - Source code and issues

## 📄 License

This project is licensed under the [MIT License](docs/LICENSE.md).

---

**⭐ Star this repo if you find it useful!** | **🐛 [Report Issues](https://github.com/eightbitreaper/agent-investment-platform/issues)** | **💬 [Discussions](https://github.com/eightbitreaper/agent-investment-platform/discussions)**
