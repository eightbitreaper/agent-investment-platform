# MCP Server Overview

The Agent Investment Platform uses Model Context Protocol (MCP) servers to provide structured data access for AI assistants. This architecture enables real-time financial data integration while maintaining clean separation of concerns.

## What is MCP?

Model Context Protocol (MCP) is a standard for connecting AI assistants to external data sources and tools. It provides:

- **Structured Communication**: Standardized request/response format
- **Tool Integration**: Expose functions as callable tools for AI models
- **Resource Management**: Efficient data access and caching
- **Security**: Controlled access to external APIs and services

## Platform MCP Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│   MCP Gateway    │◄──►│  Financial APIs │
│ (Ollama/OpenAI) │    │                  │    │  (TradingView)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌──────────────────┐
                    │   MCP Servers    │
                    │                  │
                    │ • Financial Data │
                    │ • News Analysis  │
                    │ • Report Generator│
                    │ • Analysis Engine│
                    └──────────────────┘
```

## Available MCP Servers

### 1. Financial Data Server
**Port**: 3000
**Purpose**: Real-time financial market data
**Documentation**: [Financial Data Server](financial-data-server.md)

**Tools**:
- `get_stock_quote` - Current stock prices and metrics
- `get_market_overview` - Major market indices
- `get_stock_news` - Recent financial news
- `compare_stocks` - Side-by-side stock comparison
- `get_sector_performance` - Sector ETF performance

### 2. Analysis Engine Server
**Port**: 3004
**Purpose**: Investment analysis and recommendations
**Documentation**: [Analysis Engine Server](analysis-engine-server.md)

**Tools**:
- `technical_analysis` - Chart patterns and indicators
- `fundamental_analysis` - Company financial metrics
- `risk_assessment` - Portfolio risk calculations
- `generate_recommendation` - Buy/Hold/Sell decisions

### 3. News Analysis Server
**Port**: 3002
**Purpose**: News aggregation and sentiment analysis
**Documentation**: [News Analysis Server](news-analysis-server.md)

**Tools**:
- `search_financial_news` - Find relevant news articles
- `analyze_sentiment` - News sentiment scoring
- `track_social_media` - Social media mention tracking
- `identify_trends` - Trending topic detection

### 4. Report Generator Server
**Port**: 3005
**Purpose**: Automated report creation and publishing
**Documentation**: [Report Generator Server](report-generator-server.md)

**Tools**:
- `generate_investment_report` - Create comprehensive reports
- `publish_to_github` - Commit reports to repository
- `create_charts` - Generate financial charts
- `format_markdown` - Format reports for publication

## Development and Integration

### Running MCP Servers

**Individual Server:**
```bash
# Start financial data server
python -m src.mcp_servers.financial_data_server

# Start with debug logging
DEBUG=1 python -m src.mcp_servers.financial_data_server
```

**All Servers (Docker):**
```bash
# Start all MCP servers
docker-compose up mcp-financial-server mcp-analysis-server mcp-news-server -d

# View server logs
docker-compose logs -f mcp-financial-server
```

### Testing MCP Integration

**Health Checks:**
```bash
# Test server health
curl http://localhost:3000/health

# Test specific tool
curl -X POST http://localhost:3000/call \
  -H "Content-Type: application/json" \
  -d '{"method": "get_stock_quote", "params": {"symbol": "AAPL"}}'
```

### Configuration

MCP servers are configured in `config/mcp-servers.json`:

```json
{
  "mcpServers": {
    "financial-data-server": {
      "command": "python",
      "args": ["-m", "src.mcp_servers.financial_data_server"],
      "env": {"PORT": "3000"},
      "enabled": true,
      "timeout": 30000
    }
  }
}
```

## Usage Patterns

### Direct Tool Calling (Future)
When MCP integration is complete with Ollama:

```
User: "What's Apple's current stock price?"
AI: [Calls get_stock_quote("AAPL") automatically]
AI: "Apple (AAPL) is currently trading at $175.23..."
```

### Current Copy/Paste Workflow
Until direct integration is complete:

```bash
# Get data manually
python src/ollama_integration/financial_data_tool.py quote AAPL

# Copy output and paste into AI chat
```

## Security and Performance

### Security Features
- **No API Keys in Code**: All credentials via environment variables
- **Rate Limiting**: Automatic request throttling
- **Input Validation**: Sanitized parameters and responses
- **Error Handling**: Graceful failure with informative messages

### Performance Optimizations
- **Response Caching**: 30-second cache for repeated requests
- **Connection Pooling**: Reuse HTTP connections
- **Async Processing**: Non-blocking I/O for multiple requests
- **Resource Limits**: Memory and CPU usage monitoring

## Troubleshooting

### Common Issues

**Server Won't Start:**
1. Check port availability: `netstat -an | grep :3000`
2. Verify Python environment: `python --version`
3. Check dependencies: `pip list | grep -E "(asyncio|aiohttp)"`

**Connection Refused:**
1. Ensure server is running: `ps aux | grep financial_data_server`
2. Check Docker status: `docker-compose ps`
3. Verify network connectivity: `curl http://localhost:3000/health`

**Tool Calls Fail:**
1. Check server logs: `docker-compose logs mcp-financial-server`
2. Test API connectivity: Test external data sources
3. Validate parameters: Ensure correct symbol format

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Start server with debug output
python -m src.mcp_servers.financial_data_server
```

## Related Documentation

- [Financial Data Server](financial-data-server.md) - Detailed financial data API
- [Development Setup](../development/development-setup.md) - Setting up development environment
- [Debugging Guide](../development/debugging/python-scripts.md) - Troubleshooting MCP servers
- [Deployment Guide](../deployment/mcp-integration.md) - Production deployment
