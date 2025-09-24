# Financial Data Tools - Development Guide

This guide covers the technical implementation and usage of the real-time financial data tools for developers and advanced users.

## Overview

The financial data tools provide command-line access to real-time market information from TradingView and Google News. These tools bridge the gap between current market data and AI analysis by offering a copy/paste workflow for Ollama integration.

## Tool Architecture

```
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Command Line Tool   │───►│ Financial        │───►│ External APIs   │
│ financial_data_tool │    │ Functions Module │    │ (TradingView,   │
│                     │    │                  │    │  Google News)   │
└─────────────────────┘    └──────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────────┐
│ Formatted Output    │
│ (Copy to Ollama)    │
└─────────────────────┘
```

## Command-Line Interface

### Basic Usage

**Location**: `src/ollama_integration/financial_data_tool.py`

**Syntax**:
```bash
python src/ollama_integration/financial_data_tool.py [command] [arguments]
```

### Available Commands

#### Stock Quote
Get comprehensive stock information:
```bash
# Basic stock quote
python src/ollama_integration/financial_data_tool.py quote AAPL

# Multiple stocks
python src/ollama_integration/financial_data_tool.py quote MSFT
python src/ollama_integration/financial_data_tool.py quote GOOGL
```

**Output Format**:
```
📈 Apple Inc. (AAPL)
💰 Price: $175.23 USD
📊 Change: +$2.15 (+1.24%)
📅 Previous Close: $173.08
📦 Volume: 52,847,392
🏢 Company Info:
• Market Cap: $2.76T
• P/E Ratio: 29.8
• Sector: Technology
• Industry: Consumer Electronics
🕐 Last Updated: 2025-09-23 16:32:18 (TradingView)
```

#### Market Overview
Get major market indices:
```bash
python src/ollama_integration/financial_data_tool.py market
```

**Output Format**:
```
📊 Market Overview (TradingView)
🟢 S&P 500: 4,567.89 (+12.34, +0.27%)
🔴 Dow Jones: 35,123.45 (-89.76, -0.25%)
🟢 NASDAQ: 14,234.56 (+45.67, +0.32%)
🟢 VIX: 16.42 (-0.23, -1.38%)
🕐 Updated: 2025-09-23 16:32:18
```

#### Stock News
Get recent news for a specific stock:
```bash
python src/ollama_integration/financial_data_tool.py news TSLA
```

**Output Format**:
```
📰 Recent News for TSLA (Google News)
• Tesla Announces New Model Updates
  📅 September 23, 2025
  📝 Tesla Inc. announced significant updates to its Model lineup...
  🔗 https://news.example.com/tesla-updates

• Analyst Upgrades Tesla Stock Rating
  📅 September 22, 2025
  📝 Major investment firm upgrades Tesla from Hold to Buy...
  🔗 https://finance.example.com/tesla-upgrade
```

#### Stock Comparison
Compare multiple stocks side-by-side:
```bash
python src/ollama_integration/financial_data_tool.py compare AAPL,GOOGL,MSFT
```

**Output Format**:
```
📊 Stock Comparison (TradingView)
| Symbol | Price | Change | Change % | Volume | P/E |
|--------|-------|--------|----------|--------|-----|
| AAPL | $175.23 | +$2.15 | +1.24% | 52,847,392 | 29.8 |
| GOOGL | $145.67 | -$1.23 | -0.84% | 28,456,123 | 22.1 |
| MSFT | $412.89 | +$5.67 | +1.39% | 31,234,567 | 28.5 |
🕐 Updated: 2025-09-23 16:32:18
```

#### Sector Performance
Get performance across major sectors:
```bash
python src/ollama_integration/financial_data_tool.py sectors
```

**Output Format**:
```
🏭 Sector Performance Today (TradingView)
🟢 Technology: +0.45%
🔴 Financial: -0.23%
🟢 Healthcare: +0.67%
🔴 Energy: -1.12%
🟢 Industrial: +0.34%
🕐 Updated: 2025-09-23 16:32:18
```

## Programming Interface

### Direct Function Access

For Python scripts and integration:

```python
from src.ollama_integration.financial_functions import (
    get_stock_quote, get_market_overview, get_stock_news,
    compare_stocks, get_sector_performance
)

# Get stock quote
quote_data = get_stock_quote("AAPL")
print(quote_data)

# Get market data
market_data = get_market_overview()
print(market_data)

# Get news
news_data = get_stock_news("TSLA")
print(news_data)

# Compare stocks
comparison = compare_stocks("AAPL,GOOGL,MSFT")
print(comparison)

# Get sector performance
sectors = get_sector_performance()
print(sectors)
```

### TradingView API Integration

Direct API access for advanced usage:

```python
from src.ollama_integration.financial_functions import TradingViewAPI

# Initialize API client
tv_api = TradingViewAPI()

# Get raw stock data
raw_data = tv_api.get_stock_data("AAPL")
print(raw_data)

# Get market indices
indices_data = tv_api.get_market_indices()
print(indices_data)
```

## Development and Testing

### Running Tests

Test individual components:

```bash
# Test TradingView API connection
python -c "from src.ollama_integration.financial_functions import TradingViewAPI; api = TradingViewAPI(); print(api.get_stock_data('AAPL'))"

# Test command-line tool
python src/ollama_integration/financial_data_tool.py quote AAPL

# Test all functions
python -c "
from src.ollama_integration.financial_functions import *
print('Stock Quote:', get_stock_quote('AAPL')[:100])
print('Market:', get_market_overview()[:100])
print('News:', get_stock_news('AAPL')[:100])
"
```

### Debug Mode

Enable debugging for troubleshooting:

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run with debug output
python src/ollama_integration/financial_data_tool.py quote AAPL
```

### Error Handling

Common error scenarios and handling:

```python
try:
    quote = get_stock_quote("INVALID_SYMBOL")
except Exception as e:
    print(f"Error fetching quote: {e}")
    # Handle error appropriately
```

## Configuration and Customization

### API Configuration

The tools use these data sources:
- **TradingView**: Stock quotes and market data
- **Google News RSS**: Financial news feeds

No API keys required for basic functionality.

### Output Formatting

Customize output format by modifying the functions:

```python
def get_stock_quote(symbol: str) -> str:
    # Custom formatting logic
    data = tv_api.get_stock_data(symbol)

    # Format as needed
    return f"Stock: {symbol}, Price: ${data['price']}"
```

### Adding New Data Sources

Extend functionality by adding new data sources:

```python
class NewDataProvider:
    def get_custom_data(self, symbol: str):
        # Implementation for new data source
        pass

# Integrate with existing tools
def get_custom_financial_data(symbol: str) -> str:
    provider = NewDataProvider()
    data = provider.get_custom_data(symbol)
    return format_custom_data(data)
```

## Integration with Ollama

### Workflow Integration

The tools are designed for seamless Ollama integration:

1. **Run Command**: Execute financial data tool
2. **Copy Output**: Copy formatted results
3. **Paste to Chat**: Provide data as context to AI
4. **Get Analysis**: AI analyzes based on current data

### Automation Scripts

Create scripts for common workflows:

```bash
#!/bin/bash
# get_portfolio_data.sh
echo "Getting portfolio data..."
python src/ollama_integration/financial_data_tool.py quote AAPL
python src/ollama_integration/financial_data_tool.py quote GOOGL
python src/ollama_integration/financial_data_tool.py quote MSFT
python src/ollama_integration/financial_data_tool.py market
```

### Batch Processing

Process multiple symbols efficiently:

```python
# batch_quotes.py
import sys
from src.ollama_integration.financial_functions import get_stock_quote

symbols = sys.argv[1].split(',')
for symbol in symbols:
    print(f"\n=== {symbol} ===")
    print(get_stock_quote(symbol))
```

Usage:
```bash
python batch_quotes.py "AAPL,GOOGL,MSFT,TSLA"
```

## Performance Considerations

### Caching
- Responses are cached for 30 seconds to avoid rate limiting
- Multiple requests for the same data return cached results

### Rate Limiting
- Automatic delays between requests to respect API limits
- Exponential backoff for failed requests

### Error Recovery
- Graceful handling of network timeouts
- Fallback mechanisms for API failures
- Informative error messages for troubleshooting

## Advanced Usage

### Custom Data Processing

Process and analyze the raw data:

```python
import json
from src.ollama_integration.financial_functions import TradingViewAPI

api = TradingViewAPI()
raw_data = api.get_stock_data("AAPL")

# Extract specific metrics
price = raw_data.get('price', 0)
pe_ratio = raw_data.get('pe_ratio', 0)

# Custom analysis
if pe_ratio > 30:
    print(f"High P/E ratio: {pe_ratio}")
```

### Integration with Other Tools

Combine with other platform components:

```python
# Combine with analysis engine
from src.analysis.recommendation_engine import RecommendationEngine
from src.ollama_integration.financial_functions import get_stock_quote

# Get current data
current_data = get_stock_quote("AAPL")

# Generate recommendation based on current data
engine = RecommendationEngine()
recommendation = engine.analyze_stock("AAPL", current_data)
```

## Troubleshooting

### Common Issues

**Network Connectivity**:
```bash
# Test internet connection
ping tradingview.com
ping news.google.com
```

**Python Path Issues**:
```bash
# Verify Python path
echo $PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

**Encoding Problems**:
```bash
# Set UTF-8 encoding
export PYTHONIOENCODING=UTF-8
```

### Debug Output

Enable verbose output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug logging
python src/ollama_integration/financial_data_tool.py quote AAPL
```

## Related Documentation

- [Chat Guide](../setup/ollama-chat-guide.md) - Using tools with Ollama chat interface
- [API Documentation](../api/financial-data-server.md) - MCP server implementation
- [Debugging Guide](debugging/python-scripts.md) - Troubleshooting Python components
- [Contributing](contributing.md) - Contributing to financial data tools
