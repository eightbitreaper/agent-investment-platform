"""
Multi-Source Stock Data Client for Agent Investment Platform.

Provides stock data from multiple free sources:
- TradingView (free screener API)
- Yahoo Finance (free API)
- Polygon (with API key)
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class StockQuote:
    """Stock quote data structure."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    source: str

class MultiSourceStockClient:
    """Multi-source stock data client with fallback capabilities."""

    def __init__(self):
        self.polygon_key = os.environ.get("POLYGON_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get stock quote with automatic fallback between sources."""

        # Try sources in order of preference: Polygon -> Yahoo -> TradingView
        sources = []

        if self.polygon_key:
            sources.append(("Polygon", self._get_polygon_quote))

        sources.extend([
            ("Yahoo Finance", self._get_yahoo_quote),
            ("TradingView", self._get_tradingview_quote)
        ])

        for source_name, method in sources:
            try:
                quote = await method(symbol)
                if quote:
                    print(f"✅ Got quote from {source_name}: {symbol} ${quote.price:.2f}")
                    return quote
            except Exception as e:
                print(f"⚠️ {source_name} failed for {symbol}: {e}")
                continue

        return None

    async def _get_polygon_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get quote from Polygon API."""
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={self.polygon_key}"

        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")

            data = await response.json()
            if data.get("status") != "OK" or not data.get("results"):
                raise Exception("No data available")

            result = data["results"][0]
            open_price = float(result.get("o", 0))
            close_price = float(result.get("c", 0))
            change = close_price - open_price
            change_percent = (change / open_price * 100) if open_price > 0 else 0

            return StockQuote(
                symbol=symbol.upper(),
                price=close_price,
                change=change,
                change_percent=change_percent,
                volume=int(result.get("v", 0)),
                timestamp=datetime.fromtimestamp(result.get("t", 0) / 1000) if result.get("t") else datetime.now(),
                source="Polygon"
            )

    async def _get_yahoo_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get quote from Yahoo Finance."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")

            data = await response.json()
            result = data['chart']['result'][0]
            meta = result['meta']

            current_price = meta.get('regularMarketPrice')
            previous_close = meta.get('previousClose')

            if not current_price or not previous_close:
                raise Exception("Missing price data")

            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close > 0 else 0

            return StockQuote(
                symbol=meta.get('symbol', symbol).upper(),
                price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(meta.get('regularMarketVolume', 0)),
                timestamp=datetime.now(),
                source="Yahoo Finance"
            )

    async def _get_tradingview_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get quote from TradingView screener."""
        url = "https://scanner.tradingview.com/america/scan"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.tradingview.com/',
            'Origin': 'https://www.tradingview.com',
            'Content-Type': 'application/json'
        }

        payload = {
            "filter": [{"left": "name", "operation": "match", "right": symbol}],
            "columns": ["name", "close", "change", "change_abs", "volume", "market_cap_basic"],
            "sort": {"sortBy": "name", "sortOrder": "asc"},
            "range": [0, 1]
        }

        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")

            data = await response.json()
            if not data.get('data') or len(data['data']) == 0:
                raise Exception("No data found")

            row = data['data'][0]['d']  # First result

            return StockQuote(
                symbol=row[0],  # name
                price=float(row[1]),  # close
                change=float(row[3]),  # change_abs
                change_percent=float(row[2]),  # change
                volume=int(row[4]) if row[4] else 0,  # volume
                timestamp=datetime.now(),
                source="TradingView"
            )

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Optional[StockQuote]]:
        """Get quotes for multiple symbols."""
        results = {}

        # Process symbols concurrently
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.get_quote(symbol.upper()))
            tasks.append((symbol.upper(), task))

        for symbol, task in tasks:
            try:
                quote = await task
                results[symbol] = quote
            except Exception as e:
                print(f"❌ Failed to get quote for {symbol}: {e}")
                results[symbol] = None

        return results

async def test_multi_source_client():
    """Test the multi-source stock client."""
    print("🔍 Testing Multi-Source Stock Data Client...")
    print()

    async with MultiSourceStockClient() as client:
        # Test single quote
        print("📊 Testing single quote (AAPL):")
        quote = await client.get_quote("AAPL")
        if quote:
            print(f"   Symbol: {quote.symbol}")
            print(f"   Price: ${quote.price:.2f}")
            print(f"   Change: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
            print(f"   Volume: {quote.volume:,}")
            print(f"   Source: {quote.source}")
        print()

        # Test multiple quotes
        print("📈 Testing multiple quotes:")
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        quotes = await client.get_multiple_quotes(symbols)

        print("   Results:")
        for symbol, quote in quotes.items():
            if quote:
                print(f"   {symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%) [{quote.source}]")
            else:
                print(f"   {symbol}: ❌ Failed to get quote")

        print()
        print("🎉 Multi-source testing completed!")

if __name__ == "__main__":
    asyncio.run(test_multi_source_client())
