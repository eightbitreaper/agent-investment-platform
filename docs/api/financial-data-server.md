# Financial Data MCP Server Documentation

The Financial Data MCP Server provides real-time financial market data through the Model Context Protocol (MCP) interface, enabling AI assistants to access current stock prices, market indices, news, and sector performance data.

## Overview

**Location**: `src/mcp_servers/financial_data_server.py`
**Port**: 3000
**Protocol**: MCP over stdio
**Data Sources**: TradingView API, Google News RSS

## Features

### 🔄 Real-Time Data Integration
- Current stock quotes from TradingView
- Live market indices (S&P 500, Dow Jones, NASDAQ, VIX)
- Recent financial news from Google News
- Current sector performance via ETF data

### 🛠️ Available Tools

#### 1. get_stock_quote
**Description**: Get real-time stock quote with current price, P/E ratio, market cap, and company information

**Parameters**:
- `symbol` (string, required): Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)

**Returns**: Formatted stock data with:
- Current price and change
- Previous close and volume
- Market cap and P/E ratio
- Company sector and industry
- Last updated timestamp

**Example**:
```json
{
  "tool": "get_stock_quote",
  "params": {"symbol": "AAPL"}
}
```

#### 2. get_market_overview
**Description**: Get current market overview with major indices performance

**Parameters**: None

**Returns**: Current market indices with:
- S&P 500, Dow Jones, NASDAQ values
- VIX volatility index
- Daily changes and percentages
- Real-time update timestamp

#### 3. get_stock_news
**Description**: Get recent financial news headlines for a specific stock

**Parameters**:
- `symbol` (string, required): Stock ticker symbol to get news for

**Returns**: Recent news articles with:
- Headlines and publication dates
- News summaries and sources
- Direct links to full articles
- Last updated timestamp

#### 4. compare_stocks
**Description**: Compare multiple stocks side by side with key metrics

**Parameters**:
- `symbols` (string, required): Comma-separated stock symbols (e.g., "AAPL,GOOGL,MSFT")

**Returns**: Comparison table with:
- Current prices and changes
- Volume and P/E ratios
- Side-by-side performance metrics
- Formatted table view

#### 5. get_sector_performance
**Description**: Get performance of major market sectors using sector ETFs

**Parameters**: None

**Returns**: Sector performance data with:
- Technology, Healthcare, Financial sectors
- Energy, Industrial, Consumer sectors
- Real Estate, Utilities, Materials sectors
- Current percentage changes

## Technical Implementation

### Data Sources

**TradingView API Integration**:
- Real-time stock quotes and market data
- Company fundamentals (P/E ratios, market cap)
- Sector and industry classification
- Historical price data for calculations

**Google News RSS**:
- Financial news aggregation
- Stock-specific news filtering
- Recent headlines and summaries
- Publication dates and sources

### Error Handling

The server implements comprehensive error handling:
- Network timeout protection (10-30 seconds)
- API rate limiting with delays
- Graceful fallback for data unavailability
- Structured error responses with details

### Health Monitoring

Built-in health checks include:
- TradingView API connectivity test
- Basic stock quote validation (AAPL test)
- Service availability monitoring
- Tool registration verification

## Docker Integration

### Container Configuration
```yaml
mcp-financial-server:
  build:
    context: .
    dockerfile: Dockerfile
    target: production
  container_name: mcp-financial-server
  restart: unless-stopped
  ports:
    - "3000:3000"
  environment:
    - PYTHONPATH=/app
    - PORT=3000
  command: ["python", "-m", "src.mcp_servers.financial_data_server"]
```

### Dependencies
- Python 3.11+
- requests>=2.31.0
- feedparser>=6.0.11
- Base MCP server framework

## Usage Examples

### Command Line Testing
```bash
# Test the financial data tool directly
python src/ollama_integration/financial_data_tool.py quote AAPL
python src/ollama_integration/financial_data_tool.py market
python src/ollama_integration/financial_data_tool.py compare AAPL,GOOGL,MSFT
```

### Ollama Integration Workflow
1. **Get Current Data**: Run terminal command to fetch real-time data
2. **Copy Results**: Copy the formatted output from the terminal
3. **Paste to Chat**: Paste data into Ollama chat with context
4. **AI Analysis**: Get current market analysis based on real data

### Example Workflow
```bash
# Terminal: Get current Apple stock data
python src/ollama_integration/financial_data_tool.py quote AAPL

# Copy output, then in Ollama chat:
# "Here's current Apple data: [paste output]
#  Based on this current info, should I buy AAPL stock?"
```

## Development Notes

### Future Enhancements
- Direct MCP tool calling integration with Ollama
- WebSocket support for streaming data
- Additional data sources (Polygon, Alpha Vantage)
- Historical data analysis tools
- Portfolio tracking capabilities

### Known Limitations
- TradingView rate limiting during high usage
- Market hours affect data availability
- Some international stocks may have limited data
- News data depends on Google News RSS availability

## Troubleshooting

### Common Issues

**"No data available for symbol"**:
- Verify ticker symbol is correct (use AAPL not Apple)
- Check if symbol exists on TradingView
- Try alternative symbols or major stocks

**"Connection timeout"**:
- Check internet connectivity
- Verify TradingView API accessibility
- Restart MCP server container

**"Error fetching data"**:
- Check server logs: `docker-compose logs mcp-financial-server`
- Verify dependencies are installed
- Check Python environment and imports

### Health Check
```bash
# Check server health
curl http://localhost:3000/health

# Check container status
docker-compose ps mcp-financial-server

# View server logs
docker-compose logs -f mcp-financial-server
```

## Configuration

The server is configured through:
- `config/mcp-servers.json`: Server registration and settings
- `docker-compose.yml`: Container orchestration
- Environment variables: PORT, PYTHONPATH

For detailed configuration options, see the main MCP servers configuration documentation.
