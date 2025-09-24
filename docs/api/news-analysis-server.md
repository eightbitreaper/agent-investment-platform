# News Analysis Server Documentation

The News Analysis MCP Server provides financial news aggregation, sentiment analysis, and trend detection capabilities for investment decision support.

## Overview

**Location**: `src/mcp_servers/news_analysis_server.js`
**Port**: 3002
**Protocol**: MCP over stdio
**Data Sources**: NewsAPI, Reddit, Financial News Feeds

## Features

### 📰 News Aggregation
- Multi-source financial news collection
- Real-time news feed monitoring
- Article filtering and deduplication
- Source credibility scoring

### 😊 Sentiment Analysis
- Natural language processing for financial sentiment
- Bullish/Bearish sentiment scoring
- Market mood indicators
- Social media sentiment tracking

### 📊 Social Media Monitoring
- Reddit discussion tracking (r/investing, r/stocks)
- Twitter mention monitoring
- Discussion thread analysis
- Community sentiment aggregation

### 📈 Trend Detection
- Trending topic identification
- News momentum analysis
- Breaking news alerts
- Market-moving event detection

## Available Tools

### search_financial_news(query, sources, limit)
Search for financial news articles.

**Parameters**:
- `query` (string): Search terms or stock symbol
- `sources` (array): News sources to search
- `limit` (number): Maximum number of articles

**Response**: Array of news articles with metadata

### analyze_sentiment(text, context)
Analyze sentiment of financial text.

**Parameters**:
- `text` (string): Text to analyze
- `context` (string): Financial context (stock, market, sector)

**Response**: Sentiment score and classification

### track_social_media(symbol, platforms, timeframe)
Monitor social media mentions for a stock.

**Parameters**:
- `symbol` (string): Stock ticker symbol
- `platforms` (array): Social platforms to monitor
- `timeframe` (string): Time period to analyze

**Response**: Social media mentions and sentiment trends

### identify_trends(category, timeframe)
Identify trending financial topics.

**Parameters**:
- `category` (string): Category to analyze (stocks, crypto, economy)
- `timeframe` (string): Analysis period

**Response**: Trending topics with momentum scores

### generate_news_summary(articles, focus)
Generate summary of news articles.

**Parameters**:
- `articles` (array): Articles to summarize
- `focus` (string): Summary focus (bullish, bearish, neutral)

**Response**: Structured news summary with key points

## Configuration

Server configuration in `config/news-config.yaml`:

```yaml
news_sources:
  newsapi:
    api_key: "${NEWS_API_KEY}"
    rate_limit: 500

  reddit:
    client_id: "${REDDIT_CLIENT_ID}"
    client_secret: "${REDDIT_CLIENT_SECRET}"
    rate_limit: 60

  feeds:
    - name: "Reuters Finance"
      url: "https://feeds.reuters.com/reuters/businessNews"
    - name: "Bloomberg"
      url: "https://feeds.bloomberg.com/markets"

sentiment:
  model: "financial-sentiment-v1"
  confidence_threshold: 0.7
  cache_ttl: 1800

social_media:
  platforms:
    - reddit
    - twitter
  keywords:
    - stock symbols
    - market terms
    - financial phrases
```

## Development Usage

### Running the Server

**Standalone Mode**:
```bash
node src/mcp-servers/news-analysis-server.js
```

**Docker Mode**:
```bash
docker-compose up mcp-news-server -d
```

### Testing Tools

Test news analysis functions:

```bash
# Test news search
curl -X POST http://localhost:3002/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "search_financial_news",
    "params": {
      "query": "AAPL earnings",
      "sources": ["newsapi", "reddit"],
      "limit": 10
    }
  }'

# Test sentiment analysis
curl -X POST http://localhost:3002/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "analyze_sentiment",
    "params": {
      "text": "Apple stock surges after strong earnings report",
      "context": "AAPL"
    }
  }'
```

## API Integration

### NewsAPI Integration
- Real-time financial news articles
- Source filtering and categorization
- Rate limiting and quota management

### Reddit Integration
- Subreddit monitoring (r/investing, r/stocks, r/SecurityAnalysis)
- Comment sentiment analysis
- Discussion thread tracking

### RSS Feed Processing
- Financial news feed aggregation
- Article parsing and metadata extraction
- Duplicate detection and filtering

## Debugging

### Common Issues

**API Rate Limiting**:
1. Check API quota usage
2. Implement request throttling
3. Use caching to reduce API calls

**Sentiment Analysis Accuracy**:
1. Validate financial context understanding
2. Check model training data relevance
3. Adjust confidence thresholds

**Social Media Access**:
1. Verify API credentials
2. Check platform rate limits
3. Monitor for API changes

### Debug Mode

Enable detailed logging:

```bash
export DEBUG=1
export NODE_ENV=development
node src/mcp-servers/news-analysis-server.js
```

### Performance Monitoring

Monitor key metrics:
- API response times
- Sentiment analysis accuracy
- Cache hit rates
- Memory usage patterns

## Use Cases

### Investment Research
- Gather recent news for stock analysis
- Assess market sentiment for investment decisions
- Monitor social media buzz around stocks

### Risk Management
- Detect negative sentiment trends
- Monitor breaking news for portfolio positions
- Track social media for market sentiment shifts

### Market Timing
- Identify trending topics for investment opportunities
- Monitor news momentum for entry/exit decisions
- Track sentiment changes for market timing

## Related Documentation

- [MCP Server Overview](mcp-overview.md) - Understanding MCP architecture
- [Financial Data Server](financial-data-server.md) - Real-time market data
- [Development Setup](../development/development-setup.md) - Setting up development environment
- [API Keys Configuration](../setup/api-configuration.md) - Setting up external API access
