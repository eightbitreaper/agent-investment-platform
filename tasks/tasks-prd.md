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

### Notes

- Focus on configuring existing MCP tools rather than building from scratch
- Use established LLM APIs (OpenAI, Anthropic) or local models (Ollama, LMStudio)
- Docker containers isolate and manage different services
- All configuration should be externalized to config files

## Tasks

- [ ] 1.0 Infrastructure and Environment Setup
- [ ] 2.0 MCP Server Integration and Data Ingestion
- [ ] 3.0 Analysis Engine Development
- [ ] 4.0 Report Generation and Output System
- [ ] 5.0 Scheduling and Notification System