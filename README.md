# 🚀 Agent Investment Platform

> **One-command setup for AI-powered stock investment analysis**

An agent-driven platform that provides automated analysis of stocks, ETFs, and bonds with real-time insights, sentiment analysis, and comprehensive reporting.

⚠️ **Note**: The system does not execute trades. It informs the operator so they can act manually.

## ⚡ One-Command Installation

Get the complete platform running in under 10 minutes with our automated installers:

### 🪟 Windows PowerShell (Recommended)
```powershell
# Right-click PowerShell and "Run as Administrator", then:
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
.\scripts\deployment\master-installer.ps1
```

### 🔧 Windows Batch Alternative  
```batch
# Right-click and "Run as Administrator"
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
.\scripts\deployment\install-everything.bat
```

### 🐧 Linux/Mac (User Mode)
```bash
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform
pwsh ./scripts/deployment/user-installer.ps1  # PowerShell Core required
```

**✅ Complete Installation Includes:**
- 🐳 **Docker Desktop** - Container orchestration platform
- 🐍 **Python 3.11** - Virtual environment with 70+ packages
- 📦 **Node.js 18+** - JavaScript runtime for MCP servers  
- 🛠️ **Git & VS Code** - Development tools
- 🗄️ **PostgreSQL & Redis** - Database and caching layer
- 🤖 **4 MCP Servers** - Stock data, analysis, news, and reports
- 🌐 **Web Interface** - Accessible at http://localhost:8000
- 📊 **Monitoring Stack** - Grafana and Prometheus dashboards

## 🚀 Alternative: VS Code Workspace Setup

For development-focused setup with VS Code integration:

```bash
# 1. Clone the repository
git clone https://github.com/eightbitreaper/agent-investment-platform.git
cd agent-investment-platform

# 2. Open in VS Code
code .

# 3. Initialize everything with one command
@workspace /docs/setup/initialize.prompt.md
```

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
├── 📄 run_mcp_server.py        # ✅ MCP server runner
├── 📄 run_tests.py             # ✅ Test suite runner
├── 📄 TESTING.md               # ✅ Testing strategy documentation
└── 📄 .env.example            # ✅ Environment template
```

## 🧪 Testing

**Quick Testing:**
```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --integration  # MCP server tests
python run_tests.py --api          # API integration tests (Polygon, etc.)
```

**Development Tools:**
```bash
# Test Polygon API with your key
$env:POLYGON_API_KEY="your-key"; python dev-tools/test_polygon_api.py
```

See [TESTING.md](TESTING.md) for complete testing strategy.

**Current Status**: Infrastructure foundation complete with 4 production MCP servers, **real Polygon API integration**, and comprehensive testing framework.

## 🔗 Links

- **[Project Tasks & Roadmap](tasks/tasks-prd.md)** - Current development progress
- **[Product Requirements](tasks/prd.md)** - Detailed project specifications
- **[Architecture Details](docs/architecture.md)** - Technical architecture overview
- **[GitHub Repository](https://github.com/eightbitreaper/agent-investment-platform)** - Source code and issues

## 📄 License

This project is licensed under the [MIT License](docs/LICENSE.md).

---

**⭐ Star this repo if you find it useful!** | **🐛 [Report Issues](https://github.com/eightbitreaper/agent-investment-platform/issues)** | **💬 [Discussions](https://github.com/eightbitreaper/agent-investment-platform/discussions)**
