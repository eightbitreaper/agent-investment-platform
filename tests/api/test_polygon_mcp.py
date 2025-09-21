import os
import asyncio
import aiohttp
from datetime import datetime
from src.mcp_servers.stock_data_server import StockDataServer

class PolygonStockDataServer(StockDataServer):
    """Enhanced Stock Data Server with Polygon API support."""
    
    def __init__(self):
        super().__init__()
        self.polygon_key = os.environ.get("POLYGON_API_KEY")
        self.polygon_base_url = "https://api.polygon.io"
    
    async def get_polygon_quote(self, symbol: str):
        """Get real-time quote using Polygon API."""
        if not self.polygon_key:
            raise Exception("POLYGON_API_KEY not configured")
        
        url = f"{self.polygon_base_url}/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={self.polygon_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        result = data["results"][0]
                        return {
                            "success": True,
                            "data": {
                                "symbol": symbol,
                                "price": result.get("c"),
                                "high": result.get("h"),
                                "low": result.get("l"),
                                "open": result.get("o"),
                                "volume": result.get("v"),
                                "change": result.get("c", 0) - result.get("o", 0),
                                "change_percent": ((result.get("c", 0) - result.get("o", 0)) / result.get("o", 1)) * 100,
                                "timestamp": result.get("t"),
                                "source": "Polygon"
                            }
                        }
                    else:
                        return {"success": False, "error": "No data available"}
                else:
                    return {"success": False, "error": f"API error: {response.status}"}
    
    async def get_polygon_market_status(self):
        """Get current market status using Polygon API."""
        if not self.polygon_key:
            raise Exception("POLYGON_API_KEY not configured")
        
        url = f"{self.polygon_base_url}/v1/marketstatus/now?apikey={self.polygon_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": {
                            "market": data.get("market"),
                            "server_time": data.get("serverTime"),
                            "exchanges": data.get("exchanges", {}),
                            "source": "Polygon"
                        }
                    }
                else:
                    return {"success": False, "error": f"API error: {response.status}"}

async def test_polygon_mcp_integration():
    """Test our Polygon-enhanced MCP server."""
    print('Testing Polygon MCP Integration...')
    print()
    
    server = PolygonStockDataServer()
    
    # Test stock quote
    try:
        result = await server.get_polygon_quote("AAPL")
        if result["success"]:
            data = result["data"]
            print('✅ AAPL Stock Quote (via Polygon MCP):')
            print(f'   Symbol: {data["symbol"]}')
            print(f'   Price: ${data["price"]:.2f}')
            print(f'   Change: ${data["change"]:.2f} ({data["change_percent"]:.2f}%)')
            print(f'   High: ${data["high"]:.2f}')
            print(f'   Low: ${data["low"]:.2f}')
            print(f'   Volume: {data["volume"]:,}')
            print(f'   Source: {data["source"]}')
        else:
            print('❌ Quote failed:', result["error"])
        print()
    except Exception as e:
        print(f'❌ Error getting quote: {e}')
        print()
    
    # Test market status
    try:
        result = await server.get_polygon_market_status()
        if result["success"]:
            data = result["data"]
            print('✅ Market Status (via Polygon MCP):')
            print(f'   Status: {data["market"]}')
            print(f'   Server Time: {data["server_time"]}')
            print(f'   Source: {data["source"]}')
            print('   Exchanges:')
            for exchange, status in data["exchanges"].items():
                print(f'     {exchange}: {status}')
        else:
            print('❌ Market status failed:', result["error"])
        print()
    except Exception as e:
        print(f'❌ Error getting market status: {e}')
        print()
    
    # Test multiple stocks
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    print('✅ Multiple Stock Quotes:')
    for symbol in symbols:
        try:
            result = await server.get_polygon_quote(symbol)
            if result["success"]:
                data = result["data"]
                print(f'   {symbol}: ${data["price"]:.2f} ({data["change_percent"]:.2f}%)')
            else:
                print(f'   {symbol}: Error - {result["error"]}')
        except Exception as e:
            print(f'   {symbol}: Exception - {e}')
    
    print()
    print('🎉 Polygon MCP Integration test completed!')

if __name__ == "__main__":
    asyncio.run(test_polygon_mcp_integration())