"""
Simple test of TradingView and Yahoo Finance free data access.
"""

import asyncio
import aiohttp
import os
from datetime import datetime

async def compare_data_sources():
    """Compare data from different free sources."""
    print("📊 Comparing Free Stock Data Sources...")
    print()

    symbol = "AAPL"

    # Test all sources
    polygon_data = await get_polygon_data(symbol) if os.getenv("POLYGON_API_KEY") else None
    yahoo_data = await get_yahoo_data(symbol)
    tradingview_data = await get_tradingview_data(symbol)

    print(f"📈 Stock Data Comparison for {symbol}:")
    print("-" * 50)

    if polygon_data:
        print(f"🔵 Polygon:     ${polygon_data['price']:.2f} ({polygon_data['change']:+.2f}%)")

    if yahoo_data:
        print(f"🟡 Yahoo:       ${yahoo_data['price']:.2f} ({yahoo_data['change']:+.2f}%)")

    if tradingview_data:
        print(f"🟢 TradingView: ${tradingview_data['price']:.2f} ({tradingview_data['change']:+.2f}%)")

    print()

    # Test multiple symbols with TradingView (best free option)
    print("🎯 Testing Multiple Symbols (TradingView):")
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

    for test_symbol in symbols:
        data = await get_tradingview_data(test_symbol)
        if data:
            print(f"   {test_symbol}: ${data['price']:.2f} ({data['change']:+.2f}%)")
        else:
            print(f"   {test_symbol}: ❌ Failed")

    print()
    print("✅ Data source comparison completed!")

async def get_polygon_data(symbol):
    """Get data from Polygon (requires API key)."""
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        return None

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={api_key}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        result = data["results"][0]
                        open_price = result.get("o", 0)
                        close_price = result.get("c", 0)
                        change_percent = ((close_price - open_price) / open_price * 100) if open_price > 0 else 0

                        return {
                            "price": close_price,
                            "change": change_percent,
                            "volume": result.get("v", 0),
                            "source": "Polygon"
                        }
    except Exception as e:
        print(f"❌ Polygon error: {e}")

    return None

async def get_yahoo_data(symbol):
    """Get data from Yahoo Finance (free)."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']

                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose')

                    if current_price and previous_close:
                        change_percent = ((current_price - previous_close) / previous_close * 100)

                        return {
                            "price": current_price,
                            "change": change_percent,
                            "volume": meta.get('regularMarketVolume', 0),
                            "source": "Yahoo Finance"
                        }
    except Exception as e:
        print(f"❌ Yahoo error: {e}")

    return None

async def get_tradingview_data(symbol):
    """Get data from TradingView (free)."""
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

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and len(data['data']) > 0:
                        row = data['data'][0]['d']

                        return {
                            "price": float(row[1]),  # close
                            "change": float(row[2]),  # change percent
                            "volume": int(row[4]) if row[4] else 0,
                            "source": "TradingView"
                        }
    except Exception as e:
        print(f"❌ TradingView error: {e}")

    return None

if __name__ == "__main__":
    asyncio.run(compare_data_sources())
