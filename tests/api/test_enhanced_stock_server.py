"""
Enhanced Multi-Source Stock Data Server for Agent Investment Platform.

Integrates multiple free data sources with intelligent fallback:
- Polygon API (with API key)
- Yahoo Finance (free)
- TradingView (free)
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from src.mcp_servers.stock_data_server import StockDataServer, StockQuote
from src.mcp_base.mcp_error import MCPError

class EnhancedStockDataServer(StockDataServer):
    """Enhanced Stock Data Server with multiple data sources."""
    
    def __init__(self):
        super().__init__()
        self.sources_enabled = {
            "polygon": bool(self.polygon_key),
            "yahoo": True,  # Always available
            "tradingview": True  # Always available
        }
    
    async def get_multi_source_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get stock quote with automatic fallback between sources."""
        
        # Define source priority
        sources = []
        
        if self.polygon_key:
            sources.append(("Polygon", self._get_polygon_quote_enhanced))
        
        sources.extend([
            ("Yahoo Finance", self._get_yahoo_quote),
            ("TradingView", self._get_tradingview_quote)
        ])
        
        for source_name, method in sources:
            try:
                quote = await method(symbol)
                if quote:
                    self.logger.info(f"Successfully retrieved {symbol} from {source_name}")
                    return quote
            except Exception as e:
                self.logger.warning(f"{source_name} failed for {symbol}: {e}")
                continue
        
        return None
    
    async def _get_polygon_quote_enhanced(self, symbol: str) -> Optional[StockQuote]:
        """Enhanced Polygon quote with better error handling."""
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={self.polygon_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 429:
                    raise Exception("Rate limit exceeded")
                elif response.status != 200:
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
                    timestamp=datetime.fromtimestamp(result.get("t", 0) / 1000) if result.get("t") else datetime.now()
                )
    
    async def _get_yahoo_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get quote from Yahoo Finance."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
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
                    timestamp=datetime.now()
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
            "columns": ["name", "close", "change", "change_abs", "volume"],
            "sort": {"sortBy": "name", "sortOrder": "asc"},
            "range": [0, 1]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                data = await response.json()
                if not data.get('data') or len(data['data']) == 0:
                    raise Exception("No data found")
                
                row = data['data'][0]['d']
                
                return StockQuote(
                    symbol=row[0],
                    price=float(row[1]),
                    change=float(row[3]),
                    change_percent=float(row[2]),
                    volume=int(row[4]) if row[4] else 0,
                    timestamp=datetime.now()
                )
    
    async def _handle_get_stock_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced stock quote handler with multi-source fallback."""
        symbol = params.get("symbol", "").upper()

        if not symbol:
            raise MCPError(-32602, "Symbol parameter is required")

        # Use multi-source quote method
        quote = await self.get_multi_source_quote(symbol)

        if not quote:
            raise MCPError(-32602, f"No data found for symbol: {symbol} from any source")

        return {
            "success": True,
            "data": {
                "symbol": quote.symbol,
                "price": quote.price,
                "change": quote.change,
                "change_percent": quote.change_percent,
                "volume": quote.volume,
                "timestamp": quote.timestamp.isoformat(),
                "source": "Multi-source fallback"
            },
            "metadata": {
                "sources_available": list(self.sources_enabled.keys()),
                "sources_active": [k for k, v in self.sources_enabled.items() if v]
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check showing all data sources."""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "data_sources": {
                "polygon": {
                    "enabled": bool(self.polygon_key),
                    "requires_api_key": True
                },
                "yahoo_finance": {
                    "enabled": True,
                    "requires_api_key": False
                },
                "tradingview": {
                    "enabled": True,
                    "requires_api_key": False
                }
            }
        }
        
        # Test connectivity for available sources
        if self.polygon_key:
            try:
                quote = await self._get_polygon_quote_enhanced("AAPL")
                status["connectivity_test"] = {
                    "polygon": "healthy" if quote else "no_data"
                }
            except:
                status["connectivity_test"] = {"polygon": "failed"}
        
        return status

async def test_enhanced_server():
    """Test the enhanced multi-source server."""
    print("🚀 Testing Enhanced Multi-Source Stock Data Server...")
    print()
    
    server = EnhancedStockDataServer()
    
    # Test health check
    health = await server.health_check()
    print("📊 Health Check:")
    print(f"   Status: {health['status']}")
    print(f"   Data Sources Available: {len(health['data_sources'])}")
    for source, info in health['data_sources'].items():
        status = "✅" if info['enabled'] else "❌"
        api_key = "🔑" if info['requires_api_key'] else "🆓"
        print(f"     {status} {source} {api_key}")
    print()
    
    # Test stock quote with fallback
    test_symbols = ["AAPL", "MSFT", "INVALID"]
    
    for symbol in test_symbols:
        try:
            result = await server._handle_get_stock_quote({"symbol": symbol})
            data = result["data"]
            print(f"✅ {symbol}: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
        except Exception as e:
            print(f"❌ {symbol}: {e}")
    
    print()
    print("🎉 Enhanced server testing completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_server())