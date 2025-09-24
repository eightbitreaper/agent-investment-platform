# Real-Time Financial Data Integration for Ollama

This integration provides Ollama with access to current, real-time financial data through custom functions.

## 🚀 Quick Setup

1. **Install required dependencies** (should already be included in requirements.txt):
```bash
pip install yfinance requests feedparser
```

2. **Start Ollama services:**
```bash
docker-compose up ollama ollama-webui -d
```

3. **Access the chat interface:**
   - Open http://localhost:8080 in your browser
   - Download a model: `docker exec ollama-investment ollama pull llama3.1:8b`

4. **Get current financial data using the command-line tool:**
```bash
python src/ollama_integration/financial_data_tool.py quote AAPL
```

## 💡 How to Use Real-Time Data in Chat

**Important**: Ollama's training data is from 2023. For current market analysis, use this workflow:

### 1. Get Current Data in Terminal
```bash
# Get current stock quote
python src/ollama_integration/financial_data_tool.py quote AAPL

# Get market overview
python src/ollama_integration/financial_data_tool.py market

# Get recent news
python src/ollama_integration/financial_data_tool.py news TSLA

# Compare stocks
python src/ollama_integration/financial_data_tool.py compare AAPL,GOOGL,MSFT

# Get sector performance
python src/ollama_integration/financial_data_tool.py sectors
```

### 2. Copy Results and Paste into Ollama Chat

Instead of asking "What's Apple's current price?" (which gives 2023 data), do this:

1. **Run command**: `python src/ollama_integration/financial_data_tool.py quote AAPL`
2. **Copy the output**
3. **Paste into chat**: "Here's today's Apple data: [paste output]. Based on this current information, should I invest in AAPL?"

### Sample Chat Interactions

**❌ Don't do this** (gives outdated 2023 data):
```
You: "What's Apple's current stock price?"
Ollama: "As of my last update in 2023, AAPL was around $150..." ❌
```

**✅ Do this instead** (gets current data):
```
You: [After running the command] "Here's today's Apple data from TradingView:
📈 Apple Inc. (AAPL)
💰 Price: $175.23 USD
📊 Change: +$2.15 (+1.24%)
...
Based on this current data, should I invest in AAPL?"

Ollama: "Based on this current data from today, Apple shows..." ✅
```

## 🔧 Available Functions

| Function | Description | Example Usage |
|----------|-------------|---------------|
| `get_stock_quote(symbol)` | Real-time stock price and metrics | "Get AAPL quote" |
| `get_market_overview()` | Major indices performance | "Market overview" |
| `get_stock_news(symbol)` | Recent news for a stock | "TSLA news" |
| `compare_stocks(symbols)` | Compare multiple stocks | "Compare AAPL,GOOGL,MSFT" |
| `get_sector_performance()` | Sector ETF performance | "Sector performance" |

## 💻 System Integration

The integration works by:

1. **Real-Time Data Sources**: Uses `yfinance` for live market data
2. **Function Bridge**: Python functions that fetch current data
3. **Chat Integration**: Functions available through natural language
4. **Response Formatting**: Results formatted for easy reading

## 📊 Data Sources

- **Stock Prices**: Yahoo Finance (real-time)
- **News**: Yahoo Finance News API
- **Market Indices**: S&P 500, Dow Jones, NASDAQ, VIX
- **Sector Data**: Major sector ETFs (XLK, XLF, XLV, etc.)

## ⚡ Performance Notes

- Data fetched in real-time (1-2 second delay)
- Cached for 30 seconds to improve performance
- Graceful error handling for market closures
- Works during market hours and after-hours

## 🔍 Troubleshooting

### "No data available for symbol"
- Check if the ticker symbol is correct
- Some symbols may not be available in all markets

### "Error fetching data"
- Check internet connection
- Verify market is open (some data limited when closed)
- Try a different symbol

### Functions not working
- Run the setup script again
- Check if yfinance is installed: `pip install yfinance`
- Restart Open WebUI: `docker-compose restart ollama-webui`

## 📈 Example Conversation

**User:** "What's the current price of Apple stock and how is it performing?"

**Assistant:** *[Calls get_stock_quote("AAPL")]*

📈 **Apple Inc. (AAPL)**
💰 **Price:** $175.43
📊 **Change:** +$2.15 (+1.24%)
📅 **Previous Close:** $173.28
📦 **Volume:** 52,847,392

🏢 **Company Info:**
• Market Cap: $2,756,234,567,890
• P/E Ratio: 29.8
• Sector: Technology
• Industry: Consumer Electronics

🕐 **Last Updated:** 2025-09-23 16:32:18

Based on the current data, Apple is performing well today with a 1.24% gain. The stock is trading above its previous close with healthy volume, indicating positive investor sentiment.

## 🛡️ Disclaimer

This integration provides real-time financial data for informational purposes only. It is not financial advice. Always consult with qualified financial professionals before making investment decisions.
