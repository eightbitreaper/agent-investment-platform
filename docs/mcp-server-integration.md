# MCP Server Integration - Documentation

## Overview

The Agent Investment Platform implements a comprehensive Model Context Protocol (MCP) server infrastructure for AI agent communication and data exchange. This integration provides a robust foundation for connecting AI agents with various financial data sources and analysis capabilities.

## Architecture

### MCP Server Framework

The platform implements a complete MCP server framework with:

- **Base Infrastructure**: Common MCP protocol handling, message routing, and error management
- **Server Manager**: Orchestration, health monitoring, and lifecycle management
- **Individual Servers**: Specialized servers for different financial domains

### Server Components

#### 1. Stock Data Server (Python)
- **File**: `src/mcp_servers/stock_data_server.py`
- **Purpose**: Real-time stock data, prices, and financial metrics
- **Capabilities**:
  - Real-time stock quotes
  - Historical price data
  - Company fundamental data
  - Batch quote processing
- **Data Sources**: Alpha Vantage, Polygon (configurable)

#### 2. Analysis Engine Server (Python)
- **File**: `src/mcp_servers/analysis_engine_server.py`
- **Purpose**: Core financial analysis and strategy engine
- **Capabilities**:
  - Technical analysis (SMA, EMA, RSI, MACD, Bollinger Bands)
  - Fundamental analysis and valuation
  - Risk assessment and metrics
  - Portfolio optimization
- **Storage**: SQLite database for analysis history

#### 3. Report Generator Server (Python)
- **File**: `src/mcp_servers/report_generator_server.py`
- **Purpose**: Automated investment report generation and publishing
- **Capabilities**:
  - Template-based report generation
  - Multiple output formats (Markdown, HTML)
  - GitHub publishing integration
  - Chart generation support
  - Batch report processing

#### 4. News Analysis Server (Node.js)
- **File**: `src/mcp-servers/news-analysis-server.js`
- **Purpose**: Financial news aggregation and sentiment analysis
- **Capabilities**:
  - News search across multiple sources
  - Sentiment analysis
  - Social media monitoring (Reddit)
  - Trend detection
  - News summarization

#### 5. MCP Server Manager (Python)
- **File**: `src/mcp_servers/manager.py`
- **Purpose**: Orchestration and lifecycle management
- **Features**:
  - Start/stop individual or all servers
  - Health monitoring and auto-restart
  - Configuration management
  - Process monitoring and metrics
  - Graceful shutdown handling

## Configuration

### MCP Servers Configuration
- **File**: `config/mcp-servers.json`
- **Format**: JSON configuration with server definitions, environment variables, and global settings
- **Features**:
  - Per-server configuration (command, args, environment)
  - Global settings (health check interval, auto-restart, logging)
  - Security settings (authentication, rate limiting)
  - Monitoring configuration (metrics, health endpoints)

### Environment Variables
Required environment variables for different servers:
- `ALPHA_VANTAGE_API_KEY`: Stock data access
- `POLYGON_API_KEY`: Alternative stock data source
- `NEWS_API_KEY`: News aggregation
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`: Social media monitoring
- `GITHUB_TOKEN`, `GITHUB_REPO`: Report publishing

## Usage

### Running Individual Servers

Use the MCP server runner script:

```bash
# Run specific server
python run_mcp_server.py --server stock-data
python run_mcp_server.py --server analysis-engine
python run_mcp_server.py --server report-generator

# Run Node.js server
cd src/mcp-servers
node news-analysis-server.js
```

### Running Server Manager

```bash
# Run all servers with manager
python run_mcp_server.py --manager

# Custom configuration
python run_mcp_server.py --manager --config custom-config.json
```

### List Available Servers

```bash
python run_mcp_server.py --list
```

## MCP Protocol Implementation

### Base Classes (Python)
- **MCPServerBase**: Abstract base class for Python MCP servers
- **MCPHandler**: Request handling and method routing
- **MCPMessage**: Message structure and serialization
- **MCPTool, MCPPrompt, MCPResource**: MCP capability definitions

### Base Classes (Node.js)
- **MCPServer**: Base class for Node.js MCP servers
- **MCPMessage**: Message handling and JSON-RPC compliance
- **MCPTool, MCPPrompt, MCPResource**: Capability definitions
- **Error Classes**: Structured error handling

### Protocol Features
- JSON-RPC 2.0 compliance
- Stdio transport for communication
- Standard MCP methods (initialize, ping, tools/call, tools/list)
- Error handling and validation
- Capability negotiation

## Tools and Capabilities

### Stock Data Server Tools
- `get_stock_quote`: Real-time stock quotes
- `get_historical_data`: Historical price data
- `get_company_fundamentals`: Company financial metrics
- `get_batch_quotes`: Multiple stock quotes

### Analysis Engine Server Tools
- `technical_analysis`: Technical indicator calculations
- `fundamental_analysis`: Company valuation analysis
- `risk_assessment`: Risk metrics and assessment
- `portfolio_optimization`: Portfolio allocation optimization

### Report Generator Server Tools
- `generate_report`: Create reports from templates
- `list_templates`: Available report templates
- `publish_report`: Publish reports to GitHub
- `generate_chart`: Chart generation for reports
- `generate_batch_reports`: Multiple report generation

### News Analysis Server Tools
- `search_financial_news`: News search across sources
- `analyze_sentiment`: Sentiment analysis of text/articles
- `monitor_social_media`: Social media monitoring
- `detect_trends`: Trending topic detection
- `summarize_news`: News summarization with key insights

## Dependencies

### Python Dependencies
- `aiohttp`: HTTP client for API requests
- `jinja2`: Template engine for reports
- `markdown`: Markdown to HTML conversion
- `pandas`, `numpy`: Data analysis libraries
- `psutil`: Process monitoring (optional)

### Node.js Dependencies
- `axios`: HTTP client
- `sentiment`: Sentiment analysis
- `winston`: Logging
- `cheerio`: HTML parsing
- `natural`: Natural language processing

## Testing and Validation

### Health Checks
Each server implements health check functionality:
- API connectivity testing
- Database connection validation
- Service availability verification
- Configuration validation

### Logging
Comprehensive logging with:
- Structured JSON logging
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File and console output
- Request/response tracking

## Integration Points

### VS Code Integration
- Task definitions for running servers
- Debugging configurations
- Environment management
- Workspace settings

### Docker Integration
- Containerized deployment support
- Environment variable management
- Service orchestration
- Health monitoring

### AI Agent Integration
- Standard MCP protocol compliance
- Tool discovery and execution
- Error handling and recovery
- Session management

## Security Considerations

### Authentication
- Token-based authentication (configurable)
- API key management
- Secure environment variable handling

### Rate Limiting
- Request rate limiting per server
- Burst protection
- API quota management

### Data Protection
- Input validation and sanitization
- Error message sanitization
- Secure API key storage

## Performance Optimizations

### Caching
- Response caching for repeated requests
- Data persistence for analysis results
- Template caching for report generation

### Connection Management
- HTTP connection pooling
- Session reuse
- Resource cleanup

### Monitoring
- Performance metrics collection
- Response time tracking
- Error rate monitoring
- Resource usage tracking

## Extension Points

### Adding New Servers
1. Implement base class (Python: `MCPServerBase`, Node.js: `MCPServer`)
2. Register tools and capabilities
3. Add configuration to `mcp-servers.json`
4. Update runner script and documentation

### Custom Tools
1. Define tool schema with input validation
2. Implement handler function with error handling
3. Register with server using the base class methods
4. Add comprehensive testing

### Custom Templates (Reports)
1. Create Jinja2 template in `templates/reports/`
2. Define required data structure and validation
3. Register template with the report generator
4. Test generation and output formats

## Troubleshooting

### Common Issues
1. **API Key Errors**: Check environment variable configuration
2. **Connection Failures**: Verify network access and API endpoints
3. **Permission Errors**: Check file system permissions for data/logs
4. **Process Startup**: Verify Python/Node.js versions and dependencies

### Debug Mode
Enable debug logging:
```bash
python run_mcp_server.py --server stock-data --log-level DEBUG
```

### Health Status
Check server health:
```bash
# Individual server health via MCP ping
# Manager provides health endpoints (if configured)
```

## Future Enhancements

### Planned Features
- WebSocket transport support
- Additional data sources (Bloomberg, Reuters)
- Real-time streaming capabilities
- Advanced analytics and ML integration
- Multi-language support

### Scalability
- Horizontal scaling support
- Load balancing
- Distributed caching
- Message queuing

---

The MCP Server Integration provides a comprehensive foundation for AI agent communication with robust server implementations, management tools, and extensive documentation. The system is production-ready with proper error handling, monitoring, and security features.
