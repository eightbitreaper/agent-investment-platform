# MCP Server Reference

Detailed technical reference for the Agent Investment Platform's Model Context Protocol (MCP) servers, including API specifications, tool descriptions, and integration examples.

## Table of Contents

- [Overview](#overview)
- [Server Architecture](#server-architecture)
- [Stock Data Server](#stock-data-server)
- [News Analysis Server](#news-analysis-server)
- [YouTube Transcript Server](#youtube-transcript-server)
- [Analysis Engine Server](#analysis-engine-server)
- [Common Patterns](#common-patterns)
- [Error Handling](#error-handling)
- [Integration Examples](#integration-examples)
- [Development Guidelines](#development-guidelines)

## Overview

The Agent Investment Platform implements 4 specialized MCP servers that provide financial analysis capabilities through a standardized protocol. Each server operates independently and can be scaled horizontally.

### MCP Protocol Basics

The Model Context Protocol (MCP) is a standardized way for AI systems to communicate with external tools and data sources. Each server exposes:

- **Tools** - Callable functions with defined schemas
- **Resources** - Data sources and content providers
- **Prompts** - Template-based interaction patterns

### Server Endpoints

| Server | Port | Protocol | Health Check |
|--------|------|----------|--------------|
| Stock Data | 3001 | HTTP/JSON-RPC | `GET /health` |
| News Analysis | 3002 | HTTP/JSON-RPC | `GET /health` |
| YouTube Transcript | 3003 | HTTP/JSON-RPC | `GET /health` |
| Analysis Engine | 3004 | HTTP/JSON-RPC | `GET /health` |

## Server Architecture

### Common MCP Structure

Each server implements the standard MCP protocol with:

```python
# Standard MCP server structure
class MCPServer:
    def __init__(self):
        self.tools = {}
        self.resources = {}
        self.prompts = {}

    async def handle_request(self, request):
        if request.method == \"tools/list\":
            return self.list_tools()
        elif request.method == \"tools/call\":
            return await self.call_tool(request.params)
        # ... other methods
```

### Configuration

Servers are configured via `config/mcp-servers.json`:

```json
{
  \"servers\": {
    \"stock-data-server\": {
      \"command\": \"python\",
      \"args\": [\"src/mcp_servers/stock_data_server.py\"],
      \"env\": {
        \"POLYGON_API_KEY\": \"${POLYGON_API_KEY}\",
        \"ALPHA_VANTAGE_API_KEY\": \"${ALPHA_VANTAGE_API_KEY}\"
      }
    }
  }
}
```

## Stock Data Server

**Port**: 3001
**File**: `src/mcp_servers/stock_data_server.py`
**Purpose**: Real-time and historical stock market data

### Available Tools

#### 1. get_stock_quote

Get current or previous day stock quote with optional fundamentals.

**Schema**:
```json
{
  \"name\": \"get_stock_quote\",
  \"description\": \"Get current stock quote with price, volume, and optional fundamental data\",
  \"inputSchema\": {
    \"type\": \"object\",
    \"properties\": {
      \"symbol\": {
        \"type\": \"string\",
        \"description\": \"Stock ticker symbol (e.g., AAPL, MSFT)\"
      },
      \"include_fundamentals\": {
        \"type\": \"boolean\",
        \"description\": \"Include P/E ratio, market cap, etc.\",
        \"default\": false
      }
    },
    \"required\": [\"symbol\"]
  }
}
```

**Example Request**:
```json
{
  \"jsonrpc\": \"2.0\",
  \"method\": \"tools/call\",
  \"params\": {
    \"name\": \"get_stock_quote\",
    \"arguments\": {
      \"symbol\": \"AAPL\",
      \"include_fundamentals\": true
    }
  },
  \"id\": 1
}
```

**Example Response**:
```json
{
  \"jsonrpc\": \"2.0\",
  \"result\": {
    \"content\": [
      {
        \"type\": \"text\",
        \"text\": \"AAPL Stock Quote:\\nPrice: $150.25 (+$2.15, +1.45%)\\nVolume: 45,678,900\\nMarket Cap: $2.80T\\nP/E Ratio: 25.4\\nLast Updated: 2024-09-22 16:00:00\"
      }
    ]
  },
  \"id\": 1
}
```

#### 2. get_historical_data

Retrieve historical price data for backtesting and analysis.

**Schema**:
```json
{
  \"name\": \"get_historical_data\",
  \"description\": \"Get historical stock price data for specified date range\",
  \"inputSchema\": {
    \"type\": \"object\",
    \"properties\": {
      \"symbol\": {
        \"type\": \"string\",
        \"description\": \"Stock ticker symbol\"
      },
      \"start_date\": {
        \"type\": \"string\",
        \"description\": \"Start date (YYYY-MM-DD)\"
      },
      \"end_date\": {
        \"type\": \"string\",
        \"description\": \"End date (YYYY-MM-DD)\"
      },
      \"interval\": {
        \"type\": \"string\",
        \"enum\": [\"1d\", \"1wk\", \"1mo\"],
        \"default\": \"1d\",
        \"description\": \"Data interval\"
      }
    },
    \"required\": [\"symbol\", \"start_date\", \"end_date\"]
  }
}
```

#### 3. get_technical_indicators

Calculate technical analysis indicators.

**Available Indicators**:
- **SMA** - Simple Moving Average
- **EMA** - Exponential Moving Average
- **RSI** - Relative Strength Index
- **MACD** - Moving Average Convergence Divergence
- **BOLLINGER** - Bollinger Bands
- **VWAP** - Volume Weighted Average Price

**Schema**:
```json
{
  \"name\": \"get_technical_indicators\",
  \"description\": \"Calculate technical analysis indicators for a stock\",
  \"inputSchema\": {
    \"type\": \"object\",
    \"properties\": {
      \"symbol\": {
        \"type\": \"string\",
        \"description\": \"Stock ticker symbol\"
      },
      \"indicators\": {
        \"type\": \"array\",
        \"items\": {
          \"type\": \"string\",
          \"enum\": [\"SMA\", \"EMA\", \"RSI\", \"MACD\", \"BOLLINGER\", \"VWAP\"]
        },
        \"description\": \"List of indicators to calculate\"
      },
      \"period\": {
        \"type\": \"integer\",
        \"default\": 20,
        \"description\": \"Period for calculations (e.g., 20-day SMA)\"
      }
    },
    \"required\": [\"symbol\", \"indicators\"]
  }
}
```

#### 4. get_company_fundamentals

Retrieve fundamental financial metrics.

**Metrics Included**:
- P/E Ratio, P/B Ratio, EPS
- Market Cap, Enterprise Value
- Revenue, Profit Margins
- Debt-to-Equity, Current Ratio
- ROE, ROA, ROIC

#### 5. search_stocks

Search for stocks by symbol or company name.

#### 6. get_market_movers

Get top gainers, losers, and most active stocks.

## News Analysis Server

**Port**: 3002
**File**: `src/mcp-servers/news-analysis-server.js`
**Purpose**: News sentiment analysis and market trend detection

### Available Tools

#### 1. get_news_sentiment

Analyze sentiment for specific stocks or overall market.

**Schema**:
```json
{
  \"name\": \"get_news_sentiment\",
  \"description\": \"Analyze news sentiment for a stock or market topic\",
  \"inputSchema\": {
    \"type\": \"object\",
    \"properties\": {
      \"symbol\": {
        \"type\": \"string\",
        \"description\": \"Stock ticker symbol (optional for general market)\"
      },
      \"days_back\": {
        \"type\": \"integer\",
        \"default\": 7,
        \"description\": \"Number of days to analyze\"
      },
      \"include_social\": {
        \"type\": \"boolean\",
        \"default\": false,
        \"description\": \"Include social media sentiment\"
      }
    }
  }
}
```

**Response Format**:
```json
{
  \"overall_sentiment\": 0.65,
  \"sentiment_label\": \"POSITIVE\",
  \"confidence\": 0.82,
  \"article_count\": 45,
  \"sources\": [\"Reuters\", \"Bloomberg\", \"CNBC\"],
  \"key_topics\": [\"earnings\", \"growth\", \"AI\"],
  \"social_sentiment\": 0.71,
  \"trending_score\": 8.3
}
```

#### 2. get_trending_topics

Identify trending financial topics and themes.

#### 3. analyze_social_sentiment

Analyze sentiment from Reddit, Twitter, and other social platforms.

#### 4. get_market_news

Retrieve latest financial news with sentiment scores.

#### 5. track_insider_trading

Monitor insider trading activity and sentiment impact.

#### 6. get_earnings_calendar

Upcoming earnings with sentiment context and expectations.

## YouTube Transcript Server

**Port**: 3003
**File**: `src/mcp-servers/youtube-transcript-server.js`
**Purpose**: Financial video analysis and expert opinion extraction

### Available Tools

#### 1. analyze_video_transcript

Extract investment insights from financial YouTube videos.

**Schema**:
```json
{
  \"name\": \"analyze_video_transcript\",
  \"description\": \"Analyze YouTube video transcript for investment insights\",
  \"inputSchema\": {
    \"type\": \"object\",
    \"properties\": {
      \"video_url\": {
        \"type\": \"string\",
        \"description\": \"YouTube video URL\"
      },
      \"focus_symbol\": {
        \"type\": \"string\",
        \"description\": \"Stock symbol to focus analysis on (optional)\"
      },
      \"extract_predictions\": {
        \"type\": \"boolean\",
        \"default\": true,
        \"description\": \"Extract price predictions and targets\"
      }
    },
    \"required\": [\"video_url\"]
  }
}
```

#### 2. get_channel_sentiment

Analyze overall sentiment from financial YouTube channels.

#### 3. search_financial_videos

Find videos about specific stocks or financial topics.

#### 4. track_analyst_opinions

Monitor analyst videos and track recommendation changes.

## Analysis Engine Server

**Port**: 3004
**File**: `src/mcp_servers/analysis_engine_server.py`
**Purpose**: Advanced financial analysis and investment recommendations

### Available Tools

#### 1. fundamental_analysis

Comprehensive fundamental analysis of individual stocks.

**Analysis Components**:
- Financial statement analysis
- Valuation metrics and ratios
- Industry comparison
- Growth projections
- Risk assessment

**Schema**:
```json
{
  \"name\": \"fundamental_analysis\",
  \"description\": \"Perform comprehensive fundamental analysis\",
  \"inputSchema\": {
    \"type\": \"object\",
    \"properties\": {
      \"symbol\": {
        \"type\": \"string\",
        \"description\": \"Stock ticker symbol\"
      },
      \"comparison_peers\": {
        \"type\": \"array\",
        \"items\": {\"type\": \"string\"},
        \"description\": \"Peer companies for comparison\"
      },
      \"include_projections\": {
        \"type\": \"boolean\",
        \"default\": true,
        \"description\": \"Include growth projections\"
      }
    },
    \"required\": [\"symbol\"]
  }
}
```

#### 2. technical_analysis

Advanced technical analysis with multiple indicators.

#### 3. generate_recommendation

Generate buy/sell/hold recommendations with detailed reasoning.

**Recommendation Format**:
```json
{
  \"recommendation\": \"BUY\",
  \"confidence\": 0.85,
  \"price_target\": 165.00,
  \"time_horizon\": \"6-12 months\",
  \"reasoning\": \"Strong fundamentals with...\",
  \"risk_factors\": [\"Market volatility\", \"Sector rotation\"],
  \"catalysts\": [\"Earnings growth\", \"New product launch\"]
}
```

#### 4. analyze_portfolio_risk

Portfolio risk assessment and optimization suggestions.

#### 5. backtest_strategy

Historical strategy performance testing.

#### 6. screen_stocks

Screen stocks based on custom criteria.

## Common Patterns

### Request Format

All MCP servers use JSON-RPC 2.0 format:

```json
{
  \"jsonrpc\": \"2.0\",
  \"method\": \"tools/call\",
  \"params\": {
    \"name\": \"tool_name\",
    \"arguments\": {
      \"param1\": \"value1\",
      \"param2\": \"value2\"
    }
  },
  \"id\": 1
}
```

### Response Format

Standard response structure:

```json
{
  \"jsonrpc\": \"2.0\",
  \"result\": {
    \"content\": [
      {
        \"type\": \"text\",
        \"text\": \"Response content here\"
      }
    ]
  },
  \"id\": 1
}
```

### Authentication

Servers use environment variables for API keys:

```python
# Example authentication pattern
import os

class DataProvider:
    def __init__(self):
        self.api_key = os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError(\"API key not configured\")
```

## Error Handling

### Standard Error Codes

| Code | Name | Description |
|------|------|-------------|
| -32700 | Parse Error | Invalid JSON |
| -32600 | Invalid Request | Invalid request object |
| -32601 | Method Not Found | Unknown method |
| -32602 | Invalid Params | Invalid parameters |
| -32603 | Internal Error | Server error |
| -32001 | Server Error | API unavailable |
| -32002 | Rate Limited | Too many requests |
| -32003 | Authentication Error | Invalid API key |

### Error Response Format

```json
{
  \"jsonrpc\": \"2.0\",
  \"error\": {
    \"code\": -32603,
    \"message\": \"Internal error\",
    \"data\": {
      \"details\": \"API rate limit exceeded\",
      \"retry_after\": 60
    }
  },
  \"id\": 1
}
```

### Retry Logic

```python
async def call_with_retry(tool_name, arguments, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = await mcp_client.call_tool(tool_name, arguments)
            return response
        except RateLimitError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(e.retry_after)
                continue
            raise
        except APIError as e:
            if e.code in [-32001, -32603] and attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

## Integration Examples

### Python Client Integration

```python
import asyncio
from mcp_client import MCPClient

class InvestmentAnalyzer:
    def __init__(self):
        self.stock_client = MCPClient(\"http://localhost:3001\")
        self.news_client = MCPClient(\"http://localhost:3002\")
        self.analysis_client = MCPClient(\"http://localhost:3004\")

    async def analyze_stock(self, symbol: str):
        # Get current quote
        quote = await self.stock_client.call_tool(
            \"get_stock_quote\",
            {\"symbol\": symbol, \"include_fundamentals\": True}
        )

        # Get technical indicators
        technical = await self.stock_client.call_tool(
            \"get_technical_indicators\",
            {\"symbol\": symbol, \"indicators\": [\"RSI\", \"MACD\", \"SMA\"]}
        )

        # Get news sentiment
        sentiment = await self.news_client.call_tool(
            \"get_news_sentiment\",
            {\"symbol\": symbol, \"days_back\": 7}
        )

        # Generate recommendation
        recommendation = await self.analysis_client.call_tool(
            \"generate_recommendation\",
            {\"symbol\": symbol}
        )

        return {
            \"quote\": quote,
            \"technical\": technical,
            \"sentiment\": sentiment,
            \"recommendation\": recommendation
        }

# Usage
analyzer = InvestmentAnalyzer()
result = await analyzer.analyze_stock(\"AAPL\")
```

### JavaScript Integration

```javascript
const MCPClient = require('./mcp-client');

class MarketAnalyzer {
    constructor() {
        this.stockClient = new MCPClient('http://localhost:3001');
        this.newsClient = new MCPClient('http://localhost:3002');
    }

    async getMarketOverview() {
        // Get market movers
        const movers = await this.stockClient.callTool('get_market_movers', {});

        // Get overall market sentiment
        const sentiment = await this.newsClient.callTool('get_news_sentiment', {
            days_back: 1
        });

        // Get trending topics
        const topics = await this.newsClient.callTool('get_trending_topics', {});

        return {
            movers,
            sentiment,
            topics
        };
    }
}
```

### Health Check Implementation

```python
async def check_server_health():
    servers = [
        ('Stock Data', 'http://localhost:3001'),
        ('News Analysis', 'http://localhost:3002'),
        ('YouTube', 'http://localhost:3003'),
        ('Analysis Engine', 'http://localhost:3004')
    ]

    results = {}
    for name, url in servers:
        try:
            response = await httpx.get(f\"{url}/health\", timeout=5.0)
            results[name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            results[name] = {
                'status': 'error',
                'error': str(e)
            }

    return results
```

## Development Guidelines

### Adding New Tools

1. **Define Schema**: Create JSON schema for input parameters
2. **Implement Handler**: Add async handler function
3. **Register Tool**: Add to server's tool registry
4. **Add Tests**: Create unit and integration tests
5. **Update Documentation**: Document in this reference

### Tool Development Template

```python
async def new_tool_handler(arguments: dict) -> dict:
    \"\"\"
    Tool description here.

    Args:
        arguments: Tool input parameters

    Returns:
        Tool response data

    Raises:
        ValueError: Invalid parameters
        APIError: External API error
    \"\"\"
    # Validate inputs
    symbol = arguments.get('symbol')
    if not symbol:
        raise ValueError(\"Symbol is required\")

    try:
        # Implement tool logic
        result = await some_api_call(symbol)

        return {
            \"content\": [{
                \"type\": \"text\",
                \"text\": format_result(result)
            }]
        }
    except Exception as e:
        raise APIError(f\"Tool failed: {e}\")

# Register tool
server.register_tool(
    name=\"new_tool\",
    description=\"Tool description\",
    schema=NEW_TOOL_SCHEMA,
    handler=new_tool_handler
)
```

### Testing Guidelines

```python
import pytest
from mcp_servers.stock_data_server import StockDataServer

@pytest.fixture
async def server():
    return StockDataServer()

@pytest.mark.asyncio
async def test_get_stock_quote(server):
    result = await server.call_tool(\"get_stock_quote\", {
        \"symbol\": \"AAPL\",
        \"include_fundamentals\": True
    })

    assert \"content\" in result
    assert len(result[\"content\"]) > 0
    assert \"AAPL\" in result[\"content\"][0][\"text\"]

@pytest.mark.asyncio
async def test_invalid_symbol(server):
    with pytest.raises(ValueError):
        await server.call_tool(\"get_stock_quote\", {
            \"symbol\": \"INVALID\"
        })
```

### Performance Considerations

1. **Caching**: Implement Redis caching for expensive API calls
2. **Rate Limiting**: Respect external API rate limits
3. **Connection Pooling**: Use connection pools for HTTP clients
4. **Async Operations**: Use async/await for all I/O operations
5. **Error Recovery**: Implement circuit breakers and fallbacks

### Security Best Practices

1. **API Key Management**: Use environment variables, never hardcode
2. **Input Validation**: Validate all tool parameters
3. **Rate Limiting**: Implement per-client rate limiting
4. **Logging**: Log requests but not sensitive data
5. **Error Messages**: Don't expose internal details in errors

## Related Documentation

- [API Documentation](README.md) - High-level API overview
- [Configuration Guide](../setup/configuration-guide.md) - MCP server configuration
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common MCP issues
- [Docker Deployment](../deployment/docker-deployment.md) - Containerized deployment

---

This reference provides complete technical documentation for integrating with and extending the MCP server architecture. For questions or contributions, please refer to the [Development Guide](../development/README.md).
