"""
Stock Data MCP Server for the Agent Investment Platform.

This server provides real-time stock data, prices, and financial metrics
through the Polygon API for reliable financial data access.
"""

import asyncio
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass

from .base import MCPServerBase, MCPTool, MCPError, MCPValidationError, create_tool_schema


@dataclass
class StockQuote:
    """Represents a stock quote."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class CompanyFundamentals:
    """Represents company fundamental data."""
    symbol: str
    name: str
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    eps: Optional[float]
    revenue: Optional[float]
    debt_to_equity: Optional[float]
    roe: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "dividend_yield": self.dividend_yield,
            "eps": self.eps,
            "revenue": self.revenue,
            "debt_to_equity": self.debt_to_equity,
            "roe": self.roe
        }


class PolygonClient:
    """Client for Polygon API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get previous day quote for a symbol (Polygon free tier)."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={self.api_key}"

        try:
            async with self.session.get(url) as response:
                if response.status == 401:
                    raise MCPError(-32503, "Invalid Polygon API key")
                elif response.status == 429:
                    raise MCPError(-32503, "Polygon API rate limit exceeded")
                elif response.status != 200:
                    raise MCPError(-32603, f"Polygon API error: {response.status}")

                data = await response.json()

                if data.get("status") != "OK" or not data.get("results"):
                    raise MCPError(-32602, f"No data available for symbol: {symbol}")

                result = data["results"][0]
                
                # Calculate change from open to close
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

        except aiohttp.ClientError as e:
            raise MCPError(-32603, f"Network error: {str(e)}")
        except (ValueError, KeyError) as e:
            raise MCPError(-32603, f"Data parsing error: {str(e)}")

    async def get_historical_data(self, symbol: str, interval: str = "daily",
                                outputsize: str = "compact") -> Dict[str, Any]:
        """Get historical price data using Polygon API."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Map intervals to Polygon timespan
        timespan_map = {
            "daily": "day",
            "weekly": "week", 
            "monthly": "month"
        }
        
        timespan = timespan_map.get(interval, "day")
        
        # Get data for last 30 days for daily, adjust for other intervals
        from datetime import datetime, timedelta
        end_date = datetime.now()
        if interval == "daily":
            start_date = end_date - timedelta(days=30)
        elif interval == "weekly":
            start_date = end_date - timedelta(weeks=52) 
        else:  # monthly
            start_date = end_date - timedelta(days=365)
            
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/{timespan}/{start_str}/{end_str}?adjusted=true&sort=asc&apikey={self.api_key}"

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise MCPError(-32603, f"Polygon API error: {response.status}")

                data = await response.json()
                
                if data.get("status") != "OK":
                    return {"Time Series": {}}
                
                # Convert Polygon format to Alpha Vantage-like format for compatibility
                time_series = {}
                for result in data.get("results", []):
                    date_str = datetime.fromtimestamp(result["t"] / 1000).strftime("%Y-%m-%d")
                    time_series[date_str] = {
                        "1. open": str(result.get("o", 0)),
                        "2. high": str(result.get("h", 0)), 
                        "3. low": str(result.get("l", 0)),
                        "4. close": str(result.get("c", 0)),
                        "5. volume": str(result.get("v", 0))
                    }
                
                return {"Time Series": time_series}

        except aiohttp.ClientError as e:
            raise MCPError(-32603, f"Network error: {str(e)}")

    async def get_company_overview(self, symbol: str) -> Optional[CompanyFundamentals]:
        """Get company fundamental data using Polygon API."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = f"{self.base_url}/v3/reference/tickers/{symbol}?apikey={self.api_key}"

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                
                if data.get("status") != "OK" or not data.get("results"):
                    return None
                
                result = data["results"]
                
                return CompanyFundamentals(
                    symbol=result.get("ticker", symbol),
                    name=result.get("name", ""),
                    market_cap=self._safe_float(result.get("market_cap")),
                    pe_ratio=None,  # Not available in basic Polygon response
                    dividend_yield=None,  # Not available in basic Polygon response
                    eps=None,  # Not available in basic Polygon response
                    revenue=None,  # Not available in basic Polygon response
                    debt_to_equity=None,  # Not available in basic Polygon response
                    roe=None  # Not available in basic Polygon response
                )

        except aiohttp.ClientError as e:
            raise MCPError(-32603, f"Network error: {str(e)}")

    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or value == "None" or value == "-":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None




class StockDataServer(MCPServerBase):
    """
    MCP Server for stock data operations.

    Provides tools for:
    - Getting real-time stock quotes
    - Retrieving historical price data
    - Accessing company fundamental data
    - Market indicators and analysis
    """

    def __init__(self):
        super().__init__(
            name="stock-data-server",
            version="1.0.0",
            description="Real-time stock data, prices, and financial metrics"
        )

        # Initialize API clients
        self.polygon_key = os.environ.get("POLYGON_API_KEY")

        if not self.polygon_key:
            self.logger.warning("POLYGON_API_KEY not set - stock data features will be limited")

    def _register_capabilities(self):
        """Register stock data tools."""

        # Stock quote tool
        quote_tool = MCPTool(
            name="get_stock_quote",
            description="Get real-time stock quote including price, change, and volume",
            inputSchema=create_tool_schema(
                name="get_stock_quote",
                description="Get stock quote",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL, TSLA)",
                        "pattern": "^[A-Z]{1,5}$"
                    }
                },
                required=["symbol"]
            )
        )
        self.register_tool(quote_tool, self._handle_get_stock_quote)

        # Historical data tool
        historical_tool = MCPTool(
            name="get_historical_data",
            description="Get historical price data for a stock",
            inputSchema=create_tool_schema(
                name="get_historical_data",
                description="Get historical stock data",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL, TSLA)",
                        "pattern": "^[A-Z]{1,5}$"
                    },
                    "interval": {
                        "type": "string",
                        "description": "Data interval",
                        "enum": ["daily", "weekly", "monthly"],
                        "default": "daily"
                    },
                    "outputsize": {
                        "type": "string",
                        "description": "Amount of data to return",
                        "enum": ["compact", "full"],
                        "default": "compact"
                    }
                },
                required=["symbol"]
            )
        )
        self.register_tool(historical_tool, self._handle_get_historical_data)

        # Company fundamentals tool
        fundamentals_tool = MCPTool(
            name="get_company_fundamentals",
            description="Get company fundamental data including financial metrics",
            inputSchema=create_tool_schema(
                name="get_company_fundamentals",
                description="Get company fundamentals",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL, TSLA)",
                        "pattern": "^[A-Z]{1,5}$"
                    }
                },
                required=["symbol"]
            )
        )
        self.register_tool(fundamentals_tool, self._handle_get_company_fundamentals)

        # Batch quotes tool
        batch_quotes_tool = MCPTool(
            name="get_batch_quotes",
            description="Get real-time quotes for multiple stocks",
            inputSchema=create_tool_schema(
                name="get_batch_quotes",
                description="Get multiple stock quotes",
                properties={
                    "symbols": {
                        "type": "array",
                        "description": "Array of stock symbols",
                        "items": {
                            "type": "string",
                            "pattern": "^[A-Z]{1,5}$"
                        },
                        "maxItems": 10
                    }
                },
                required=["symbols"]
            )
        )
        self.register_tool(batch_quotes_tool, self._handle_get_batch_quotes)

    async def _handle_get_stock_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stock quote request."""
        symbol = params.get("symbol", "").upper()

        if not symbol:
            raise MCPValidationError("Symbol is required")

        if not self.polygon_key:
            raise MCPError(-32503, "Polygon API key not configured")

        async with PolygonClient(self.polygon_key) as client:
            quote = await client.get_quote(symbol)

            if not quote:
                raise MCPError(-32602, f"No data found for symbol: {symbol}")

            return {
                "success": True,
                "data": quote.to_dict()
            }

    async def _handle_get_historical_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle historical data request."""
        symbol = params.get("symbol", "").upper()
        interval = params.get("interval", "daily")
        outputsize = params.get("outputsize", "compact")

        if not symbol:
            raise MCPValidationError("Symbol is required")

        if not self.polygon_key:
            raise MCPError(-32503, "Polygon API key not configured")

        async with PolygonClient(self.polygon_key) as client:
            data = await client.get_historical_data(symbol, interval, outputsize)

            return {
                "success": True,
                "data": data,
                "metadata": {
                    "symbol": symbol,
                    "interval": interval,
                    "outputsize": outputsize
                }
            }

    async def _handle_get_company_fundamentals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle company fundamentals request."""
        symbol = params.get("symbol", "").upper()

        if not symbol:
            raise MCPValidationError("Symbol is required")

        if not self.polygon_key:
            raise MCPError(-32503, "Polygon API key not configured")

        async with PolygonClient(self.polygon_key) as client:
            fundamentals = await client.get_company_overview(symbol)

            if not fundamentals:
                raise MCPError(-32602, f"No fundamental data found for symbol: {symbol}")

            return {
                "success": True,
                "data": fundamentals.to_dict()
            }

    async def _handle_get_batch_quotes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch quotes request."""
        symbols = params.get("symbols", [])

        if not symbols:
            raise MCPValidationError("Symbols array is required")

        if len(symbols) > 10:
            raise MCPValidationError("Maximum 10 symbols allowed per request")

        if not self.polygon_key:
            raise MCPError(-32503, "Polygon API key not configured")

        results = []
        errors = []

        async with PolygonClient(self.polygon_key) as client:
            # Process symbols concurrently but with rate limiting
            for symbol in symbols:
                try:
                    symbol = symbol.upper()
                    quote = await client.get_quote(symbol)
                    if quote:
                        results.append(quote.to_dict())
                    else:
                        errors.append(f"No data for {symbol}")

                    # Rate limiting - Alpha Vantage allows 5 calls per minute for free tier
                    await asyncio.sleep(0.2)  # 200ms between calls

                except MCPError as e:
                    errors.append(f"Error for {symbol}: {e.message}")
                except Exception as e:
                    errors.append(f"Unexpected error for {symbol}: {str(e)}")

        return {
            "success": True,
            "data": results,
            "errors": errors,
            "metadata": {
                "requested_symbols": symbols,
                "successful_quotes": len(results),
                "failed_quotes": len(errors)
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "api_keys": {
                "polygon": bool(self.polygon_key)
            }
        }

        # Test API connectivity if keys are available
        if self.polygon_key:
            try:
                async with PolygonClient(self.polygon_key) as client:
                    # Test with a simple quote request
                    quote = await client.get_quote("AAPL")
                    status["api_connectivity"] = {
                        "alpha_vantage": "healthy" if quote else "limited"
                    }
            except Exception as e:
                status["api_connectivity"] = {
                    "alpha_vantage": f"error: {str(e)}"
                }
                status["status"] = "degraded"

        return status


async def main():
    """Main entry point for the Stock Data Server."""
    server = StockDataServer()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
