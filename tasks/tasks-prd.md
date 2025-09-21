# Tasks for Agent-Driven Stock Investment Platform

## Relevant Files

- `docker-compose.yml` - Multi-service orchestration for MCP servers, LLM services, and schedulers
- `Dockerfile` - Container configuration for custom orchestration layer  
- `config/mcp-servers.json` - MCP server configurations for stock data, news, YouTube APIs
- `config/llm-config.yaml` - LLM configuration (local vs API, model settings)
- `config/strategies.yaml` - Investment strategy configurations (value, meme, momentum)
- `config/data-sources.yaml` - API keys and endpoints for external data sources
- `config/notification-config.yaml` - Email/Discord notification settings for urgent alerts
- `scripts/setup-env.sh` - Environment setup script for API keys and dependencies
- `templates/report-template.md` - Markdown template for generated reports
- `templates/strategy-prompts/` - Directory containing LLM prompts for different strategies
- `reports/` - Directory where generated reports will be stored
- `logs/` - Directory for system logs and debugging information
- `requirements.txt` - Python dependencies for orchestration scripts
- `orchestrator.py` - Main coordination script for MCP servers and LLM integration
- `scheduler.py` - Cron-like scheduler for report generation intervals
- `src/agents/stock_data_agent.py` - MCP client for stock/ETF/bond price data
- `src/agents/news_agent.py` - MCP client for news headline ingestion
- `src/agents/youtube_agent.py` - MCP client for YouTube transcript processing
- `src/analysis/sentiment_analyzer.py` - Sentiment analysis processor
- `src/analysis/chart_analyzer.py` - Technical chart trend analysis
- `src/reports/markdown_generator.py` - Markdown report generation engine
- `src/github/report_uploader.py` - GitHub integration for report versioning
- `docs/setup/local-llm-setup.md` - Instructions for installing and configuring local LLMs
- `docs/setup/quick-start-guide.md` - Step-by-step setup guide for new users
- `docs/configuration/llm-configuration.md` - LLM configuration options and examples
- `docs/configuration/strategy-configuration.md` - How to configure investment strategies
- `docs/deployment/docker-deployment.md` - Docker deployment instructions
- `docs/troubleshooting/common-issues.md` - Common setup and runtime issues
- `docs/setup/initialize.prompt.md` - VS Code agent prompt for one-command setup
- `docs/setup/installation-guide.md` - Comprehensive installation instructions
- `.vscode/guidelines.prompt.md` - Master development guidelines and documentation standards
- `.memory/` - AI memory bank system for persistent knowledge and context
- `.memory/project-context.md` - Comprehensive project context and evolution
- `.memory/user-preferences.json` - User preferences and working patterns
- `.memory/architecture-decisions.md` - Technical decisions and rationale
- `.memory/patterns-knowledge.json` - Implementation patterns and code quality standards
- `.memory/knowledge-graph.json` - Semantic relationships between project components
- `.memory/memory_bank.py` - Memory bank API for context retrieval and updates
- `docs/setup/configuration-guide.md` - Configuration and customization guide
- `docs/api/README.md` - API documentation index
- `docs/development/README.md` - Development guide index
- `scripts/initialize.py` - Main initialization script for VS Code agent
- `scripts/setup/install-dependencies.py` - Automated dependency installation
- `scripts/setup/configure-environment.py` - Environment configuration automation
- `scripts/setup/download-models.py` - Local LLM model download automation
- `scripts/setup/validate-setup.py` - Setup validation and testing
- `.vscode/tasks.json` - VS Code tasks for initialization and common operations
- `.vscode/settings.json` - VS Code workspace settings and extensions
- `README.md` - Main entry point with quick start and links to docs/

### Notes

- Focus on configuring existing MCP tools rather than building from scratch
- Use established LLM APIs (OpenAI, Anthropic) or local models (Ollama, LMStudio)
- Docker containers isolate and manage different services
- All configuration should be externalized to config files
- Comprehensive documentation ensures junior developers can set up and contribute
- One-command initialization via VS Code agent for seamless onboarding

### MANDATORY: Development Guidelines Reference

**⚠️ CRITICAL: Before starting ANY task:**
1. **ALWAYS read** `.vscode/guidelines.prompt.md` for current project standards
2. **Verify** the guidelines are being followed for file placement and organization
3. **Check** that documentation will be placed in the correct `docs/` subdirectory

**⚠️ CRITICAL: After completing ANY task:**
1. **ALWAYS verify** all files are placed according to guidelines
2. **Update** parent README files with navigation links to new documentation
3. **Cross-reference** related documentation sections as specified in guidelines
4. **Validate** that all markdown files follow the established directory structure

**These guidelines are MANDATORY and must be followed without exception.**

## Tasks

**🚨 BEFORE STARTING ANY TASK: Read [.vscode/guidelines.prompt.md](../.vscode/guidelines.prompt.md) for mandatory project standards**

- [ ] 0.0 VS Code Agent Initialization System
  - [x] 0.1 Create `docs/setup/initialize.prompt.md` with VS Code agent setup instructions
  - [x] 0.2 Create `scripts/initialize.py` main initialization orchestrator
  - [x] 0.3 Create `scripts/setup/install-dependencies.py` for automated dependency installation
  - [x] 0.4 Create `scripts/setup/configure-environment.py` for environment configuration
  - [x] 0.5 Create `scripts/setup/download-models.py` for local LLM model management
  - [x] 0.6 Create `scripts/setup/validate-setup.py` for setup verification
  - [x] 0.7 Create `.vscode/tasks.json` with initialization and common tasks
  - [ ] 0.8 Create `.vscode/settings.json` with workspace configuration
  - [ ] 0.9 Update `README.md` as main entry point with links to docs/

- [ ] 1.0 Infrastructure and Environment Setup
  - [ ] 1.1 Create `docker-compose.yml` with services for MCP servers, LLM, and scheduler
  - [ ] 1.2 Create `Dockerfile` for custom orchestration container
  - [ ] 1.3 Create `requirements.txt` with Python dependencies
  - [ ] 1.4 Create `config/` directory structure for all configuration files
  - [ ] 1.5 Create `scripts/setup-env.sh` for environment variable setup
  - [ ] 1.6 Create `logs/` and `reports/` directory structure
  - [ ] 1.7 Create `.env.example` template for required environment variables
  - [ ] 1.8 Create `scripts/health-check.py` for system health monitoring

- [ ] 2.0 MCP Server Integration and Data Ingestion
  - [ ] 2.1 Create `config/mcp-servers.json` configuration file
  - [ ] 2.2 Create `src/agents/stock_data_agent.py` for stock/ETF/bond data
  - [ ] 2.3 Create `src/agents/news_agent.py` for news headline ingestion
  - [ ] 2.4 Create `src/agents/youtube_agent.py` for YouTube transcript processing
  - [ ] 2.5 Create `config/data-sources.yaml` for API endpoints and keys
  - [ ] 2.6 Create `src/mcp/client_manager.py` for MCP server coordination
  - [ ] 2.7 Create unit tests for each agent in `tests/agents/`
  - [ ] 2.8 Create integration tests for MCP server connectivity

- [ ] 3.0 Analysis Engine Development
  - [ ] 3.1 Create `src/analysis/sentiment_analyzer.py` for news/transcript sentiment
  - [ ] 3.2 Create `src/analysis/chart_analyzer.py` for technical analysis
  - [ ] 3.3 Create `config/strategies.yaml` for investment strategy configurations
  - [ ] 3.4 Create `templates/strategy-prompts/` directory with LLM prompts
  - [ ] 3.5 Create `src/analysis/strategy_engine.py` for strategy application
  - [ ] 3.6 Create `src/analysis/recommendation_engine.py` for buy/sell/hold decisions
  - [ ] 3.7 Create unit tests for analysis components in `tests/analysis/`
  - [ ] 3.8 Create backtesting framework in `src/backtesting/`

- [ ] 4.0 Report Generation and Output System
  - [ ] 4.1 Create `templates/report-template.md` for structured reports
  - [ ] 4.2 Create `src/reports/markdown_generator.py` for report generation
  - [ ] 4.3 Create `src/github/report_uploader.py` for GitHub integration
  - [ ] 4.4 Create `config/llm-config.yaml` for LLM service configuration
  - [ ] 4.5 Create `src/llm/client.py` for LLM API abstraction
  - [ ] 4.6 Create report validation and quality checks
  - [ ] 4.7 Create `src/reports/report_history.py` for tracking past predictions
  - [ ] 4.8 Create unit tests for report generation in `tests/reports/`

- [ ] 5.0 Scheduling and Notification System
  - [ ] 5.1 Create `scheduler.py` for cron-like report scheduling
  - [ ] 5.2 Create `orchestrator.py` for coordinating all system components
  - [ ] 5.3 Create `config/notification-config.yaml` for alert settings
  - [ ] 5.4 Create `src/notifications/email_notifier.py` for email alerts
  - [ ] 5.5 Create `src/notifications/discord_notifier.py` for Discord integration
  - [ ] 5.6 Create urgency detection system for market-moving events
  - [ ] 5.7 Create system monitoring and error recovery mechanisms
  - [ ] 5.8 Create integration tests for scheduling system

- [ ] 6.0 Documentation and Local LLM Setup
  - [ ] 6.1 Create `docs/setup/local-llm-setup.md` with installation guides (follow guidelines for placement and navigation updates)
  - [ ] 6.2 Create `docs/setup/installation-guide.md` comprehensive setup guide (follow guidelines for placement and navigation updates)
  - [ ] 6.3 Create `docs/setup/configuration-guide.md` with LLM and strategy examples (follow guidelines for placement and navigation updates)
  - [ ] 6.4 Create `docs/deployment/docker-deployment.md` instructions (follow guidelines for placement and navigation updates)
  - [ ] 6.5 Create `docs/troubleshooting/common-issues.md` guide (follow guidelines for placement and navigation updates)
  - [ ] 6.6 Create `docs/api/README.md` API documentation index (follow guidelines for placement and navigation updates)
  - [ ] 6.7 Create `docs/api/mcp-server-reference.md` for developers (follow guidelines for placement and navigation updates)
  - [ ] 6.8 Create `docs/development/README.md` development guide index (follow guidelines for placement and navigation updates)
  - [ ] 6.9 Create `docs/development/contributing.md` for contributors (follow guidelines for placement and navigation updates)
  - [ ] 6.10 Create `docs/README.md` documentation index linking all sections (follow guidelines for placement and navigation updates)
  - [ ] 6.11 Validate all documentation follows guidelines and update navigation links