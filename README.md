# 🚀 Agent Investment Platform

> **One-command setup for AI-powered stock investment analysis**

An agent-driven platform that provides automated analysis of stocks, ETFs, and bonds with real-time insights, sentiment analysis, and comprehensive reporting.

⚠️ **Note**: The system does not execute trades. It informs the operator so they can act manually.

## ⚡ Quick Installation

Get the complete platform running in under 10 minutes:

**📋 [Complete Installation Guide](docs/setup/installation-guide.md)**

**✅ What You Get:**
- 🧠 **AI Investment Assistant** - Local LLM chat interface with GPU acceleration
- 📊 **Real-Time Data** - Current stock prices, market data, and news
- 📈 **Investment Analysis** - Automated reports and recommendations
- 🐳 **Docker Infrastructure** - Containerized services and databases
- � **MCP Servers** - Model Context Protocol for financial data integration
- 🌐 **Web Interfaces** - Monitoring dashboards and analysis tools

**🚀 Installation Options:**
- **[One-Command Setup](docs/setup/installation-guide.md#one-command-installation)** - Automated installer scripts
- **[VS Code Integration](docs/setup/installation-guide.md#vs-code-workspace-setup)** - Development-focused setup
- **[Manual Installation](docs/setup/installation-guide.md#manual-installation)** - Step-by-step custom setup

## 📋 Installation Methods Comparison

| Method | Best For | Time | Requirements | What You Get |
|--------|----------|------|--------------|--------------|
| **scripts/deployment/master-installer.ps1** | Production deployment | 10-15 min | Admin rights | Complete Docker stack |
| **scripts/deployment/install-everything.bat** | Windows users | 10-15 min | Admin rights | Full platform + tools |
| **scripts/deployment/user-installer.ps1** | Limited permissions | 8-10 min | User rights | Core platform |
| **VS Code Workspace** | Development work | 5-8 min | VS Code | Dev environment |

### 🔧 Manual Installation

If automatic installers don't work in your environment:

```bash
# 1. Install Docker Desktop manually
# 2. Install Python 3.11
# 3. Clone and setup:
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
docker-compose --profile development up -d
```

## 🚀 How to Use the Platform

Once installation is complete, you have several ways to use the platform:

### 1. 🤖 Generate AI Investment Analysis (Recommended)

Run a complete investment analysis with AI-powered insights:

```powershell
# Generate a test report (safe, uses demo data)
.\.venv\Scripts\python.exe orchestrator.py --test-mode

# Generate live analysis (requires API keys)
.\.venv\Scripts\python.exe orchestrator.py --live

# Run in development mode with detailed logging
.\.venv\Scripts\python.exe orchestrator.py --mode development --log-level DEBUG
```

**Output**: Creates detailed reports in `reports/` directory with:
- Stock analysis and recommendations
- Market sentiment analysis
- Risk assessments
- Buy/Hold/Sell recommendations

## 💬 Using the Platform

### AI Investment Assistant
Interactive chat interface with **real-time financial data** and GPU-accelerated local LLM:

- **🧠 Smart Analysis**: Uses Llama 3.1 8B optimized for financial reasoning
- **📈 Current Data**: Access to live stock prices, market indices, and news
- **🔒 Private**: No data leaves your machine, completely local processing
- **⚡ Fast**: GPU acceleration for instant responses

**📋 [Complete Chat Guide](docs/setup/ollama-chat-guide.md)**

### Investment Analysis & Reports
Generate comprehensive investment analysis with automated reporting:

- **📊 Technical Analysis**: Chart patterns, indicators, and trend analysis
- **📰 Sentiment Analysis**: News and social media sentiment tracking
- **🎯 Recommendations**: Buy/Hold/Sell decisions with risk assessment
- **� Automated Reports**: Markdown reports with GitHub integration

**📋 [Analysis Workflow Guide](docs/setup/analysis-workflow.md)**

### Web Interfaces
Access monitoring dashboards and analysis tools:

- **🤖 AI Chat**: http://localhost:8080 - Investment assistant interface
- **📊 Monitoring**: http://localhost:3000 - Grafana dashboards
- **📈 Metrics**: http://localhost:9090 - Prometheus system metrics

**📋 [Web Interface Guide](docs/setup/web-interfaces.md)**### 5. ⚙️ Configuration

Customize the platform for your needs:

```powershell
# Edit environment variables (API keys, etc.)
notepad .env

# Modify investment strategies
notepad config\strategies.yaml

# Adjust data sources
notepad config\data-sources.yaml
```

### 6. 📝 View Generated Reports

All analysis reports are saved in structured format:

```powershell
# View latest reports
ls reports\

# Open latest report
notepad "reports\investment-analysis-$(Get-Date -Format 'yyyy-MM-dd').md"
```

### 🆘 Troubleshooting

**If something isn't working:**

1. **Check platform health**: `.\.venv\Scripts\python.exe scripts\health-check.py`
2. **Verify Docker**: `docker-compose ps`
3. **Check logs**: `docker-compose logs`
4. **Restart services**: `docker-compose restart`

**Common Issues:**
- **Port conflicts**: Stop other services using ports 8000, 3000, 5432, 6379
- **API key errors**: Configure your API keys in `.env` file
- **Memory issues**: Ensure at least 4GB RAM available for Docker

## 🎯 What This Platform Does

- **📊 Real-time Analysis**: Continuously monitors stocks, ETFs, and bonds
- **🤖 AI-Powered Insights**: Uses LLMs for sentiment analysis and strategy recommendations
- **📰 Multi-Source Data**: Integrates news, YouTube transcripts, and market data
- **📝 Automated Reports**: Generates markdown reports with buy/sell/hold recommendations
- **🔄 Version Control**: All reports are versioned and stored in GitHub
- **🐋 Container Ready**: Full Docker deployment for any platform

## 📚 Documentation

| Section | Description | Status |
|---------|-------------|---------|
| **[📖 Documentation Index](docs/index.md)** | Complete documentation overview | ✅ Available |
| **[⚙️ Initialization Guide](docs/setup/initialize.prompt.md)** | One-command VS Code setup | ✅ Complete |
| **[🏗️ Architecture Overview](docs/architecture.md)** | Technical architecture & design | ✅ Available |
| **[� Development Guidelines](.vscode/guidelines.prompt.md)** | Code standards & best practices | ✅ Active |
| **[� Contributing Guide](docs/CONTRIBUTING.md)** | How to contribute to the project | ✅ Available |
| **[🚀 Project Requirements](tasks/prd.md)** | Complete product specification | ✅ Available |

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
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ 🤖 Chat UI      │◀───│ Ollama API   │◀───│ GPU Accelerated │
│ localhost:8080  │    │ localhost:11434│   │ Llama 3.1 8B   │
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

```
agent-investment-platform/
├── 📁 docs/                    # ✅ Complete documentation
│   ├── setup/initialize.prompt.md  # ✅ One-command initialization
│   ├── architecture.md            # ✅ Technical architecture
│   ├── CONTRIBUTING.md            # ✅ Development guidelines
│   └── mcp-server-integration.md   # ✅ MCP server documentation
├── 📁 src/                     # ✅ Source code
│   ├── mcp_servers/               # ✅ Python MCP servers
│   └── mcp-servers/               # ✅ Node.js MCP servers
├── 📁 scripts/                 # ✅ Setup & utility scripts
│   ├── initialize.py              # ✅ Main orchestration
│   ├── health-check.py            # ✅ System health monitoring
│   └── setup/                     # ✅ All setup modules
├── 📁 tests/                   # ✅ Comprehensive test suites
│   ├── integration/               # ✅ MCP server integration tests
│   └── api/                       # ✅ External API tests (Polygon, etc.)
├── 📁 dev-tools/               # ✅ Development utilities
│   └── README.md                  # ✅ Development tool documentation
├── 📁 config/                  # ✅ Configuration management
│   ├── mcp-servers.json           # ✅ MCP server configuration
│   ├── llm-config.yaml            # ✅ LLM configuration
│   └── data-sources.yaml          # ✅ API configurations
├── 📁 .vscode/                 # ✅ VS Code integration
│   ├── tasks.json                 # ✅ 20 automation tasks
│   ├── settings.json              # ✅ 85+ optimized settings
│   └── guidelines.prompt.md       # ✅ Development standards
├── 📁 .memory/                 # ✅ AI memory bank system
├── 📁 tasks/                   # ✅ Project requirements
│   ├── prd.md                     # ✅ Product specification
│   └── tasks-prd.md               # ✅ Task breakdown
├── 📄 docker-compose.yml       # ✅ Multi-service orchestration
├── 📄 Dockerfile              # ✅ Container configuration
├── 📄 requirements.txt         # ✅ Python dependencies
├── scripts/
│   ├── 📄 run_mcp_server.py    # ✅ MCP server runner
├── 📄 run_tests.py             # ✅ Test suite runner
├── 📄 TESTING.md               # ✅ Testing strategy documentation
└── 📄 .env.example            # ✅ Environment template
```

## 🧪 Testing & Development

The platform includes comprehensive testing and development tools:

- **Automated Test Suites** - Integration tests for all MCP servers
- **API Testing Tools** - Validation of external data sources
- **Health Monitoring** - System health checks and diagnostics
- **Development Environment** - VS Code integration with automation tasks

**📋 [Complete Testing Guide](docs/development/testing-guide.md)**

**Current Status**: Infrastructure foundation complete with 4 production MCP servers, real-time data integration, and comprehensive testing framework.

## 🔗 Links

- **[Project Tasks & Roadmap](tasks/tasks-prd.md)** - Current development progress
- **[Product Requirements](tasks/prd.md)** - Detailed project specifications
- **[Architecture Details](docs/architecture.md)** - Technical architecture overview
- **[GitHub Repository](https://github.com/eightbitreaper/agent-investment-platform)** - Source code and issues

## 📄 License

This project is licensed under the [MIT License](docs/LICENSE.md).

---

**⭐ Star this repo if you find it useful!** | **🐛 [Report Issues](https://github.com/eightbitreaper/agent-investment-platform/issues)** | **💬 [Discussions](https://github.com/eightbitreaper/agent-investment-platform/discussions)**
