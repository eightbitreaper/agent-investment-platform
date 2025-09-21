import asyncio
import aiohttp
import json
from datetime import datetime
import time

async def test_tradingview_free_access():
    """Test various TradingView free data access methods."""
    print("🔍 Testing TradingView Free Data Access Methods...")
    print()
    
    # Method 1: TradingView's public symbol info API
    await test_symbol_info()
    
    # Method 2: TradingView chart data (if accessible)
    await test_chart_data()
    
    # Method 3: TradingView websocket real-time data
    await test_websocket_data()
    
    print("🎉 TradingView testing completed!")

async def test_symbol_info():
    """Test TradingView symbol information API."""
    print("📊 Testing Symbol Info API...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Try TradingView's symbol info endpoint
            symbol = "NASDAQ:AAPL"
            url = f"https://symbol-search.tradingview.com/symbol_search/?text={symbol}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.tradingview.com/',
                'Origin': 'https://www.tradingview.com'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Symbol Search Response: {response.status}")
                    print(f"   Data available: {len(data) if isinstance(data, list) else 'Unknown format'}")
                    if isinstance(data, list) and data:
                        print(f"   First result: {data[0].get('symbol', 'N/A')}")
                else:
                    print(f"❌ Symbol Search failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Symbol Info error: {e}")
    
    print()

async def test_chart_data():
    """Test TradingView chart data access."""
    print("📈 Testing Chart Data Access...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Try to access chart data endpoint
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.tradingview.com/',
                'Origin': 'https://www.tradingview.com'
            }
            
            # This is a common pattern for TradingView chart data
            url = "https://scanner.tradingview.com/america/scan"
            
            # Basic screener request
            payload = {
                "filter": [{"left": "name", "operation": "match", "right": "AAPL"}],
                "columns": ["name", "close", "change", "change_abs", "volume"],
                "sort": {"sortBy": "name", "sortOrder": "asc"},
                "range": [0, 50]
            }
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Scanner Response: {response.status}")
                    if data.get('data'):
                        for row in data['data'][:3]:  # Show first 3 results
                            print(f"   {row['d'][0]}: ${row['d'][1]:.2f} ({row['d'][2]:+.2f}%)")
                else:
                    print(f"❌ Scanner failed: {response.status}")
                    print(f"   Response: {await response.text()}")
                    
        except Exception as e:
            print(f"❌ Chart Data error: {e}")
    
    print()

async def test_websocket_data():
    """Test TradingView WebSocket for real-time data."""
    print("🔌 Testing WebSocket Real-time Data...")
    
    try:
        import websockets
        
        # TradingView uses WebSocket for real-time data
        # This is more complex and requires specific message formatting
        print("   WebSocket library available - could implement real-time data")
        print("   Note: Requires reverse engineering TradingView's WebSocket protocol")
        
    except ImportError:
        print("   WebSocket library not available - would need: pip install websockets")
    
    print()

async def test_yahoo_finance_alternative():
    """Test Yahoo Finance as alternative free source."""
    print("📊 Testing Yahoo Finance Alternative...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Yahoo Finance API endpoint
            symbol = "AAPL"
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    print(f"✅ Yahoo Finance Response: {response.status}")
                    print(f"   Symbol: {meta.get('symbol')}")
                    print(f"   Current Price: ${meta.get('regularMarketPrice', 'N/A')}")
                    print(f"   Previous Close: ${meta.get('previousClose', 'N/A')}")
                    print(f"   Volume: {meta.get('regularMarketVolume', 'N/A'):,}")
                else:
                    print(f"❌ Yahoo Finance failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Yahoo Finance error: {e}")
    
    print()

if __name__ == "__main__":
    asyncio.run(test_tradingview_free_access())
    asyncio.run(test_yahoo_finance_alternative())