# Open WebUI Function Configuration for Real-Time Financial Data

# This file defines custom functions that Open WebUI can use to provide
# real-time financial data to Ollama models during conversations.

import sys
from pathlib import Path
import importlib.util

# Add the financial functions module to the path
functions_path = Path(__file__).parent / "financial_functions.py"
spec = importlib.util.spec_from_file_location("financial_functions", functions_path)
financial_functions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(financial_functions)

# Function registry for Open WebUI
FUNCTIONS = {
    "get_stock_quote": {
        "function": financial_functions.get_stock_quote,
        "description": "Get real-time stock quote, price, and key metrics for any stock symbol",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)"
            }
        }
    },

    "get_market_overview": {
        "function": financial_functions.get_market_overview,
        "description": "Get current market overview with major indices (S&P 500, Dow Jones, NASDAQ, VIX)",
        "parameters": {}
    },

    "get_stock_news": {
        "function": financial_functions.get_stock_news,
        "description": "Get recent news and headlines for a specific stock",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock ticker symbol to get news for"
            }
        }
    },

    "compare_stocks": {
        "function": financial_functions.compare_stocks,
        "description": "Compare multiple stocks side by side with key metrics",
        "parameters": {
            "symbols": {
                "type": "string",
                "description": "Comma-separated stock symbols (e.g., 'AAPL,GOOGL,MSFT')"
            }
        }
    },

    "get_sector_performance": {
        "function": financial_functions.get_sector_performance,
        "description": "Get performance of major market sectors using sector ETFs",
        "parameters": {}
    }
}

# Helper function to execute functions
def execute_function(function_name: str, **kwargs):
    """Execute a registered function with given parameters"""
    if function_name in FUNCTIONS:
        func = FUNCTIONS[function_name]["function"]
        return func(**kwargs)
    else:
        return f"Function {function_name} not found"

# Export functions for Open WebUI integration
__all__ = ["FUNCTIONS", "execute_function"] + list(FUNCTIONS.keys())
