# Tasks for Agent-Driven Stock Investment Platform

## Relevant Files

- `docker-compose.yml` - Multi-service orchestration for existing tools (LLM, MCP servers, schedulers)
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
- `orchestrator.py` - Lightweight script to coordinate existing MCP servers and LLM
- `scheduler.py` - Cron-like scheduler for report generation intervals

### Notes

- Focus on configuring existing tools rather than building from scratch
- Use established MCP servers for data ingestion where available
- Leverage existing LLM APIs (OpenAI, Anthropic) or local models (Ollama, LMStudio)
- Use Docker containers to isolate and manage different services
- Configuration files should contain all customizable parameters

## Tasks

- [ ] 1.0 Docker Environment and Tool Setup
- [ ] 2.0 MCP Server Configuration and Integration  
- [ ] 3.0 LLM Setup and Strategy Configuration
- [ ] 4.0 Data Source API Configuration
- [ ] 5.0 Report Generation and GitHub Integration
- [ ] 6.0 Scheduling and Notification System