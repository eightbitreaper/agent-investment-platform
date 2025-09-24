"""
Real-time Financial Data Functions for Open WebUI - TradingView Integration
These functions provide current market data to Ollama through TradingView APIs
"""

import requests
import json
from datetime import datetime, timedelta
import time
import random
from typing import Dict, Any, List

class TradingViewAPI:
    """TradingView API client for real-time financial data"""

    def __init__(self):
        self.base_url = "https://scanner.tradingview.com"
        self.quote_url = "https://symbol-search.tradingview.com/symbol_search/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Origin': 'https://www.tradingview.com',
            'Referer': 'https://www.tradingview.com/'
        })

    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock data from TradingView"""
        try:
            # TradingView scanner API payload
            payload = {
                "filter": [
                    {"left": "name,description", "operation": "match", "right": symbol.upper()}
                ],
                "columns": [
                    "name", "close", "change", "change_abs", "volume", "market_cap_basic",
                    "price_earnings_ttm", "sector", "industry", "description", "type",
                    "subtype", "update_mode", "pricescale", "minmov", "fractional",
                    "minmove2", "currency", "fundamental_currency_code"
                ],
                "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
                "range": [0, 1]
            }

            response = self.session.post(
                f"{self.base_url}/america/scan",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    stock_data = data['data'][0]
                    return self._parse_stock_data(stock_data, symbol)

            # Fallback: Try alternative endpoint
            return self._get_quote_fallback(symbol)

        except Exception as e:
            return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}

    def _parse_stock_data(self, data: Dict, symbol: str) -> Dict[str, Any]:
        """Parse TradingView stock data response"""
        try:
            d = data.get('d', [])
            if len(d) < 10:
                return {"error": "Insufficient data received"}

            return {
                "symbol": symbol.upper(),
                "name": d[9] or symbol.upper(),  # description
                "price": d[1] or 0,  # close
                "change": d[2] or 0,  # change_abs
                "change_percent": d[3] or 0,  # change
                "volume": d[4] or 0,  # volume
                "market_cap": d[5] or 0,  # market_cap_basic
                "pe_ratio": d[6] or 0,  # price_earnings_ttm
                "sector": d[7] or "N/A",  # sector
                "industry": d[8] or "N/A",  # industry
                "currency": d[17] if len(d) > 17 else "USD",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error parsing data: {str(e)}"}

    def _get_quote_fallback(self, symbol: str) -> Dict[str, Any]:
        """Fallback method to get basic quote data"""
        try:
            # Use symbol search endpoint
            search_url = f"{self.quote_url}?text={symbol.upper()}&hl=1&exchange=&lang=en&search_type=&domain=production"

            response = self.session.get(search_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    stock = data[0]
                    return {
                        "symbol": symbol.upper(),
                        "name": stock.get('description', symbol.upper()),
                        "price": 0,  # Price not available in search endpoint
                        "change": 0,
                        "change_percent": 0,
                        "volume": 0,
                        "market_cap": "N/A",
                        "pe_ratio": "N/A",
                        "sector": "N/A",
                        "industry": "N/A",
                        "currency": "USD",
                        "timestamp": datetime.now().isoformat(),
                        "note": "Limited data available"
                    }

            return {"error": f"No data found for {symbol}"}

        except Exception as e:
            return {"error": f"Fallback failed: {str(e)}"}

    def get_market_indices(self) -> Dict[str, Any]:
        """Get major market indices data"""
        indices = {
            "SPX": "S&P 500",
            "DJI": "Dow Jones",
            "IXIC": "NASDAQ",
            "VIX": "VIX"
        }

        results = {}

        for symbol, name in indices.items():
            try:
                data = self.get_stock_data(symbol)
                if "error" not in data and data.get('price', 0) > 0:
                    results[name] = {
                        "value": data.get("price", 0),
                        "change": data.get("change", 0),
                        "change_percent": data.get("change_percent", 0)
                    }
                else:
                    results[name] = {"error": "Data unavailable"}

                # Small delay to avoid rate limiting
                time.sleep(0.3)

            except Exception as e:
                results[name] = {"error": str(e)}

        return {
            "timestamp": datetime.now().isoformat(),
            "indices": results
        }

# Initialize TradingView API client
tv_api = TradingViewAPI()

def get_stock_quote(symbol: str) -> str:
    """
    Get real-time stock quote and key metrics from TradingView

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')

    Returns:
        Current stock price, change, volume, and key metrics
    """
    try:
        data = tv_api.get_stock_data(symbol)

        if "error" in data:
            return f"❌ {data['error']}"

        # Format market cap
        market_cap = data.get("market_cap", 0)
        if isinstance(market_cap, (int, float)) and market_cap > 0:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
        else:
            market_cap_str = "N/A"

        # Format P/E ratio
        pe_ratio = data.get("pe_ratio", 0)
        pe_str = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) and pe_ratio > 0 else "N/A"

        # Format volume
        volume = data.get("volume", 0)
        volume_str = f"{int(volume):,}" if volume > 0 else "N/A"

        # Calculate previous close
        price = data.get("price", 0)
        change = data.get("change", 0)
        prev_close = price - change if price > 0 and change != 0 else price

        # Format the response
        response = f"""📈 **{data.get('name', symbol.upper())} ({symbol.upper()})**

💰 **Price:** ${price:.2f} {data.get('currency', 'USD')}
📊 **Change:** ${change:+.2f} ({data.get('change_percent', 0):+.2f}%)
📅 **Previous Close:** ${prev_close:.2f}
📦 **Volume:** {volume_str}

🏢 **Company Info:**
• Market Cap: {market_cap_str}
• P/E Ratio: {pe_str}
• Sector: {data.get('sector', 'N/A')}
• Industry: {data.get('industry', 'N/A')}

🕐 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (TradingView)
"""

        # Add note if limited data
        if data.get('note'):
            response += f"\n⚠️ **Note:** {data['note']}"

        return response

    except Exception as e:
        return f"❌ Error fetching data for {symbol.upper()}: {str(e)}"

def get_market_overview() -> str:
    """
    Get current market overview with major indices from TradingView

    Returns:
        Current values of major market indices
    """
    try:
        market_data = tv_api.get_market_indices()

        if "error" in market_data:
            return f"❌ Error fetching market overview: {market_data['error']}"

        response = "📊 **Market Overview (TradingView)**\n\n"

        indices = market_data.get('indices', {})
        for name, data in indices.items():
            if "error" in data:
                response += f"⚪ **{name}:** Data unavailable\n"
            else:
                value = data.get('value', 0)
                change = data.get('change', 0)
                change_pct = data.get('change_percent', 0)

                emoji = "🟢" if change >= 0 else "🔴"
                response += f"{emoji} **{name}:** {value:.2f} ({change:+.2f}, {change_pct:+.2f}%)\n"

        response += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return response

    except Exception as e:
        return f"❌ Error fetching market overview: {str(e)}"

def get_stock_news(symbol: str) -> str:
    """
    Get recent news for a stock symbol from web sources

    Args:
        symbol: Stock ticker symbol

    Returns:
        Recent news headlines and summaries
    """
    try:
        # Use Google News RSS feed for financial news
        import feedparser
        import urllib.parse

        query = f"{symbol} stock news finance"
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"

        feed = feedparser.parse(url)

        if not feed.entries:
            return f"📰 No recent news found for {symbol.upper()}"

        response = f"📰 **Recent News for {symbol.upper()}** (Google News)\n\n"

        for i, entry in enumerate(feed.entries[:5]):  # Top 5 news items
            title = entry.title
            pub_date = getattr(entry, 'published', 'Unknown date')
            summary = getattr(entry, 'summary', title)
            link = entry.link

            response += f"• **{title}**\n"
            response += f"  📅 {pub_date}\n"
            response += f"  📝 {summary[:200]}{'...' if len(summary) > 200 else ''}\n"
            response += f"  🔗 {link}\n\n"

        response += f"🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return response

    except Exception as e:
        return f"❌ Error fetching news for {symbol.upper()}: {str(e)}"

def compare_stocks(symbols: str) -> str:
    """
    Compare multiple stocks side by side using TradingView data

    Args:
        symbols: Comma-separated stock symbols (e.g., 'AAPL,GOOGL,MSFT')

    Returns:
        Comparison table of stock metrics
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]

        if len(symbol_list) > 10:
            return "❌ Please compare no more than 10 stocks at once"

        response = "📊 **Stock Comparison (TradingView)**\n\n"
        response += "| Symbol | Price | Change | Change % | Volume | P/E |\n"
        response += "|--------|-------|--------|----------|--------|----||\n"

        for symbol in symbol_list:
            try:
                data = tv_api.get_stock_data(symbol)

                if "error" not in data:
                    price = data.get('price', 0)
                    change = data.get('change', 0)
                    change_pct = data.get('change_percent', 0)
                    volume = data.get('volume', 0)
                    pe_ratio = data.get('pe_ratio', 0)

                    volume_str = f"{int(volume):,}" if volume > 0 else "N/A"
                    pe_str = f"{pe_ratio:.2f}" if pe_ratio > 0 else "N/A"

                    response += f"| {symbol} | ${price:.2f} | ${change:+.2f} | {change_pct:+.2f}% | {volume_str} | {pe_str} |\n"
                else:
                    response += f"| {symbol} | Error | Error | Error | Error | Error |\n"

                # Small delay to avoid rate limiting
                time.sleep(0.3)

            except Exception as e:
                response += f"| {symbol} | Error | Error | Error | Error | Error |\n"

        response += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return response

    except Exception as e:
        return f"❌ Error comparing stocks: {str(e)}"

def get_sector_performance() -> str:
    """
    Get performance of major market sectors using TradingView data

    Returns:
        Current performance of sector ETFs
    """
    try:
        # Major sector ETFs with TradingView symbols
        sectors = {
            "AMEX:XLK": "Technology",
            "AMEX:XLF": "Financial",
            "AMEX:XLV": "Healthcare",
            "AMEX:XLE": "Energy",
            "AMEX:XLI": "Industrial",
            "AMEX:XLY": "Consumer Discretionary",
            "AMEX:XLP": "Consumer Staples",
            "AMEX:XLB": "Materials",
            "AMEX:XLU": "Utilities",
            "AMEX:XLRE": "Real Estate"
        }

        response = "🏭 **Sector Performance Today (TradingView)**\n\n"

        for symbol, sector in sectors.items():
            try:
                data = tv_api.get_stock_data(symbol)

                if "error" not in data:
                    change_pct = data.get('change_percent', 0)
                    emoji = "🟢" if change_pct >= 0 else "🔴"
                    response += f"{emoji} **{sector}:** {change_pct:+.2f}%\n"
                else:
                    response += f"⚪ **{sector}:** Data unavailable\n"

                # Small delay to avoid rate limiting
                time.sleep(0.2)

            except Exception:
                response += f"⚪ **{sector}:** Data unavailable\n"

        response += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return response

    except Exception as e:
        return f"❌ Error fetching sector performance: {str(e)}"
