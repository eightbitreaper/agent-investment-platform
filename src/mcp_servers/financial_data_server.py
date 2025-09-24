#!/usr/bin/env python3
"""
Real-Time Financial Data MCP Server
Provides TradingView financial data as MCP tools for Ollama integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.mcp_servers.base import MCPServerBase, MCPTool, MCPError, create_tool_schema

# Import our financial functions
try:
    from src.ollama_integration.financial_functions import (
        TradingViewAPI, get_stock_quote, get_market_overview,
        get_stock_news, compare_stocks, get_sector_performance
    )
except ImportError as e:
    logging.error(f"Failed to import financial functions: {e}")
    # Create fallback functions
    def get_stock_quote(symbol): return f"Error: Unable to get quote for {symbol}"
    def get_market_overview(): return "Error: Unable to get market overview"
    def get_stock_news(symbol): return f"Error: Unable to get news for {symbol}"
    def compare_stocks(symbols): return f"Error: Unable to compare {symbols}"
    def get_sector_performance(): return "Error: Unable to get sector performance"

    class TradingViewAPI:
        def __init__(self): pass

# Configure logging
logger = logging.getLogger(__name__)

class FinancialDataServer(MCPServerBase):
    """MCP Server for real-time financial data from TradingView"""

    def __init__(self):
        super().__init__(
            name="financial-data-server",
            version="1.0.0",
            description="Real-time financial data from TradingView including stock quotes, market overview, news, and sector performance"
        )

        # Initialize TradingView API
        self.tv_api = TradingViewAPI()

        logger.info("Financial Data MCP Server initialized")

    def _register_capabilities(self):
        """Register financial data tools."""

        # Stock quote tool
        quote_tool = MCPTool(
            name="get_stock_quote",
            description="Get real-time stock quote with current price, P/E ratio, market cap, and company information from TradingView",
            inputSchema=create_tool_schema(
                name="get_stock_quote",
                description="Get real-time stock quote",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)"
                    }
                },
                required=["symbol"]
            )
        )
        self.register_tool(quote_tool, self._handle_get_stock_quote)

        # Market overview tool
        market_tool = MCPTool(
            name="get_market_overview",
            description="Get current market overview with major indices performance (S&P 500, Dow Jones, NASDAQ, VIX)",
            inputSchema=create_tool_schema(
                name="get_market_overview",
                description="Get market overview",
                properties={},
                required=[]
            )
        )
        self.register_tool(market_tool, self._handle_get_market_overview)

        # Stock news tool
        news_tool = MCPTool(
            name="get_stock_news",
            description="Get recent financial news headlines for a specific stock symbol from Google News",
            inputSchema=create_tool_schema(
                name="get_stock_news",
                description="Get stock news",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol to get news for (e.g., AAPL, TSLA)"
                    }
                },
                required=["symbol"]
            )
        )
        self.register_tool(news_tool, self._handle_get_stock_news)

        # Compare stocks tool
        compare_tool = MCPTool(
            name="compare_stocks",
            description="Compare multiple stocks side by side with current prices, changes, volume, and P/E ratios",
            inputSchema=create_tool_schema(
                name="compare_stocks",
                description="Compare multiple stocks",
                properties={
                    "symbols": {
                        "type": "string",
                        "description": "Comma-separated stock symbols to compare (e.g., 'AAPL,GOOGL,MSFT')"
                    }
                },
                required=["symbols"]
            )
        )
        self.register_tool(compare_tool, self._handle_compare_stocks)

        # Sector performance tool
        sector_tool = MCPTool(
            name="get_sector_performance",
            description="Get performance of major market sectors using sector ETFs (Technology, Healthcare, Financial, etc.)",
            inputSchema=create_tool_schema(
                name="get_sector_performance",
                description="Get sector performance",
                properties={},
                required=[]
            )
        )
        self.register_tool(sector_tool, self._handle_get_sector_performance)

    async def _handle_get_stock_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stock quote requests"""
        try:
            symbol = params.get("symbol", "").upper()
            if not symbol:
                raise MCPError(message="Stock symbol is required")

            result = get_stock_quote(symbol)
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "tool": "get_stock_quote",
                    "symbol": symbol,
                    "source": "TradingView"
                }
            }
        except Exception as e:
            logger.error(f"Error getting stock quote for {params.get('symbol', 'unknown')}: {e}")
            raise MCPError(message=f"Failed to get stock quote: {str(e)}")

    async def _handle_get_market_overview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market overview requests"""
        try:
            result = get_market_overview()
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "tool": "get_market_overview",
                    "source": "TradingView"
                }
            }
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            raise MCPError(message=f"Failed to get market overview: {str(e)}")

    async def _handle_get_stock_news(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stock news requests"""
        try:
            symbol = params.get("symbol", "").upper()
            if not symbol:
                raise MCPError(message="Stock symbol is required")

            result = get_stock_news(symbol)
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "tool": "get_stock_news",
                    "symbol": symbol,
                    "source": "Google News"
                }
            }
        except Exception as e:
            logger.error(f"Error getting news for {params.get('symbol', 'unknown')}: {e}")
            raise MCPError(message=f"Failed to get stock news: {str(e)}")

    async def _handle_compare_stocks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stock comparison requests"""
        try:
            symbols = params.get("symbols", "")
            if not symbols:
                raise MCPError(message="Stock symbols are required (comma-separated)")

            result = compare_stocks(symbols)
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "tool": "compare_stocks",
                    "symbols": symbols,
                    "source": "TradingView"
                }
            }
        except Exception as e:
            logger.error(f"Error comparing stocks {params.get('symbols', 'unknown')}: {e}")
            raise MCPError(message=f"Failed to compare stocks: {str(e)}")

    async def _handle_get_sector_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sector performance requests"""
        try:
            result = get_sector_performance()
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "tool": "get_sector_performance",
                    "source": "TradingView"
                }
            }
        except Exception as e:
            logger.error(f"Error getting sector performance: {e}")
            raise MCPError(message=f"Failed to get sector performance: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        try:
            # Test TradingView API connection with a simple quote
            test_result = get_stock_quote("AAPL")

            return {
                "status": "healthy",
                "message": "Financial Data MCP Server operational",
                "services": {
                    "tradingview_api": "connected" if "Error" not in test_result else "error",
                    "google_news": "available"
                },
                "tools_count": len(self.tools)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "degraded",
                "message": f"Health check failed: {str(e)}",
                "services": {
                    "tradingview_api": "error",
                    "google_news": "unknown"
                }
            }

async def main():
    """Main entry point for the Financial Data MCP Server"""
    server = FinancialDataServer()

    try:
        logger.info("Starting Financial Data MCP Server...")
        await server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Financial Data MCP Server shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main())
