# API Documentation

Comprehensive API documentation for the Agent Investment Platform, covering MCP servers, REST endpoints, and integration interfaces.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [MCP Server APIs](#mcp-server-apis)
- [REST API Endpoints](#rest-api-endpoints)
- [Authentication](#authentication)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [SDK and Client Libraries](#sdk-and-client-libraries)
- [Examples and Tutorials](#examples-and-tutorials)

## Overview

The Agent Investment Platform provides multiple API interfaces for accessing financial data, analysis capabilities, and platform functionality:

- **MCP (Model Context Protocol) Servers** - Specialized microservices for specific financial analysis tasks
- **REST API** - Standard HTTP API for web and mobile applications
- **WebSocket API** - Real-time data streaming and notifications
- **GraphQL API** - Flexible query interface for complex data requirements

### Key Features

- **Real-time Financial Data** - Stock prices, market data, and economic indicators
- **AI-Powered Analysis** - Fundamental analysis, technical indicators, and sentiment analysis
- **Portfolio Management** - Position tracking, risk assessment, and performance analytics
- **Report Generation** - Automated investment reports and recommendations
- **Multi-Channel Notifications** - Email, Discord, Slack, and webhook integrations

## Architecture

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  Mobile App     │    │  Third-party    │
│                 │    │                 │    │  Integration    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
          ┌─────────────────────────────────────────────┐
          │           API Gateway / Load Balancer       │
          │              (Nginx + SSL)                  │
          └─────────────────────┬───────────────────────┘
                                │
          ┌─────────────────────────────────────────────┐
          │         Main Application Server             │
          │           (FastAPI + WebSocket)             │
          └─────────────────────┬───────────────────────┘
                                │
    ┌───────────┬───────────────┼───────────────┬───────────┐
    │           │               │               │           │
┌───▼────┐ ┌───▼────┐ ┌────▼─────┐ ┌─────▼────┐ ┌────▼────┐
│ Stock  │ │ News   │ │YouTube   │ │Analysis  │ │  ...    │
│Data    │ │Analysis│ │Transcript│ │Engine    │ │  More   │
│Server  │ │Server  │ │Server    │ │Server    │ │Servers  │
│:3001   │ │:3002   │ │:3003     │ │:3004     │ │         │
└────────┘ └────────┘ └──────────┘ └──────────┘ └─────────┘
```

### MCP Server Network

Each MCP server operates independently with its own:
- **Port and Endpoint** - Dedicated network interface
- **Data Sources** - Specialized external API integrations
- **Capabilities** - Specific financial analysis functions
- **Caching Layer** - Optimized data storage and retrieval

## MCP Server APIs

The platform includes 4 production MCP servers with 20+ specialized tools:

### 1. Stock Data Server (Port 3001)

**Capabilities**: Real-time stock data, historical prices, technical indicators

**Available Tools**:
- `get_stock_quote` - Get current or previous day stock quote
- `get_historical_data` - Historical price data with date range
- `get_technical_indicators` - SMA, EMA, RSI, MACD, Bollinger Bands
- `get_company_fundamentals` - P/E ratio, market cap, financial metrics
- `search_stocks` - Search for stocks by symbol or company name
- `get_market_movers` - Top gainers, losers, and most active stocks

**Example Request**:
```json
{
  \"tool\": \"get_stock_quote\",
  \"arguments\": {
    \"symbol\": \"AAPL\",
    \"include_fundamentals\": true
  }
}
```

**Example Response**:
```json
{
  \"result\": {
    \"symbol\": \"AAPL\",
    \"price\": 150.25,
    \"change\": 2.15,
    \"change_percent\": 1.45,
    \"volume\": 45678900,
    \"market_cap\": 2800000000000,
    \"pe_ratio\": 25.4,
    \"timestamp\": \"2024-09-22T16:00:00Z\"
  }
}
```

### 2. News Analysis Server (Port 3002)

**Capabilities**: News sentiment analysis, trend detection, social media monitoring

**Available Tools**:
- `get_news_sentiment` - Analyze sentiment for specific stocks or market
- `get_trending_topics` - Current trending financial topics
- `analyze_social_sentiment` - Reddit, Twitter sentiment analysis
- `get_market_news` - Latest financial news with sentiment scores
- `track_insider_trading` - Insider trading activity and sentiment
- `get_earnings_calendar` - Upcoming earnings with sentiment context

**Example Request**:
```json
{
  \"tool\": \"get_news_sentiment\",
  \"arguments\": {
    \"symbol\": \"TSLA\",
    \"days_back\": 7,
    \"include_social\": true
  }
}
```

### 3. YouTube Transcript Server (Port 3003)

**Capabilities**: Financial video analysis, transcript processing, expert sentiment

**Available Tools**:
- `analyze_video_transcript` - Extract insights from financial videos
- `get_channel_sentiment` - Analyze sentiment from financial channels
- `search_financial_videos` - Find videos about specific stocks or topics
- `track_analyst_opinions` - Monitor analyst videos and recommendations
- `get_earnings_call_analysis` - Analyze earnings call transcripts

### 4. Analysis Engine Server (Port 3004)

**Capabilities**: Advanced financial analysis, recommendations, strategy execution

**Available Tools**:
- `fundamental_analysis` - Complete fundamental analysis of stocks
- `technical_analysis` - Advanced technical indicator analysis
- `generate_recommendation` - Buy/sell/hold recommendations with rationale
- `analyze_portfolio_risk` - Portfolio risk assessment and optimization
- `backtest_strategy` - Historical strategy performance testing
- `screen_stocks` - Screen stocks based on custom criteria

For detailed MCP server documentation, see: [MCP Server Reference](mcp-server-reference.md)

## REST API Endpoints

### Core Endpoints

#### Health and Status
```http
GET /health
GET /status
GET /metrics
```

#### Authentication
```http
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET /auth/profile
```

#### Portfolio Management
```http
GET /api/v1/portfolio
POST /api/v1/portfolio/positions
PUT /api/v1/portfolio/positions/{symbol}
DELETE /api/v1/portfolio/positions/{symbol}
GET /api/v1/portfolio/performance
```

#### Analysis and Reports
```http
GET /api/v1/analysis/{symbol}
POST /api/v1/analysis/batch
GET /api/v1/reports
POST /api/v1/reports/generate
GET /api/v1/reports/{report_id}
```

#### Market Data
```http
GET /api/v1/market/quotes
GET /api/v1/market/historical/{symbol}
GET /api/v1/market/news
GET /api/v1/market/indicators/{symbol}
```

### WebSocket Endpoints

#### Real-time Data Streams
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to real-time quotes
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'quotes',
  symbols: ['AAPL', 'GOOGL', 'MSFT']
}));

// Subscribe to portfolio updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'portfolio',
  user_id: 'user123'
}));
```

## Authentication

### API Key Authentication

Most endpoints require API key authentication:

```http
GET /api/v1/portfolio
Authorization: Bearer YOUR_API_KEY
```

### JWT Token Authentication

For user-specific operations:

```http
POST /auth/login
Content-Type: application/json

{
  \"username\": \"your_username\",
  \"password\": \"your_password\"
}
```

Response:
```json
{
  \"access_token\": \"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\",
  \"token_type\": \"bearer\",
  \"expires_in\": 3600
}
```

### MCP Server Authentication

MCP servers use internal service authentication:

```json
{
  \"jsonrpc\": \"2.0\",
  \"method\": \"initialize\",
  \"params\": {
    \"capabilities\": {},
    \"clientInfo\": {
      \"name\": \"agent-investment-platform\",
      \"version\": \"1.0.0\"
    }
  },
  \"id\": 1
}
```

## Data Models

### Stock Quote Model

```typescript
interface StockQuote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap?: number;
  pe_ratio?: number;
  timestamp: string;
}
```

### Analysis Result Model

```typescript
interface AnalysisResult {
  symbol: string;
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  confidence: number; // 0-1
  price_target: number;
  reasoning: string;
  technical_indicators: TechnicalIndicators;
  fundamental_metrics: FundamentalMetrics;
  sentiment_score: number; // -1 to 1
  risk_assessment: RiskAssessment;
  timestamp: string;
}
```

### Portfolio Position Model

```typescript
interface PortfolioPosition {
  symbol: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  weight: number; // Portfolio weight percentage
  last_updated: string;
}
```

### News Sentiment Model

```typescript
interface NewsSentiment {
  symbol: string;
  overall_sentiment: number; // -1 to 1
  sentiment_label: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  confidence: number;
  article_count: number;
  sources: string[];
  key_topics: string[];
  time_period: string;
  timestamp: string;
}
```

## Error Handling

### Standard Error Response

```json
{
  \"error\": {
    \"code\": -32603,
    \"message\": \"Internal error\",
    \"data\": {
      \"details\": \"Specific error details\",
      \"request_id\": \"req_123456789\",
      \"timestamp\": \"2024-09-22T10:30:00Z\"
    }
  }
}
```

### Common Error Codes

| Code | Name | Description |
|------|------|-------------|
| -32700 | Parse Error | Invalid JSON |
| -32600 | Invalid Request | Invalid request format |
| -32601 | Method Not Found | Unknown method |
| -32602 | Invalid Params | Invalid parameters |
| -32603 | Internal Error | Server error |
| -32503 | Service Unavailable | External service unavailable |
| -32401 | Unauthorized | Authentication required |
| -32403 | Forbidden | Insufficient permissions |
| -32429 | Rate Limited | Too many requests |

### Error Handling Best Practices

```javascript
// Example error handling in JavaScript
async function getStockQuote(symbol) {
  try {
    const response = await fetch(`/api/v1/market/quotes?symbol=${symbol}`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`API Error ${error.code}: ${error.message}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch stock quote:', error);
    // Handle specific error types
    if (error.message.includes('Rate Limited')) {
      // Implement exponential backoff
      await new Promise(resolve => setTimeout(resolve, 1000));
      return getStockQuote(symbol); // Retry
    }
    throw error;
  }
}
```

## Rate Limiting

### Rate Limit Headers

All API responses include rate limiting information:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 3600
```

### Rate Limits by Endpoint Type

| Endpoint Type | Rate Limit | Window |
|---------------|------------|--------|
| Market Data | 100 req/min | 60 seconds |
| Analysis | 50 req/min | 60 seconds |
| Portfolio | 200 req/min | 60 seconds |
| Reports | 10 req/hour | 3600 seconds |
| WebSocket | 1000 msg/min | 60 seconds |

### Rate Limit Handling

```python
import time
import requests
from typing import Dict, Any

def api_request_with_retry(url: str, headers: Dict[str, str], max_retries: int = 3) -> Dict[str, Any]:
    \"\"\"Make API request with automatic retry on rate limit.\"\"\"
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Rate limited - check retry-after header
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f\"Rate limited. Waiting {retry_after} seconds...\")
            time.sleep(retry_after)
            continue
        else:
            response.raise_for_status()

    raise Exception(f\"Failed after {max_retries} attempts\")
```

## SDK and Client Libraries

### Python SDK

```python
from agent_investment_platform import InvestmentPlatformClient

# Initialize client
client = InvestmentPlatformClient(
    api_key=\"your_api_key\",
    base_url=\"http://localhost:8000\"
)

# Get stock quote
quote = await client.stocks.get_quote(\"AAPL\")
print(f\"AAPL: ${quote.price} ({quote.change_percent:+.2f}%)\")

# Get analysis
analysis = await client.analysis.analyze_stock(\"AAPL\")
print(f\"Recommendation: {analysis.recommendation} (Confidence: {analysis.confidence:.2f})\")

# Get portfolio
portfolio = await client.portfolio.get_positions()
for position in portfolio:
    print(f\"{position.symbol}: {position.quantity} shares @ ${position.current_price}\")
```

### JavaScript SDK

```javascript
import { InvestmentPlatformClient } from 'agent-investment-platform-js';

// Initialize client
const client = new InvestmentPlatformClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000'
});

// Get stock quote
const quote = await client.stocks.getQuote('AAPL');
console.log(`AAPL: $${quote.price} (${quote.changePercent:+.2f}%)`);

// Real-time data stream
const stream = client.stream.quotes(['AAPL', 'GOOGL']);
stream.on('quote', (quote) => {
  console.log(`${quote.symbol}: $${quote.price}`);
});
```

### cURL Examples

```bash
# Get stock quote
curl -X GET \"http://localhost:8000/api/v1/market/quotes?symbol=AAPL\" \\
  -H \"Authorization: Bearer YOUR_API_KEY\" \\
  -H \"Content-Type: application/json\"

# Generate analysis
curl -X POST \"http://localhost:8000/api/v1/analysis\" \\
  -H \"Authorization: Bearer YOUR_API_KEY\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"symbol\": \"AAPL\", \"analysis_type\": \"full\"}'

# Get portfolio
curl -X GET \"http://localhost:8000/api/v1/portfolio\" \\
  -H \"Authorization: Bearer YOUR_API_KEY\"
```

## Examples and Tutorials

### Complete Stock Analysis Workflow

```python
async def analyze_stock_complete(symbol: str):
    \"\"\"Complete stock analysis workflow example.\"\"\"

    # 1. Get basic quote
    quote = await client.mcp.stock_data.get_stock_quote(symbol)
    print(f\"{symbol} Current Price: ${quote['price']:.2f}\")

    # 2. Get technical analysis
    technical = await client.mcp.stock_data.get_technical_indicators(
        symbol=symbol,
        indicators=['SMA', 'RSI', 'MACD']
    )
    print(f\"RSI: {technical['RSI']:.2f}\")

    # 3. Get news sentiment
    sentiment = await client.mcp.news_analysis.get_news_sentiment(
        symbol=symbol,
        days_back=7
    )
    print(f\"News Sentiment: {sentiment['overall_sentiment']:.2f}\")

    # 4. Generate recommendation
    recommendation = await client.mcp.analysis_engine.generate_recommendation(
        symbol=symbol,
        include_reasoning=True
    )
    print(f\"Recommendation: {recommendation['recommendation']}\")
    print(f\"Reasoning: {recommendation['reasoning']}\")

    return {
        'quote': quote,
        'technical': technical,
        'sentiment': sentiment,
        'recommendation': recommendation
    }

# Usage
analysis = await analyze_stock_complete('AAPL')
```

### Real-time Portfolio Monitoring

```javascript
// Real-time portfolio monitoring example
class PortfolioMonitor {
  constructor(apiKey, portfolioId) {
    this.client = new InvestmentPlatformClient({ apiKey });
    this.portfolioId = portfolioId;
    this.ws = null;
  }

  async start() {
    // Get initial portfolio state
    const portfolio = await this.client.portfolio.get();
    console.log('Initial Portfolio Value:', portfolio.totalValue);

    // Connect to real-time updates
    this.ws = new WebSocket('ws://localhost:8000/ws');

    this.ws.onopen = () => {
      // Subscribe to portfolio updates
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        channel: 'portfolio',
        portfolio_id: this.portfolioId
      }));

      // Subscribe to price updates for all holdings
      const symbols = portfolio.positions.map(p => p.symbol);
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        channel: 'quotes',
        symbols: symbols
      }));
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.channel === 'quotes') {
        this.handlePriceUpdate(data);
      } else if (data.channel === 'portfolio') {
        this.handlePortfolioUpdate(data);
      }
    };
  }

  handlePriceUpdate(data) {
    console.log(`${data.symbol}: $${data.price} (${data.change_percent:+.2f}%)`);

    // Check for significant moves
    if (Math.abs(data.change_percent) > 5) {
      this.sendAlert(`Large move in ${data.symbol}: ${data.change_percent:+.2f}%`);
    }
  }

  handlePortfolioUpdate(data) {
    console.log('Portfolio Update:', data);

    // Check for risk alerts
    if (data.daily_pnl_percent < -2) {
      this.sendAlert(`Portfolio down ${data.daily_pnl_percent:.2f}% today`);
    }
  }

  sendAlert(message) {
    // Send alert via webhook, email, etc.
    console.log('ALERT:', message);
  }
}

// Usage
const monitor = new PortfolioMonitor('your_api_key', 'portfolio_123');
monitor.start();
```

## Related Documentation

- [MCP Server Reference](mcp-server-reference.md) - Detailed MCP server API documentation
- [Configuration Guide](../setup/configuration-guide.md) - API configuration and setup
- [Installation Guide](../setup/installation-guide.md) - Complete platform setup
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common API issues and solutions

## Next Steps

1. **Explore MCP Servers**: Review the [MCP Server Reference](mcp-server-reference.md) for detailed API documentation
2. **Set Up Authentication**: Configure API keys and authentication methods
3. **Try Examples**: Use the provided code examples to get started
4. **Build Integration**: Develop your application using the SDK or direct API calls
5. **Monitor Usage**: Set up monitoring and alerting for your API usage

---

The Agent Investment Platform API provides comprehensive access to financial data and AI-powered analysis capabilities. Start with the examples above and refer to the detailed MCP server documentation for advanced features.
