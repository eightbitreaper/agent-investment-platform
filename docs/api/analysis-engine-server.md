# Analysis Engine Server Documentation

The Analysis Engine MCP Server provides comprehensive investment analysis capabilities including technical analysis, fundamental analysis, risk assessment, and investment recommendations.

## Overview

**Location**: `src/mcp_servers/analysis_engine_server.py`
**Port**: 3004
**Protocol**: MCP over stdio
**Dependencies**: PostgreSQL, Redis

## Features

### 🔍 Technical Analysis
- Chart pattern recognition and trend analysis
- Technical indicators (RSI, MACD, Bollinger Bands)
- Support and resistance level identification
- Volume analysis and momentum indicators

### 📊 Fundamental Analysis
- Financial statement analysis and ratio calculations
- DCF (Discounted Cash Flow) valuation models
- Peer comparison and industry analysis
- ESG (Environmental, Social, Governance) scoring

### ⚖️ Risk Assessment
- Portfolio volatility and VaR calculations
- Correlation analysis and diversification metrics
- Stress testing and scenario analysis
- Risk-adjusted return measurements (Sharpe ratio, Alpha, Beta)

### 🎯 Investment Recommendations
- Buy/Hold/Sell decision generation
- Price target calculations
- Investment strategy recommendations
- Portfolio optimization suggestions

## Available Tools

### technical_analysis(symbol, timeframe, indicators)
Perform technical analysis on a stock symbol.

**Parameters**:
- `symbol` (string): Stock ticker symbol
- `timeframe` (string): Time period (1d, 1w, 1m, 3m, 1y)
- `indicators` (array): List of indicators to calculate

**Response**: Technical analysis results with charts and indicator values

### fundamental_analysis(symbol, metrics)
Conduct fundamental analysis of a company.

**Parameters**:
- `symbol` (string): Stock ticker symbol
- `metrics` (array): Fundamental metrics to analyze

**Response**: Financial ratios, valuation metrics, and analysis

### risk_assessment(portfolio, timeframe)
Assess risk metrics for a portfolio.

**Parameters**:
- `portfolio` (object): Portfolio composition with weights
- `timeframe` (string): Assessment period

**Response**: Risk metrics, correlation matrix, and recommendations

### generate_recommendation(symbol, analysis_type)
Generate investment recommendation based on analysis.

**Parameters**:
- `symbol` (string): Stock ticker symbol
- `analysis_type` (string): Type of analysis (technical, fundamental, combined)

**Response**: Buy/Hold/Sell recommendation with reasoning

### portfolio_optimization(holdings, constraints)
Optimize portfolio allocation based on modern portfolio theory.

**Parameters**:
- `holdings` (array): Current portfolio holdings
- `constraints` (object): Optimization constraints

**Response**: Optimized allocation and performance metrics

## Configuration

The server requires database configuration in `config/analysis-config.yaml`:

```yaml
database:
  url: postgresql://user:password@localhost:5432/investment_db
  pool_size: 10

redis:
  url: redis://localhost:6379/0
  cache_ttl: 3600

analysis:
  default_timeframe: "1y"
  risk_free_rate: 0.02
  confidence_level: 0.95
```

## Development Usage

### Running the Server

**Standalone Mode**:
```bash
python -m src.mcp_servers.analysis_engine_server
```

**Docker Mode**:
```bash
docker-compose up mcp-analysis-server -d
```

### Testing Tools

Test individual analysis functions:

```bash
# Test technical analysis
curl -X POST http://localhost:3004/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "technical_analysis",
    "params": {
      "symbol": "AAPL",
      "timeframe": "3m",
      "indicators": ["RSI", "MACD", "BB"]
    }
  }'

# Test fundamental analysis
curl -X POST http://localhost:3004/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "fundamental_analysis",
    "params": {
      "symbol": "AAPL",
      "metrics": ["PE_RATIO", "ROE", "DEBT_EQUITY"]
    }
  }'
```

## Debugging

### Common Issues

**Database Connection Failed**:
1. Verify PostgreSQL is running
2. Check connection string in configuration
3. Ensure database permissions are correct

**Analysis Calculations Error**:
1. Verify market data is available
2. Check data quality and completeness
3. Validate calculation parameters

**Performance Issues**:
1. Monitor database query performance
2. Check Redis cache hit rates
3. Optimize calculation algorithms

### Debug Mode

Enable debug logging:

```bash
export DEBUG=1
export LOG_LEVEL=DEBUG
python -m src.mcp_servers.analysis_engine_server
```

## Related Documentation

- [MCP Server Overview](mcp-overview.md) - Understanding MCP architecture
- [Development Setup](../development/development-setup.md) - Setting up development environment
- [Debugging Guide](../development/debugging/python-scripts.md) - Troubleshooting MCP servers
- [Database Setup](../setup/database-configuration.md) - PostgreSQL configuration
