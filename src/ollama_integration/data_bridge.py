#!/usr/bin/env python3
"""
Ollama Data Bridge Service
Provides real-time financial data integration for Ollama through Open WebUI functions
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests
import yfinance as yf
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaDataBridge:
    """Bridge service to provide real-time data to Ollama"""

    def __init__(self):
        self.base_url = "http://localhost:8080/api/v1"
        self.mcp_servers = {
            "stock_data": "http://localhost:3001",
            "news": "http://localhost:3002",
            "youtube": "http://localhost:3003",
            "analysis": "http://localhost:3004"
        }

    def get_real_time_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock data for a symbol"""
        try:
            # Use yfinance for immediate real-time data
            ticker = yf.Ticker(symbol.upper())

            # Get current info
            info = ticker.info
            history = ticker.history(period="5d")

            if history.empty:
                return {"error": f"No data available for {symbol}"}

            current_price = history['Close'].iloc[-1]
            prev_close = history['Close'].iloc[-2] if len(history) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

            return {
                "symbol": symbol.upper(),
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(prev_close), 2),
                "change": round(float(change), 2),
                "change_percent": round(float(change_pct), 2),
                "volume": int(history['Volume'].iloc[-1]),
                "timestamp": datetime.now().isoformat(),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "company_name": info.get("longName", symbol.upper()),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A")
            }
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}

    def get_latest_news(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest financial news"""
        try:
            # Use NewsAPI or similar service
            # For now, using a simple Google News RSS approach
            import feedparser

            # Google News RSS for financial queries
            url = f"https://news.google.com/rss/search?q={query}+stock+finance&hl=en&gl=US&ceid=US:en"

            feed = feedparser.parse(url)
            news_items = []

            for entry in feed.entries[:limit]:
                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                    "summary": entry.summary if hasattr(entry, 'summary') else entry.title,
                    "source": entry.source.href if hasattr(entry, 'source') else "Google News"
                })

            return news_items

        except Exception as e:
            logger.error(f"Error fetching news for {query}: {e}")
            return [{"error": f"Failed to fetch news: {str(e)}"}]

    def get_market_overview(self) -> Dict[str, Any]:
        """Get current market overview"""
        try:
            # Get major indices
            indices = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ",
                "^VIX": "VIX"
            }

            market_data = {}

            for symbol, name in indices.items():
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="2d")

                if not history.empty:
                    current = history['Close'].iloc[-1]
                    prev = history['Close'].iloc[-2] if len(history) > 1 else current
                    change = current - prev
                    change_pct = (change / prev) * 100 if prev != 0 else 0

                    market_data[name] = {
                        "value": round(float(current), 2),
                        "change": round(float(change), 2),
                        "change_percent": round(float(change_pct), 2)
                    }

            return {
                "timestamp": datetime.now().isoformat(),
                "indices": market_data
            }

        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {"error": f"Failed to fetch market data: {str(e)}"}

# Function definitions for Open WebUI integration
def get_stock_quote(symbol: str) -> str:
    """Get real-time stock quote for a symbol"""
    bridge = OllamaDataBridge()
    data = bridge.get_real_time_stock_data(symbol)

    if "error" in data:
        return f"Error: {data['error']}"

    return f"""
**{data['company_name']} ({data['symbol']})**
Price: ${data['current_price']} ({data['change']:+.2f}, {data['change_percent']:+.2f}%)
Previous Close: ${data['previous_close']}
Volume: {data['volume']:,}
Market Cap: {data['market_cap']}
P/E Ratio: {data['pe_ratio']}
Sector: {data['sector']}
Industry: {data['industry']}
Last Updated: {data['timestamp']}
"""

def get_market_news(query: str = "stock market") -> str:
    """Get latest financial news"""
    bridge = OllamaDataBridge()
    news = bridge.get_latest_news(query, limit=5)

    if not news or "error" in news[0]:
        return "Error fetching news"

    news_text = f"**Latest News for '{query}':**\n\n"
    for item in news:
        news_text += f"• **{item['title']}**\n"
        news_text += f"  Published: {item['published']}\n"
        news_text += f"  Summary: {item['summary']}\n"
        news_text += f"  Link: {item['link']}\n\n"

    return news_text

def get_market_status() -> str:
    """Get current market status and major indices"""
    bridge = OllamaDataBridge()
    data = bridge.get_market_overview()

    if "error" in data:
        return f"Error: {data['error']}"

    status_text = "**Current Market Status:**\n\n"
    for name, info in data['indices'].items():
        status_text += f"**{name}:** {info['value']} ({info['change']:+.2f}, {info['change_percent']:+.2f}%)\n"

    status_text += f"\nLast Updated: {data['timestamp']}"
    return status_text

if __name__ == "__main__":
    # Test the functions
    print("Testing Ollama Data Bridge...")
    print("\n" + "="*50)
    print(get_stock_quote("AAPL"))
    print("\n" + "="*50)
    print(get_market_status())
    print("\n" + "="*50)
    print(get_market_news("AAPL"))
